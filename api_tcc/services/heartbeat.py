"""Heartbeat compartilhado do worker MQTT."""

from django.conf import settings
from django.utils.timezone import now

from api_tcc.models import WorkerHeartbeat


WORKER_NAME = "mqtt"


def beat(instance_id: str, *, status: str = "running") -> None:
    WorkerHeartbeat.objects.update_or_create(
        worker_name=WORKER_NAME,
        defaults={
            "instance_id": instance_id,
            "last_heartbeat_at": now(),
            "status": status,
        },
    )


def expected_device_ids() -> set[str]:
    """Dispositivos explicitamente esperados para ingestão MQTT."""
    configured = getattr(settings, "FIELDNODE_EXPECTED_MQTT_DEVICES", "")
    return {item.strip() for item in configured.split(",") if item.strip()}


def heartbeat_snapshot() -> dict:
    expected = expected_device_ids()
    heartbeat = WorkerHeartbeat.objects.filter(worker_name=WORKER_NAME).first()
    if not expected:
        return {"status": "not_required", "required": False, "expected_devices": 0}
    if heartbeat is None:
        return {
            "status": "unknown",
            "required": True,
            "expected_devices": len(expected),
            "reason": "worker ainda não inicializado",
        }
    age = max(0, int((now() - heartbeat.last_heartbeat_at).total_seconds()))
    limit = int(getattr(settings, "FIELDNODE_WORKER_HEARTBEAT_TIMEOUT_SECONDS", 60))
    status = "ok" if heartbeat.status == "running" and age <= limit else "stale"
    return {
        "status": status,
        "required": True,
        "expected_devices": len(expected),
        "instance_id": heartbeat.instance_id,
        "last_heartbeat_at": heartbeat.last_heartbeat_at.isoformat(),
        "age_seconds": age,
        "timeout_seconds": limit,
    }
