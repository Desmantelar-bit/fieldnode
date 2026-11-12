import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from django.test import TestCase

from api_tcc.models import Event, LeituraTelemetria
from api_tcc.services.eventos import calcular_priority_score
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
        self.assertIsNotNone(event.priority_score)
        self.assertGreaterEqual(float(event.priority_score), 0.0)
        self.assertLessEqual(float(event.priority_score), 1.0)
        self.assertEqual(event.dados_contexto["temperatura"], 86.0)

    def test_nao_duplica_evento_aberto_do_mesmo_tipo_na_janela_de_supressao(self):
        status_1, _ = registrar_leitura(_payload(timestamp="2026-06-01T10:00:00Z"))
        status_2, _ = registrar_leitura(_payload(timestamp="2026-06-01T10:01:00Z"))

        self.assertEqual(status_1, "criado")
        self.assertEqual(status_2, "criado")
        self.assertEqual(Event.objects.count(), 1)


class PriorityScoreTest(TestCase):
    def _event(self, *, severity=Event.Severidade.CRITICO, confidence=0.8,
               event_type=Event.Tipo.TEMP_ALTA, timestamp=None):
        reading = SimpleNamespace(
            timestamp=timestamp or datetime(2026, 6, 1, 10, tzinfo=timezone.utc),
            temperatura=90.0,
            vibracao=0.4,
            rpm=1800,
            trust_score=confidence,
        )
        return SimpleNamespace(
            severidade=severity,
            tipo=event_type,
            trust_score_herdado=confidence,
            leitura_origem=reading,
        )

    def test_severidades_produzem_score_no_intervalo(self):
        for severity in Event.Severidade.values:
            score = calcular_priority_score(self._event(severity=severity), [])
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

    def test_confianca_diferente_altera_score(self):
        alto = calcular_priority_score(self._event(confidence=0.9), [])
        baixo = calcular_priority_score(self._event(confidence=0.3), [])
        self.assertGreater(alto, baixo)

    def test_confianca_zero_zera_formula(self):
        self.assertEqual(calcular_priority_score(self._event(confidence=0.0), []), 0.0)

    def test_urgencia_zero_zera_formula(self):
        event = self._event()
        antigo = SimpleNamespace(
            timestamp=event.leitura_origem.timestamp - timedelta(hours=24),
            temperatura=90.0,
            vibracao=0.4,
            rpm=1800,
        )
        self.assertEqual(calcular_priority_score(event, [antigo]), 0.0)

    def test_agravamento_preserva_urgencia_acima_do_simples_envelhecimento(self):
        event = self._event()
        antigo = SimpleNamespace(
            timestamp=event.leitura_origem.timestamp - timedelta(hours=24),
            temperatura=85.0,
            vibracao=0.4,
            rpm=1800,
        )
        event.leitura_origem.temperatura = 90.0
        piorando = calcular_priority_score(event, [antigo])
        event.leitura_origem.temperatura = 85.0
        sem_piora = calcular_priority_score(event, [antigo])
        self.assertGreater(piorando, sem_piora)

    def test_tipo_desconhecido_usa_impacto_conservador(self):
        event = self._event(event_type="TIPO_NOVO")
        self.assertEqual(calcular_priority_score(event, []), 0.25 * 0.8)

    def test_confianca_ausente_nao_produz_score_otimista(self):
        event = self._event(confidence=None)
        event.trust_score_herdado = None
        event.leitura_origem.trust_score = None
        self.assertEqual(calcular_priority_score(event, []), 0.0)
