from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from api_tcc.models import Decision, Event, Machine, MachineDataHealth, Membership, Organization


class AttentionSummaryViewTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="attention-reader", password="test-password")
        self.organization = Organization.objects.create(nome="Attention Org")
        Membership.objects.create(user=user, organization=self.organization, role="viewer")
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_summary_counts_authorized_objects_and_returns_priority_events(self):
        machine = Machine.objects.create(external_code="ATT-01", organization=self.organization)
        event = Event.objects.create(
            machine=machine,
            tipo=Event.Tipo.TEMP_ALTA,
            severidade=Event.Severidade.CRITICO,
            status=Event.Status.ABERTO,
            priority_score="0.1000",
            needs_verification=True,
        )
        Decision.objects.create(
            machine=machine,
            event=event,
            texto="Verificar condição crítica",
            acao_recomendada="Inspecionar",
            severidade=Event.Severidade.CRITICO,
            status=Decision.Status.PENDENTE,
        )
        MachineDataHealth.objects.create(
            machine=machine,
            trust_score_medio=0.70,
            ultima_atualizacao=timezone.now(),
            leituras_analisadas=1,
        )

        response = self.client.get("/api/attention/summary/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["decisoes_pendentes"], 1)
        self.assertEqual(response.data["riscos_criticos"], 1)
        self.assertEqual(response.data["eventos_criticos"], 1)
        self.assertEqual(response.data["maquinas_dados_instaveis"], 1)
        self.assertEqual(response.data["eventos"][0]["id"], str(event.id))
        self.assertTrue(response.data["eventos"][0]["needs_verification"])

    def test_summary_does_not_include_other_organizations(self):
        other = Organization.objects.create(nome="Other Org")
        machine = Machine.objects.create(external_code="ATT-OTHER", organization=other)
        Event.objects.create(
            machine=machine,
            tipo=Event.Tipo.TEMP_ALTA,
            severidade=Event.Severidade.CRITICO,
            status=Event.Status.ABERTO,
            priority_score="1.0000",
        )

        response = self.client.get("/api/attention/summary/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["eventos_criticos"], 0)
        self.assertEqual(response.data["eventos"], [])
