from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.models import Event
from api_tcc.permissions import IsAuthenticatedOrPublicDemo, get_machines_for_request
from api_tcc.services.consequence import avaliar


class ConsequenceAssessmentView(APIView):
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request, event_id):
        event = Event.objects.select_related("machine", "machine__organization").filter(
            pk=event_id,
            machine__in=get_machines_for_request(request),
        ).first()
        if event is None:
            return Response({"detail": "evento não encontrado"}, status=404)
        return Response(avaliar(event).as_dict())
