"""Regras conservadoras para materializar janelas rotuladas de decisões."""

from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from api_tcc.models import Decision, Event, LabeledWindow, Reevaluation, WorkOrder


RULE_VERSION = "decision-outcome-v1"
CRITICAL_FOLLOWUP_HOURS = 24


def _window_features(decision, reevaluation=None, followup=None):
    reading = decision.event.leitura_origem if decision.event_id and decision.event.leitura_origem_id else None
    features = {
        "temperatura": getattr(reading, "temperatura", None),
        "vibracao": getattr(reading, "vibracao", None),
        "rpm": getattr(reading, "rpm", None),
        "evidence_quality": getattr(reading, "evidence_quality", None) or getattr(decision.event, "evidence_quality", None),
    }
    if reevaluation is not None:
        features["reevaluation_after_pct"] = (reevaluation.metricas or {}).get("depois")
        features["reevaluation_before_pct"] = (reevaluation.metricas or {}).get("antes")
    if followup is not None:
        features["followup_event_type"] = followup.tipo
        features["followup_severity"] = followup.severidade
    return features


def _reference_time(decision):
    if decision.event_id and decision.event.leitura_origem_id and decision.event.leitura_origem.timestamp:
        return decision.event.leitura_origem.timestamp
    return decision.decidido_em or decision.criado_em


def _candidate(decision):
    reference = _reference_time(decision)
    reevaluation = None
    try:
        reevaluation = decision.work_order.reevaluation
    except (WorkOrder.DoesNotExist, Reevaluation.DoesNotExist):
        pass

    if decision.status == Decision.Status.EXECUTADA and reevaluation and reevaluation.resultado == Reevaluation.Resultado.SINTOMA_CESSOU:
        start = reevaluation.janela_antes_inicio or reference
        end = reevaluation.janela_depois_fim or reference
        return {
            "label": LabeledWindow.Label.ACAO_ASSOCIADA_RESOLUCAO,
            "categoria": "acao_associada_resolucao",
            "source": LabeledWindow.LabelSource.AMBOS,
            "justificativa": "Decision executada e Reevaluation registrou SINTOMA_CESSOU; associação temporal, não causalidade.",
            "start": start,
            "end": end,
            "features": _window_features(decision, reevaluation),
        }

    if decision.status == Decision.Status.REJEITADA and decision.motivo_rejeicao == "FALSO_ALARME":
        return {
            "label": LabeledWindow.Label.NEGATIVO,
            "categoria": "falso_alarme_rejeitado",
            "source": LabeledWindow.LabelSource.HUMANO,
            "justificativa": "Rejeição humana explicitamente classificada como FALSO_ALARME.",
            "start": reference,
            "end": decision.decidido_em or decision.criado_em,
            "features": _window_features(decision),
        }

    if reference is not None and decision.status in {Decision.Status.REJEITADA, Decision.Status.EXPIRADA, Decision.Status.PENDENTE} and not hasattr(decision, "work_order"):
        followup = (
            Event.objects.filter(
                machine=decision.machine,
                severidade=Event.Severidade.CRITICO,
                criado_em__gt=reference,
                criado_em__lte=reference + timedelta(hours=CRITICAL_FOLLOWUP_HOURS),
            )
            .order_by("criado_em", "id")
            .first()
        )
        if followup is not None:
            return {
                "label": LabeledWindow.Label.POSITIVO,
                "categoria": "evento_critico_posterior_sem_acao",
                "source": LabeledWindow.LabelSource.TELEMETRIA,
                "justificativa": "Evento crítico posterior no horizonte definido, sem WorkOrder vinculada; não prova causalidade.",
                "start": reference,
                "end": followup.criado_em,
                "features": _window_features(decision, followup=followup),
            }
    return None


def materialize_decision(decision):
    candidate = _candidate(decision)
    if candidate is None:
        return None
    window, created = LabeledWindow.objects.get_or_create(
        decision=decision,
        regra_versao=RULE_VERSION,
        defaults={
            "machine": decision.machine,
            "organization": decision.machine.organization,
            "janela_inicio": candidate["start"],
            "janela_fim": candidate["end"],
            "features": candidate["features"],
            "label": candidate["label"],
            "categoria": candidate["categoria"],
            "justificativa": candidate["justificativa"],
            "fonte_rotulo": candidate["source"],
        },
    )
    return window


def eligible_windows(*, organization_id=None, machine=None):
    queryset = LabeledWindow.objects.filter(elegivel_exportacao=True).select_related("machine", "decision")
    if organization_id:
        queryset = queryset.filter(organization_id=organization_id)
    if machine is not None:
        queryset = queryset.filter(machine=machine)
    return queryset.order_by("machine__external_code", "janela_inicio", "id")
