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
from datetime import datetime, timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.timezone import is_aware, make_aware

from api_tcc.contracts import metric_definition
from api_tcc.models import (
    DeadLetterEntry,
    DeviceClockAnchor,
    LeituraTelemetria,
    Machine,
    SyncCursor,
)
from api_tcc.services.anomaly_detection import REGISTRY, detect_anomaly
from api_tcc.services.data_health import (
    HISTORY_LIMIT,
    atualizar_machine_data_health,
    calcular_trust_score,
)
from api_tcc.services.decisions import persistir_decision_da_anomalia
from api_tcc.services.dlq import registrar_falha_dlq
from api_tcc.services.eventos import (
    avaliar_leitura,
    criar_evento_anomalia_estatistica,
)
from api_tcc.services.normalizacao import registrar_e_normalizar
from api_tcc.services.sensor_limits import LIMITES

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

    campos_obrigatorios = ["maquina_id", "temperatura", "vibracao", "rpm"]
    for campo in campos_obrigatorios:
        if campo not in dados or dados[campo] is None:
            return False, f"campo obrigatório ausente: {campo}"

    time_source = dados.get("time_source", "unsynced")
    if time_source not in {"rtc", "gateway", "ntp", "unsynced"}:
        return False, f"time_source inválido: {time_source!r}"

    boot_id = dados.get("boot_id")
    if boot_id not in (None, ""):
        try:
            uuid_lib.UUID(str(boot_id))
        except (TypeError, ValueError, AttributeError):
            return False, "boot_id deve ser um UUID válido"
    else:
        boot_id = None

    uptime_raw = dados.get("uptime_ms")
    uptime_ms = None
    if uptime_raw is not None:
        if isinstance(uptime_raw, bool):
            return False, "uptime_ms deve ser um inteiro não negativo"
        try:
            numeric_uptime = float(uptime_raw)
            uptime_ms = int(uptime_raw)
        except (TypeError, ValueError, OverflowError):
            return False, "uptime_ms deve ser um inteiro não negativo"
        if (
            not math.isfinite(numeric_uptime)
            or numeric_uptime != uptime_ms
            or uptime_ms < 0
        ):
            return False, "uptime_ms deve ser um inteiro não negativo"
    if (boot_id is None) != (uptime_ms is None):
        return False, "boot_id e uptime_ms devem ser informados juntos"

    clock_skew_raw = dados.get("clock_skew_ms")
    clock_skew_ms = None
    if clock_skew_raw is not None:
        if time_source != "gateway" or isinstance(clock_skew_raw, bool):
            return (
                False,
                "clock_skew_ms só pode vir de uma medição confiável do gateway",
            )
        try:
            numeric_skew = float(clock_skew_raw)
            clock_skew_ms = int(clock_skew_raw)
        except (TypeError, ValueError, OverflowError):
            return False, "clock_skew_ms deve ser um inteiro"
        if not math.isfinite(numeric_skew) or numeric_skew != clock_skew_ms:
            return False, "clock_skew_ms deve ser um inteiro"

    has_timestamp = dados.get("timestamp") is not None
    timestamp_optional = time_source == "gateway" or (
        time_source == "unsynced" and boot_id is not None and uptime_ms is not None
    )
    if not has_timestamp and not timestamp_optional:
        return False, "campo obrigatório ausente: timestamp"

    maquina_id = str(dados.get("maquina_id", "")).strip()
    if not maquina_id:
        return False, "maquina_id não pode ser vazio"

    # CORREÇÃO: Removida validação contra Colheitadeira que impedia dados de entrar
    # O simulador envia IDs como "CASE-TC5000-01" mas o banco tem Modelo.nome = "TC5000"
    # Agora aceitamos qualquer maquina_id e deixamos o sistema criar registros dinamicamente

    vibracao_unit = dados.get("vibracao_unit", "indice_0_10")
    if vibracao_unit not in metric_definition("vibracao").get("allowed_units", []):
        return False, (
            f"vibracao_unit inválida: {vibracao_unit!r}; "
            "a unidade aceita no contrato v1 é 'indice_0_10'"
        )

    for campo, (minimo, maximo) in LIMITES.items():
        if isinstance(dados[campo], bool):
            return False, f"{campo} não é numérico: {dados[campo]!r}"
        try:
            valor = float(dados[campo])
        except (TypeError, ValueError):
            return False, f"{campo} não é numérico: {dados[campo]!r}"

        if not math.isfinite(valor):
            return False, f"{campo} deve ser finito: {dados[campo]!r}"

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

    return True, ""


