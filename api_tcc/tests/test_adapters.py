from unittest import TestCase

from api_tcc.adapters import Adapter, AdapterError, get_adapter, register, validar_param
from api_tcc.services.j1939 import Param


class AdapterSdkTest(TestCase):
    def test_registry_resolve_fingerprint_e_campos_desconhecidos(self):
        adapter = get_adapter("demo_metrics_v1")
        parsed = adapter.parse({
            "device_id": "demo-1",
            "metrics": {"rpm": {"value": 2000, "unit": "rpm"}, "vendor_future": 7},
            "future_block": {"x": 1},
        })
        self.assertEqual(adapter.fingerprint(), "demo-metrics-v1")
        self.assertEqual(parsed[0].canonical, "engine.rpm")
        unknown = [item for item in parsed if item.status == "unsupported"]
        self.assertEqual({item.raw_field for item in unknown}, {"metrics.vendor_future", "future_block"})

    def test_segundo_formato_e_validacao_uniforme(self):
        parsed = get_adapter("demo_readings_v1").parse({
            "asset_id": "demo-2",
            "readings": [
                {"name": "engine_speed", "value": 6001, "unit": "rpm"},
                {"name": "coolant_temperature", "value": 80, "unit": "C"},
                {"name": "future_signal", "value": 4, "unit": "x"},
            ],
        })
        self.assertEqual(parsed[0].status, "invalid")
        self.assertEqual(parsed[0].quality, "out_of_physical_range")
        self.assertEqual(parsed[1].canonical, "engine.coolant_temp")
        self.assertEqual(parsed[2].status, "unsupported")

    def test_adaptador_de_teste_extensivel_sem_alterar_normalizacao(self):
        @register("test_extension_s11")
        class TestExtension(Adapter):
            def fingerprint(self):
                return "test-extension-v1"

            def _parse(self, payload):
                return [Param("engine.rpm", payload["rpm"], "rpm", origem="simulado", fonte="test")]

        result = get_adapter("test_extension_s11").parse({"rpm": 1200})
        self.assertEqual(result[0].value, 1200)
        self.assertEqual(result[0].status, "decoded")

    def test_registry_rejeita_conflito_e_adaptador_inexistente(self):
        with self.assertRaises(AdapterError):
            register("demo_metrics_v1")(type("Conflict", (Adapter,), {
                "fingerprint": lambda self: "x",
                "_parse": lambda self, payload: [],
            }))
        with self.assertRaises(AdapterError):
            get_adapter("does-not-exist")

    def test_validar_param_nao_inventa_limite_para_parametro_sem_limite(self):
        param = Param("engine.oil_pressure", 800, "kPa", origem="simulado", fonte="test")
        self.assertEqual(validar_param(param).status, "unsupported")
