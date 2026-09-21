from datetime import timedelta

from django.utils import timezone

from api_tcc.models import Event, LeituraTelemetria


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
        if evento is not None:
            eventos.append(evento)

    return eventos


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
