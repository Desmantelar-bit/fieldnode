from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.api.serializers_dlq import DeadLetterEntrySerializer
from api_tcc.models import DeadLetterEntry


class DeadLetterEntryListView(APIView):
    """Inspeção autenticada de falhas persistidas, sem mutação ou retry."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        entradas = DeadLetterEntry.objects.filter(resolvido=False)
        return Response(DeadLetterEntrySerializer(entradas, many=True).data)
