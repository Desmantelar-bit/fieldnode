from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.models import Incident
from api_tcc.permissions import IsAuthenticatedOrPublicDemo, get_machines_for_request


def _incident_payload(incident):
    events = incident.eventos.select_related("leitura_origem").order_by("leitura_origem__timestamp", "criado_em")
    return {
        "id": str(incident.pk),
        "machine_id": str(incident.machine_id) if incident.machine_id else None,
        "machine_external_code": incident.machine.external_code if incident.machine_id else None,
        "front_id": str(incident.front_id) if incident.front_id else None,
        "status": incident.status,
        "aberto_em": incident.aberto_em.isoformat(),
        "fechado_em": incident.fechado_em.isoformat() if incident.fechado_em else None,
        "rotulo": incident.rotulo,
        "hipotese_causa": incident.hipotese_causa,
        "hipotese_causa_confirmada": False if incident.hipotese_causa else None,
        "event_count": events.count(),
        "eventos": [
            {
                "id": str(event.pk),
                "tipo": event.tipo,
                "severidade": event.severidade,
                "event_time": event.leitura_origem.timestamp.isoformat()
                if event.leitura_origem and event.leitura_origem.timestamp else None,
            }
            for event in events
        ],
    }


class IncidentListView(APIView):
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request):
        incidents = (
            Incident.objects.filter(machine__in=get_machines_for_request(request))
            .select_related("machine", "front")
            .prefetch_related("eventos__leitura_origem")
        )
        status_filter = request.query_params.get("status")
        if status_filter:
            incidents = incidents.filter(status=status_filter)
        return Response({"results": [_incident_payload(incident) for incident in incidents]})
