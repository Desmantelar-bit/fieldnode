import json
import os
from types import SimpleNamespace
from unittest.mock import patch
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from api_tcc.api.throttles import (
    SecurityCounterUnavailable, increment_security_counter, normalized_login_identity,
    record_login_failure, security_counter_value,
)
from api_tcc.management.commands import mqtt_listen
from api_tcc.models import DeadLetterEntry, DeviceCredential


class AuthenticationAbuseControlsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @override_settings(REGISTRATION_ENABLED=False, DEMO_MODE=False)
    def test_disabled_registration_always_returns_403_and_creates_nothing(self):
        for index in range(50):
            response = self.client.post("/api/auth/register/", {
                "username": f"disabled-{index}", "password": "A-strong-password-123!",
            }, format="json")
            self.assertEqual(response.status_code, 403)
        self.assertFalse(User.objects.filter(username__startswith="disabled-").exists())

    @override_settings(REGISTRATION_ENABLED=True, DEMO_MODE=True)
    def test_demo_always_disables_registration(self):
        response = self.client.post("/api/auth/register/", {
            "username": "demo-blocked", "password": "A-strong-password-123!",
        }, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertFalse(User.objects.filter(username="demo-blocked").exists())

    def test_sixth_login_attempt_is_throttled(self):
        for _ in range(5):
            response = self.client.post("/api/auth/login/", {
                "username": "missing-user", "password": "wrong",
            }, format="json")
            self.assertEqual(response.status_code, 401)
        response = self.client.post("/api/auth/login/", {
            "username": "missing-user", "password": "wrong",
        }, format="json")
        self.assertEqual(response.status_code, 429)

    def test_ip_limit_cannot_be_evaded_by_changing_usernames(self):
        self.client.defaults["REMOTE_ADDR"] = "192.0.2.10"
        for index in range(5):
            response = self.client.post("/api/auth/login/", {
                "username": f"different-{index}", "password": "wrong",
            }, format="json")
            self.assertEqual(response.status_code, 401)
        response = self.client.post("/api/auth/login/", {
            "username": "another-user", "password": "wrong",
        }, format="json")
        self.assertEqual(response.status_code, 429)

    def test_identity_limit_cannot_be_evaded_by_changing_ip(self):
        for index in range(5):
            self.client.defaults["REMOTE_ADDR"] = f"192.0.2.{index + 1}"
            response = self.client.post("/api/auth/login/", {
                "username": "same-identity", "password": "wrong",
            }, format="json")
            self.assertEqual(response.status_code, 401)
        self.client.defaults["REMOTE_ADDR"] = "192.0.2.20"
        response = self.client.post("/api/auth/login/", {
            "username": "same-identity", "password": "wrong",
        }, format="json")
        self.assertEqual(response.status_code, 429)

    @override_settings(REGISTRATION_ENABLED=True, DEMO_MODE=False)
    def test_enabled_registration_is_limited_to_three_per_ip_hour(self):
        for index in range(3):
            response = self.client.post("/api/auth/register/", {
                "username": f"allowed-{index}", "password": "A-strong-password-123!",
            }, format="json")
            self.assertEqual(response.status_code, 201)
        response = self.client.post("/api/auth/register/", {
            "username": "limited-fourth", "password": "A-strong-password-123!",
        }, format="json")
        self.assertEqual(response.status_code, 429)
        self.assertFalse(User.objects.filter(username="limited-fourth").exists())

    def test_login_error_is_indistinguishable_for_existing_and_missing_user(self):
        User.objects.create_user(username="present-user", password="Correct-123!x")
        existing = self.client.post("/api/auth/login/", {
            "username": "present-user", "password": "wrong",
        }, format="json")
        missing = self.client.post("/api/auth/login/", {
            "username": "absent-user", "password": "wrong",
        }, format="json")
        self.assertEqual(existing.status_code, missing.status_code)
        self.assertEqual(existing.data, missing.data)

    def test_login_counters_are_distinctly_hashed_and_user_limit_uses_identity(self):
        self.assertEqual(normalized_login_identity(SimpleNamespace(data={"username": "  USER@X "})), "user@x")
        self.assertEqual(increment_security_counter("test-identity", 60), 1)
        self.assertEqual(increment_security_counter("test-identity", 60), 2)

    def test_lockout_counter_expires_after_15_minutes(self):
        for _ in range(5):
            record_login_failure("locked-identity")
        key = "login:failed:locked-identity"
        self.assertEqual(security_counter_value(key), 5)
        start = timezone.now()
        with patch("api_tcc.api.throttles.timezone.now", return_value=start + timedelta(minutes=16)):
            self.assertEqual(security_counter_value(key), 0)

    def test_counter_backend_failure_is_fail_closed(self):
        with patch("api_tcc.api.throttles.increment_security_counter", side_effect=SecurityCounterUnavailable()):
            response = self.client.post("/api/auth/login/", {
                "username": "service-unavailable", "password": "wrong",
            }, format="json")
        self.assertEqual(response.status_code, 503)


class MqttIdentityBoundaryTests(TestCase):
    def setUp(self):
        DeviceCredential.objects.create(
            device_id="device-A", username="device-A", credential_hash="!",
            active=True, provisioning_state="active",
        )

    def test_payload_spoof_is_written_to_dlq_without_ingestion(self):
        message = SimpleNamespace(
            topic="fieldnode/device-A/telemetria",
            payload=json.dumps({"device_id": "device-B", "maquina_id": "TRACTOR-B"}).encode(),
        )
        with patch.object(mqtt_listen, "registrar_leitura") as registrar:
            mqtt_listen.on_message(None, None, message)
        registrar.assert_not_called()
        entry = DeadLetterEntry.objects.get(contexto="MQTT_SPOOF")
        self.assertEqual(entry.payload_referencia["topic_device_id"], "device-A")
        self.assertEqual(entry.payload_referencia["declared_device_id"], "device-B")

    def test_malformed_json_does_not_escape_message_callback(self):
        message = SimpleNamespace(topic="fieldnode/device-A/telemetria", payload=b"{")
        mqtt_listen.on_message(None, None, message)

    def test_malformed_topic_is_rejected_before_ingestion(self):
        message = SimpleNamespace(topic="fieldnode/device-A/telemetria/extra", payload=b"{}")
        with patch.object(mqtt_listen, "registrar_leitura") as registrar:
            mqtt_listen.on_message(None, None, message)
        registrar.assert_not_called()

    def test_revoked_device_cannot_ingest(self):
        DeviceCredential.objects.filter(device_id="device-A").update(active=False)
        message = SimpleNamespace(
            topic="fieldnode/device-A/telemetria",
            payload=json.dumps({"device_id": "device-A"}).encode(),
        )
        with patch.object(mqtt_listen, "registrar_leitura") as registrar:
            mqtt_listen.on_message(None, None, message)
        registrar.assert_not_called()
        self.assertTrue(DeadLetterEntry.objects.filter(contexto="MQTT_SPOOF").exists())

    @override_settings(DEBUG=False)
    def test_worker_refuses_missing_password_before_connect(self):
        with patch.dict(os.environ, {
            "MQTT_WORKER_USERNAME": "fieldnode-worker",
            "MQTT_WORKER_PASSWORD_FILE": "Z:/path/that/does/not/exist",
        }, clear=False), patch.object(mqtt_listen.mqtt, "Client") as client_class:
            with self.assertRaisesRegex(RuntimeError, "Credenciais MQTT"):
                mqtt_listen.Command().handle()
        client_class.assert_not_called()
