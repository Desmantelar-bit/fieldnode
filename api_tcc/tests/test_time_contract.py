import uuid
from datetime import timedelta
from types import SimpleNamespace

from django.test import TestCase
from django.utils import timezone

from api_tcc.api.serializers import LeituraTelemetriaSerializer
from api_tcc.models import Event, LeituraTelemetria, MachineDataHealth
from api_tcc.services.data_health import calcular_trust_score
from api_tcc.services.telemetria import _computar_payload_hash, registrar_leitura


class TelemetryTimeContractTests(TestCase):
    def test_hash_logico_compartilha_vetor_backend_edge_e_service_worker(self):
        payload = {
            "id": "row-ignored",
            "device_id": "EDGE-ACK-01",
            "message_id": "logical-message-1",
            "sequence_number": 7,
            "maquina_id": "EDGE-ACK-01",
            "temperatura": 86,
            "vibracao": 0.35,
            "rpm": 1800,
            "timestamp": "2026-11-05T12:00:00Z",
            "time_source": "unsynced",
            "boot_id": "12345678-1234-5678-1234-567812345678",
            "uptime_ms": 7000,
        }

        self.assertEqual(
            _computar_payload_hash(payload),
            "62d356c473139e1d59d1d36bd0b6ddb01e91e3b621aeb0fbc582b302161e36e1",
        )

    def _payload(self, *, boot_id, uptime_ms, time_source="unsynced", **overrides):
        payload = {
            "device_id": "TIME-CONTRACT-01",
            "maquina_id": "TIME-CONTRACT-01",
            "message_id": str(uuid.uuid4()),
            "sequence_number": uptime_ms,
            "temperatura": 72.0,
            "vibracao": 0.35,
            "rpm": 1800,
            "boot_id": boot_id,
            "uptime_ms": uptime_ms,
            "time_source": time_source,
        }
        payload.update(overrides)
        return payload

    def test_offline_readings_reconstruct_from_anchor_in_the_same_boot(self):
        boot_id = str(uuid.uuid4())
        status, reading_id = registrar_leitura(
            self._payload(boot_id=boot_id, uptime_ms=1_000)
        )
        self.assertEqual(status, "criado")
        provisional = LeituraTelemetria.objects.get(id=reading_id).timestamp

        anchor_status, anchor_id = registrar_leitura(
            self._payload(
                boot_id=boot_id,
                uptime_ms=21_601_000,
                time_source="gateway",
            )
        )
        self.assertEqual(anchor_status, "criado")

        delayed = LeituraTelemetria.objects.get(id=reading_id)
        anchor = LeituraTelemetria.objects.get(id=anchor_id)
        self.assertEqual(delayed.timestamp, anchor.timestamp - timedelta(hours=6))
        self.assertNotEqual(delayed.timestamp, provisional)
        self.assertEqual(delayed.time_source, "unsynced")
        self.assertEqual(delayed.event_time_confidence, "low")
        self.assertIsNone(delayed.clock_skew_ms)
        serialized = LeituraTelemetriaSerializer(delayed).data
        self.assertEqual(serialized["event_time_confidence"], "low")

    def test_clock_anchors_from_different_boots_are_isolated(self):
        boot_a = str(uuid.uuid4())
        boot_b = str(uuid.uuid4())
        status, reading_id = registrar_leitura(
            self._payload(boot_id=boot_a, uptime_ms=1_000)
        )
        self.assertEqual(status, "criado")
        delayed = LeituraTelemetria.objects.get(id=reading_id)
        provisional = delayed.timestamp

        status, _ = registrar_leitura(
            self._payload(
                boot_id=boot_b,
                uptime_ms=21_601_000,
                time_source="gateway",
            )
        )
        self.assertEqual(status, "criado")
        delayed.refresh_from_db()
        self.assertEqual(delayed.timestamp, provisional)

    def test_unsynced_time_reduces_trust_and_records_reason(self):
        values = {
            "timestamp": timezone.now(),
            "temperatura": 72.0,
            "vibracao": 0.35,
            "rpm": 1800,
        }
        trusted = SimpleNamespace(**values, time_source="ntp")
        unsynced = SimpleNamespace(**values, time_source="unsynced")

        trusted_score, _ = calcular_trust_score(trusted, [])
        unsynced_score, reasons = calcular_trust_score(unsynced, [])

        self.assertLess(unsynced_score, trusted_score)
        self.assertTrue(any("hora do dispositivo" in reason for reason in reasons))

    def test_ingestao_expõe_penalidade_e_selo_no_evento(self):
        status, reading_id = registrar_leitura(
            self._payload(
                boot_id=str(uuid.uuid4()),
                uptime_ms=10_000,
                temperatura=86.0,
            )
        )

        self.assertEqual(status, "criado")
        reading = LeituraTelemetria.objects.get(id=reading_id)
        health = MachineDataHealth.objects.get(machine=reading.machine)
        event = Event.objects.get(leitura_origem=reading)

        self.assertTrue(health.sinais_de_alerta["hora_dispositivo_nao_confiavel"])
        self.assertLess(reading.trust_score, 0.8)
        self.assertEqual(event.evidence_quality, Event.EvidenceQuality.SUSPEITA)
        self.assertTrue(event.needs_verification)
