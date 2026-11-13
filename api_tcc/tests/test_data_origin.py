from django.test import TestCase

from api_tcc.api.serializers import LeituraTelemetriaSerializer
from api_tcc.models import LeituraTelemetria
from api_tcc.services.telemetria import registrar_leitura
from api_tcc.tests.test_telemetria import _payload


class DataOriginTest(TestCase):
    def test_simulator_ingest_persists_and_serializes_simulated_origin(self):
        payload = _payload(maquina_id="ORIGIN-SIM", source="simulador")
        result, reading_id = registrar_leitura(payload)
        self.assertEqual(result, "criado")
        reading = LeituraTelemetria.objects.get(pk=reading_id)
        self.assertEqual(reading.data_origin, "simulado")
        self.assertEqual(LeituraTelemetriaSerializer(reading).data["data_origin"], "simulado")

    def test_authenticated_device_is_measured_but_unverified_origin_stays_unknown(self):
        measured = _payload(maquina_id="ORIGIN-DEVICE", device_id="ORIGIN-DEVICE", source="gateway")
        result, reading_id = registrar_leitura(measured, authenticated_device_id="ORIGIN-DEVICE")
        self.assertEqual(result, "criado")
        self.assertEqual(LeituraTelemetria.objects.get(pk=reading_id).data_origin, "medido")

        unknown = _payload(maquina_id="ORIGIN-UNKNOWN", source="api", manufacturer="gateway_v1")
        result, unknown_id = registrar_leitura(unknown)
        self.assertEqual(result, "criado")
        self.assertIsNone(LeituraTelemetria.objects.get(pk=unknown_id).data_origin)