# ──────────────────────────────────────────────────────────────
# REGISTRO DE LEITURA
# ──────────────────────────────────────────────────────────────


def _computar_payload_hash(dados: dict, *, incluir_id: bool = False) -> str:
    """Hash canônico do conteúdo; o UUID interno de linha não é conteúdo lógico."""
    conteudo = (
        dados
        if incluir_id
        else {chave: valor for chave, valor in dados.items() if chave != "id"}
    )
    raw = json.dumps(conteudo, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _atualizar_sync_cursor(device_id: str, sequence_number: int) -> None:
    """
    Atualiza SyncCursor para o device_id com monotonicidade garantida.

    Regra: last_acked_sequence = MAX(atual, novo_sequence).
    O cursor nunca retrocede, mesmo que o evento chegue fora de ordem.

    Deve ser chamado dentro de uma transação atômica (garantido por registrar_leitura).
    """
    cursor, criado = SyncCursor.objects.get_or_create(
        device_id=device_id,
        defaults={"last_acked_sequence": sequence_number},
    )
    if not criado and sequence_number > cursor.last_acked_sequence:
        anterior = cursor.last_acked_sequence
        nova_sequencia = sequence_number
        cursor.last_acked_sequence = nova_sequencia
        cursor.save(update_fields=["last_acked_sequence", "atualizado_em"])
        logger.debug(
            "SyncCursor avançado: device=%s seq=%d → %d",
            device_id,
            anterior,
            nova_sequencia,
        )
    elif criado:
        logger.debug("SyncCursor criado: device=%s seq=%d", device_id, sequence_number)


def _obter_ou_atualizar_ancora(
    *, device_id: str, boot_id, uptime_ms: int, timestamp: datetime, time_source: str
) -> tuple[DeviceClockAnchor, bool]:
    anchor, created = DeviceClockAnchor.objects.get_or_create(
        device_id=device_id,
        boot_id=boot_id,
        defaults={
            "anchor_uptime_ms": uptime_ms,
            "anchor_timestamp": timestamp,
            "time_source": time_source,
        },
    )
    if created:
        return anchor, True
    if uptime_ms < anchor.anchor_uptime_ms:
        anchor.anchor_uptime_ms = uptime_ms
        anchor.anchor_timestamp = timestamp
        anchor.time_source = time_source
        anchor.save(
            update_fields=[
                "anchor_uptime_ms",
                "anchor_timestamp",
                "time_source",
                "atualizado_em",
            ]
        )
        return anchor, True
    return anchor, False


def _reconstruir_leituras_do_boot(anchor: DeviceClockAnchor) -> None:
    leituras = list(
        LeituraTelemetria.objects.filter(
            device_id=anchor.device_id,
            boot_id=anchor.boot_id,
            time_source="unsynced",
            uptime_ms__isnull=False,
        )
    )
    for leitura in leituras:
        if leitura.uptime_ms is None:
            continue
        leitura.timestamp = anchor.anchor_timestamp + timedelta(
            milliseconds=leitura.uptime_ms - anchor.anchor_uptime_ms
        )
    if leituras:
        LeituraTelemetria.objects.bulk_update(leituras, ["timestamp"])


def registrar_leitura(dados: dict) -> tuple[str, str | None]:
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
    dados = dict(dados)
    payload_hash = _computar_payload_hash(dados)
    legacy_payload_hash = _computar_payload_hash(dados, incluir_id=True)
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

    time_source = dados.get("time_source", "unsynced")
    boot_id = uuid_lib.UUID(str(dados["boot_id"])) if dados.get("boot_id") else None
    uptime_ms = int(dados["uptime_ms"]) if dados.get("uptime_ms") is not None else None
    clock_skew_ms = (
        int(dados["clock_skew_ms"]) if dados.get("clock_skew_ms") is not None else None
    )
    received_at = timezone.now()

    try:
        timestamp = (
            received_at
            if time_source == "gateway" or dados.get("timestamp") is None
            else _normalizar_timestamp(dados["timestamp"])
        )

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
                if leitura.payload_hash not in {payload_hash, legacy_payload_hash}:
                    motivo = "message_id reutilizado com payload_hash diferente"
                    registrar_falha_dlq(
                        contexto=DeadLetterEntry.Contexto.SYNC,
                        payload_referencia={
                            "device_id": device_id,
                            "message_id": message_id,
                            "sequence_number": sequence_number,
                            "stored_payload_hash": leitura.payload_hash,
                            "received_payload_hash": payload_hash,
                        },
                        motivo=motivo,
                    )
                    logger.warning(
                        "Conflito de sincronização: device=%s msg=%s",
                        device_id,
                        message_id,
                    )
                    return "conflito", str(leitura.id)
                logger.info(
                    "Replay ignorado (idempotencia): device=%s msg=%s | leitura_id=%s",
                    device_id,
                    message_id,
                    leitura.id,
                )
                return "duplicata", str(leitura.id)

            anchor = None
            anchor_changed = False
            if boot_id is not None and uptime_ms is not None:
                if time_source != "unsynced":
                    anchor, anchor_changed = _obter_ou_atualizar_ancora(
                        device_id=device_id,
                        boot_id=boot_id,
                        uptime_ms=uptime_ms,
                        timestamp=timestamp,
                        time_source=time_source,
                    )
                else:
                    anchor = DeviceClockAnchor.objects.filter(
                        device_id=device_id,
                        boot_id=boot_id,
                    ).first()
                    if anchor is not None:
                        timestamp = anchor.anchor_timestamp + timedelta(
                            milliseconds=uptime_ms - anchor.anchor_uptime_ms
                        )

            if foi_criada:
                historico_recente = list(
                    LeituraTelemetria.objects.filter(machine=machine_obj)
                    .order_by("-timestamp")[:HISTORY_LIMIT]
                )
                leitura = LeituraTelemetria(
                    id=uuid_recebido or uuid_lib.uuid4(),
                    device_id=device_id,
                    message_id=message_id,
                    maquina_id=maquina_id_normalizado,
                    machine=machine_obj,
                    temperatura=float(dados["temperatura"]),
                    vibracao=float(dados["vibracao"]),
                    vibracao_unit=dados.get("vibracao_unit", "indice_0_10"),
                    rpm=int(dados["rpm"]),
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
                    sequence_number=sequence_number,
                    source=source,
                    transport=transport,
                    payload_hash=payload_hash,
                    sync_status="sincronizado",
                )
                trust_score, trust_motivos = calcular_trust_score(
                    leitura,
                    historico_recente,
                )
                leitura.trust_score = trust_score
                anomaly_result = detect_anomaly(
                    machine_obj.external_code,
                    {
                        "temperatura": leitura.temperatura,
                        "vibracao": leitura.vibracao,
                        "rpm": leitura.rpm,
                    },
                )
                leitura.save(force_insert=True)
                if anchor_changed and anchor is not None:
                    _reconstruir_leituras_do_boot(anchor)
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
                atualizar_machine_data_health(
                    machine=machine_obj,
                    trust_score=leitura.trust_score,
                    motivos=trust_motivos,
                    timestamp=leitura.timestamp,
                    anomalia_detectada=anomaly_result.is_anomaly,
                )
                avaliar_leitura(leitura)
                if anomaly_result.is_anomaly and anomaly_result.anomaly_score >= 0.70:
                    event = criar_evento_anomalia_estatistica(leitura, anomaly_result)
                    persistir_decision_da_anomalia(
                        machine_obj,
                        event,
                        anomaly_result,
                    )
            # Leitura nova: só atualizar o cursor quando a sequência veio no payload.
            if sequence_informada:
                _atualizar_sync_cursor(device_id, sequence_number)

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

        TelemetriaInvalida.objects.create(
            payload_raw=json.dumps(dados, default=str)[:2000],  # trunca se necessário
            motivo_rejeicao=motivo[:500],
            maquina_id=str(dados.get("maquina_id", "desconhecida"))[:50],
        )
    except Exception as exc:
        # Não deixa falha de auditoria derrubar o fluxo principal
        logger.error("Falha ao registrar leitura inválida (auditoria): %s", str(exc))


def calcular_status_risco(temperatura: float, vibracao: float, rpm: int) -> dict:
    """
    Centraliza a lógica de classificação de risco da máquina.
    Define cores e rótulos baseados nos thresholds operacionais.
    """
    from api_tcc.contracts import classify

    temp_status = classify("temperatura", temperatura)
    vib_status = classify("vibracao", vibracao)
    if "CRITICO" in (temp_status, vib_status):
        return {
            "nivelCor": "#FFFFFF",
            "nivelBg": "#FF5252",  # Vermelho
            "rotuloRisco": "Crítico",
        }

    # Thresholds de Alerta
    elif "ATENCAO" in (temp_status, vib_status):
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
