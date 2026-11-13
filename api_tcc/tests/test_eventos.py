import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from django.test import TestCase

from api_tcc.models import Event, LeituraTelemetria
from api_tcc.services.eventos import (
    _persistir_evento_com_priority,
    calcular_priority_score,
    evidence_quality,
)
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
        self.assertEqual(event.evidence_quality, "boa")
        self.assertFalse(event.needs_verification)
        self.assertIsNotNone(event.priority_score)
        self.assertGreaterEqual(float(event.priority_score), 0.0)
        self.assertLessEqual(float(event.priority_score), 1.0)
        self.assertEqual(event.dados_contexto["temperatura"], 86.0)

    def test_leitura_120c_com_trust_baixo_cria_evento_critico_para_verificacao(self):
        _, leitura_id = registrar_leitura(_payload(temperatura=120.0))
        leitura = LeituraTelemetria.objects.get(id=leitura_id)
        leitura.trust_score = 0.2
        leitura.save(update_fields=["trust_score"])
        event = _persistir_evento_com_priority(
            machine=leitura.machine,
            leitura_origem=leitura,
            tipo=Event.Tipo.TEMP_ALTA,
            severidade=Event.Severidade.CRITICO,
            dados_contexto={"temperatura": 120.0},
        )
        self.assertEqual(event.severidade, Event.Severidade.CRITICO)
        self.assertEqual(float(event.priority_score), 1.0)
        self.assertEqual(event.evidence_quality, "insuficiente")
        self.assertTrue(event.needs_verification)

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

    def test_confianca_diferente_nao_altera_score(self):
        evento_boa = self._event(confidence=0.95)
        evento_insuficiente = self._event(confidence=0.2)
        alto = calcular_priority_score(evento_boa, [])
        baixo = calcular_priority_score(evento_insuficiente, [])
        self.assertEqual(alto, baixo)
        self.assertEqual(evidence_quality(evento_boa.trust_score_herdado), "boa")
        self.assertEqual(evidence_quality(evento_insuficiente.trust_score_herdado), "insuficiente")
        self.assertFalse(evidence_quality(evento_boa.trust_score_herdado) != "boa")
        self.assertTrue(evidence_quality(evento_insuficiente.trust_score_herdado) != "boa")

    def test_confianca_zero_nao_zera_formula(self):
        self.assertEqual(calcular_priority_score(self._event(confidence=0.0), []), 1.0)

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
        self.assertEqual(calcular_priority_score(event, []), 0.25)

    def test_confianca_ausente_nao_altera_score(self):
        event = self._event(confidence=None)
        event.trust_score_herdado = None
        event.leitura_origem.trust_score = None
        self.assertEqual(calcular_priority_score(event, []), 1.0)

    def test_evidence_quality_limites_e_entradas_invalidas(self):
        for value, expected in ((0.95, "boa"), (0.8, "boa"), (0.79, "suspeita"),
                                (0.5, "suspeita"), (0.49, "insuficiente"),
                                (0.2, "insuficiente"), (None, "insuficiente"),
                                (float("nan"), "insuficiente"), (float("inf"), "insuficiente"),
                                (-0.1, "insuficiente"), (1.1, "insuficiente"),
                                (10 ** 10000, "insuficiente"), ("inválido", "insuficiente")):
            with self.subTest(value=value):
                self.assertEqual(evidence_quality(value), expected)

    def test_evento_de_120c_preserva_severidade_e_prioridade_com_evidencia_insuficiente(self):
        event = self._event(confidence=0.2)
        event.leitura_origem.temperatura = 120.0
        score = calcular_priority_score(event, [])
        self.assertEqual(event.severidade, Event.Severidade.CRITICO)
        self.assertEqual(score, 1.0)
        self.assertEqual(evidence_quality(event.trust_score_herdado), "insuficiente")
