from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connections
from django.db.utils import OperationalError


class HealthView(APIView):
    """
    Endpoint leve para verificação de integridade da API e do Banco de Dados.
    """
    authentication_classes = []  # Deixar aberto para evitar overhead de checagem
    permission_classes = []

    def get(self, request):
        db_status = 'ok'
        try:
            # Tenta executar uma operação inofensiva para garantir que o banco responde
            connections['default'].cursor()
        except OperationalError:
            db_status = 'erro'

        return Response({
            'status': 'ok' if db_status == 'ok' else 'degradado',
            'database': db_status,
        })
