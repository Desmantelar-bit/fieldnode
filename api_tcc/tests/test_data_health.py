import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from django.db import connection
from django.test import SimpleTestCase, TestCase
from django.test.utils import CaptureQueriesContext

from api_tcc.models import LeituraTelemetria, Machine, MachineDataHealth
from api_tcc.services.data_health import (
    TRUST_SCORE_EMA_ALPHA,
    atualizar_machine_data_health,
    calcular_trust_score,
)
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


def _payload(
    *,
    maquina_id: str = "COLH-HEALTH",
    message_id: str | None = None,
    timestamp: datetime | None = None,
    temperatura: float = 72.0,
    vibracao: float = 0.35,
    rpm: int = 1800,
) -> dict:
    timestamp = timestamp or _dt(10)
    return {
        "device_id": maquina_id,
        "message_id": message_id or str(uuid.uuid4()),
        "maquina_id": maquina_id,
        "temperatura": temperatura,
        "vibracao": vibracao,
        "rpm": rpm,
        "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
    }


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


class MachineDataHealthServiceTest(TestCase):
    def test_primeira_atualizacao_cria_health(self):
        machine = Machine.objects.create(external_code="COLH-EMA-01")

        health = atualizar_machine_data_health(
            machine=machine,
            trust_score=0.9,
            motivos=["primeira leitura da machine: sem baseline temporal"],
            timestamp=_dt(10),
        )

        self.assertIsNotNone(health)
        self.assertEqual(MachineDataHealth.objects.count(), 1)
        self.assertEqual(health.trust_score_medio, 0.9)
        self.assertEqual(health.leituras_analisadas, 1)
        self.assertTrue(health.sinais_de_alerta["primeira_leitura"])

    def test_segunda_atualizacao_usa_ema_e_nao_substitui_score(self):
        machine = Machine.objects.create(external_code="COLH-EMA-02")
        atualizar_machine_data_health(
            machine=machine,
            trust_score=0.9,
            motivos=[],
            timestamp=_dt(10),
        )

        health = atualizar_machine_data_health(
            machine=machine,
            trust_score=0.6,
            motivos=["salto abrupto em relacao a leitura anterior"],
            timestamp=_dt(10, 5),
        )

        esperado = round(TRUST_SCORE_EMA_ALPHA * 0.6 + (1 - TRUST_SCORE_EMA_ALPHA) * 0.9, 4)
        self.assertEqual(health.trust_score_medio, esperado)
        self.assertNotEqual(health.trust_score_medio, 0.6)
        self.assertEqual(health.leituras_analisadas, 2)
        self.assertTrue(health.sinais_de_alerta["salto_abrupto"])


class MachineDataHealthIntegrationTest(TestCase):
    def test_dez_leituras_consecutivas_atualizam_health_unico_sem_custo_crescente(self):
        base_ts = _dt(10)
        scores_observados = []

        for idx in range(9):
            status, _ = registrar_leitura(
                _payload(
                    message_id=f"msg-{idx}",
                    timestamp=base_ts + timedelta(minutes=idx * 5),
                    temperatura=72.0 + idx,
                    vibracao=0.35 + idx * 0.01,
                    rpm=1800 + idx,
                )
            )
            self.assertEqual(status, "criado")
            health = MachineDataHealth.objects.get(machine__external_code="COLH-HEALTH")
            scores_observados.append(health.trust_score_medio)

        with CaptureQueriesContext(connection) as ctx:
            status, _ = registrar_leitura(
                _payload(
                    message_id="msg-9",
                    timestamp=base_ts + timedelta(minutes=45),
                    temperatura=81.0,
                    vibracao=0.44,
                    rpm=1809,
                )
            )

        self.assertEqual(status, "criado")
        health = MachineDataHealth.objects.get(machine__external_code="COLH-HEALTH")
        scores_observados.append(health.trust_score_medio)

        self.assertEqual(MachineDataHealth.objects.count(), 1)
        self.assertEqual(health.leituras_analisadas, 10)
        self.assertGreaterEqual(health.trust_score_medio, 0.0)
        self.assertLessEqual(health.trust_score_medio, 1.0)
        self.assertEqual(len(scores_observados), 10)

        sql = "\n".join(query["sql"].upper() for query in ctx.captured_queries)
        self.assertNotIn("AVG(", sql)
        self.assertNotIn("GROUP BY", sql)
        self.assertNotIn("COUNT(", sql)

    def test_replay_idempotente_nao_incrementa_health(self):
        payload = _payload(message_id="msg-replay")

        status_1, _ = registrar_leitura(payload)
        status_2, _ = registrar_leitura(payload)

        health = MachineDataHealth.objects.get(machine__external_code="COLH-HEALTH")
        self.assertEqual(status_1, "criado")
        self.assertEqual(status_2, "duplicata")
        self.assertEqual(LeituraTelemetria.objects.count(), 1)
        self.assertEqual(health.leituras_analisadas, 1)

    def test_health_permanece_isolado_por_machine(self):
        registrar_leitura(_payload(maquina_id="COLH-A", message_id="a-1", timestamp=_dt(10)))
        registrar_leitura(_payload(maquina_id="COLH-B", message_id="b-1", timestamp=_dt(10), temperatura=149.0))
        registrar_leitura(_payload(maquina_id="COLH-A", message_id="a-2", timestamp=_dt(10, 5)))

        health_a = MachineDataHealth.objects.get(machine__external_code="COLH-A")
        health_b = MachineDataHealth.objects.get(machine__external_code="COLH-B")

        self.assertEqual(health_a.leituras_analisadas, 2)
        self.assertEqual(health_b.leituras_analisadas, 1)
        self.assertNotEqual(health_a.machine_id, health_b.machine_id)

    def test_endpoint_retorna_contrato_do_health_persistido(self):
        registrar_leitura(_payload(message_id="endpoint-1"))
        machine = Machine.objects.get(external_code="COLH-HEALTH")

        response = self.client.get(f"/api/machines/{machine.id}/health/")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["machine_id"], str(machine.id))
        self.assertEqual(data["external_code"], "COLH-HEALTH")
        self.assertEqual(data["status"], "ok")
        self.assertIsInstance(data["trust_score_medio"], float)
        self.assertGreaterEqual(data["trust_score_medio"], 0.0)
        self.assertLessEqual(data["trust_score_medio"], 1.0)
        self.assertEqual(data["leituras_analisadas"], 1)
        self.assertIsNotNone(data["ultima_atualizacao"])
        self.assertIn("score_baixo", data["sinais_de_alerta"])

    def test_endpoint_machine_inexistente_retorna_404(self):
        response = self.client.get(f"/api/machines/{uuid.uuid4()}/health/")

        self.assertEqual(response.status_code, 404)

    def test_endpoint_machine_existente_sem_health_nao_inventa_score(self):
        machine = Machine.objects.create(external_code="COLH-SEM-DADOS")

        response = self.client.get(f"/api/machines/{machine.id}/health/")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "sem_dados")
        self.assertIsNone(data["trust_score_medio"])
        self.assertIsNone(data["ultima_atualizacao"])
        self.assertEqual(data["leituras_analisadas"], 0)
        self.assertEqual(data["sinais_de_alerta"], {})
