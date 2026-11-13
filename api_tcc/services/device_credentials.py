"""Lifecycle operations for per-device HTTP ingestion credentials."""
import hashlib
import secrets
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from api_tcc.models import DeviceCredential, Machine
from api_tcc.services.audit import record


def _key_hash(key):
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


@transaction.atomic
def provision_http_credential(device_id, request=None, *, rotate=False, revoke=False, actor=None):
    machine = Machine.objects.select_for_update().filter(external_code__iexact=device_id.strip()).first()
    if not machine:
        raise ValueError("A identidade do dispositivo não existe como Machine.")
    credential, _ = DeviceCredential.objects.select_for_update().get_or_create(
        device_id=machine.external_code,
        defaults={"username": machine.external_code, "credential_hash": "!", "active": False},
    )
    now = timezone.now()
    before = {"http_active": bool(credential.http_key_hash and not credential.http_revoked_at), "http_revoked_at": credential.http_revoked_at}
    if revoke:
        if not credential.http_key_hash or credential.http_revoked_at:
            raise ValueError("Nenhuma credencial HTTP ativa para revogar.")
        credential.http_revoked_at = now
        credential.http_previous_key_hash = ""
        credential.http_rotation_deadline = None
        credential.save(update_fields=["http_revoked_at", "http_previous_key_hash", "http_rotation_deadline"])
        record("credential.revoked", credential, request, before=before, after={"http_revoked_at": now}, actor=actor)
        return None
    if credential.http_key_hash and not credential.http_revoked_at and not rotate:
        raise ValueError("Credencial HTTP já existe; solicite rotação explícita.")
    key = secrets.token_urlsafe(32)
    if rotate and credential.http_key_hash and not credential.http_revoked_at:
        credential.http_previous_key_hash = credential.http_key_hash
        credential.http_rotation_deadline = now + timedelta(hours=24)
        action = "credential.rotated"
    else:
        credential.http_previous_key_hash = ""
        credential.http_rotation_deadline = None
        credential.http_created_at = now
        action = "credential.created"
    credential.http_key_hash = _key_hash(key)
    credential.http_revoked_at = None
    credential.save(update_fields=["http_key_hash", "http_created_at", "http_revoked_at", "http_previous_key_hash", "http_rotation_deadline"])
    record(action, credential, request, before=before, after={"http_active": True, "http_rotation_deadline": credential.http_rotation_deadline}, actor=actor)
    return key
