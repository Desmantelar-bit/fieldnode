from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api_tcc.models import Decision, Machine, Membership, Organization


class LegacyDecisionCompatibilityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("s4-compat", password="unused")
        self.organization = Organization.objects.create(nome="S4 compatibility")
        self.machine = Machine.objects.create(
            external_code="S4-COMPAT-01", organization=self.organization
        )
        Membership.objects.create(
            user=self.user, organization=self.organization, role="admin"
        )
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=self.user).key}"
        )

    def test_legacy_list_reads_decision_and_marks_deprecation(self):
        decision = Decision.objects.create(
            machine=self.machine,
            texto="Texto central",
            acao_recomendada="Ação central",
            severidade="ATENCAO",
        )

        response = self.client.get(
            "/api/prescricoes/lista/", {"maquina_id": self.machine.external_code}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Deprecation"], "true")
        self.assertEqual(response.data[0]["decision_id"], str(decision.id))
        self.assertEqual(response.data[0]["descricao"], "Texto central")
        self.assertEqual(response.data[0]["titulo"], "Ação central")

