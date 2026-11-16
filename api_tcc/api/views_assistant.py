from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from api_tcc.services.assistant_tools import execute_tool


class AssistantToolView(APIView):
    """Executa apenas chamadas explícitas da allowlist, sem escrita ou SQL livre."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not isinstance(request.data, dict):
            return Response({"detail": "payload inválido"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = execute_tool(request.user, request.data.get("tool"), request.data.get("arguments", {}))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)
