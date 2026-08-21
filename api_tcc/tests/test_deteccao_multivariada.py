from django.test import SimpleTestCase

from api_tcc.ia.deteccao_multivariada import MODELO_PATH, calcular_score_anomalia
from api_tcc.ia.pipeline import detectar_anomalia


class DeteccaoMultivariadaTests(SimpleTestCase):
    def test_modelo_de_bancada_esta_disponivel(self):
        self.assertTrue(MODELO_PATH.exists())

    def test_cenario_normal_nao_dispara_o_isolation_forest(self):
        resultado = calcular_score_anomalia(68.0, 1.4, 1500.0)

        self.assertFalse(resultado['anomalia_multivariada'])

    def test_threshold_deterministico_permanece_prioritario(self):
        tem_anomalia, motivos = detectar_anomalia(
            {'temp_max': 86.0, 'temp_tendencia': 0.0, 'vib_media': 1.5},
            {'temperatura': 86.0, 'vibracao': 1.5, 'rpm': 1500.0},
        )

        self.assertTrue(tem_anomalia)
        self.assertEqual(motivos, ['temperatura acima de 85°C'])

    def test_caso_multivariado_complementa_thresholds(self):
        tem_anomalia, motivos = detectar_anomalia(
            {'temp_max': 82.0, 'temp_tendencia': 0.0, 'vib_media': 4.8},
            {'temperatura': 82.0, 'vibracao': 4.8, 'rpm': 1200.0},
        )

        self.assertTrue(tem_anomalia)
        self.assertEqual(
            motivos,
            ['padrão combinado de sensores fora do comportamento usual (Isolation Forest)'],
        )
