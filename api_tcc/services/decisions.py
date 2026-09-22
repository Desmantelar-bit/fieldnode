from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from api_tcc.models import Decision, Event, Machine


DECISION_DEDUP_WINDOW = timedelta(minutes=30)


def persistir_decision_da_analise(analise) -> Decision:
    """
    Persiste ou reutiliza uma Decision pendente equivalente para a analise atual.

    O pipeline atual nao produz confianca numerica propria. Por isso, confianca
    fica null em vez de reutilizar trust_score ou fabricar um score artificial.
    """
    machine, _created = Machine.objects.get_or_create(
        external_code=str(analise.maquina_id).strip().upper()
    )
    severidade = _normalizar_severidade(analise.status)
    texto = _texto_recomendacao(analise)
    acao_recomendada = _acao_recomendada(analise, texto)
    event = _event_aberto_recente(machine, severidade)
    janela_inicio = timezone.now() - DECISION_DEDUP_WINDOW

    with transaction.atomic():
        existente = (
            Decision.objects.select_for_update()
            .filter(
                machine=machine,
                event=event,
                texto=texto,
                acao_recomendada=acao_recomendada,
                severidade=severidade,
                status=Decision.Status.PENDENTE,
                criado_em__gte=janela_inicio,
            )
            .order_by("-criado_em")
            .first()
        )
        if existente is not None:
            return existente

        return Decision.objects.create(
            machine=machine,
            event=event,
            texto=texto,
            acao_recomendada=acao_recomendada,
            severidade=severidade,
            confianca=None,
            status=Decision.Status.PENDENTE,
        )


def _normalizar_severidade(status: str) -> str:
    if status in Event.Severidade.values:
        return status
    return Event.Severidade.NORMAL


def _texto_recomendacao(analise) -> str:
    if analise.recomendacao:
        return analise.recomendacao
    return "Todos os parametros dentro dos limites esperados. Nenhuma acao necessaria."


def _acao_recomendada(analise, texto: str) -> str:
    return texto


def _event_aberto_recente(machine: Machine, severidade: str) -> Event | None:
    if severidade == Event.Severidade.NORMAL:
        return None

    return (
        Event.objects.filter(
            machine=machine,
            severidade=severidade,
            status=Event.Status.ABERTO,
        )
        .order_by("-criado_em")
        .first()
    )
