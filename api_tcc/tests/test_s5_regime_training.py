from datetime import timedelta

from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from api_tcc.models import LeituraTelemetria, Machine
from api_tcc.services.anomaly_detection import (
    TRAINING_POLICY,
    aprovar_challenger,
    pode_treinar,
)
from api_tcc.services.regime import inferir_regime


class RegimeInferenceTest(SimpleTestCase):
    def test_limites_e_velocidade(self):
        self.assertEqual(inferir_regime(None), "desconhecido")
        self.assertEqual(inferir_regime(0), "desligada")
        self.assertEqual(inferir_regime(299), "desligada")
        self.assertEqual(inferir_regime(300), "marcha_lenta")
        self.assertEqual(inferir_regime(1000), "trabalhando")
        self.assertEqual(inferir_regime(1700, 9), "deslocamento")
        self.assertEqual(inferir_regime(1800, 9), "trabalhando")


class TrainingPolicyTest(TestCase):
    def test_leituras_insuficientes_expoem_motivos(self):
        machine = Machine.objects.create(external_code="S5-POLICY-01")
        eligible, reasons = pode_treinar(machine)
        self.assertFalse(eligible)
        self.assertIn("INSUFFICIENT_READINGS", reasons)
        self.assertEqual(TRAINING_POLICY["minimum_regimes"], 2)

    def test_challenger_pior_nao_substitui_champion(self):
        accepted, reason = aprovar_challenger({"f1": 0.8}, {"f1": 0.7})
        self.assertFalse(accepted)
        self.assertEqual(reason, "CHALLENGER_NOT_BETTER")

    def test_challenger_sem_validacao_nao_e_aprovado(self):
        accepted, reason = aprovar_challenger({"f1": 0.8}, {"f1": None})
        self.assertFalse(accepted)
        self.assertEqual(reason, "METRIC_UNDEFINED")
