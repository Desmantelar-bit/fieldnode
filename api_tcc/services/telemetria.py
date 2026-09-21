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
import uuid as uuid_lib
from datetime import datetime

from django.db import IntegrityError, transaction
from django.utils.timezone import make_aware, is_aware

from api_tcc.models import LeituraTelemetria, Colheitadeira, Machine, SyncCursor
from api_tcc.services.data_health import (
    HISTORY_LIMIT,
    atualizar_machine_data_health,
    calcular_trust_score,
)
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

    campos_obrigatorios = ["maquina_id", "temperatura", "vibracao", "rpm", "timestamp"]
    for campo in campos_obrigatorios:
        if campo not in dados or dados[campo] is None:
            return False, f"campo obrigatório ausente: {campo}"

    maquina_id = str(dados.get("maquina_id", "")).strip()
    if not maquina_id:
        return False, "maquina_id não pode ser vazio"

    # CORREÇÃO: Removida validação contra Colheitadeira que impedia dados de entrar
    # O simulador envia IDs como "CASE-TC5000-01" mas o banco tem Modelo.nome = "TC5000"
    # Agora aceitamos qualquer maquina_id e deixamos o sistema criar registros dinamicamente

    for campo, (minimo, maximo) in LIMITES.items():
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

    return True, ""


# ──────────────────────────────────────────────────────────────
# REGISTRO DE LEITURA
# ──────────────────────────────────────────────────────────────


def _computar_payload_hash(dados: dict) -> str:
    """
    Computa SHA-256 do payload original (serializado) para rastreabilidade.
    Não é usado como chave de idempotência — apenas como fingerprint.
    """
    raw = json.dumps(dados, sort_keys=True, default=str).encode("utf-8")
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

    # payload_hash para rastreabilidade
    payload_hash = _computar_payload_hash(dados)

    try:
        timestamp = _normalizar_timestamp(dados["timestamp"])

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
                    rpm=int(dados["rpm"]),
                    latitude=float(dados["latitude"])
                    if dados.get("latitude") is not None
                    else None,
                    longitude=float(dados["longitude"])
                    if dados.get("longitude") is not None
                    else None,
                    timestamp=timestamp,
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
                leitura.save(force_insert=True)
                atualizar_machine_data_health(
                    machine=machine_obj,
                    trust_score=leitura.trust_score,
                    motivos=trust_motivos,
                    timestamp=leitura.timestamp,
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
            logger.exception(
                "IntegrityError inesperado ao salvar leitura. device=%s msg=%s",
                device_id,
                message_id,
            )
            return "erro", "conflito de integridade ao salvar a leitura"

    except Exception as exc:
        logger.error(
            "Falha inesperada ao salvar leitura. device=%s | erro: %s",
            device_id,
            str(exc),
            exc_info=True,
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


def calcular_status_risco(temperatura: float, vibracao: float, rpm: int) -> dict:
    """
    Centraliza a lógica de classificação de risco da máquina.
    Define cores e rótulos baseados nos thresholds operacionais.
    """
    # Thresholds Críticos
    if temperatura > 110.0 or vibracao > 8.0:
        return {
            "nivelCor": "#FFFFFF",
            "nivelBg": "#FF5252",  # Vermelho
            "rotuloRisco": "Crítico",
        }

    # Thresholds de Alerta
    elif temperatura > 95.0 or vibracao > 5.0:
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
