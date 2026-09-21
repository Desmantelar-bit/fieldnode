from datetime import datetime, timezone
from types import SimpleNamespace

from django.test import SimpleTestCase, TestCase

from api_tcc.models import LeituraTelemetria, Machine
from api_tcc.services.data_health import calcular_trust_score
from api_tcc.services.telemetria import registrar_leitura


def _dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 6, 1, hour, minute, tzinfo=timezone.utc)


def _leitura(
    *,
    timestamp: datetime,
    temperatura: float = 72.0,
    vibracao: float = 0.35,
    rpm: int = 1800,
    machine: object | None = None,
):
    return SimpleNamespace(
        timestamp=timestamp,
        temperatura=temperatura,
        vibracao=vibracao,
        rpm=rpm,
        machine=machine,
    )


class CalcularTrustScoreTest(SimpleTestCase):
    def test_leitura_limpa_recebe_score_alto(self):
        leitura = _leitura(timestamp=_dt(10), temperatura=72.0, vibracao=0.35, rpm=1800)
        historico = [
            _leitura(timestamp=_dt(9, 55), temperatura=70.0, vibracao=0.33, rpm=1785),
            _leitura(timestamp=_dt(9, 50), temperatura=68.0, vibracao=0.31, rpm=1770),
        ]

        score, motivos = calcular_trust_score(leitura, historico)

        self.assertGreaterEqual(score, 0.95)
        self.assertTrue(any("continuidade suave" in motivo for motivo in motivos))

    def test_sensor_repetido_cinco_vezes_reduz_score(self):
        leitura = _leitura(timestamp=_dt(10), temperatura=100.0, vibracao=1.0, rpm=2000)
        historico = [
            _leitura(timestamp=_dt(9, 59 - idx), temperatura=100.0, vibracao=1.0, rpm=2000)
            for idx in range(4)
        ]

        score, motivos = calcular_trust_score(leitura, historico)

        self.assertLess(score, 0.70)
        self.assertTrue(any("repetidos consecutivamente" in motivo for motivo in motivos))

    def test_gap_de_duas_horas_penaliza_score(self):
        leitura_gap = _leitura(timestamp=_dt(12), temperatura=72.0, vibracao=0.35, rpm=1800)
        leitura_normal = _leitura(timestamp=_dt(10, 5), temperatura=72.0, vibracao=0.35, rpm=1800)
        historico = [_leitura(timestamp=_dt(10), temperatura=70.0, vibracao=0.33, rpm=1785)]

        score_gap, motivos_gap = calcular_trust_score(leitura_gap, historico)
        score_normal, _ = calcular_trust_score(leitura_normal, historico)

        self.assertLess(score_gap, score_normal)
        self.assertTrue(any("gap temporal acima" in motivo for motivo in motivos_gap))

    def test_leitura_no_limite_fisico_sofre_penalidade_leve(self):
        leitura = _leitura(timestamp=_dt(10), temperatura=150.0, vibracao=0.35, rpm=1800)

        score, motivos = calcular_trust_score(leitura, [])

        self.assertGreaterEqual(score, 0.85)
        self.assertLess(score, 1.0)
        self.assertTrue(any("limite fisico" in motivo for motivo in motivos))

    def test_timestamp_fora_de_ordem_penaliza_score(self):
        leitura = _leitura(timestamp=_dt(9, 59), temperatura=72.0, vibracao=0.35, rpm=1800)
        historico = [_leitura(timestamp=_dt(10), temperatura=71.0, vibracao=0.34, rpm=1790)]

        score, motivos = calcular_trust_score(leitura, historico)

        self.assertLess(score, 0.80)
        self.assertTrue(any("fora de ordem" in motivo for motivo in motivos))

    def test_continuidade_suave_supera_salto_abrupto(self):
        historico = [_leitura(timestamp=_dt(10), temperatura=70.0, vibracao=0.33, rpm=1785)]
        leitura_suave = _leitura(timestamp=_dt(10, 5), temperatura=72.0, vibracao=0.35, rpm=1800)
        leitura_abrupta = _leitura(timestamp=_dt(10, 5), temperatura=140.0, vibracao=7.0, rpm=3600)

        score_suave, motivos_suave = calcular_trust_score(leitura_suave, historico)
        score_abrupto, motivos_abrupto = calcular_trust_score(leitura_abrupta, historico)

        self.assertGreater(score_suave, score_abrupto)
        self.assertTrue(any("continuidade suave" in motivo for motivo in motivos_suave))
        self.assertTrue(any("salto abrupto" in motivo for motivo in motivos_abrupto))

    def test_primeira_leitura_nao_quebra_e_nao_penaliza_gap(self):
        leitura = _leitura(timestamp=_dt(10))

        score, motivos = calcular_trust_score(leitura, [])

        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        self.assertTrue(any("primeira leitura" in motivo for motivo in motivos))
        self.assertFalse(any("gap temporal acima" in motivo for motivo in motivos))

    def test_score_permanece_no_dominio(self):
        leitura = _leitura(timestamp=_dt(8), temperatura=150.0, vibracao=10.0, rpm=5000)
        historico = [
            _leitura(timestamp=_dt(10), temperatura=150.0, vibracao=10.0, rpm=5000)
            for _ in range(5)
        ]

        score, _ = calcular_trust_score(leitura, historico)

        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_resultado_e_deterministico(self):
        leitura = _leitura(timestamp=_dt(10), temperatura=72.0, vibracao=0.35, rpm=1800)
        historico = [_leitura(timestamp=_dt(9, 55), temperatura=70.0, vibracao=0.33, rpm=1785)]

        resultado_1 = calcular_trust_score(leitura, historico)
        resultado_2 = calcular_trust_score(leitura, historico)

        self.assertEqual(resultado_1, resultado_2)


class RegistrarLeituraTrustScoreIntegrationTest(TestCase):
    def test_registrar_leitura_persiste_trust_score_da_machine_correta(self):
        registrar_leitura(
            {
                "id": "00000000-0000-4000-8000-000000000001",
                "maquina_id": "COLH-B",
                "temperatura": 99.0,
                "vibracao": 2.0,
                "rpm": 2100,
                "timestamp": "2026-06-01T09:55:00Z",
            }
        )

        status, leitura_id = registrar_leitura(
            {
                "id": "00000000-0000-4000-8000-000000000002",
                "maquina_id": "COLH-A",
                "temperatura": 72.0,
                "vibracao": 0.35,
                "rpm": 1800,
                "timestamp": "2026-06-01T10:00:00Z",
            }
        )

        leitura = LeituraTelemetria.objects.get(id=leitura_id)

        self.assertEqual(status, "criado")
        self.assertEqual(leitura.machine.external_code, "COLH-A")
        self.assertIsNotNone(leitura.trust_score)
        self.assertGreaterEqual(leitura.trust_score, 0.0)
        self.assertLessEqual(leitura.trust_score, 1.0)
        self.assertEqual(Machine.objects.count(), 2)
