from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from api_tcc.models import CanonicalTelemetry, Machine, RawTelemetry


class MachineCapabilitiesViewTest(TestCase):
    def setUp(self):
        self.machine = Machine.objects.create(external_code="CAP-01")

    def _canonical(self, parameter, value, received_at, quality="mapped"):
        raw = RawTelemetry.objects.create(
            machine=self.machine,
            manufacturer="j1939_bancada_v1",
            raw_parameter=parameter,
            raw_value=value,
            unit="C" if parameter.endswith("temp") else "rpm",
            source_protocol_simulado="j1939_publico_bancada",
            payload_original={parameter: value},
        )
        RawTelemetry.objects.filter(pk=raw.pk).update(recebido_em=received_at)
        canonical = CanonicalTelemetry.objects.create(
            raw_telemetry=raw,
            canonical_parameter=parameter,
            value=value,
            unit=raw.unit,
            quality=quality,
            mapping_version="j1939_v1",
            origem="simulado",
            fonte="j1939_publico_bancada",
            unidade_original=raw.unit,
        )
        CanonicalTelemetry.objects.filter(pk=canonical.pk).update(criado_em=received_at)

    def test_lista_apenas_o_que_foi_observado(self):
        now = timezone.now()
        self._canonical("engine.coolant_temp", 80, now - timedelta(hours=1))
        self._canonical("engine.coolant_temp", 82, now)

        response = self.client.get(f"/api/machines/{self.machine.external_code}/capabilities/")

        self.assertEqual(response.status_code, 401)

    def test_maquina_sem_parametro_nao_recebe_zero(self):
        matrix = self.machine.capabilities(detailed=True)
        self.assertEqual(matrix, [])

    def test_matriz_agrega_fonte_ultima_leitura_e_taxa(self):
        now = timezone.now()
        self._canonical("engine.coolant_temp", 80, now - timedelta(hours=1))
        self._canonical("engine.coolant_temp", 82, now)

        item = self.machine.capabilities(detailed=True)[0]
        self.assertEqual(item["canonical_parameter"], "engine.coolant_temp")
        self.assertEqual(item["fonte"]["protocol"], "j1939_publico_bancada")
        self.assertEqual(item["amostras"], 2)
        self.assertEqual(item["taxa_media_por_hora"], 2.0)
