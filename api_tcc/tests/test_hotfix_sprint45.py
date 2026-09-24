import uuid

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from api_tcc.models import (
    Decision,
    Event,
    Machine,
    Membership,
    Organization,
)
from api_tcc.permissions import get_machines_for_user, user_can_access_machine


class Sprint45AuthorizationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org_a = Organization.objects.create(nome="Org A")
        self.org_b = Organization.objects.create(nome="Org B")
        self.admin = User.objects.create_user(username="admin-a")
        self.viewer = User.objects.create_user(username="viewer-a")
        self.foreign = User.objects.create_user(username="foreign")
        Membership.objects.create(user=self.admin, organization=self.org_a, role="admin")
        Membership.objects.create(user=self.viewer, organization=self.org_a, role="viewer")
        Membership.objects.create(user=self.foreign, organization=self.org_b, role="admin")
        self.machine = Machine.objects.create(
            external_code="HOTFIX-A",
            organization=self.org_a,
        )
        self.foreign_machine = Machine.objects.create(
            external_code="HOTFIX-B",
            organization=self.org_b,
        )

    def test_machine_queryset_is_limited_to_user_tenant(self):
        self.assertEqual(
            list(get_machines_for_user(self.admin)),
            [self.machine],
        )
        self.assertTrue(user_can_access_machine(self.admin, self.machine))
        self.assertFalse(user_can_access_machine(self.admin, self.foreign_machine))

    def test_viewer_cannot_change_decision(self):
        decision = Decision.objects.create(
            machine=self.machine,
            texto="Temperatura alta",
            acao_recomendada="Inspecionar",
            severidade=Event.Severidade.CRITICO,
        )
        self.client.force_authenticate(self.viewer)

        response = self.client.patch(
            f"/api/decisions/{decision.id}/",
            {"status": Decision.Status.APROVADA},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        decision.refresh_from_db()
        self.assertEqual(decision.status, Decision.Status.PENDENTE)

    def test_foreign_tenant_cannot_change_decision(self):
        decision = Decision.objects.create(
            machine=self.machine,
            texto="Temperatura alta",
            acao_recomendada="Inspecionar",
            severidade=Event.Severidade.CRITICO,
        )
        self.client.force_authenticate(self.foreign)

        response = self.client.patch(
            f"/api/decisions/{decision.id}/",
            {"status": Decision.Status.APROVADA},
            format="json",
        )

        self.assertEqual(response.status_code, 403)


class Sprint45BatchIngestionTest(TestCase):
    @override_settings(FIELDNODE_API_KEY="test-key")
    def test_batch_uses_composite_identity_and_domain_pipeline(self):
        payload = {
            "device_id": "HOTFIX-DEVICE",
            "message_id": "message-001",
            "maquina_id": "HOTFIX-BATCH",
            "sequence_number": 7,
            "temperatura": 86.0,
            "vibracao": 0.4,
            "rpm": 1800,
            "timestamp": "2026-09-24T10:00:00Z",
        }
        client = APIClient()

        response = client.post(
            "/api/telemetria/lote/",
            {"leituras": [payload, {**payload, "id": str(uuid.uuid4())}]},
            format="json",
            HTTP_X_API_KEY="test-key",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["salvas"], 1)
        self.assertEqual(response.data["duplicadas"], 1)
        self.assertEqual(response.data["invalidas"], 0)

        machine = Machine.objects.get(external_code="HOTFIX-BATCH")
        leitura = machine.leituras.get()
        self.assertIsNotNone(leitura.trust_score)
        self.assertEqual(machine.events.count(), 1)
        self.assertEqual(machine.leituras.count(), 1)
