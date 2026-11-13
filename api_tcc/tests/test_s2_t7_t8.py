import hashlib
from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from api_tcc.models import AuditLog, DeviceCredential, LeituraTelemetria, Machine
from api_tcc.services.device_credentials import provision_http_credential
from simulators.edge_client import generate_payload


class AuditLogAppendOnlyTest(TestCase):
    def test_rota_de_login_sem_barra_nao_redireciona_mutacao(self):
        response = APIClient().post("/api/auth/login", {}, format="json")
        self.assertEqual(response.status_code, 404)

    def test_orm_rejeita_update_delete_e_bulk_update(self):
        entry = AuditLog.objects.create(action="unit.test", result="allowed")
        with self.assertRaises(TypeError):
            entry.action = "changed"
            entry.save()
        with self.assertRaises(TypeError):
            entry.delete()
        with self.assertRaises(TypeError):
            AuditLog.objects.filter(pk=entry.pk).update(action="changed")
        with self.assertRaises(TypeError):
            AuditLog.objects.filter(pk=entry.pk).delete()
        with self.assertRaises(TypeError):
            AuditLog.objects.bulk_update([entry], ["action"])
        with self.assertRaises(TypeError):
            AuditLog.objects.bulk_create(
                [AuditLog(id=entry.pk, action="changed", result="allowed")],
                update_conflicts=True,
                update_fields=["action"],
                unique_fields=["id"],
            )

    def test_admin_consulta_sem_mutar(self):
        from api_tcc.admin import AuditLogAdmin
        from django.contrib import admin
        from django.test import RequestFactory

        instance = AuditLogAdmin(AuditLog, admin.site)
        request = RequestFactory().get("/admin/api_tcc/auditlog/")
        request.user = User.objects.create_superuser("audit-admin", "audit@example.com", "pass")
        self.assertFalse(instance.has_add_permission(request))
        self.assertTrue(instance.has_view_permission(request))
        self.assertFalse(instance.has_change_permission(request))
        self.assertFalse(instance.has_delete_permission(request))


class DeviceHTTPIngestionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.device_id = "HTTP-DEVICE-A"
        Machine.objects.create(external_code=self.device_id)
        self.credential = DeviceCredential.objects.create(
            device_id=self.device_id, username=self.device_id,
            credential_hash="!", active=False,
        )
        self.key = "unique-test-http-device-secret"
        self.credential.http_key_hash = hashlib.sha256(self.key.encode()).hexdigest()
        self.credential.save(update_fields=["http_key_hash"])

    def _post(self, payload, key=None, device_id=None):
        return self.client.post(
            "/api/telemetria/", payload, format="json",
            HTTP_X_DEVICE_ID=device_id or self.device_id,
            HTTP_X_DEVICE_KEY=key or self.key,
        )

    @override_settings(DEBUG=False, ALLOW_LEGACY_INGESTION_KEY=False, FIELDNODE_API_KEY="legacy")
    def test_credencial_individual_autentica_e_rejeita_spoof_sem_persistir(self):
        payload = generate_payload(self.device_id, 1, 1)
        response = self._post(payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(LeituraTelemetria.objects.count(), 1)
        self.credential.refresh_from_db()
        self.assertIsNotNone(self.credential.http_last_seen_at)
        spoof = self._post({**generate_payload(self.device_id, 2, 2), "device_id": "HTTP-DEVICE-B"})
        self.assertEqual(spoof.status_code, 403)
        self.assertEqual(LeituraTelemetria.objects.count(), 1)

    @override_settings(DEBUG=False, ALLOW_LEGACY_INGESTION_KEY=True, FIELDNODE_API_KEY="legacy")
    def test_chave_global_nao_autentica_fora_de_debug(self):
        response = self.client.post(
            "/api/telemetria/", generate_payload(self.device_id, 1, 1), format="json",
            HTTP_X_API_KEY="legacy",
        )
        self.assertEqual(response.status_code, 401)

    def test_revogacao_e_rotacao_de_24_horas(self):
        new_key = provision_http_credential(self.device_id, rotate=True)
        self.credential.refresh_from_db()
        self.assertEqual(self.credential.http_previous_key_hash, hashlib.sha256(self.key.encode()).hexdigest())
        self.assertTrue(self.credential.http_rotation_deadline)
        self.assertEqual(len(new_key), 43)
        self.assertEqual(self._post(generate_payload(self.device_id, 1, 1), key=self.key).status_code, 201)
        self.assertEqual(self._post(generate_payload(self.device_id, 2, 2), key=new_key).status_code, 201)
        DeviceCredential.objects.filter(pk=self.credential.pk).update(
            http_rotation_deadline=timezone.now() - timedelta(seconds=1)
        )
        self.assertEqual(self._post(generate_payload(self.device_id, 3, 3), key=self.key).status_code, 401)
        provision_http_credential(self.device_id, revoke=True)
        self.credential.refresh_from_db()
        self.assertIsNotNone(self.credential.http_revoked_at)
        self.assertEqual(AuditLog.objects.filter(action="credential.rotated").count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="credential.revoked").count(), 1)

    @override_settings(DEBUG=True, ALLOW_LEGACY_INGESTION_KEY=True, FIELDNODE_API_KEY="dev-legacy")
    def test_chave_global_legada_somente_em_debug(self):
        response = self.client.post(
            "/api/telemetria/", generate_payload(self.device_id, 1, 1), format="json",
            HTTP_X_API_KEY="dev-legacy",
        )
        self.assertEqual(response.status_code, 201)

    @override_settings(DEBUG=True, ALLOW_LEGACY_INGESTION_KEY=True, FIELDNODE_API_KEY="dev-legacy")
    def test_credencial_individual_invalida_nao_faz_fallback_global(self):
        response = self.client.post(
            "/api/telemetria/", generate_payload(self.device_id, 1, 1), format="json",
            HTTP_X_DEVICE_ID=self.device_id,
            HTTP_X_DEVICE_KEY="invalid-device-key",
            HTTP_X_API_KEY="dev-legacy",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(LeituraTelemetria.objects.count(), 0)

