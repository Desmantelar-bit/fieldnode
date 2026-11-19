from django.test import TestCase

from api_tcc.adapters import get_adapter
from api_tcc.models import CanonicalTelemetry, FabricanteMapping, Machine, RawTelemetry
from api_tcc.services.j1939 import decode
from api_tcc.services.normalizacao import normalizar


class UMMConformidadeTest(TestCase):
    """Convergência controlada de J1939 e dois formatos demonstrativos."""

    def setUp(self):
        self.machine = Machine.objects.create(external_code="S11-T5-01")
        mappings = [
            ("j1939_test", "SPN_190", "engine.rpm", "rpm"),
            ("j1939_test", "SPN_110", "engine.coolant_temp", "C"),
            ("demo_metrics_v1", "rpm", "engine.rpm", "rpm"),
            ("demo_metrics_v1", "coolant_temp", "engine.coolant_temp", "C"),
            ("demo_readings_v1", "engine_speed", "engine.rpm", "rpm"),
            ("demo_readings_v1", "coolant_temperature", "engine.coolant_temp", "C"),
        ]
        for manufacturer, raw_parameter, canonical, unit in mappings:
            FabricanteMapping.objects.create(
                manufacturer=manufacturer, raw_parameter=raw_parameter,
                canonical_parameter=canonical, mapping_version="umm-test-v1",
                unit_conversion_factor=1.0, ativo=True,
            )

    def _canonical(self, manufacturer, raw_parameter, value, unit, origem):
        raw = RawTelemetry.objects.create(
            machine=self.machine, manufacturer=manufacturer, raw_parameter=raw_parameter,
            raw_value=value, unit=unit, source_protocol_simulado=manufacturer,
            origem=origem, payload_original={raw_parameter: value},
        )
        return normalizar(raw)

    def test_rpm_e_temperatura_convergem_sem_apagar_proveniencia(self):
        j1939 = decode(0x0CF00401, bytes.fromhex("FF FF FF 80 3E FF FF FF"))
        j1939_temp = decode(0x18FEEE22, bytes.fromhex("78 FF FF FF FF FF FF FF"))
        a = get_adapter("demo_metrics_v1").parse({
            "metrics": {"rpm": {"value": 2000, "unit": "rpm"}, "coolant_temp": {"value": 80, "unit": "C"}}
        })
        b = get_adapter("demo_readings_v1").parse({
            "readings": [{"name": "engine_speed", "value": 2000, "unit": "rpm"}, {"name": "coolant_temperature", "value": 80, "unit": "C"}]
        })
        results = [
            self._canonical("j1939_test", "SPN_190", j1939[0].value, "rpm", "medido"),
            self._canonical("demo_metrics_v1", "rpm", a[0].value, "rpm", "simulado"),
            self._canonical("demo_readings_v1", "engine_speed", b[0].value, "rpm", "simulado"),
            self._canonical("j1939_test", "SPN_110", j1939_temp[0].value, "C", "medido"),
            self._canonical("demo_metrics_v1", "coolant_temp", a[1].value, "C", "simulado"),
            self._canonical("demo_readings_v1", "coolant_temperature", b[1].value, "C", "simulado"),
        ]
        for group in (results[:3], results[3:]):
            self.assertEqual({item.canonical_parameter for item in group}, {group[0].canonical_parameter})
            self.assertEqual({item.unit for item in group}, {group[0].unit})
            self.assertTrue(all(abs(item.value - group[0].value) <= 0.001 for item in group))
        self.assertEqual([item.origem for item in results[:3]], ["medido", "simulado", "simulado"])
