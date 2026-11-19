from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.permissions import get_machine_for_request


class MachineCapabilitiesView(APIView):
    """GET the parameters actually observed for one machine."""

    def get(self, request, machine_id):
        machine = get_machine_for_request(request, machine_id)
        if machine is None:
            return Response(
                {"detail": "machine nao encontrada ou sem acesso."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            days = max(1, min(int(request.query_params.get("days", 7)), 90))
        except (TypeError, ValueError):
            days = 7

        return Response({
            "machine_id": str(machine.id),
            "external_code": machine.external_code,
            "periodo_dias": days,
            "capabilities": machine.capabilities(detailed=True, days=days),
        })
