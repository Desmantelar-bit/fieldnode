from django.test import TestCase
from django.core.exceptions import ValidationError

from api_tcc.models import CanonicalTelemetry, Machine, RawTelemetry
from api_tcc.services.conversoes import convert_value
from api_tcc.services.normalizacao import normalizar


class ProvenienciaTelemetryTest(TestCase):
    def setUp(self):
        self.machine = Machine.objects.create(external_code="S11-T2-01")

    def test_conversoes_declarativas(self):
        value, unit, factor, offset = convert_value(212, "F", "engine.temperature")
        self.assertAlmostEqual(value, 100.0)
        self.assertEqual(unit, "C")
        self.assertAlmostEqual(factor, 5 / 9)
        self.assertAlmostEqual(offset, -32 * 5 / 9)
        value, unit, factor, offset = convert_value(10, "psi", "engine.oil_pressure")
        self.assertAlmostEqual(value, 68.94757293168)
        self.assertEqual((unit, offset), ("kPa", 0.0))

    def test_origem_e_controlada_e_obrigatoria(self):
        raw = RawTelemetry.objects.create(
            machine=self.machine, manufacturer="sim", raw_parameter="rpm",
            raw_value=100, unit="rpm", source_protocol_simulado="sim",
            origem="simulado", payload_original={},
        )
        for origem in ("medido", "calculado", "estimado", "simulado"):
            CanonicalTelemetry(
                raw_telemetry=raw, canonical_parameter=f"engine.rpm.{origem}",
                value=100, unit="rpm", mapping_version="test", origem=origem,
                fonte="sim",
            ).save()
        with self.assertRaises(ValidationError):
            CanonicalTelemetry(
                raw_telemetry=raw, canonical_parameter="engine.rpm.missing",
                value=100, unit="rpm", mapping_version="test", fonte="sim",
            ).save()
        with self.assertRaises(ValidationError):
            CanonicalTelemetry(
                raw_telemetry=raw, canonical_parameter="engine.rpm.invalid",
                value=100, unit="rpm", mapping_version="test", origem="inventada",
                fonte="sim",
            ).save()

    def test_normalizacao_preserva_proveniencia_e_unidade(self):
        raw = RawTelemetry.objects.create(
            machine=self.machine, manufacturer="fieldnode_simulator_v1",
            raw_parameter="temperatura", raw_value=212, unit="F",
            source_protocol_simulado="sensor:simulado", origem="simulado",
            payload_original={"temperatura": 212},
        )
        canonical = normalizar(raw)
        self.assertAlmostEqual(canonical.value, 100.0)
        self.assertEqual(canonical.unit, "C")
        self.assertEqual(canonical.unidade_original, "F")
        self.assertEqual(canonical.fonte, "sensor:simulado")
        self.assertEqual(canonical.origem, "simulado")

    def test_unidade_desconhecida_nao_fabrica_canonico(self):
        raw = RawTelemetry.objects.create(
            machine=self.machine, manufacturer="fieldnode_simulator_v1",
            raw_parameter="temperatura", raw_value=80, unit="kelvin-ish",
            source_protocol_simulado="api", origem="simulado", payload_original={},
        )
        self.assertIsNone(normalizar(raw))
        raw.refresh_from_db()
        self.assertEqual(raw.quality, "unsupported_unit")
        self.assertFalse(CanonicalTelemetry.objects.filter(raw_telemetry=raw).exists())
