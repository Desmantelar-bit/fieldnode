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
        import hmac
        supplied = request.headers.get('X-API-Key', '')
        expected = getattr(settings, 'FIELDNODE_API_KEY', '')
        if supplied and expected and hmac.compare_digest(supplied, expected):
            request.authenticated_ingestion_device_id = None
            return True
        for device_id, device_key in getattr(settings, 'FIELDNODE_DEVICE_API_KEYS', {}).items():
            if supplied and hmac.compare_digest(supplied, device_key):
                request.authenticated_ingestion_device_id = device_id
                return True
        return False


class HasIngestionCredential(BasePermission):
    """Accept device API keys or authorized members sending browser telemetry."""
    message = 'Credencial inválida ou sem acesso de escrita à máquina.'

    def has_permission(self, request, view):
        if HasValidIngestionAPIKey().has_permission(request, view):
            device_id = getattr(request, 'authenticated_ingestion_device_id', None)
            if not device_id:
                return True
            payloads = request.data.get('leituras') if isinstance(request.data, dict) else None
            if payloads is None:
                payloads = [request.data]
            return bool(
                isinstance(payloads, list)
                and payloads
                and all(
                    isinstance(payload, dict)
                    and str(payload.get('device_id') or '').strip() == device_id
                    for payload in payloads
                )
            )
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
