import logging
import math
from datetime import timedelta

from django.utils import timezone

from api_tcc.models import DeadLetterEntry, Event, LeituraTelemetria
from api_tcc.services.dlq import registrar_falha_dlq

logger = logging.getLogger(__name__)


TEMP_ALTA_CRITICA_C = 85.0
SUPPRESSAO_EVENTO_MINUTOS = 15
PRIORITY_URGENCY_DECAY_HOURS = 24.0

# Heurística v0.1: impacto operacional estimado, não medido em campo.
# Os valores ficam separados da fórmula para permitir calibração posterior.
OPERATIONAL_IMPACT_WEIGHTS = {
    Event.Tipo.TEMP_ALTA: 1.0,
    Event.Tipo.VIBRACAO_ALTA: 0.8,
    Event.Tipo.ANOMALIA_ESTATISTICA: 0.75,
    Event.Tipo.ANOMALIA_ML: 0.7,
    Event.Tipo.TENDENCIA_RISCO: 0.6,
}
UNKNOWN_OPERATIONAL_IMPACT = 0.25
SEVERITY_NORMALIZED = {
    Event.Severidade.NORMAL: 0.0,
    Event.Severidade.ATENCAO: 0.5,
    Event.Severidade.CRITICO: 1.0,
}


def avaliar_leitura(leitura: LeituraTelemetria) -> list[Event]:
    """
    Avalia uma leitura salva e persiste eventos operacionais derivados dela.

    Mantido sincrono nesta fase, mas isolado para futura execucao em fila sem
    acoplar a ingestao HTTP/MQTT as regras do Event Engine.
    """
    eventos: list[Event] = []

    if leitura.machine is None:
        return eventos

    if leitura.temperatura > TEMP_ALTA_CRITICA_C:
        try:
            evento = _criar_evento_se_nao_suprimido(
                leitura=leitura,
                tipo=Event.Tipo.TEMP_ALTA,
                severidade=Event.Severidade.CRITICO,
                dados_contexto={
                    "temperatura": leitura.temperatura,
                    "limite_critico": TEMP_ALTA_CRITICA_C,
                    "unidade": "C",
                },
            )
        except Exception as exc:
            referencia = _referencia_leitura(leitura)
            setattr(exc, "_dlq_contexto", DeadLetterEntry.Contexto.EVENTO)
            setattr(exc, "_dlq_referencia", referencia)
            setattr(exc, "_dlq_logado", True)
            registrar_falha_dlq(
                contexto=DeadLetterEntry.Contexto.EVENTO,
                payload_referencia=referencia,
                motivo=f"falha inesperada ao gerar Event: {exc}",
            )
            logger.exception("Falha inesperada ao gerar Event. leitura_id=%s", leitura.id)
            raise
        if evento is not None:
            eventos.append(evento)

    return eventos


def _referencia_leitura(leitura: LeituraTelemetria) -> dict:
    return {
        "leitura_id": str(leitura.id),
        "device_id": leitura.device_id,
        "message_id": leitura.message_id,
        "sequence_number": leitura.sequence_number,
    }


def criar_evento_anomalia_estatistica(leitura, resultado) -> Event:
    return _persistir_evento_com_priority(
        machine=leitura.machine,
        leitura_origem=leitura,
        tipo=Event.Tipo.ANOMALIA_ESTATISTICA,
        severidade=Event.Severidade.CRITICO,
        dados_contexto={
            "anomaly_score": resultado.anomaly_score,
            "detection_method": resultado.detection_method,
            "contributing_feature": resultado.contributing_feature,
            "explanation": resultado.explanation,
        },
    )


def calcular_priority_score(event, historico) -> float:
    """Calcula S × I × U × C para um evento sem efeitos colaterais.

    ``historico`` deve conter leituras anteriores da mesma máquina e condição.
    A função não consulta o banco: isso mantém o contrato determinístico e
    permite testar a metodologia com objetos simples.
    """
    severidade = SEVERITY_NORMALIZED.get(event.severidade)
    if severidade is None:
        severidade = 0.0

    impacto = OPERATIONAL_IMPACT_WEIGHTS.get(
        event.tipo,
        UNKNOWN_OPERATIONAL_IMPACT,
    )
    confianca = _clamp_score(
        getattr(event, "trust_score_herdado", None)
        if getattr(event, "trust_score_herdado", None) is not None
        else getattr(getattr(event, "leitura_origem", None), "trust_score", None)
    )
    urgencia = _calcular_urgencia(event, historico)
    return _clamp_score(severidade * impacto * urgencia * confianca)


