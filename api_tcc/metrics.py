"""Métricas Prometheus do FieldNode.

O módulo mantém a definição das séries em um único lugar. Labels são enums
pequenos e nunca recebem IDs, payloads ou texto livre.
"""

from __future__ import annotations

import os
import time

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest


REGISTRY = CollectorRegistry(auto_describe=True)

INGEST_TOTAL = Counter(
    "fieldnode_ingest_total",
    "Mensagens processadas pela ingestão.",
    ("status",),
    registry=REGISTRY,
)
INGEST_LATENCY = Histogram(
    "fieldnode_ingest_latency_seconds",
    "Tempo de processamento da ingestão no backend.",
    registry=REGISTRY,
)
DLQ_OPEN = Gauge("fieldnode_dlq_open", "Itens não resolvidos na DLQ.", registry=REGISTRY)
OUTBOX_PENDING = Gauge(
    "fieldnode_outbox_pending",
    "Leituras pendentes de sincronização por classe.",
    ("class",),
    registry=REGISTRY,
)
SYNC_DELAY = Histogram(
    "fieldnode_sync_delay_seconds",
    "Atraso observado entre evento e recebimento no backend.",
    ("class",),
    registry=REGISTRY,
)
EVENTS_CREATED = Counter(
    "fieldnode_events_created_total",
    "Events persistidos pela primeira vez.",
    ("tipo", "severidade"),
    registry=REGISTRY,
)
DECISIONS_PENDING = Gauge(
    "fieldnode_decisions_pending",
    "Decisions no estado PENDENTE.",
    registry=REGISTRY,
)
LLM_LATENCY = Histogram(
    "fieldnode_llm_latency_seconds",
    "Latência de chamadas ao provedor LLM.",
    registry=REGISTRY,
)
LLM_FAILURES = Counter(
    "fieldnode_llm_failures_total",
    "Falhas de chamadas LLM por categoria controlada.",
    ("category",),
    registry=REGISTRY,
)
MODEL_VERSION_INFO = Gauge(
    "fieldnode_model_version_info",
    "Método e versão do detector ativo; não representa acurácia.",
    ("method", "version"),
    registry=REGISTRY,
)
WORKER_LAST_MESSAGE_AGE = Gauge(
    "fieldnode_worker_last_message_age_seconds",
    "Segundos desde a última mensagem processada pelo backend.",
    registry=REGISTRY,
)

MODEL_VERSION_INFO.labels(method="isolation_forest", version="runtime-registry").set(1)

ALLOWED_EVENT_TYPES = {
    "ANOMALIA",
    "MANUTENCAO",
    "FALHA",
    "ALERTA",
    "PRESCRICAO",
}
ALLOWED_EVENT_SEVERITIES = {"BAIXA", "MEDIA", "ALTA", "CRITICA"}


def record_ingest_result(status: str, started_at: float) -> None:
    """Registra uma operação lógica de ingestão, sem deixar métrica derrubar o fluxo."""
    status = status if status in {"accepted", "rejected", "duplicate", "conflict", "failed"} else "failed"
    try:
        INGEST_TOTAL.labels(status=status).inc()
        INGEST_LATENCY.observe(max(0.0, time.monotonic() - started_at))
        if status in {"accepted", "duplicate"}:
            WORKER_LAST_MESSAGE_AGE.set(0)
    except Exception:
        return


def observe_sync_delay(priority_class: str, seconds: float | None) -> None:
    if priority_class not in {"A", "B", "C"} or seconds is None:
        return
    try:
        if seconds >= 0:
            SYNC_DELAY.labels(**{"class": priority_class}).observe(float(seconds))
    except Exception:
        return


def record_event_created(event_type: str, severity: str) -> None:
    if event_type not in ALLOWED_EVENT_TYPES or severity not in ALLOWED_EVENT_SEVERITIES:
        return
    try:
        EVENTS_CREATED.labels(tipo=str(event_type), severidade=str(severity)).inc()
    except Exception:
        return


def record_llm_success(seconds: float) -> None:
    try:
        LLM_LATENCY.observe(max(0.0, float(seconds)))
    except Exception:
        return


def record_llm_failure(category: str) -> None:
    if category not in {"timeout", "unavailable", "validation", "configuration", "unknown"}:
        category = "unknown"
    try:
        LLM_FAILURES.labels(category=category).inc()
    except Exception:
        return


def refresh_state_metrics() -> None:
    """Atualiza gauges de estado com contagens indexadas e limitadas.

    Falhas de banco são ignoradas: observabilidade não pode interromper a API.
    """
    try:
        from api_tcc.models import DeadLetterEntry, Decision, LeituraTelemetria

        DLQ_OPEN.set(DeadLetterEntry.objects.filter(resolvido=False).count())
        DECISIONS_PENDING.set(Decision.objects.filter(status=Decision.Status.PENDENTE).count())
        for priority_class in ("A", "B", "C"):
            OUTBOX_PENDING.labels(**{"class": priority_class}).set(
                LeituraTelemetria.objects.filter(
                    sync_status="pendente", priority_class=priority_class
                ).count()
            )
        latest = LeituraTelemetria.objects.order_by("-recebido_em").values_list("recebido_em", flat=True).first()
        if latest is not None:
            from django.utils import timezone

            WORKER_LAST_MESSAGE_AGE.set(max(0.0, (timezone.now() - latest).total_seconds()))
    except Exception:
        return


def metrics_payload() -> bytes:
    refresh_state_metrics()
    return generate_latest(REGISTRY)


def metrics_token_is_valid(request) -> bool:
    expected = str(getattr(request, "_metrics_token", "") or "")
    from django.conf import settings

    configured = str(getattr(settings, "FIELDNODE_METRICS_TOKEN", "") or "").strip()
    if not configured:
        configured = str(os.environ.get("FIELDNODE_METRICS_TOKEN", "") or "").strip()
    return bool(configured and expected and expected == configured)


def reset_metrics_for_tests() -> None:
    """Limpa labels em testes de processo único; não é usado pela aplicação."""
    for metric in (INGEST_TOTAL, OUTBOX_PENDING, SYNC_DELAY, EVENTS_CREATED, LLM_FAILURES):
        metric.clear()
    for metric in (INGEST_LATENCY, LLM_LATENCY):
        metric._sum.set(0)
    DLQ_OPEN.set(0)
    DECISIONS_PENDING.set(0)
    WORKER_LAST_MESSAGE_AGE.set(0)
