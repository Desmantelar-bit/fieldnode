"""Temporal provenance and deterministic per-boot event-time reconstruction."""

from datetime import timedelta
from uuid import UUID

from django.utils import timezone

from api_tcc.models import LeituraTelemetria

TRUSTED_SOURCES = {"rtc", "ntp", "gateway"}
CONFIDENCE = {"rtc": 0.95, "ntp": 0.95, "gateway": 0.80}


def resolve_event_time(data: dict, *, ingested_at=None):
    """Return event_time, confidence and provenance without inventing an anchor."""
    source = data.get("time_source", "unsynced")
    if source not in {"rtc", "gateway", "ntp", "unsynced"}:
        raise ValueError("time_source deve ser rtc, gateway, ntp ou unsynced")
    boot_value = data.get("boot_id")
    boot_id = UUID(str(boot_value)) if boot_value is not None else None
    uptime = data.get("uptime_ms")
    if uptime is not None:
        try:
            if isinstance(uptime, bool) or not float(uptime).is_integer() or float(uptime) < 0:
                raise ValueError
            uptime = int(uptime)
        except (TypeError, ValueError, OverflowError):
            raise ValueError("uptime_ms deve ser inteiro não negativo") from None
    event_time = None
    confidence = 0.0
    provenance = {"time_source": source, "resolution": "unresolved"}

    raw_time = data.get("timestamp", data.get("event_time"))
    if source in TRUSTED_SOURCES and raw_time is not None:
        event_time = _parse_time(raw_time)
        confidence = CONFIDENCE[source]
        provenance = {"time_source": source, "resolution": "source_anchor"}
    elif source == "unsynced" and raw_time is not None:
        # Legacy clients sent a timestamp without stating its clock source. Keep
        # the supplied value for compatibility, but mark it unverified.
        event_time = _parse_time(raw_time)
        confidence = 0.5
        provenance = {"time_source": "unsynced", "resolution": "legacy_unverified_timestamp"}
    elif source == "unsynced" and boot_id and uptime is not None:
        anchor = (LeituraTelemetria.objects.filter(boot_id=boot_id, uptime_ms__isnull=False,
                    timestamp__isnull=False, time_source__in=TRUSTED_SOURCES)
                  .order_by("recebido_em", "id").first())
        if anchor:
            event_time = anchor.timestamp + timedelta(milliseconds=uptime - anchor.uptime_ms)
            confidence = min(anchor.event_time_confidence, 0.65)
            provenance = {"time_source": "unsynced", "resolution": "boot_anchor",
                          "anchor_message_id": anchor.message_id}
            skew = None
        else:
            skew = None
    else:
        skew = None

    skew = data.get("clock_skew_ms")
    if skew is not None:
        if isinstance(skew, bool):
            raise ValueError("clock_skew_ms deve ser inteiro")
        try:
            if not float(skew).is_integer():
                raise ValueError
            skew = int(skew)
        except (TypeError, ValueError, OverflowError):
            raise ValueError("clock_skew_ms deve ser inteiro") from None
    return boot_id, uptime, source, event_time, confidence, skew, provenance


def _parse_time(value):
    parsed = value if hasattr(value, "tzinfo") else None
    if parsed is None:
        from django.utils.dateparse import parse_datetime
        parsed = parse_datetime(str(value))
    if parsed is None:
        raise ValueError("timestamp/event_time inválido; esperado ISO-8601")
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def reconstruct_boot(boot_id) -> int:
    """Reapply the earliest reliable anchor to unresolved records in one boot."""
    anchor = (LeituraTelemetria.objects.filter(boot_id=boot_id, uptime_ms__isnull=False,
                timestamp__isnull=False, time_source__in=TRUSTED_SOURCES)
              .order_by("recebido_em", "id").first())
    if anchor is None:
        return 0
    updated = 0
    rows = LeituraTelemetria.objects.filter(boot_id=boot_id, uptime_ms__isnull=False,
        time_source="unsynced").exclude(id=anchor.id)
    for row in rows.iterator():
        resolved = anchor.timestamp + timedelta(milliseconds=row.uptime_ms - anchor.uptime_ms)
        original = row.time_provenance.get("original", row.time_provenance)
        provenance = {"time_source": "unsynced", "resolution": "boot_anchor",
                      "anchor_message_id": anchor.message_id, "original": original}
        if row.timestamp != resolved or row.time_provenance != provenance:
            row.timestamp = resolved
            row.event_time_confidence = min(anchor.event_time_confidence, 0.65)
            row.time_provenance = provenance
            row.save(update_fields=["timestamp", "event_time_confidence", "time_provenance"])
            updated += 1
    return updated
