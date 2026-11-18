"""Incident Engine v0.1: agrupamento temporal de sintomas correlacionados."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone

from api_tcc.models import Event, Incident, IncidentEvent

logger = logging.getLogger(__name__)

INCIDENT_WINDOW_MINUTES = 10
INCIDENT_LABEL = "Sintomas simultâneos"


def event_time(event: Event):
    """Retorna somente o horário factual da origem; nunca usa created_at como fallback."""

    return getattr(event.leitura_origem, "timestamp", None)


def _eligible_open_incident(event: Event, occurred_at: datetime) -> Incident | None:
    start = occurred_at - timedelta(minutes=INCIDENT_WINDOW_MINUTES)
    return (
        Incident.objects.select_for_update()
        .filter(
            organization_id=event.machine.organization_id,
            machine_id=event.machine_id,
            status=Incident.Status.ABERTO,
            aberto_em__gte=start,
            aberto_em__lte=occurred_at + timedelta(minutes=INCIDENT_WINDOW_MINUTES),
        )
        .order_by("-aberto_em")
        .first()
    )


@transaction.atomic
def agrupar_evento(event: Event, *, em: datetime | None = None) -> Incident | None:
    """Associa um evento a um incidente aberto ou cria um novo.

    A operação é idempotente. Eventos sem ``event_time`` não são agrupados,
    porque ``criado_em``/hora de recebimento não representa o fato operacional.
    A proximidade temporal recebe rótulo de sintomas, nunca diagnóstico.
    """

    if event.machine_id is None or event.machine.organization_id is None:
        return None
    occurred_at = event_time(event)
    if occurred_at is None:
        return None

    existing_link = IncidentEvent.objects.filter(event=event).select_related("incident").first()
    if existing_link:
        return existing_link.incident

    incident = _eligible_open_incident(event, occurred_at)
    if incident is None:
        incident = Incident.objects.create(
            organization_id=event.machine.organization_id,
            machine_id=event.machine_id,
            aberto_em=occurred_at,
            rotulo=INCIDENT_LABEL,
        )
    IncidentEvent.objects.get_or_create(incident=incident, event=event)
    return incident


@transaction.atomic
def fechar_incidente(incident: Incident, *, em: datetime | None = None) -> Incident:
    """Fecha explicitamente um incidente; o agrupamento não fecha por silêncio."""

    if incident.status != Incident.Status.FECHADO:
        incident.status = Incident.Status.FECHADO
        incident.fechado_em = em or timezone.now()
        incident.save(update_fields=["status", "fechado_em"])
    return incident
