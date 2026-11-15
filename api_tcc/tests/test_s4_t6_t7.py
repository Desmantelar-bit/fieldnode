from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from api_tcc.models import AuditLog, Decision, Event, Machine, MaintenanceContact, Membership, Organization, ThresholdOverride, WorkOrder
from api_tcc.services.thresholds import create_threshold_override, effective_thresholds


class S4T6ThresholdOverrideTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("mechanic", password="password")
        self.org = Organization.objects.create(nome="Org thresholds")
        Membership.objects.create(user=self.user, organization=self.org, role="member")
        self.machine = Machine.objects.create(external_code="THRESHOLD-01", organization=self.org)

    def test_override_never_exceeds_contract_critical_limit(self):
        with self.assertRaises(ValueError):
            create_threshold_override(machine=self.machine, metric="temperatura", atencao=84, critico=86, motivo="teste", criado_por=self.user, expira_em=timezone.now() + timedelta(days=1))

    def test_override_expires_and_is_auditable(self):
        override = create_threshold_override(machine=self.machine, metric="temperatura", atencao=80, critico=85, motivo="falso alarme confirmado", criado_por=self.user, expira_em=timezone.now() + timedelta(hours=1))
        self.assertEqual(effective_thresholds(self.machine, "temperatura")["atencao"], 80)
        self.assertEqual(effective_thresholds(self.machine, "temperatura", at=override.expira_em + timedelta(seconds=1))["atencao"], 75)
        self.assertTrue(ThresholdOverride.objects.filter(pk=override.pk).exists())


class S4T7WorkOrderAgendaTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("planner", password="password")
        self.org = Organization.objects.create(nome="Org agenda")
        Membership.objects.create(user=self.user, organization=self.org, role="admin")
        self.machine = Machine.objects.create(external_code="AGENDA-01", organization=self.org)
        contact = MaintenanceContact.objects.create(organization=self.org, nome="Joao", funcao="Mecanico", email="joao@example.com")
        decision = Decision.objects.create(machine=self.machine, texto="Inspecionar", acao_recomendada="Inspecionar", severidade=Event.Severidade.ATENCAO)
        self.order = WorkOrder.objects.create(decision=decision, machine=self.machine, titulo="OS agenda", descricao="Teste", prioridade=Event.Severidade.ATENCAO, prazo=timezone.now() + timedelta(days=2), responsavel_contato=contact, criado_por=self.user)
        self.client = APIClient(); self.client.force_authenticate(self.user)

    def test_list_filters_period_and_reschedule_writes_history_and_audit(self):
        response = self.client.get("/api/workorders/", {"de": (timezone.localdate() + timedelta(days=1)).isoformat(), "ate": (timezone.localdate() + timedelta(days=3)).isoformat()})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        new_deadline = timezone.now() + timedelta(days=4)
        response = self.client.patch(f"/api/workorders/{self.order.id}/", {"prazo": new_deadline.isoformat()}, format="json")
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.historico[-1]["tipo"], "reagendamento")
        self.assertEqual(AuditLog.objects.filter(action="workorder.reschedule", object_id=str(self.order.id)).count(), 1)
