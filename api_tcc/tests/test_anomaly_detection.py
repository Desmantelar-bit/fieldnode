import time
import uuid

from django.test import TransactionTestCase

from api_tcc.models import Decision, Event, Machine, MachineDataHealth
from api_tcc.services.anomaly_detection import REGISTRY, detect_anomaly
from api_tcc.services.telemetria import registrar_leitura


class AnomalyDetectionTest(TransactionTestCase):
    def setUp(self):
        REGISTRY.clear()

    def tearDown(self):
        REGISTRY.clear()

    def _payload(self, machine_id, index, temperatura, vibracao, rpm):
        return {
            "id": str(uuid.uuid4()),
            "device_id": machine_id,
            "message_id": f"message-{index}",
            "maquina_id": machine_id,
            "temperatura": temperatura,
            "vibracao": vibracao,
            "rpm": rpm,
            "timestamp": f"2026-09-24T{10 + index // 60:02d}:{index % 60:02d}:00Z",
        }

    def test_cold_start_uses_zscore_and_detects_temperature_peak(self):
        machine_id = "ML-COLD-START"
        for index in range(5):
            registrar_leitura(self._payload(machine_id, index, 70.0 + index, 0.4, 1800))

        status, _ = registrar_leitura(
            self._payload(machine_id, 5, 120.0, 0.4, 1800)
        )

        self.assertEqual(status, "criado")
        event = Event.objects.get(
            machine__external_code=machine_id,
            tipo=Event.Tipo.ANOMALIA_ESTATISTICA,
        )
        decision = Decision.objects.get(event=event)
        self.assertEqual(event.dados_contexto["detection_method"], "COLD_START_ZSCORE")
        self.assertTrue(event.dados_contexto["anomaly_score"] >= 0.70)
        self.assertEqual(decision.confianca, event.dados_contexto["anomaly_score"])
        self.assertIn("explanation", decision.detalhes)
        self.assertEqual(
            MachineDataHealth.objects.get(machine__external_code=machine_id).anomalias_detectadas,
            1,
        )

    def test_isolation_forest_handles_multidimensional_outlier(self):
        machine_id = "ML-ISOLATION"
        for index in range(101):
            registrar_leitura(
                self._payload(
                    machine_id,
                    index,
                    70.0 + (index % 5),
                    0.35 + (index % 4) * 0.01,
                    1750 + (index % 6) * 10,
                )
            )

        result = detect_anomaly(
            machine_id,
            {"temperatura": 72.0, "vibracao": 8.0, "rpm": 800},
        )

        self.assertEqual(result.detection_method, "ISOLATION_FOREST")
        self.assertTrue(result.is_anomaly)
        self.assertGreaterEqual(result.anomaly_score, 0.70)

    def test_detector_cached_execution_is_under_twenty_milliseconds(self):
        machine_id = "ML-PERFORMANCE"
        for index in range(100):
            registrar_leitura(self._payload(machine_id, index, 72.0, 0.4, 1800))
        detect_anomaly(machine_id, {"temperatura": 72.0, "vibracao": 0.4, "rpm": 1800})

        started = time.perf_counter()
        detect_anomaly(machine_id, {"temperatura": 72.0, "vibracao": 0.4, "rpm": 1800})
        elapsed = time.perf_counter() - started

        self.assertLess(elapsed, 0.020)
