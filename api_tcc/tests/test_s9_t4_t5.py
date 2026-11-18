from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from api_tcc.models import Event, Incident, IncidentEvent, LeituraTelemetria, Machine, MachineSpec, Organization, OrganizationPolicy
from api_tcc.services.consequence import avaliar
from api_tcc.services.incidents import agrupar_evento


class S9PolicyAndConsequenceTests(TestCase):
    def setUp(self):
        self.now = timezone.now().replace(microsecond=0)
        self.org = Organization.objects.create(nome="Org")
        self.machine = Machine.objects.create(external_code="COLH-S9", tipo="colhedora", organization=self.org)
        MachineSpec.objects.create(machine=self.machine, limites_json={"temperatura": {"critico": 90}})

    def _reading(self, minute, temperature):
        return LeituraTelemetria.objects.create(
            maquina_id=self.machine.external_code,
            machine=self.machine,
            device_id=self.machine.external_code,
            message_id=f"s9-{minute}",
            timestamp=self.now - timedelta(minutes=30 - minute),
            temperatura=temperature,
            vibracao=1.0,
        )

    def _event(self):
        return Event.objects.create(
            machine=self.machine,
            tipo=Event.Tipo.TEMP_ALTA,
            severidade=Event.Severidade.CRITICO,
            evidence_quality="boa",
        )

    def test_without_policy_financial_field_is_absent(self):
        for minute, temperature in ((0, 60), (15, 67.5), (30, 75)):
            self._reading(minute, temperature)
        payload = avaliar(self._event(), em=self.now).as_dict()
        self.assertNotIn("custo_estimado", payload)

    def test_client_cost_is_decimal_estimate_and_zero_is_explicit(self):
        for minute, temperature in ((0, 60), (15, 67.5), (30, 75)):
            self._reading(minute, temperature)
        OrganizationPolicy.objects.create(organization=self.org, custo_hora_parada=Decimal("1200.00"))
        assessment = avaliar(self._event(), em=self.now)
        self.assertEqual(assessment.custo_estimado, Decimal("600.00"))
        self.assertEqual(assessment.as_dict()["origem_premissa"], "premissa informada pelo cliente; estimativa matemática")

        policy = OrganizationPolicy.objects.get(organization=self.org)
        policy.custo_hora_parada = Decimal("0.00")
        policy.save()
        self.assertEqual(avaliar(self._event(), em=self.now).custo_estimado, Decimal("0.00"))

    def test_policy_rejects_negative_cost_and_unknown_deadline(self):
        policy = OrganizationPolicy(
            organization=self.org,
            custo_hora_parada=Decimal("-1.00"),
            prazo_por_severidade={"URGENTE": 10},
        )
        with self.assertRaises(ValidationError):
            policy.full_clean()


class S9IncidentTests(TestCase):
    def setUp(self):
        self.now = timezone.now().replace(microsecond=0)
        self.org = Organization.objects.create(nome="Org")
        self.machine = Machine.objects.create(external_code="COLH-I", tipo="colhedora", organization=self.org)

    def _event(self, offset_minutes):
        reading = LeituraTelemetria.objects.create(
            maquina_id=self.machine.external_code,
            machine=self.machine,
            device_id=self.machine.external_code,
            message_id=f"incident-{offset_minutes}",
            timestamp=self.now + timedelta(minutes=offset_minutes),
            temperatura=80,
            vibracao=1,
        )
        return Event.objects.create(
            machine=self.machine,
            leitura_origem=reading,
            tipo=Event.Tipo.TEMP_ALTA,
            severidade=Event.Severidade.ATENCAO,
        )

    def test_three_events_in_eight_minutes_share_one_incident(self):
        incidents = [agrupar_evento(self._event(offset)) for offset in (0, 4, 8)]
        self.assertEqual(Incident.objects.count(), 1)
        self.assertEqual({incident.pk for incident in incidents}, {incidents[0].pk})
        self.assertEqual(IncidentEvent.objects.count(), 3)
        self.assertEqual(incidents[0].rotulo, "Sintomas simultâneos")

    def test_event_at_forty_minutes_opens_another_incident(self):
        first = agrupar_evento(self._event(0))
        second = agrupar_evento(self._event(40))
        self.assertNotEqual(first.pk, second.pk)
        self.assertEqual(Incident.objects.count(), 2)

    def test_missing_event_time_is_not_fabricated(self):
        event = Event.objects.create(machine=self.machine, tipo=Event.Tipo.TEMP_ALTA)
        self.assertIsNone(agrupar_evento(event))
        self.assertEqual(Incident.objects.count(), 0)
