import hashlib
import hmac
import logging
from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import APIException
from rest_framework.throttling import BaseThrottle, SimpleRateThrottle

from api_tcc.models import AuditLog, SecurityCounter

logger = logging.getLogger(__name__)


class SecurityCounterUnavailable(APIException):
    status_code = 503
    default_detail = "Controles de autenticação temporariamente indisponíveis."
    default_code = "security_counter_unavailable"


def _counter_key(value):
    digest = hmac.new(settings.SECRET_KEY.encode(), value.encode(), hashlib.sha256).hexdigest()
    return digest


def increment_security_counter(value, window_seconds):
    """Increment a fixed-window database counter atomically across app workers."""
    now = timezone.now()
    key = _counter_key(value)
    try:
        with transaction.atomic():
            row = SecurityCounter.objects.select_for_update().filter(key=key).first()
            if row is None:
                SecurityCounter.objects.create(
                    key=key, count=1, window_started_at=now,
                    expires_at=now + timedelta(seconds=window_seconds),
                )
                return 1
            if row.expires_at <= now:
                row.count = 1
                row.window_started_at = now
                row.expires_at = now + timedelta(seconds=window_seconds)
            else:
                row.count += 1
            row.save(update_fields=["count", "window_started_at", "expires_at"])
            return row.count
    except IntegrityError:
        # A competing worker inserted this key. Retry after the transaction ends.
        return increment_security_counter(value, window_seconds)
    except Exception:
        logger.exception("Falha no contador persistente de segurança")
        raise SecurityCounterUnavailable() from None


def security_counter_value(value):
    try:
        row = SecurityCounter.objects.filter(key=_counter_key(value), expires_at__gt=timezone.now()).first()
        return row.count if row else 0
    except Exception:
        logger.exception("Falha ao consultar contador persistente de segurança")
        raise SecurityCounterUnavailable() from None


def reset_security_counter(value):
    SecurityCounter.objects.filter(key=_counter_key(value)).delete()


def audit_security_event(action, result, *, identity="", metadata=None, actor=None):
    try:
        AuditLog.objects.create(
            actor=actor,
            actor_key=_counter_key(identity) if identity else "",
            action=action,
            result=result,
            metadata=metadata or {},
        )
    except Exception:
        logger.exception("Falha ao persistir evento de auditoria de segurança: %s", action)


def normalized_login_identity(request):
    raw = request.data.get("username", "") if hasattr(request, "data") else ""
    return str(raw).strip().casefold()[:150]


def request_ip(request):
    # REMOTE_ADDR is trustworthy unless an explicitly trusted proxy middleware is configured.
    return request.META.get("REMOTE_ADDR", "unknown")


class LoginThrottle(BaseThrottle):
    """Atomically enforce five attempts/minute by both peer IP and login identity."""

    def allow_request(self, request, view):
        identity = normalized_login_identity(request)
        ip = request_ip(request)
        if not identity:
            identity = "<missing>"
        self.wait_seconds = 60
        ip_count = increment_security_counter(f"login:ip:{ip}", 60)
        if ip_count > 5:
            audit_security_event("login_throttled", "blocked", identity=identity, metadata={"reason": "ip"})
            return False
        identity_count = increment_security_counter(f"login:user:{identity}", 60)
        allowed = ip_count <= 5 and identity_count <= 5
        if not allowed:
            audit_security_event("login_throttled", "blocked", identity=identity, metadata={"reason": "identity"})
        return allowed

    def wait(self):
        return self.wait_seconds


class RegisterThrottle(BaseThrottle):
    """Three registration requests/hour/IP, backed by the shared counter table."""

    def allow_request(self, request, view):
        count = increment_security_counter(f"register:ip:{request_ip(request)}", 60 * 60)
        self.wait_seconds = 60 * 60
        if count > 3:
            audit_security_event("registration_throttled", "blocked", metadata={"reason": "ip"})
        return count <= 3

    def wait(self):
        return self.wait_seconds


def record_login_failure(identity):
    count = increment_security_counter(f"login:failed:{identity}", 15 * 60)
    if count >= 5:
        logger.warning("Lockout temporário de login aplicado; identidade=%s", _counter_key(identity)[:16])
        audit_security_event("login_lockout_armed", "active", identity=identity, metadata={"window_seconds": 900})
    return count


class IngestaoThrottle(SimpleRateThrottle):
    scope = 'ingestao'

    def get_cache_key(self, request, view):
        authenticated_device = getattr(request, 'authenticated_ingestion_device_id', None)
        if authenticated_device:
            identity = f'device:{hashlib.sha256(authenticated_device.encode()).hexdigest()}'
        elif getattr(request.user, 'is_authenticated', False):
            identity = f'user:{request.user.pk}'
        else:
            supplied_key = request.headers.get('X-API-Key', '')
            identity = (
                f'credential:{hashlib.sha256(supplied_key.encode()).hexdigest()}'
                if supplied_key else self.get_ident(request)
            )
        return self.cache_format % {'scope': self.scope, 'ident': identity}
