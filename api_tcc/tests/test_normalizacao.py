from django.test import TestCase

from api_tcc.models import (
    CanonicalTelemetry,
    FabricanteMapping,
    Machine,
    RawTelemetry,
)
from api_tcc.services.normalizacao import normalizar
from api_tcc.services.telemetria import registrar_leitura


class UniversalTelemetryModelTest(TestCase):
    def setUp(self):
        self.machine = Machine.objects.create(external_code="S9-T2-01")

    def test_dois_fabricantes_convergem_para_engine_rpm(self):
        case_raw = RawTelemetry.objects.create(
            machine=self.machine,
            manufacturer="case_ih_v1",
            raw_parameter="SPN_190",
            raw_value=1800,
            unit="rpm",
            source_protocol_simulado="can_simulado",
            payload_original={"SPN_190": 1800},
        )
        john_deere_raw = RawTelemetry.objects.create(
            machine=self.machine,
            manufacturer="john_deere_v1",
            raw_parameter="engine_speed",
            raw_value=1800,
            unit="rpm",
            source_protocol_simulado="j1939_simulado",
            payload_original={"engine_speed": 1800},
        )

        case_canonical = normalizar(case_raw)
        john_deere_canonical = normalizar(john_deere_raw)

        self.assertEqual(case_canonical.canonical_parameter, "engine.rpm")
        self.assertEqual(john_deere_canonical.canonical_parameter, "engine.rpm")
        self.assertEqual(case_canonical.value, john_deere_canonical.value)
        self.assertEqual(case_canonical.mapping_version, "v0.1")

    def test_parametro_sem_mapeamento_fica_persistido_como_unsupported(self):
        raw = RawTelemetry.objects.create(
            machine=self.machine,
            manufacturer="case_ih_v1",
            raw_parameter="proprietary_unknown_signal",
            raw_value=7,
            unit="",
            source_protocol_simulado="can_simulado",
            payload_original={"proprietary_unknown_signal": 7},
        )

        canonical = normalizar(raw)

        self.assertIsNone(canonical)
        raw.refresh_from_db()
        self.assertEqual(raw.quality, "unsupported_parameter")
        self.assertFalse(
            CanonicalTelemetry.objects.filter(raw_telemetry=raw).exists()
        )

    def test_capabilities_lista_mapeamentos_ativos_do_fabricante(self):
        self.assertEqual(self.machine.capabilities("case_ih_v1"), ["engine.rpm"])

    def test_mapping_inativo_nao_normaliza(self):
        mapping = FabricanteMapping.objects.get(
            manufacturer="case_ih_v1", raw_parameter="SPN_190"
        )
        mapping.ativo = False
        mapping.save(update_fields=["ativo"])
        raw = RawTelemetry.objects.create(
            machine=self.machine,
            manufacturer="case_ih_v1",
            raw_parameter="SPN_190",
            raw_value=1800,
            unit="rpm",
            source_protocol_simulado="can_simulado",
            payload_original={"SPN_190": 1800},
        )

        self.assertIsNone(normalizar(raw))

    def test_ingestao_legada_grava_raw_antes_da_normalizacao(self):
        status, _ = registrar_leitura(
            {
                "id": "00000000-0000-4000-8000-000000000901",
                "maquina_id": "S9-T2-INGEST",
                "manufacturer": "fieldnode_simulator_v1",
                "temperatura": 80.0,
                "vibracao": 0.5,
                "rpm": 1800,
                "timestamp": "2026-10-09T10:00:00Z",
            }
        )

        self.assertEqual(status, "criado")
        self.assertEqual(RawTelemetry.objects.count(), 3)
        self.assertEqual(CanonicalTelemetry.objects.count(), 3)
        self.assertEqual(
            set(CanonicalTelemetry.objects.values_list("canonical_parameter", flat=True)),
            {"engine.temperature", "engine.vibration", "engine.rpm"},
        )
