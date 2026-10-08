from datetime import timedelta
import logging

from django.utils import timezone

from api_tcc.models import DeadLetterEntry, Event, LeituraTelemetria
from api_tcc.services.dlq import registrar_falha_dlq

logger = logging.getLogger(__name__)


TEMP_ALTA_CRITICA_C = 85.0
SUPPRESSAO_EVENTO_MINUTOS = 15


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
    return Event.objects.create(
        machine=leitura.machine,
        leitura_origem=leitura,
        tipo=Event.Tipo.ANOMALIA_ESTATISTICA,
        severidade=Event.Severidade.CRITICO,
        status=Event.Status.ABERTO,
        trust_score_herdado=leitura.trust_score,
        dados_contexto={
            "anomaly_score": resultado.anomaly_score,
            "detection_method": resultado.detection_method,
            "contributing_feature": resultado.contributing_feature,
            "explanation": resultado.explanation,
        },
    )


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

    return Event.objects.create(
        machine=leitura.machine,
        leitura_origem=leitura,
        tipo=tipo,
        severidade=severidade,
        status=Event.Status.ABERTO,
        trust_score_herdado=leitura.trust_score,
        dados_contexto=dados_contexto,
    )
