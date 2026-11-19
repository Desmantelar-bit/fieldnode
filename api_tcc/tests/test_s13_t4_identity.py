from datetime import datetime, timezone
from unittest.mock import patch

from django.test import SimpleTestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.test import TestCase

from api_tcc.models import Decision, Event, Machine, Membership, Organization

from api_tcc.services.hlc import HLC, decision_id, event_id


class S13T4IdentityTest(SimpleTestCase):
    def test_same_fact_on_two_nodes_has_same_event_and_decision_ids(self):
        timestamp = datetime(2026, 11, 19, 12, 17, tzinfo=timezone.utc)
        first = event_id("COLH-01", "TEMP_ALTA", timestamp)
        second = event_id("COLH-01", "TEMP_ALTA", timestamp)
        self.assertEqual(first, second)
        self.assertEqual(decision_id(first, "TEMP_ALTA"), decision_id(second, "TEMP_ALTA"))

    def test_hlc_stays_monotonic_when_physical_clock_goes_back(self):
        logical = HLC("edge-a")
        with patch("api_tcc.services.hlc.time.time", side_effect=[100.0, 99.0, 99.0]):
            first = logical.now()
            second = logical.now()
            third = logical.now()
        self.assertLess((first[0], first[1]), (second[0], second[1]))
        self.assertLess((second[0], second[1]), (third[0], third[1]))

    def test_update_advances_after_remote_clock(self):
        logical = HLC("cloud")
        with patch("api_tcc.services.hlc.time.time", return_value=10.0):
            value = logical.update((20_000, 4, "edge"))
        self.assertEqual(value, (20_000, 5, "cloud"))


class S13T4ActionReplayTest(TestCase):
    def test_same_idempotency_key_replays_the_original_result(self):
        user = User.objects.create_user(username="offline-operator", password="test-pass")
        token = Token.objects.create(user=user)
        organization = Organization.objects.create(nome="Offline Org")
        Membership.objects.create(user=user, organization=organization, role="admin")
        machine = Machine.objects.create(external_code="OFFLINE-01", organization=organization)
        decision = Decision.objects.create(
            machine=machine,
            texto="Inspecionar",
            acao_recomendada="Validar sensor",
            severidade=Event.Severidade.ATENCAO,
        )
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        body = {"status": Decision.Status.REJEITADA, "motivo_rejeicao": "OUTRO"}
        first = client.patch(f"/api/decisions/{decision.pk}/", body, format="json", HTTP_IDEMPOTENCY_KEY="offline-key-1")
        second = client.patch(f"/api/decisions/{decision.pk}/", body, format="json", HTTP_IDEMPOTENCY_KEY="offline-key-1")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data, second.data)
        self.assertEqual(Decision.objects.get(pk=decision.pk).status, Decision.Status.REJEITADA)
