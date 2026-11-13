from django.test import SimpleTestCase

from api_tcc.contracts import classify, transmission_class
from api_tcc.services.telemetria import validar_payload


class SeverityContractTests(SimpleTestCase):
    def test_inclusive_boundaries(self):
        self.assertEqual(classify("temperatura", 84.9999), "ATENCAO")
        self.assertEqual(classify("temperatura", 85.0), "CRITICO")
        self.assertEqual(classify("temperatura", 85.0001), "CRITICO")
        self.assertEqual(classify("vibracao", 4.999), "NORMAL")
        self.assertEqual(classify("vibracao", 5.0), "ATENCAO")
        self.assertEqual(classify("vibracao", 8.0), "CRITICO")

    def test_critical_always_transmits_as_class_a(self):
        for quality in ("boa", "suspeita", "insuficiente"):
            for delayed in (False, True):
                self.assertEqual(transmission_class("CRITICO", quality, delayed), "A")

    def test_vibration_unit_is_explicit_or_legacy_default_and_g_is_rejected(self):
        payload = {
            "maquina_id": "UNIT-TEST", "temperatura": 70, "vibracao": 0.6,
            "rpm": 1200, "timestamp": "2026-11-12T12:00:00Z",
        }
        self.assertEqual(validar_payload(payload), (True, ""))
        self.assertEqual(payload["vibracao_unit"], "indice_0_10")
        payload["vibracao_unit"] = "g"
        valid, reason = validar_payload(payload)
        self.assertFalse(valid)
        self.assertIn("vibracao_unit inválida", reason)

    def test_edges_of_vibration_contract_range(self):
        self.assertEqual(classify("vibracao", 0), "NORMAL")
        self.assertEqual(classify("vibracao", 10), "CRITICO")
