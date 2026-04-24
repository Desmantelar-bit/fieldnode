"""
api_tcc/services/telemetria.py

Camada de serviço de domínio para telemetria.
Views e workers MQTT chamam estas funções — nunca acessam o modelo diretamente.

Decisão de arquitetura: separar regra de negócio da camada de transporte
permite reutilização entre a API REST e o listener MQTT sem duplicação de lógica.
"""
import logging
from datetime import datetime
from django.utils.timezone import make_aware, is_aware
from django.db import IntegrityError
from api_tcc.models import LeituraTelemetria

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# VALIDAÇÃO DE PAYLOAD
# Limites baseados em especificação operacional de motores diesel agrícolas.
# Valores fora desses ranges indicam falha de sensor, não condição real.
# ──────────────────────────────────────────────────────────────
LIMITES = {
    "temperatura": (0.0, 150.0),    # °C — abaixo de 0 ou acima de 150 = sensor morto
    "vibracao":    (0.0, 10.0),     # adimensional — negativo impossível, >10 = ruído
    "rpm":         (0, 5000),       # RPM — motor diesel agrícola não passa de 4500 em carga
}


def validar_payload(dados: dict) -> tuple[bool, str]:
    """
    Verifica se os campos obrigatórios existem e estão dentro dos limites físicos.

    Retorna (True, "") se válido.
    Retorna (False, motivo) se inválido.

    Usamos tipos explícitos aqui porque o ESP32 às vezes manda string "85.5"
    em vez de float 85.5 dependendo da biblioteca JSON usada no firmware.
    """
    campos_obrigatorios = ["maquina_id", "temperatura", "vibracao", "rpm", "timestamp"]
    for campo in campos_obrigatorios:
        if campo not in dados or dados[campo] is None:
            return False, f"campo obrigatório ausente: {campo}"

    maquina_id = str(dados.get("maquina_id", "")).strip()
    if not maquina_id:
        return False, "maquina_id não pode ser vazio"

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

    return True, ""


# ──────────────────────────────────────────────────────────────
# REGISTRO DE LEITURA
# ──────────────────────────────────────────────────────────────
def registrar_leitura(dados: dict) -> tuple[str, str | None]:
    """
    Persiste uma leitura de telemetria com deduplicação por UUID.

    Retorna:
        ("criado", id_str)      — leitura nova salva com sucesso
        ("duplicata", id_str)   — UUID já existia, ignorado (idempotente)
        ("invalido", motivo)    — payload inválido, descartado
        ("erro", detalhe)       — falha inesperada de banco

    Decisão: tratamos IntegrityError separado de Exception genérico.
    IntegrityError = race condition de UUID duplicado (ok, idempotente).
    Exception      = algo inesperado que precisa de atenção imediata.
    """
    valido, motivo = validar_payload(dados)
    if not valido:
        _registrar_leitura_invalida(dados, motivo)
        logger.warning("Payload rejeitado — motivo: %s | maquina_id: %s",
                       motivo, dados.get("maquina_id", "desconhecida"))
        return "invalido", motivo

    uuid_recebido = dados.get("id")

    # Deduplicação: evita gravar o mesmo pacote duas vezes
    # (o ESP32 pode reenviar após timeout mesmo que o servidor já recebeu)
    if uuid_recebido and LeituraTelemetria.objects.filter(id=uuid_recebido).exists():
        logger.debug("Duplicata ignorada. UUID: %s | maquina: %s",
                     uuid_recebido, dados.get("maquina_id"))
        return "duplicata", str(uuid_recebido)

    try:
        timestamp = _normalizar_timestamp(dados["timestamp"])
        leitura = LeituraTelemetria.objects.create(
            id=uuid_recebido,
            maquina_id=str(dados["maquina_id"]).strip(),
            temperatura=float(dados["temperatura"]),
            vibracao=float(dados["vibracao"]),
            rpm=int(dados["rpm"]),
            timestamp=timestamp,
        )
        logger.info("Leitura registrada com sucesso. UUID: %s | maquina: %s | temp: %.1f°C",
                    leitura.id, leitura.maquina_id, leitura.temperatura)
        return "criado", str(leitura.id)

    except IntegrityError:
        # Race condition: dois workers receberam o mesmo UUID ao mesmo tempo
        logger.debug("IntegrityError — duplicata por race condition. UUID: %s", uuid_recebido)
        return "duplicata", str(uuid_recebido)

    except Exception as exc:
        logger.error("Falha inesperada ao salvar leitura. maquina: %s | erro: %s",
                     dados.get("maquina_id"), str(exc), exc_info=True)
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
