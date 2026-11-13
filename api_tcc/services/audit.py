"""Centralized, deterministic audit records for sensitive operations."""
import hashlib
import json
from datetime import date, datetime
from decimal import Decimal

from api_tcc.correlation import get_correlation_id
from api_tcc.models import AuditLog


def _state_hash(value):
    if value is None:
        return ""
    if hasattr(value, "_meta"):
        # Never hash every model field: new secrets could otherwise silently
        # enter audit evidence after a future schema change.
        allowed = {
            "api_tcc.decision": ("status", "decidido_por_id", "decidido_em", "outcome_texto"),
            "auth.user": ("username", "email", "first_name", "last_name", "is_active"),
        }.get(value._meta.label_lower)
        if allowed is None:
            raise ValueError("Estado de auditoria de modelo exige campos explicitamente selecionados.")
        state = {field: getattr(value, field) for field in allowed}
        state["pk"] = str(value.pk)
        state["model"] = value._meta.label_lower
    else:
        state = value

    def normalize(item):
        if isinstance(item, dict):
            return {str(key): normalize(val) for key, val in sorted(item.items(), key=lambda pair: str(pair[0]))}
        if isinstance(item, (list, tuple)):
            return [normalize(val) for val in item]
        if isinstance(item, (datetime, date)):
            return item.isoformat()
        if isinstance(item, Decimal):
            return str(item)
        if hasattr(item, "pk"):
            return str(item.pk)
        return item

    encoded = json.dumps(normalize(state), sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


def record(action, obj, request=None, *, before=None, after=None, actor=None, result="allowed", metadata=None):
    if actor is None and request is not None and getattr(request, "user", None) is not None:
        user = request.user
        actor = user if user.is_authenticated else None
    ip = request.META.get("REMOTE_ADDR") if request is not None else None
    user_agent = request.META.get("HTTP_USER_AGENT", "")[:512] if request is not None else ""
    correlation_id = request.META.get("HTTP_X_CORRELATION_ID", "") if request is not None else ""
    if request is not None:
        correlation_id = getattr(request, "correlation_id", "") or correlation_id
    correlation_id = correlation_id or get_correlation_id() or ""
    if ip:
        import ipaddress
        try:
            ip = str(ipaddress.ip_address(ip))
        except ValueError:
            ip = None
    model = getattr(getattr(obj, "_meta", None), "label_lower", "") if obj is not None else ""
    object_id = str(getattr(obj, "pk", "")) if obj is not None else ""
    safe_metadata = metadata or {}
    return AuditLog.objects.create(
        actor=actor, action=action[:64], result=result[:24], metadata=safe_metadata,
        object_type=model[:100], object_id=object_id[:100], ip=ip,
        user_agent=user_agent, correlation_id=correlation_id[:100],
        before_hash=_state_hash(before), after_hash=_state_hash(after),
    )
