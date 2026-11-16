import csv
import tempfile
from datetime import date
from pathlib import Path

from django.core import management
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from api_tcc.models import Decision, Event, Machine, MachineSpec, MaintenanceRecord, Organization
from api_tcc.services.labeled_dataset import materialize_decision
from api_tcc.services.thresholds import effective_thresholds


class S5T9LabeledDatasetTest(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(nome="Org dataset")
        self.machine = Machine.objects.create(external_code="DATASET-01", organization=self.organization)

    def test_falso_alarme_is_human_negative_and_reproducible(self):
        decision = Decision.objects.create(
            machine=self.machine, texto="Inspecionar", acao_recomendada="Inspecionar",
            severidade=Event.Severidade.ATENCAO, status=Decision.Status.REJEITADA,
            motivo_rejeicao="FALSO_ALARME", decidido_em=timezone.now(),
        )
        first = materialize_decision(decision)
        second = materialize_decision(decision)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(first.label, "negativo")
        self.assertEqual(first.fonte_rotulo, "humano")

    def test_sem_desfecho_nao_materializa(self):
        decision = Decision.objects.create(
            machine=self.machine, texto="Inspecionar", acao_recomendada="Inspecionar",
            severidade=Event.Severidade.ATENCAO,
        )
        self.assertIsNone(materialize_decision(decision))


class S5T10MaintenanceTest(TestCase):
    def setUp(self):
        self.machine = Machine.objects.create(external_code="MAINT-01")

    def test_horas_acumuladas_nao_diminuem(self):
        MachineSpec.objects.create(machine=self.machine, horas_motor="100.00")
        with self.assertRaises(ValidationError):
            MachineSpec.objects.create(machine=Machine.objects.create(external_code="MAINT-02"), horas_motor="-1")

    def test_limite_da_machine_spec_e_clamped_pelo_contrato(self):
        MachineSpec.objects.create(machine=self.machine, limites_json={"temperatura": {"atencao": 80, "critico": 140}})
        thresholds = effective_thresholds(self.machine, "temperatura")
        self.assertEqual(thresholds["atencao"], 80)
        self.assertEqual(thresholds["critico"], 85)
        self.assertEqual(thresholds["limite_origem"], "machine_spec_clamped")

    def test_importacao_rejeita_linha_invalida_e_nao_duplica(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "maintenance.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["machine", "registro_id", "data", "tipo", "horas_motor", "pecas", "observacao"], delimiter=";")
                writer.writeheader()
                writer.writerow({"machine": "MAINT-01", "registro_id": "M-1", "data": "2026-01-10", "tipo": "filtro", "horas_motor": "100", "pecas": "[]", "observacao": "sintetico"})
                writer.writerow({"machine": "MAINT-01", "registro_id": "M-2", "data": "data-invalida", "tipo": "filtro", "horas_motor": "100", "pecas": "[]", "observacao": "sintetico"})
            management.call_command("importar_manutencao", str(path), stdout=None)
            management.call_command("importar_manutencao", str(path), stdout=None)
        self.assertEqual(MaintenanceRecord.objects.filter(machine=self.machine).count(), 1)