def _calcular_urgencia(event, historico) -> float:
    """Retorna uma urgência temporal 0..1 para a condição do evento.

    Um evento sem leitura histórica comparável é tratado como condição nova e
    recebe urgência 1. Leituras antigas reduzem a atualidade, mas uma subida
    observada na métrica da condição preserva urgência alta. Isso não estima
    tempo até falha e não altera a severidade factual do evento.
    """
    historico = list(historico or [])
    if not historico:
        return 1.0

    leitura_atual = getattr(event, "leitura_origem", None)
    timestamp_atual = getattr(leitura_atual, "timestamp", None)
    timestamps = [getattr(item, "timestamp", None) for item in historico]
    timestamps = [item for item in timestamps if item is not None]
    if timestamp_atual is None or not timestamps:
        return 0.5

    ultima = max(timestamps)
    idade_horas = max((timestamp_atual - ultima).total_seconds() / 3600.0, 0.0)
    atualidade = _clamp_score(1.0 - idade_horas / PRIORITY_URGENCY_DECAY_HOURS)

    valor_atual = _valor_condicao(event.tipo, leitura_atual)
    valores_anteriores = [
        valor for valor in (_valor_condicao(event.tipo, item) for item in historico)
        if valor is not None
    ]
    if valor_atual is None or not valores_anteriores:
        return atualidade

    piora = _clamp_score(
        (valor_atual - max(valores_anteriores)) / _escala_piora(event.tipo)
    )
    return _clamp_score(max(atualidade, 0.9 * piora))


def _valor_condicao(tipo, leitura):
    if leitura is None:
        return None
    if tipo in (Event.Tipo.TEMP_ALTA, Event.Tipo.ANOMALIA_ESTATISTICA):
        return getattr(leitura, "temperatura", None)
    if tipo == Event.Tipo.VIBRACAO_ALTA:
        return getattr(leitura, "vibracao", None)
    if tipo == Event.Tipo.TENDENCIA_RISCO:
        return getattr(leitura, "temperatura", None)
    return None


def _escala_piora(tipo):
    return {
        Event.Tipo.TEMP_ALTA: 20.0,
        Event.Tipo.ANOMALIA_ESTATISTICA: 20.0,
        Event.Tipo.VIBRACAO_ALTA: 1.0,
        Event.Tipo.TENDENCIA_RISCO: 20.0,
    }.get(tipo, 1.0)


def _clamp_score(value) -> float:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(value):
        return 0.0
    return max(0.0, min(1.0, value))


def _historico_para_evento(leitura):
    """Obtém leituras anteriores da máquina para o cálculo no fluxo real."""
    return LeituraTelemetria.objects.filter(
        machine=leitura.machine,
        timestamp__lt=leitura.timestamp,
    ).order_by("-timestamp")[:50]


def _persistir_evento_com_priority(
    *, machine, leitura_origem, tipo, severidade, dados_contexto
):
    event = Event(
        machine=machine,
        leitura_origem=leitura_origem,
        tipo=tipo,
        severidade=severidade,
        status=Event.Status.ABERTO,
        trust_score_herdado=leitura_origem.trust_score,
        dados_contexto=dados_contexto,
    )
    event.priority_score = calcular_priority_score(
        event,
        _historico_para_evento(leitura_origem),
    )
    event.save(force_insert=True)
    return event


def _criar_evento_se_nao_suprimido(
    *,
    leitura: LeituraTelemetria,
    tipo: str,
    severidade: str,
    dados_contexto: dict,
) -> Event | None:
    janela_inicio = timezone.now() - timedelta(minutes=SUPPRESSAO_EVENTO_MINUTOS)

    evento_recente_aberto = Event.objects.filter(
        machine=leitura.machine,
        tipo=tipo,
        status=Event.Status.ABERTO,
        criado_em__gte=janela_inicio,
    ).exists()
    if evento_recente_aberto:
        return None

    return _persistir_evento_com_priority(
        machine=leitura.machine,
        leitura_origem=leitura,
        tipo=tipo,
        severidade=severidade,
        dados_contexto=dados_contexto,
    )
