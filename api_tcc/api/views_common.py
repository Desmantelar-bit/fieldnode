import json
import logging
import math
import uuid as uuid_lib

from django.conf import settings
from rest_framework.permissions import BasePermission

from api_tcc.models import Machine
from api_tcc.permissions import get_machine_for_request, get_machines_for_request, user_can_access_machine

logger = logging.getLogger(__name__)





def _is_public_demo_request(request) -> bool:
    return bool(settings.DEMO_MODE and not request.user.is_authenticated)


def _filter_public_demo_leituras(queryset, request):
    if _is_public_demo_request(request):
        return queryset.filter(machine__is_demo=True)
    if request.user.is_authenticated:
        return queryset.filter(machine__in=get_machines_for_request(request))
    return queryset


def _public_demo_machine_allowed(maquina_id: str | None, request) -> bool:
    if not _is_public_demo_request(request) or not maquina_id:
        return bool(request.user.is_authenticated)
    return get_machine_for_request(request, maquina_id) is not None


def _serializar_analise(analise):
    """Converte NaN das métricas estatísticas em null válido para JSON."""
    def normalizar(valor):
        if isinstance(valor, float) and not math.isfinite(valor):
            return None
        if isinstance(valor, dict):
            return {chave: normalizar(item) for chave, item in valor.items()}
        if isinstance(valor, list):
            return [normalizar(item) for item in valor]
        return valor

    return normalizar(analise.__dict__)


def _serializar_data_health(
    machine_id,
    external_code,
    trust_score_medio,
    ultima_atualizacao,
    leituras_analisadas,
    sinais_de_alerta,
):
    if machine_id is None:
        return None

    try:
        machine_id = str(uuid_lib.UUID(str(machine_id)))
    except (TypeError, ValueError, AttributeError):
        machine_id = str(machine_id)

    if isinstance(sinais_de_alerta, str):
        try:
            sinais_de_alerta = json.loads(sinais_de_alerta)
        except json.JSONDecodeError:
            sinais_de_alerta = {}

    return {
        "machine_id": machine_id,
        "external_code": external_code,
        "status": "ok" if trust_score_medio is not None else "sem_dados",
        "trust_score_medio": trust_score_medio,
        "ultima_atualizacao": ultima_atualizacao,
        "leituras_analisadas": int(leituras_analisadas or 0),
        "sinais_de_alerta": sinais_de_alerta or {},
    }


def _serializar_prescricao(p) -> dict:
    if isinstance(p, dict):
        return p
    return {
        'id': p.id,
        'maquina_id': p.colheitadeira.maquina_id,
        'titulo': p.titulo,
        'descricao': p.descricao,
        'status': p.status,
        'data_geracao': p.data_geracao,
    }


class HasValidIngestionAPIKey(BasePermission):
    """Permission gate shared by machine-to-machine ingestion endpoints."""
    message = 'API key inválida ou ausente.'

    def has_permission(self, request, view):
        return _authenticate_http_device(request)


def _authenticate_http_device(request):
    import hashlib
    import hmac
    from django.utils import timezone
    from api_tcc.models import DeviceCredential

    device_id = request.headers.get("X-Device-Id", "").strip()
    supplied = request.headers.get("X-Device-Key", "")
    request.authenticated_ingestion_device_id = None
    if device_id and supplied:
        credential = DeviceCredential.objects.filter(device_id=device_id).first()
        candidate = hashlib.sha256(supplied.encode("utf-8")).hexdigest()
        dummy = "0" * 64
        expected_current = credential.http_key_hash if credential and credential.http_key_hash else dummy
        current_valid = hmac.compare_digest(expected_current, candidate)
        now = timezone.now()
        if credential and credential.http_rotation_deadline and now > credential.http_rotation_deadline:
            DeviceCredential.objects.filter(pk=credential.pk).update(
                http_previous_key_hash="", http_rotation_deadline=None
            )
        previous_valid = bool(
            credential and credential.http_previous_key_hash and credential.http_rotation_deadline
            and now <= credential.http_rotation_deadline
            and hmac.compare_digest(credential.http_previous_key_hash, candidate)
        )
        if credential and credential.http_key_hash and not credential.http_revoked_at and (current_valid or previous_valid):
            request.authenticated_ingestion_device_id = credential.device_id
            request.authenticated_ingestion_credential = credential
            return True

    # Once an individual credential is presented, never fall through to the
    # development-only global key, even when that individual credential fails.
    if device_id or supplied:
        return False

    # Development-only escape hatch, deliberately opt-in and not used after a
    # failed individual credential check.
    if getattr(settings, "DEBUG", False) and getattr(settings, "ALLOW_LEGACY_INGESTION_KEY", False):
        legacy = getattr(settings, "FIELDNODE_API_KEY", "")
        presented = request.headers.get("X-API-Key", "")
        if legacy and presented and hmac.compare_digest(legacy, presented):
            request.authenticated_ingestion_device_id = None
            return True
        # Temporary development-only compatibility for pre-S2-T8 test fixtures.
        # This environment mapping is never consulted outside DEBUG.
        for configured_id, configured_key in getattr(settings, "FIELDNODE_DEVICE_API_KEYS", {}).items():
            if presented and hmac.compare_digest(str(configured_key), presented):
                request.authenticated_ingestion_device_id = configured_id
                return True
    return False


class HasIngestionCredential(BasePermission):
    """Accept device API keys or authorized members sending browser telemetry."""
    message = 'Credencial inválida ou sem acesso de escrita à máquina.'

    def has_permission(self, request, view):
        if _authenticate_http_device(request):
            device_id = getattr(request, 'authenticated_ingestion_device_id', None)
            if not device_id:
                return True
            payloads = request.data.get('leituras') if isinstance(request.data, dict) else None
            if payloads is None:
                payloads = [request.data]
            matches = bool(
                isinstance(payloads, list)
                and payloads
                and all(
                    isinstance(payload, dict)
                    and str(payload.get('device_id') or '').strip() == device_id
                    and str(payload.get('maquina_id') or '').strip().upper() == device_id.upper()
                    for payload in payloads
                )
            )
            if not matches:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Identidade do dispositivo não corresponde ao payload.")
            from django.utils import timezone
            from api_tcc.models import DeviceCredential
            credential = getattr(request, "authenticated_ingestion_credential", None)
            now = timezone.now()
            if credential and (
                not credential.http_last_seen_at
                or (now - credential.http_last_seen_at).total_seconds() >= 300
            ):
                DeviceCredential.objects.filter(pk=credential.pk).update(http_last_seen_at=now)
            return True
        if not request.user.is_authenticated:
            return False

        payloads = request.data.get('leituras') if isinstance(request.data, dict) else None
        if payloads is None:
            payloads = [request.data]
        if not isinstance(payloads, list) or not payloads:
            return False

        for payload in payloads:
            if not isinstance(payload, dict):
                return False
            external_code = str(payload.get('maquina_id') or '').strip().upper()
            machine = Machine.objects.filter(external_code=external_code, ativo=True).first()
            if not machine or not user_can_access_machine(request.user, machine, write=True):
                return False
        return True
