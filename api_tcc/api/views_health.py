import os
import shutil
import socket
import time

from django.conf import settings
from django.db import connection
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.models import LeituraTelemetria
from api_tcc.services.heartbeat import heartbeat_snapshot


_BROKER_CACHE = {"at": 0.0, "status": "unknown", "reason": "não verificado"}


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


def _check_broker():
    now_monotonic = time.monotonic()
    if now_monotonic - _BROKER_CACHE["at"] < 5:
        return dict(_BROKER_CACHE)
    host = os.environ.get("MQTT_BROKER", "localhost")
    try:
        port = int(os.environ.get("MQTT_PORT", "1883"))
        with socket.create_connection((host, port), timeout=1):
            result = {"status": "ok", "reason": "conexão TCP disponível"}
    except (OSError, ValueError):
        result = {"status": "unavailable", "reason": "broker MQTT indisponível"}
    _BROKER_CACHE.update(at=now_monotonic, **result)
    return result


def _check_disk():
    try:
        usage = shutil.disk_usage(settings.BASE_DIR)
        free_ratio = usage.free / usage.total if usage.total else 0
        critical = float(getattr(settings, "FIELDNODE_DISK_CRITICAL_FREE_RATIO", 0.05))
        return {
            "status": "ok" if free_ratio >= critical else "degraded",
            "free_ratio": round(free_ratio, 4),
            "critical_free_ratio": critical,
        }
    except OSError:
        return {"status": "unknown", "reason": "espaço em disco não mensurável"}


def _readiness_checks():
    database = _verificar_banco()
    expected_devices = bool(getattr(settings, "FIELDNODE_EXPECTED_MQTT_DEVICES", "").strip())
    broker = _check_broker()
    broker["required"] = expected_devices
    worker = heartbeat_snapshot()
    model = {"status": "ok", "method": "registry"}
    disk = _check_disk()
    checks = {
        "database": {"status": "ok" if database == "ok" else "unavailable", "required": True},
        "mqtt_broker": broker,
        "worker": worker,
        "model": {**model, "required": False},
        "disk": {**disk, "required": True},
    }
    blocking = any(
        check.get("required") and check.get("status") not in {"ok", "not_required"}
        for check in checks.values()
    )
    return checks, "degraded" if blocking else "ok"


class LiveHealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"})


class ReadyHealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        checks, overall = _readiness_checks()
        response = Response(
            {
                "status": overall,
                "timestamp": timezone.now().isoformat(),
                "checks": checks,
            },
            status=200 if overall == "ok" else 503,
        )
        return response


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
