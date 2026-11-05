import math

from django.test import SimpleTestCase

from api_tcc.contracts import ContractError, classify, severity_contract, transmission_class
from api_tcc.services.telemetria import validar_payload


class SeverityContractV1Tests(SimpleTestCase):
    def test_contract_values_and_boundaries(self):
        self.assertEqual(severity_contract()["schema"], "severity.v1")
        self.assertEqual(classify("temperatura", 74.9999), "NORMAL")
        self.assertEqual(classify("temperatura", 75.0), "ATENCAO")
        self.assertEqual(classify("temperatura", 84.9999), "ATENCAO")
        self.assertEqual(classify("temperatura", 85.0), "CRITICO")
        self.assertEqual(classify("temperatura", 85.0001), "CRITICO")
        self.assertEqual(classify("vibracao", 5.0), "ATENCAO")
        self.assertEqual(classify("vibracao", 8.0), "CRITICO")

    def test_invalid_values_and_rpm_are_explicit(self):
        for value in (None, "x", math.nan, math.inf, -math.inf, -1, 151):
            with self.assertRaises(ContractError):
                classify("temperatura", value)
        with self.assertRaises(ContractError):
            classify("rpm", 1800)
        with self.assertRaises(ContractError):
            classify("desconhecida", 1)

    def test_critical_always_has_transmission_class_a(self):
        for quality in ("boa", "suspeita", "insuficiente"):
            for delayed in (False, True):
                self.assertEqual(transmission_class("CRITICO", quality, delayed), "A")
        self.assertEqual(transmission_class("ATENCAO", "boa", False), "B")
        self.assertEqual(transmission_class("ATENCAO", "suspeita", False), "B")
        self.assertEqual(transmission_class("NORMAL", "insuficiente", False), "B")
        self.assertEqual(transmission_class("NORMAL", "boa", True), "B")
        self.assertEqual(transmission_class("NORMAL", "boa", False), "C")

    def test_vibration_unit_is_not_silently_converted(self):
        base = {
            "maquina_id": "M-1", "temperatura": 70, "vibracao": 0.6,
            "rpm": 1800, "timestamp": "2026-11-05T12:00:00Z",
        }
        self.assertEqual(validar_payload(dict(base)), (True, ""))
        ok, reason = validar_payload({**base, "vibracao_unit": "g"})
        self.assertFalse(ok)
        self.assertIn("vibracao_unit", reason)
        ok, reason = validar_payload({**base, "vibracao_unit": "indice_0_10", "vibracao": 10.1})
        self.assertFalse(ok)
        self.assertIn("fora do range", reason)
