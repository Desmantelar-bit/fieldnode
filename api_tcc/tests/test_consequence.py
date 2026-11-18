from datetime import timedelta

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone

from api_tcc.models import Event, Front, LeituraTelemetria, Machine, MachineLink, MachineSpec, Organization, Site
from api_tcc.services.consequence import R2_MIN, avaliar, tendencia_linear
from api_tcc.services.operation_graph import criar_machine_link


class ConsequenceEngineTests(TestCase):
    def setUp(self):
        self.now = timezone.now().replace(microsecond=0)
        self.org = Organization.objects.create(nome="Org")
        self.site = Site.objects.create(organization=self.org, nome="Site", codigo="S")
        self.harvester = Machine.objects.create(external_code="COLH-1", tipo="colhedora", organization=self.org, site=self.site)
        self.transbordo = Machine.objects.create(external_code="TRANS-1", tipo="transbordo", organization=self.org, site=self.site)
        MachineSpec.objects.create(machine=self.harvester, limites_json={"temperatura": {"critico": 90}})

    def reading(self, minute, temperature):
        return LeituraTelemetria.objects.create(
            maquina_id=self.harvester.external_code,
            machine=self.harvester,
            device_id=self.harvester.external_code,
            message_id=f"m-{minute}",
            timestamp=self.now - timedelta(minutes=30 - minute),
            temperatura=temperature,
            vibracao=1.0,
        )

    def event(self, quality="boa"):
        return Event.objects.create(
            machine=self.harvester,
            tipo=Event.Tipo.TEMP_ALTA,
            severidade=Event.Severidade.CRITICO,
            evidence_quality=quality,
        )

    def test_growing_series_returns_manual_horizon_and_premise(self):
        self.reading(0, 60)
        self.reading(15, 67.5)
        self.reading(30, 75)
        assessment = avaliar(self.event(), em=self.now)
        self.assertEqual(assessment.horizonte_minutos, 30.0)
        self.assertTrue(assessment.premissas)
        self.assertIn("R²=1.00", assessment.premissas[0])

    def test_noisy_series_below_r2_does_not_return_horizon(self):
        self.reading(0, 60)
        self.reading(5, 72)
        self.reading(10, 61)
        self.reading(15, 75)
        self.assertIsNotNone(tendencia_linear(self.harvester, em=self.now))
        self.assertLess(tendencia_linear(self.harvester, em=self.now).r2, R2_MIN)
        self.assertIsNone(avaliar(self.event(), em=self.now).horizonte_minutos)

    def test_suspect_evidence_lowers_risk_and_requests_sensor_check(self):
        assessment = avaliar(self.event("suspeita"), em=self.now)
        self.assertEqual(assessment.risco_parada, "medio")
        self.assertTrue(assessment.needs_verification)
        self.assertTrue(any("verificar sensor" in item for item in assessment.faltantes))

    def test_no_links_do_not_invent_affected_machines(self):
        assessment = avaliar(self.event(), em=self.now)
        self.assertEqual(assessment.afetados, [])
        self.assertTrue(any("não existem vínculos" in item for item in assessment.faltantes))

    def test_transbordo_without_capacity_is_explicitly_missing(self):
        criar_machine_link(origem=self.harvester, destino=self.transbordo, tipo=MachineLink.Tipo.ALIMENTA, valido_de=self.now, organization=self.org)
        assessment = avaliar(self.event(), em=self.now)
        self.assertTrue(any("capacidade do TRANS-1" in item for item in assessment.faltantes))


class ImportLinksCommandTests(TestCase):
    def test_invalid_csv_is_atomic(self):
        from tempfile import NamedTemporaryFile

        org = Organization.objects.create(nome="Org")
        a = Machine.objects.create(external_code="A", organization=org)
        b = Machine.objects.create(external_code="B", organization=org)
        with NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".csv", delete=False) as handle:
            handle.write("origem,destino,tipo,front,de,ate\n")
            handle.write("A,B,ALIMENTA,,2026-01-01T00:00:00+00:00,\n")
            handle.write("A,INEXISTENTE,ALIMENTA,,2026-01-01T00:00:00+00:00,\n")
            filename = handle.name
        with self.assertRaises(CommandError):
            call_command("importar_links", filename, organization=str(org.pk))
        self.assertEqual(MachineLink.objects.count(), 0)
