import uuid

from django.test import TestCase

from api_tcc.models import Event, LeituraTelemetria
from api_tcc.services.telemetria import registrar_leitura


def _payload(**overrides):
    base = {
        "id": str(uuid.uuid4()),
        "maquina_id": "COLH-EVENT-01",
        "temperatura": 86.0,
        "vibracao": 0.35,
        "rpm": 1800,
        "timestamp": "2026-06-01T10:00:00Z",
    }
    base.update(overrides)
    return base


class EventEngineTest(TestCase):
    def test_leitura_com_temperatura_critica_gera_event_temp_alta(self):
        status, leitura_id = registrar_leitura(_payload())

        self.assertEqual(status, "criado")
        self.assertEqual(Event.objects.count(), 1)

        leitura = LeituraTelemetria.objects.get(id=leitura_id)
        event = Event.objects.get()

        self.assertEqual(event.machine, leitura.machine)
        self.assertEqual(event.leitura_origem, leitura)
        self.assertEqual(event.tipo, Event.Tipo.TEMP_ALTA)
        self.assertEqual(event.severidade, Event.Severidade.CRITICO)
        self.assertEqual(event.status, Event.Status.ABERTO)
        self.assertEqual(event.trust_score_herdado, leitura.trust_score)
        self.assertEqual(event.dados_contexto["temperatura"], 86.0)

    def test_nao_duplica_evento_aberto_do_mesmo_tipo_na_janela_de_supressao(self):
        status_1, _ = registrar_leitura(_payload(timestamp="2026-06-01T10:00:00Z"))
        status_2, _ = registrar_leitura(_payload(timestamp="2026-06-01T10:01:00Z"))

        self.assertEqual(status_1, "criado")
        self.assertEqual(status_2, "criado")
        self.assertEqual(Event.objects.count(), 1)
