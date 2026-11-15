from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from api_tcc.models import Decision, Event, MaintenanceContact, Machine, Membership, Organization, WorkOrder
from api_tcc.services.decision_schema import validate_decision_details
from api_tcc.services.workorders import approve


def details():
    now = timezone.now().isoformat()
    return {
        "schema": "decision.v1",
        "observado": "Temperatura acima do limiar",
        "evidencias": [{"leitura_id": "reading-1", "campo": "temperatura", "valor": 91.2, "limiar": 85.0, "event_time": now}],
        "janela_analisada": {"inicio": now, "fim": now, "n_leituras": 1},
        "qualidade_dado": {"evidence_quality": "boa", "fatores": []},
        "regra": {"id": "TEMP_ALTA_CRITICA", "versao": "1.0"},
        "modelo": {"id": "anomalia-v1", "score": 0.82, "contribuinte": "temperatura"},
        "dados_faltantes": [], "horizonte_minutos": None, "alternativas": ["reduzir carga"],
    }


class S4T2SchemaTest(TestCase):
    def test_decision_v1_requires_evidence(self):
        valid = details()
        self.assertIs(validate_decision_details(valid), valid)
        valid["evidencias"] = []
        with self.assertRaises(ValidationError):
            validate_decision_details(valid)


class S4T3WorkOrderTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("s4-t3", password="password")
        self.other = User.objects.create_user("s4-t3-other", password="password")
        self.org = Organization.objects.create(nome="Org S4-T3")
        other_org = Organization.objects.create(nome="Outra Org")
        Membership.objects.create(user=self.user, organization=self.org, role="admin")
        Membership.objects.create(user=self.other, organization=other_org, role="admin")
        self.machine = Machine.objects.create(external_code="S4-T3-MACHINE", organization=self.org)
        self.contact = MaintenanceContact.objects.create(organization=self.org, nome="Ana", funcao="Manutencao", email="ana@example.com")
        self.decision = Decision.objects.create(machine=self.machine, texto="Inspecionar", acao_recomendada="Abrir OS", severidade=Event.Severidade.CRITICO, detalhes=details())

    def test_approval_creates_work_order_atomically(self):
        order = approve(self.decision, self.user, responsavel_tipo="contact", responsavel_id=str(self.contact.pk), prazo=timezone.now() + timedelta(hours=2))
        self.assertEqual(order.status, WorkOrder.Status.ABERTA)
        self.decision.refresh_from_db()
        self.assertEqual(self.decision.status, Decision.Status.APROVADA)
        self.assertEqual(order.responsavel_contato_id, self.contact.id)

    def test_contact_from_other_organization_is_rejected(self):
        other_org = Organization.objects.create(nome="Org Contato Externo")
        foreign = MaintenanceContact.objects.create(organization=other_org, nome="Fora", funcao="Manutencao", email="fora@example.com")
        with self.assertRaises(ValueError):
            approve(self.decision, self.user, responsavel_tipo="contact", responsavel_id=str(foreign.pk), prazo=timezone.now() + timedelta(hours=2))
        self.assertFalse(WorkOrder.objects.exists())
