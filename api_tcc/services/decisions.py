from datetime import timedelta
import logging

from django.db import transaction
from django.utils import timezone

from api_tcc.models import DeadLetterEntry, Decision, Event, LeituraTelemetria, Machine
from api_tcc.services.decision_schema import validate_decision_details
from api_tcc.services.dlq import registrar_falha_dlq

logger = logging.getLogger(__name__)


DECISION_DEDUP_WINDOW = timedelta(minutes=30)
DECISION_TRANSICOES_PERMITIDAS = {
    Decision.Status.PENDENTE: {
        Decision.Status.APROVADA,
        Decision.Status.REJEITADA,
        Decision.Status.EXPIRADA,
    },
    Decision.Status.APROVADA: {Decision.Status.EXECUTADA},
}


def validar_transicao_decision(status_atual: str, novo_status: str) -> bool:
    return novo_status in DECISION_TRANSICOES_PERMITIDAS.get(status_atual, set())


def criar_decision(*, detalhes: dict, **kwargs) -> Decision:
    validate_decision_details(detalhes)
    return Decision.objects.create(detalhes=detalhes, **kwargs)


def aplicar_acao_decision(
    decision: Decision,
    *,
    usuario,
    novo_status: str,
    outcome_texto_fornecido: bool = False,
    outcome_texto: str | None = None,
    motivo_rejeicao: str | None = None,
) -> Decision:
    if not validar_transicao_decision(decision.status, novo_status):
        raise ValueError(
            f"Transicao invalida de {decision.status} para {novo_status}."
        )

    decision.status = novo_status
    if decision.decidido_por_id is None:
        decision.decidido_por = usuario
        decision.decidido_em = timezone.now()
    if outcome_texto_fornecido:
        decision.outcome_texto = outcome_texto
    if novo_status == Decision.Status.REJEITADA:
        decision.motivo_rejeicao = (motivo_rejeicao or "").strip()

    decision.save(
        update_fields=["status", "decidido_por", "decidido_em", "outcome_texto", "motivo_rejeicao"]
    )
    if novo_status == Decision.Status.EXECUTADA:
        order = getattr(decision, "work_order", None)
        if order is not None:
            now = timezone.now()
            order.status = order.Status.CONCLUIDA
            order.concluida_em = now
            order.historico = [
                *order.historico,
                {"status": order.status, "at": now.isoformat(), "by": usuario.pk},
            ]
            order.save(update_fields=["status", "concluida_em", "historico"])
    return decision


def persistir_decision_da_analise(analise) -> Decision:
    """
    Persiste ou reutiliza uma Decision pendente equivalente para a analise atual.

    O pipeline atual nao produz confianca numerica propria. Por isso, confianca
    fica null em vez de reutilizar trust_score ou fabricar um score artificial.
    """
    try:
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

            return criar_decision(
                machine=machine,
                event=event,
                texto=texto,
                acao_recomendada=acao_recomendada,
                severidade=severidade,
                confianca=None,
                status=Decision.Status.PENDENTE,
                detalhes=_detalhes_da_analise(machine, event, analise),
            )
    except Exception as exc:
        registrar_falha_dlq(
            contexto=DeadLetterEntry.Contexto.DECISAO,
            payload_referencia={"maquina_id": str(getattr(analise, "maquina_id", "desconhecida"))},
            motivo=f"falha inesperada ao gerar Decision: {exc}",
        )
        logger.exception("Falha inesperada ao gerar Decision. maquina_id=%s", getattr(analise, "maquina_id", None))
        raise


def persistir_decision_da_anomalia(machine, event, resultado) -> Decision:
    reading = event.leitura_origem
    if reading is None:
        raise ValueError("Decision rejeitada: evento sem leitura de evidencia.")
    event_time = reading.timestamp.isoformat()
    detalhes = {
        "schema": "decision.v1",
        "observado": resultado.explanation,
        "evidencias": [{"leitura_id": str(reading.id), "campo": resultado.contributing_feature or "telemetria", "valor": getattr(reading, resultado.contributing_feature, None), "limiar": None, "event_time": event_time}],
        "janela_analisada": {"inicio": event_time, "fim": event_time, "n_leituras": 1},
        "qualidade_dado": {"evidence_quality": event.evidence_quality, "fatores": []},
        "regra": {"id": event.tipo, "versao": "1.0"},
        "modelo": {"id": resultado.detection_method, "score": resultado.anomaly_score, "contribuinte": resultado.contributing_feature},
        "dados_faltantes": [], "horizonte_minutos": None, "alternativas": [],
        "explanation": resultado.explanation,
        "contributing_feature": resultado.contributing_feature,
        "detection_method": resultado.detection_method,
        "anomaly_score": resultado.anomaly_score,
    }
    return criar_decision(
        machine=machine,
        event=event,
        texto=resultado.explanation,
        acao_recomendada="Investigar a leitura e validar o sensor antes de intervir.",
        severidade=Event.Severidade.CRITICO,
        confianca=resultado.anomaly_score,
        detalhes=detalhes,
        status=Decision.Status.PENDENTE,
    )


def _detalhes_da_analise(machine, event, analise):
    reading = event.leitura_origem if event is not None else LeituraTelemetria.objects.filter(machine=machine).order_by("-timestamp").first()
    if reading is None:
        raise ValueError("Decision rejeitada: analise sem leitura de evidencia.")
    event_time = reading.timestamp.isoformat()
    return {
        "schema": "decision.v1", "observado": _texto_recomendacao(analise),
        "evidencias": [{"leitura_id": str(reading.id), "campo": "temperatura", "valor": reading.temperatura, "limiar": None, "event_time": event_time}],
        "janela_analisada": {"inicio": event_time, "fim": event_time, "n_leituras": 1},
        "qualidade_dado": {"evidence_quality": event.evidence_quality if event else "insuficiente", "fatores": []},
        "regra": {"id": event.tipo if event else "ANALISE_TELEMETRIA", "versao": "1.0"},
        "modelo": {"id": "pipeline-analise-v1", "score": None, "contribuinte": "temperatura"},
        "dados_faltantes": [], "horizonte_minutos": None, "alternativas": [],
    }


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
