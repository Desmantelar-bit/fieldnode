"""
api_tcc/services/telemetria.py

Camada de serviço de domínio para telemetria.
Views e workers MQTT chamam estas funções — nunca acessam o modelo diretamente.

Decisão de arquitetura: separar regra de negócio da camada de transporte
permite reutilização entre a API REST e o listener MQTT sem duplicação de lógica.

S1-T5 — Contrato de identidade e sincronização:
- registrar_leitura() usa (device_id, message_id) como chave de idempotência composta.
- UUID da linha continua sendo o identificador interno; não é a chave de idempotência.
- SyncCursor armazena o último sequence_number confirmado por device_id (monotônico).
- Fallbacks de compatibilidade preservam comportamento dos simuladores legados.
"""
import hashlib
import json
import logging
import math
import uuid as uuid_lib
from datetime import datetime

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils.timezone import make_aware, is_aware, now

from api_tcc.models import DeliveryHop, DeadLetterEntry, LeituraTelemetria, TelemetryAggregate, Colheitadeira, Machine, SyncCursor
from api_tcc.services.data_health import (
    HISTORY_LIMIT,
    atualizar_machine_data_health,
    calcular_trust_score,
)
from api_tcc.services.eventos import avaliar_leitura
from api_tcc.services.eventos import criar_evento_anomalia_estatistica
from api_tcc.services.anomaly_detection import REGISTRY, detect_anomaly
from api_tcc.services.decisions import persistir_decision_da_anomalia
from api_tcc.services.dlq import registrar_falha_dlq
from api_tcc.services.sensor_limits import LIMITES
from api_tcc.services.normalizacao import registrar_e_normalizar
from api_tcc.services.regime import inferir_regime
from api_tcc.services.event_time import resolve_event_time, reconstruct_boot
from api_tcc.services.reconstrucao import identificar_atraso, reconstruir_para_leitura
from api_tcc.contracts import severity_contract
from api_tcc.sync_contract import validate_sync_envelope
from connectivity.signing import verify_payload

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# VALIDAÇÃO DE PAYLOAD
# Limites baseados em especificação operacional de motores diesel agrícolas.
# Valores fora desses ranges indicam falha de sensor, não condição real.
# ──────────────────────────────────────────────────────────────
def validar_payload(dados: dict) -> tuple[bool, str]:
    """
    Verifica se os campos obrigatórios existem e estão dentro dos limites físicos.

    Retorna (True, "") se válido.
    Retorna (False, motivo) se inválido.

    Usamos tipos explícitos aqui porque o ESP32 às vezes manda string "85.5"
    em vez de float 85.5 dependendo da biblioteca JSON usada no firmware.

    S1-T3 — Checagem de schema_version (contrato versionado).
    Se ausente, injeta "1.0" para retrocompatibilidade e loga aviso.
    Ver docs/CONTRATO_TELEMETRIA_V1.md para o contrato formal.
    """
    # ── S1-T3: Versionamento de schema ──────────────────────────
    if "schema_version" not in dados or dados["schema_version"] is None:
        dados["schema_version"] = "1.0"
        logger.warning(
            "DeprecationWarning: Payload recebido sem schema_version. "
            "Assumindo '1.0'. Maquina ID: %s",
            dados.get("maquina_id", "Desconhecida"),
        )

    # S6-T1: payloads que optam explicitamente pelo envelope versionado passam
    # pelo mesmo contrato compartilhado usado pelo edge client. Fallbacks
    # legados sem priority_class seguem a compatibilidade S1 existente.
    if "priority_class" in dados and "message_id" in dados and "sequence_number" in dados:
        envelope = dict(dados)
        envelope["payload_hash"] = _computar_payload_hash(dados)
        valido_sync, motivo_sync = validate_sync_envelope(envelope)
        if not valido_sync:
            return False, motivo_sync

    campos_obrigatorios = ["maquina_id", "temperatura", "vibracao"]
    for campo in campos_obrigatorios:
        if campo not in dados or dados[campo] is None:
            return False, f"campo obrigatório ausente: {campo}"

    allowed_units = set(severity_contract()["metrics"]["vibracao"]["allowed_units"])
    vibration_unit = dados.get("vibracao_unit", "indice_0_10")
    feature_names = ("vibracao_rms_g", "vibracao_pico_g", "vibracao_curtose")
    feature_present = any(dados.get(name) is not None for name in feature_names)
    if feature_present:
        allowed_units.add("g")
        if vibration_unit != "g" or not all(dados.get(name) is not None for name in feature_names):
            return False, "features de vibração exigem vibracao_unit='g' e os três campos"
        for name in feature_names:
            value = dados[name]
            if not isinstance(value, dict) or set(value) != {"x", "y", "z"}:
                return False, f"{name} deve conter exatamente os eixos x, y e z"
            for axis, axis_value in value.items():
                try:
                    numeric = float(axis_value)
                except (TypeError, ValueError):
                    return False, f"{name}.{axis} deve ser numérico"
                if not math.isfinite(numeric) or numeric < 0:
                    return False, f"{name}.{axis} deve ser finito e não negativo"
    if vibration_unit not in allowed_units:
        return False, f"vibracao_unit inválida: {vibration_unit!r}; esperado {allowed_units}"
    dados["vibracao_unit"] = vibration_unit

    maquina_id = str(dados.get("maquina_id", "")).strip()
    if not maquina_id:
        return False, "maquina_id não pode ser vazio"

    if dados.get("timestamp") is None and dados.get("event_time") is None and dados.get("time_source", "unsynced") != "unsynced":
        return False, "timestamp obrigatório para time_source sincronizada"
    if dados.get("boot_id") is not None:
        try:
            uuid_lib.UUID(str(dados["boot_id"]))
        except (ValueError, TypeError, AttributeError):
            return False, "boot_id deve ser UUID válido"
    if dados.get("uptime_ms") is not None:
        try:
            if isinstance(dados["uptime_ms"], bool) or not float(dados["uptime_ms"]).is_integer() or int(dados["uptime_ms"]) < 0:
                return False, "uptime_ms deve ser inteiro não negativo"
        except (ValueError, TypeError, OverflowError):
            return False, "uptime_ms deve ser inteiro não negativo"
    if dados.get("clock_skew_ms") is not None:
        try:
            if isinstance(dados["clock_skew_ms"], bool) or not float(dados["clock_skew_ms"]).is_integer():
                return False, "clock_skew_ms deve ser inteiro"
            int(dados["clock_skew_ms"])
        except (ValueError, TypeError, OverflowError):
            return False, "clock_skew_ms deve ser inteiro"
    if dados.get("time_source", "unsynced") not in {"rtc", "gateway", "ntp", "unsynced"}:
        return False, "time_source desconhecido"
    temporal_input = dados.get("timestamp", dados.get("event_time"))
    if temporal_input is not None and not isinstance(temporal_input, datetime):
        from django.utils.dateparse import parse_datetime
        if parse_datetime(str(temporal_input)) is None:
            return False, "timestamp/event_time inválido; esperado ISO-8601"

    # CORREÇÃO: Removida validação contra Colheitadeira que impedia dados de entrar
    # O simulador envia IDs como "CASE-TC5000-01" mas o banco tem Modelo.nome = "TC5000"
    # Agora aceitamos qualquer maquina_id e deixamos o sistema criar registros dinamicamente

    for campo, (minimo, maximo) in LIMITES.items():
        if campo == "rpm" and dados.get(campo) is None:
            continue
        try:
            valor = float(dados[campo])
        except (TypeError, ValueError):
            return False, f"{campo} não é numérico: {dados[campo]!r}"

        if not (minimo <= valor <= maximo):
            return False, (
                f"{campo}={valor} fora do range operacional [{minimo}, {maximo}]. "
                f"Possível falha de sensor."
            )

    # Validação opcional de latitude e longitude
    if "latitude" in dados and dados["latitude"] is not None:
        try:
            lat = float(dados["latitude"])
            if not (-90 <= lat <= 90):
                return False, f"latitude={lat} fora do range [-90, 90]"
        except (TypeError, ValueError):
            return False, f"latitude não é numérica: {dados['latitude']!r}"

    if "longitude" in dados and dados["longitude"] is not None:
        try:
            lng = float(dados["longitude"])
            if not (-180 <= lng <= 180):
                return False, f"longitude={lng} fora do range [-180, 180]"
        except (TypeError, ValueError):
            return False, f"longitude não é numérica: {dados['longitude']!r}"

    if "velocidade_kmh" in dados and dados["velocidade_kmh"] is not None:
        try:
            velocidade = float(dados["velocidade_kmh"])
            if not 0 <= velocidade <= 300:
                return False, f"velocidade_kmh={velocidade} fora do range [0, 300]"
        except (TypeError, ValueError):
            return False, f"velocidade_kmh não é numérica: {dados['velocidade_kmh']!r}"

    if "gps_fix" in dados and dados["gps_fix"] is not None and not isinstance(dados["gps_fix"], bool):
        return False, "gps_fix deve ser booleano ou nulo"
    if "gps_hdop" in dados and dados["gps_hdop"] is not None:
        try:
            hdop = float(dados["gps_hdop"])
            if not math.isfinite(hdop) or not 0 <= hdop <= 99.9:
                return False, "gps_hdop fora do range [0, 99.9]"
        except (TypeError, ValueError, OverflowError):
            return False, f"gps_hdop não é numérico: {dados['gps_hdop']!r}"
    if dados.get("gps_fix") is False and any(
        dados.get(campo) is not None for campo in ("latitude", "longitude", "velocidade_kmh")
    ):
        return False, "GPS sem fix não pode carregar posição ou velocidade utilizável"

    return True, ""


