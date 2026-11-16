from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from api_tcc.models import LeituraTelemetria
from api_tcc.services.reconstrucao import reconstruir_janela
from api_tcc.services.telemetria import registrar_leitura


class ReconstrucaoTemporalTest(TestCase):
    def payload(self, message_id, event_time, temperature=72.0):
        return {
            "maquina_id": "RECON-01", "device_id": "RECON-01", "message_id": message_id,
            "sequence_number": int(event_time.timestamp()), "temperatura": temperature,
            "vibracao": 0.4, "rpm": 1700, "time_source": "gateway",
            "timestamp": event_time.isoformat(), "schema_version": "1.1",
        }

    def test_late_reading_is_temporally_marked_and_recalculated_locally(self):
        base = timezone.now() - timedelta(hours=6)
        for index in (0, 2):
            self.assertEqual(registrar_leitura(self.payload(f"m{index}", base + timedelta(minutes=index)))[0], "criado")
        status, reading_id = registrar_leitura(
            self.payload("m1", base + timedelta(minutes=1), temperature=97.4)
        )
        self.assertEqual(status, "criado")
        late = LeituraTelemetria.objects.get(pk=reading_id)
        self.assertTrue(late.atrasado)
        self.assertLess(late.timestamp, late.recebido_em)
        ordered = list(LeituraTelemetria.objects.filter(machine=late.machine).order_by("timestamp").values_list("message_id", flat=True))
        self.assertEqual(ordered, ["m0", "m1", "m2"])
        before = LeituraTelemetria.objects.get(message_id="m0").trust_score
        result = reconstruir_janela(machine=late.machine, event_time=late.timestamp)
        self.assertGreaterEqual(result.leituras_recalculadas, 0)
        self.assertEqual(LeituraTelemetria.objects.get(message_id="m0").trust_score, before)
