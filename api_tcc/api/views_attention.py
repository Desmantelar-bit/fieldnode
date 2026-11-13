from django.db.models import F
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.api.serializers import EventSerializer
from api_tcc.models import Decision, Event, MachineDataHealth
from api_tcc.permissions import IsAuthenticatedOrPublicDemo, get_machines_for_request
from api_tcc.services.data_health import LOW_TRUST_SCORE_THRESHOLD


class AttentionSummaryView(APIView):
    """Resumo operacional agregado, limitado às máquinas acessíveis ao usuário."""

    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request):
        machines = get_machines_for_request(request)
        events = Event.objects.filter(machine__in=machines, status=Event.Status.ABERTO)
        decisions = Decision.objects.filter(machine__in=machines)
        pending_decisions = decisions.filter(status=Decision.Status.PENDENTE)
        health = MachineDataHealth.objects.filter(machine__in=machines)

        return Response({
            "decisoes_pendentes": pending_decisions.count(),
            "riscos_criticos": pending_decisions.filter(severidade="CRITICO").count(),
            "eventos_criticos": events.filter(severidade="CRITICO").count(),
            "maquinas_dados_instaveis": health.filter(
                trust_score_medio__lt=LOW_TRUST_SCORE_THRESHOLD,
            ).count(),
            "eventos": EventSerializer(
                events.select_related("machine", "leitura_origem").order_by(
                    F("priority_score").desc(nulls_last=True), "-criado_em", "-id",
                )[:10],
                many=True,
            ).data,
        })