# ──────────────────────────────────────────────────────────────
# REGISTRO DE LEITURA
# ──────────────────────────────────────────────────────────────


def _computar_payload_hash(dados: dict) -> str:
    """
    Computa SHA-256 do corpo logico canonico, antes de qualquer compressao.
    Não é usado como chave de idempotência — apenas como fingerprint.
    """
    canonical = dict(dados)
    # ``id`` identifies the physical DB row for legacy callers. With an explicit
    # message_id, a client may regenerate this incidental field on retry.
    if canonical.get("message_id"):
        canonical.pop("id", None)
    canonical.pop("via", None)
    raw = json.dumps(canonical, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def registrar_agregado(dados: dict) -> tuple[str, str | None]:
    """Persiste um agregado C sem fingir que ele e uma leitura instantanea."""
    from django.utils.dateparse import parse_datetime

    if str(dados.get("priority_class", "C")) != "C":
        return "invalido", "agregados sao permitidos apenas para classe C"
    agregado = dados.get("aggregate")
    if not isinstance(agregado, dict):
        return "invalido", "campo aggregate ausente"
    try:
        inicio = parse_datetime(str(agregado["window_start"]))
        fim = parse_datetime(str(agregado["window_end"]))
        sample_count = int(agregado["sample_count"])
        valid_count = int(agregado["valid_count"])
    except (KeyError, TypeError, ValueError):
        return "invalido", "janela ou contagem do agregado invalida"
    if inicio is None or fim is None or fim <= inicio or sample_count < 1 or not isinstance(agregado.get("statistics"), dict):
        return "invalido", "agregado sem janela/estatisticas validas"
    aggregate_hash = _computar_payload_hash({"device_id": dados.get("device_id"), "aggregate": agregado})
    existente = TelemetryAggregate.objects.filter(aggregate_hash=aggregate_hash).first()
    if existente:
        return "duplicata", str(existente.id)
    machine, _ = Machine.objects.get_or_create(external_code=str(dados.get("maquina_id", dados.get("device_id", ""))).strip().upper())
    try:
        obj = TelemetryAggregate.objects.create(
            machine=machine,
            device_id=str(dados.get("device_id", "")).strip(),
            boot_id=dados.get("boot_id"),
            window_start=inicio,
            window_end=fim,
            sample_count=sample_count,
            valid_count=valid_count,
            missing_count=int(agregado.get("missing_count", 0)),
            statistics=agregado["statistics"],
            source_message_ids=list(agregado.get("source_message_ids", [])),
            aggregate_hash=aggregate_hash,
        )
    except IntegrityError:
        existente = TelemetryAggregate.objects.get(aggregate_hash=aggregate_hash)
        return "duplicata", str(existente.id)
    return "criado", str(obj.id)


def _atualizar_sync_cursor(device_id: str, sequence_number: int) -> None:
    """
    Avança apenas pela maior sequência contígua persistida para o dispositivo.

    Deve ser chamado dentro de uma transação atômica (garantido por registrar_leitura).
    """
    cursor, criado = SyncCursor.objects.get_or_create(device_id=device_id, defaults={"last_acked_sequence": 0})
    anterior = cursor.last_acked_sequence
    presentes = set(LeituraTelemetria.objects.filter(device_id=device_id, sequence_number__gt=0)
                    .values_list("sequence_number", flat=True))
    nova_sequencia = anterior
    while nova_sequencia + 1 in presentes:
        nova_sequencia += 1
    if nova_sequencia > anterior:
        cursor.last_acked_sequence = nova_sequencia
        cursor.save(update_fields=["last_acked_sequence", "atualizado_em"])
        logger.debug(
            "SyncCursor avançado: device=%s seq=%d → %d",
            device_id,
            anterior,
            nova_sequencia,
        )
    elif criado:
        logger.debug("SyncCursor criado sem saltar lacunas: device=%s seq=%d", device_id, nova_sequencia)


def registrar_leitura(
    dados: dict,
    *,
    authenticated_device_id: str | None = None,
) -> tuple[str, str | None]:
    """
    Persiste uma leitura de telemetria com idempotência composta por (device_id, message_id).

    Retorna:
        ("criado",    id_str)    — leitura nova salva com sucesso
        ("duplicata", id_str)   — (device_id, message_id) já existia; replay ignorado
        ("invalido",  motivo)   — payload inválido, descartado
        ("erro",      detalhe)  — falha inesperada de banco

    Contrato de identidade (S1-T5):
    ─────────────────────────────────────────────────────────────────
    • device_id   = dados["device_id"]   ou fallback: maquina_id.strip().upper()
    • message_id  = dados["message_id"]  ou fallback: UUID gerado por envio
                    ↳ ATENÇÃO: sem message_id, o reenvio NÃO é idempotente.
                      Cada envio sem message_id gera um novo UUID → nova linha.
                      Isso é comportamento intencional e documentado para preservar
                      compatibilidade com simuladores legados.
    • UUID da linha (id): continua sendo o identificador interno; não é idempotência.

    Transação atômica:
    ─────────────────────────────────────────────────────────────────
    LeituraTelemetria + SyncCursor são atualizados atomicamente.
    Não pode haver estado parcial (leitura criada sem cursor ou vice-versa).

    Compatibilidade legada:
    ─────────────────────────────────────────────────────────────────
    • Payload sem device_id → fallback para maquina_id (idempotência preservada por machine_id)
    • Payload sem message_id → UUID por envio (NÃO idempotente — documentado)
    • Payload com id (UUID) explícito: usado como PK da linha, não como idempotência
    """
    # Work on a copy: validation may add legacy defaults, but callers retain
    # their original object for retries and deterministic hashing.
    dados = dict(dados)
    device_for_signature = str(dados.get("device_id") or dados.get("maquina_id") or "").strip()
    signing_keys = getattr(settings, "FIELDNODE_DEVICE_SIGNING_KEYS", {})
    signing_key = signing_keys.get(device_for_signature) or signing_keys.get(device_for_signature.upper())
    signature_present = bool(dados.get("signature") or dados.get("signature_alg"))
    if getattr(settings, "REQUIRE_MESSAGE_SIGNATURES", False) and not signature_present:
        motivo = "assinatura_invalida: assinatura ausente"
        registrar_falha_dlq(
            contexto=DeadLetterEntry.Contexto.SYNC,
            payload_referencia={"device_id": device_for_signature, "message_id": dados.get("message_id")},
            motivo=motivo,
        )
        return "invalido", motivo
    if signature_present and not verify_payload(dados, str(signing_key or "")):
        motivo = "assinatura_invalida"
        registrar_falha_dlq(
            contexto=DeadLetterEntry.Contexto.SYNC,
            payload_referencia={"device_id": device_for_signature, "message_id": dados.get("message_id")},
            motivo=motivo,
        )
        return "invalido", motivo
    # Fingerprint exactly the submitted payload before validation adds legacy
    # defaults such as schema_version or vibracao_unit.
    payload_hash = _computar_payload_hash(dados)
    valido, motivo = validar_payload(dados)
    if not valido:
        _registrar_leitura_invalida(dados, motivo)
        logger.warning(
            "Payload rejeitado — motivo: %s | maquina_id: %s",
            motivo,
            dados.get("maquina_id", "desconhecida"),
        )
        return "invalido", motivo

    # ── Resolução de identidade ────────────────────────────────
    # device_id: usa campo explícito quando presente; fallback para maquina_id normalizado.
    maquina_id_normalizado = str(dados.get("maquina_id", "")).strip().upper()
    device_id = str(
        dados.get("device_id") or maquina_id_normalizado or "DESCONHECIDO"
    ).strip()

    # message_id: usa campo explícito quando presente.
    # SEM message_id, MAS COM id: usa o id como message_id para manter
    # a retrocompatibilidade da idempotência legada (simuladores antigos).
    # SEM message_id E SEM id: gera UUID por envio — NÃO idempotente.
    message_id_recebido = dados.get("message_id")
    uuid_recebido = dados.get("id") or None

    if message_id_recebido:
        message_id = str(message_id_recebido).strip()
    elif uuid_recebido:
        # Fallback de retrocompatibilidade: simuladores antigos mandavam apenas 'id'
        message_id = str(uuid_recebido).strip()
        logger.debug(
            "message_id ausente, usando id %s como fallback de idempotência | device: %s",
            message_id,
            device_id,
        )
    else:
        message_id = str(uuid_lib.uuid4())
        logger.debug(
            "message_id e id ausentes → UUID gerado por envio (não idempotente): %s | device: %s",
            message_id,
            device_id,
        )

    # Ausência de sequence_number é compatibilidade legada, não um ACK real.
    sequence_number_recebido = dados.get("sequence_number")
    sequence_informada = sequence_number_recebido is not None
    sequence_number = int(sequence_number_recebido or 0)

    # source / transport: origem e protocolo de transporte
    source = str(dados.get("source") or "api").strip()[:50]
    transport = str(dados.get("transport") or "http").strip()[:50]
    manufacturer = str(dados.get("manufacturer") or "fieldnode_simulator_v1").strip()[:100]
    source_protocol_simulado = str(
        dados.get("source_protocol_simulado") or transport
    ).strip()[:80]
    # A origem é decidida no servidor. Identificadores de simulador legados
    # indicam simulação; origem física só é marcada quando a credencial HTTP
    # individual validada pelo permission class corresponde ao dispositivo.
    simulator_markers = {"sim", "simulador", "simulated", "simulator"}
    if (
        source.lower() in simulator_markers
        or str(dados.get("manufacturer") or "").strip()[:100] == "fieldnode_simulator_v1"
    ):
        data_origin = "simulado"
    elif authenticated_device_id and authenticated_device_id.upper() == device_id.upper():
        data_origin = "medido"
    else:
        data_origin = None

    try:
        received_at = now()
        temporal = resolve_event_time(dados, ingested_at=received_at)
        boot_id, uptime_ms, time_source, timestamp, event_time_confidence, clock_skew_ms, time_provenance = temporal

        # Resolução de Machine on-the-fly (S1-T2 — preservado)
        machine_obj, maq_criada = Machine.objects.get_or_create(
            external_code=maquina_id_normalizado
        )
        if maq_criada:
            logger.info("Machine criada on-the-fly: %s", maquina_id_normalizado)

        with transaction.atomic():
            # Idempotency first: duplicate messages return the existing row
            # without recalculating Trust Score. The database constraint remains
            # the final protection against concurrent inserts.
            leitura = LeituraTelemetria.objects.filter(
                device_id=device_id,
                message_id=message_id,
            ).first()
            foi_criada = leitura is None

            if not foi_criada:
                if leitura.payload_hash != payload_hash:
                    registrar_falha_dlq(
                        contexto=DeadLetterEntry.Contexto.SYNC,
                        payload_referencia={"device_id": device_id, "message_id": message_id,
                                            "stored_payload_hash": leitura.payload_hash,
                                            "received_payload_hash": payload_hash},
                        motivo="conflito de payload_hash para identidade de mensagem existente",
                    )
                    return "conflito", str(leitura.id)
                logger.info(
                    "Replay ignorado (idempotencia): device=%s msg=%s | leitura_id=%s",
                    device_id,
                    message_id,
                    leitura.id,
                )
                return "duplicata", str(leitura.id)

            if foi_criada:
                historico_recente = list(
                    LeituraTelemetria.objects.filter(machine=machine_obj)
                    .filter(timestamp__isnull=False).order_by("-timestamp")[:HISTORY_LIMIT]
                )
                leitura = LeituraTelemetria(
                    id=uuid_recebido or uuid_lib.uuid4(),
                    device_id=device_id,
                    message_id=message_id,
                    maquina_id=maquina_id_normalizado,
                    machine=machine_obj,
                    temperatura=float(dados["temperatura"]),
                    vibracao=float(dados["vibracao"]),
                    vibracao_unit=dados["vibracao_unit"],
                    vibracao_rms_g=dados.get("vibracao_rms_g"),
                    vibracao_pico_g=dados.get("vibracao_pico_g"),
                    vibracao_curtose=dados.get("vibracao_curtose"),
                    rpm=int(dados["rpm"]) if dados.get("rpm") is not None else None,
                    velocidade_kmh=(
                        float(dados["velocidade_kmh"])
                        if dados.get("velocidade_kmh") is not None
                        else None
                    ),
                    regime=inferir_regime(dados.get("rpm"), dados.get("velocidade_kmh")),
                    latitude=float(dados["latitude"])
                    if dados.get("latitude") is not None
                    else None,
                    longitude=float(dados["longitude"])
                    if dados.get("longitude") is not None
                    else None,
                    timestamp=timestamp,
                    boot_id=boot_id,
                    uptime_ms=uptime_ms,
                    time_source=time_source,
                    clock_skew_ms=clock_skew_ms,
                    event_time_confidence=event_time_confidence,
                    time_provenance=time_provenance,
                    atrasado=identificar_atraso(
                        event_time=timestamp,
                        received_at=received_at,
                        time_source=time_source,
                        clock_skew_ms=clock_skew_ms,
                    ),
                    sequence_number=sequence_number,
                    source=source,
                    data_origin=data_origin,
                    transport=transport,
                    payload_hash=payload_hash,
                    sync_status="sincronizado",
                    priority_class=str(dados.get("priority_class", "C")),
                )
                trust_score, trust_motivos = calcular_trust_score(
                    leitura,
                    historico_recente,
                )
                leitura.trust_score = trust_score
                leitura.trust_factors = trust_motivos
                from api_tcc.services.eventos import evidence_quality
                leitura.evidence_quality = evidence_quality(trust_score)
                anomaly_result = None
                if leitura.rpm is not None:
                    anomaly_result = detect_anomaly(
                        machine_obj.external_code,
                        {
                            "temperatura": leitura.temperatura,
                            "vibracao": leitura.vibracao,
                            "rpm": leitura.rpm,
                            "regime": leitura.regime,
                            "velocidade_kmh": leitura.velocidade_kmh,
                        },
                    )
                leitura.save(force_insert=True)
                via = dados.get("via", [])
                if isinstance(via, list):
                    from django.utils.dateparse import parse_datetime

                    leitura.via = via
                    leitura.save(update_fields=["via"])
                    for hop_index, hop in enumerate(via):
                        if not isinstance(hop, dict) or not hop.get("node") or not hop.get("t"):
                            continue
                        hop_time = parse_datetime(str(hop["t"]))
                        if hop_time is None:
                            continue
                        DeliveryHop.objects.create(
                            leitura=leitura,
                            hop_index=hop_index,
                            node_id=str(hop["node"])[:100],
                            recebido_em=hop_time,
                            entregue_em=received_at if hop_index == len(via) - 1 else None,
                        )
                # A leitura tardia entra na posicao do event_time e recalcula
                # apenas sua vizinhanca. recebido_em permanece auto_now_add.
                if leitura.atrasado:
                    reconstruir_para_leitura(leitura)
                    leitura.refresh_from_db()
                for raw_parameter, raw_value, unit in (
                    ("temperatura", leitura.temperatura, "C"),
                    ("vibracao", leitura.vibracao, leitura.vibracao_unit),
                    ("rpm", float(leitura.rpm), "rpm"),
                ):
                    registrar_e_normalizar(
                        machine=machine_obj,
                        manufacturer=manufacturer,
                        raw_parameter=raw_parameter,
                        raw_value=raw_value,
                        unit=unit,
                        source_protocol_simulado=source_protocol_simulado,
                        payload_original=dados,
                    )
                transaction.on_commit(
                    lambda: REGISTRY.record_reading(
                        machine_obj.external_code,
                        {
                            "temperatura": leitura.temperatura,
                            "vibracao": leitura.vibracao,
                            "rpm": leitura.rpm,
                        },
                    )
                )
                if leitura.timestamp is not None:
                    atualizar_machine_data_health(
                        machine=machine_obj,
                        trust_score=leitura.trust_score,
                        motivos=trust_motivos,
                        timestamp=leitura.timestamp,
                        anomalia_detectada=bool(anomaly_result and anomaly_result.is_anomaly),
                    )
                    avaliar_leitura(leitura)
                if (leitura.timestamp is not None and anomaly_result is not None
                        and anomaly_result.is_anomaly and anomaly_result.anomaly_score >= 0.70):
                    event = criar_evento_anomalia_estatistica(leitura, anomaly_result)
                    persistir_decision_da_anomalia(
                        machine_obj,
                        event,
                        anomaly_result,
                    )
            # Leitura nova: só atualizar o cursor quando a sequência veio no payload.
            if sequence_informada:
                _atualizar_sync_cursor(device_id, sequence_number)
            if boot_id is not None and time_source in {"rtc", "ntp", "gateway"}:
                transaction.on_commit(lambda: reconstruct_boot(boot_id))

        logger.info(
            "Leitura registrada: id=%s | device=%s | msg=%s | seq=%d | temp=%.1f°C",
            leitura.id,
            device_id,
            message_id,
            sequence_number,
            leitura.temperatura,
        )
        return "criado", str(leitura.id)

    except IntegrityError:
        # Race condition: dois processos tentaram inserir o mesmo (device_id, message_id)
        # simultaneamente. O banco rejeitou o segundo via unique_together.
        # Comportamento correto: tratar como duplicata.
        try:
            existente = LeituraTelemetria.objects.get(
                device_id=device_id, message_id=message_id
            )
            logger.info(
                "Race condition resolvida (IntegrityError): device=%s msg=%s → duplicata existente=%s",
                device_id,
                message_id,
                existente.id,
            )
            if existente.payload_hash != payload_hash:
                registrar_falha_dlq(
                    contexto=DeadLetterEntry.Contexto.SYNC,
                    payload_referencia={"device_id": device_id, "message_id": message_id,
                                        "stored_payload_hash": existente.payload_hash,
                                        "received_payload_hash": payload_hash},
                    motivo="conflito de payload_hash após corrida de idempotência",
                )
                return "conflito", str(existente.id)
            return "duplicata", str(existente.id)
        except LeituraTelemetria.DoesNotExist:
            registrar_falha_dlq(
                contexto=DeadLetterEntry.Contexto.VALIDACAO,
                payload_referencia={
                    "device_id": device_id,
                    "message_id": message_id,
                    "sequence_number": sequence_number,
                    "maquina_id": maquina_id_normalizado,
                },
                motivo="falha inesperada de integridade ao salvar leitura",
            )
            logger.exception(
                "IntegrityError inesperado ao salvar leitura. device=%s msg=%s",
                device_id,
                message_id,
            )
            return "erro", "conflito de integridade ao salvar a leitura"

    except Exception as exc:
        registrar_falha_dlq(
            contexto=getattr(exc, "_dlq_contexto", DeadLetterEntry.Contexto.VALIDACAO),
            payload_referencia=getattr(
                exc,
                "_dlq_referencia",
                {
                    "device_id": device_id,
                    "message_id": message_id,
                    "sequence_number": sequence_number,
                    "maquina_id": maquina_id_normalizado,
                },
            ),
            motivo=f"falha inesperada ao registrar/processar leitura: {exc}",
        )
        if not getattr(exc, "_dlq_logado", False):
            logger.exception(
                "Falha inesperada ao salvar leitura. device=%s | erro: %s",
                device_id,
                str(exc),
            )
        return "erro", str(exc)


def _normalizar_timestamp(valor) -> datetime:
    """
    Garante que o timestamp seja timezone-aware (America/Sao_Paulo).

    Problema enfrentado durante desenvolvimento:
    O firmware do ESP32 gera timestamps sem offset de fuso (naive datetime).
    Django com USE_TZ=True rejeita naive datetimes, causando RuntimeWarning.
    Solução: converter para aware antes de salvar.
    """
    if isinstance(valor, str):
        from django.utils.dateparse import parse_datetime
        dt = parse_datetime(valor)
        if dt is None:
            raise ValueError(f"Timestamp inválido: {valor!r}")
    else:
        dt = valor

    if not is_aware(dt):
        dt = make_aware(dt)
    return dt


def _registrar_leitura_invalida(dados: dict, motivo: str) -> None:
    """
    Persiste payload inválido para auditoria.

    Isso permite:
    - Detectar sensores com defeito (padrão de erros por maquina_id)
    - Auditar tentativas de injeção de dados
    - Entender drift de sensor ao longo do tempo

    Decisão consciente: não descartamos silenciosamente. Dado inválido
    ainda é dado — sobre o estado do sensor, se não da máquina.
    """
    try:
        from api_tcc.models import TelemetriaInvalida
        import json
        TelemetriaInvalida.objects.create(
            payload_raw=json.dumps(dados, default=str)[:2000],  # trunca se necessário
            motivo_rejeicao=motivo[:500],
            maquina_id=str(dados.get("maquina_id", "desconhecida"))[:50],
        )
    except Exception as exc:
        # Não deixa falha de auditoria derrubar o fluxo principal
        logger.error("Falha ao registrar leitura inválida (auditoria): %s", str(exc))


def calcular_status_risco(temperatura: float, vibracao: float, rpm: int | None) -> dict:
    """
    Centraliza a lógica de classificação de risco da máquina.
    Define cores e rótulos baseados nos thresholds operacionais.
    """
    from api_tcc.contracts import classify

    severidades = (classify("temperatura", temperatura), classify("vibracao", vibracao))
    if "CRITICO" in severidades:
        return {
            "nivelCor": "#FFFFFF",
            "nivelBg": "#FF5252",  # Vermelho
            "rotuloRisco": "Crítico",
        }

    # Thresholds de Alerta
    elif "ATENCAO" in severidades:
        return {
            "nivelCor": "#000000",
            "nivelBg": "#FFD740",  # Amarelo/Âmbar
            "rotuloRisco": "Alerta",
        }

    # Operação Normal
    return {
        "nivelCor": "#FFFFFF",
        "nivelBg": "#4CAF50",  # Verde
        "rotuloRisco": "Normal",
    }
