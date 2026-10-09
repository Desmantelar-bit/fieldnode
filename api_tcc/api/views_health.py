from django.conf import settings
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.models import LeituraTelemetria


def _verificar_banco():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return "erro"
    return "ok"


def _mqtt_last_seen_seconds():
    recebido_em = (
        LeituraTelemetria.objects.order_by("-recebido_em")
        .values_list("recebido_em", flat=True)
        .first()
    )
    if recebido_em is None:
        return None

    from django.utils import timezone

    return max(0, int((timezone.now() - recebido_em).total_seconds()))


class HealthView(APIView):
    """Endpoint leve para verificar a integridade da API e do banco."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        db_status = _verificar_banco()
        return Response(
            {
                "status": "ok" if db_status == "ok" else "degradado",
                "database": db_status,
                "mqtt_last_seen_seconds": _mqtt_last_seen_seconds(),
                "version": getattr(settings, "FIELDNODE_VERSION", "1.0"),
            }
        )
