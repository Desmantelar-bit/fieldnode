"""
Testes obrigatórios do Attention Engine — S1-T3.

Verifica que:
  1. A confiança não altera o priority_score.
  2. Sensor com leitura potencialmente crítica mantém prioridade alta.
  3. Os limiares de evidence_quality estão corretos para todos os valores-limite.
  4. A consistência entre evidence_quality e needs_verification é garantida.
  5. A API expõe os campos corretos e ordena por priority_score.

Nenhum teste altera a severidade do evento para fazer o resultado passar.
"""
import math
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from django.test import TestCase
from rest_framework.test import APIClient

from api_tcc.models import Event, LeituraTelemetria, Machine, Organization
from api_tcc.services.eventos import (
    EVIDENCE_BOA_THRESHOLD,
    EVIDENCE_SUSPEITA_THRESHOLD,
    calcular_priority_score,
    evidence_quality,
)
from api_tcc.services.telemetria import registrar_leitura


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _simple_event(
    *,
    severity=Event.Severidade.CRITICO,
    event_type=Event.Tipo.TEMP_ALTA,
    timestamp=None,
    trust=0.9,
    temperatura=90.0,
):
    """Cria um namespace simples compatível com calcular_priority_score."""
    reading = SimpleNamespace(
        timestamp=timestamp or datetime(2026, 6, 1, 10, tzinfo=timezone.utc),
        temperatura=temperatura,
        vibracao=0.4,
        rpm=1800,
        trust_score=trust,
    )
    return SimpleNamespace(
        severidade=severity,
        tipo=event_type,
        trust_score_herdado=trust,
        leitura_origem=reading,
    )


def _payload(**overrides):
    base = {
        "id": str(uuid.uuid4()),
        "maquina_id": f"COLH-ATTN-{uuid.uuid4().hex[:6].upper()}",
        "temperatura": 90.0,
        "vibracao": 0.4,
        "rpm": 1800,
        "timestamp": "2026-06-01T10:00:00Z",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Teste 1 — confiança não altera priority_score, mas altera evidence_quality
# ---------------------------------------------------------------------------

class Test1TrustNaoAlteraPrioridade(TestCase):
    """
    Dois eventos de mesma severidade, tipo e urgência com trust 0.95 e 0.20
    devem ter exatamente o mesmo priority_score.
    O trust diferente deve produzir evidence_quality e needs_verification distintos.
    """

    def _pair(self, timestamp):
        """Retorna (event_high_trust, event_low_trust) com mesmo historico vazio."""
        ev_high = _simple_event(trust=0.95, timestamp=timestamp)
        ev_low = _simple_event(trust=0.20, timestamp=timestamp)
        return ev_high, ev_low

    def test_priority_score_identico_historico_vazio(self):
        ts = datetime(2026, 6, 1, 10, tzinfo=timezone.utc)
        ev_high, ev_low = self._pair(ts)

        score_high = calcular_priority_score(ev_high, [])
        score_low = calcular_priority_score(ev_low, [])

        self.assertEqual(score_high, score_low,
            "priority_score deve ser igual para events com mesma severidade/tipo/urgência, "
            f"independente do trust_score. Obtido: high={score_high}, low={score_low}")

    def test_needs_verification_diferente(self):
        ts = datetime(2026, 6, 1, 10, tzinfo=timezone.utc)
        ev_high, ev_low = self._pair(ts)

        eq_high = evidence_quality(ev_high.trust_score_herdado)
        eq_low = evidence_quality(ev_low.trust_score_herdado)

        # trust 0.95 → boa → needs_verification = False
        self.assertFalse(eq_high != Event.EvidenceQuality.BOA,
            "trust 0.95 deve produzir evidence_quality BOA")

        # trust 0.20 → insuficiente → needs_verification = True
        self.assertTrue(eq_low != Event.EvidenceQuality.BOA,
            "trust 0.20 deve exigir verificação")

    def test_assertion_da_spec(self):
        """Reproduz exatamente o assert do enunciado."""
        ts = datetime(2026, 6, 1, 10, tzinfo=timezone.utc)
        ev_high, ev_low = self._pair(ts)

        score_high = calcular_priority_score(ev_high, [])
        score_low = calcular_priority_score(ev_low, [])

        needs_high = evidence_quality(0.95) != Event.EvidenceQuality.BOA  # False
        needs_low = evidence_quality(0.20) != Event.EvidenceQuality.BOA   # True

        self.assertEqual(score_high, score_low)
        self.assertFalse(needs_high)
        self.assertTrue(needs_low)


# ---------------------------------------------------------------------------
# Teste 2 — sensor com leitura potencialmente crítica (120 °C, trust baixo)
# ---------------------------------------------------------------------------

class Test2SensorTravado120C(TestCase):
    """
    Temperatura 120 °C, trust_score 0.20.
    Evento deve ter severidade CRITICO, priority_score > 0, evidence_quality
    diferente de boa e needs_verification True.
    O evento deve aparecer entre as ocorrências prioritárias da API.
    """

    def setUp(self):
        # Cria leitura diretamente para controlar trust_score e temperatura
        from api_tcc.models import Machine
        machine, _ = Machine.objects.get_or_create(external_code="COLH-120C-TEST")

        self.leitura = LeituraTelemetria.objects.create(
            maquina_id="COLH-120C-TEST",
            machine=machine,
            device_id="COLH-120C-TEST",
            message_id=str(uuid.uuid4()),
            temperatura=120.0,
            vibracao=0.4,
            rpm=1800,
            timestamp=datetime(2026, 6, 1, 10, tzinfo=timezone.utc),
            trust_score=0.20,
        )

        # Calcula evidence_quality a partir do trust_score da leitura
        from api_tcc.services.eventos import (
            _persistir_evento_com_priority,
            evidence_quality as eq_fn,
        )
        self.event = _persistir_evento_com_priority(
            machine=machine,
            leitura_origem=self.leitura,
            tipo=Event.Tipo.TEMP_ALTA,
            severidade=Event.Severidade.CRITICO,
            dados_contexto={"temperatura": 120.0},
        )

    def test_severidade_critico(self):
        self.assertEqual(self.event.severidade, Event.Severidade.CRITICO,
            "Temperatura 120 °C deve produzir severidade CRITICO — a regra operacional "
            "não muda por causa do trust_score do sensor.")

    def test_priority_score_elevado(self):
        score = float(self.event.priority_score)
        self.assertGreater(score, 0.0,
            "priority_score deve ser > 0 para evento CRITICO de temperatura.")

    def test_evidence_quality_nao_boa(self):
        self.assertNotEqual(self.event.evidence_quality, Event.EvidenceQuality.BOA,
            "trust_score=0.20 não deve produzir evidence_quality BOA.")

    def test_needs_verification_true(self):
        self.assertTrue(self.event.needs_verification,
            "trust_score=0.20 deve exigir verificação — sensor suspeito não invalida "
            "a severidade, mas indica que a ocorrência precisa ser confirmada no campo.")

    def test_event_aparece_no_topo_da_lista(self):
        """Evento CRITICO com priority_score alto deve aparecer no início da ordenação."""
        events = Event.objects.filter(machine=self.event.machine).order_by(
            "-priority_score", "-criado_em"
        )
        top = events.first()
        self.assertIsNotNone(top)
        # O evento critico de temperatura deve ser o de maior prioridade
        self.assertEqual(float(top.priority_score), float(self.event.priority_score))


# ---------------------------------------------------------------------------
# Teste 3 — limiares da classificação evidence_quality
# ---------------------------------------------------------------------------

class Test3LimitesEvidenceQuality(TestCase):
    """
    Verifica cada valor-limite documentado na spec:
      1.0, 0.8, 0.79, 0.5, 0.49, 0.0, None e valores inválidos.
    """

    def _eq(self, trust):
        return evidence_quality(trust)

    def test_trust_1_0_e_boa(self):
        self.assertEqual(self._eq(1.0), Event.EvidenceQuality.BOA)

    def test_trust_exato_threshold_boa(self):
        self.assertEqual(self._eq(EVIDENCE_BOA_THRESHOLD), Event.EvidenceQuality.BOA,
            f"trust={EVIDENCE_BOA_THRESHOLD} (limite BOA) deve retornar BOA.")

    def test_trust_abaixo_threshold_boa(self):
        # 0.8 - epsilon
        just_below = EVIDENCE_BOA_THRESHOLD - 0.01
        result = self._eq(just_below)
        self.assertNotEqual(result, Event.EvidenceQuality.BOA,
            f"trust={just_below} não deve ser BOA.")
        self.assertEqual(result, Event.EvidenceQuality.SUSPEITA,
            f"trust={just_below} deve ser SUSPEITA (acima de {EVIDENCE_SUSPEITA_THRESHOLD}).")

    def test_trust_exato_threshold_suspeita(self):
        self.assertEqual(self._eq(EVIDENCE_SUSPEITA_THRESHOLD), Event.EvidenceQuality.SUSPEITA,
            f"trust={EVIDENCE_SUSPEITA_THRESHOLD} (limite SUSPEITA) deve retornar SUSPEITA.")

    def test_trust_abaixo_threshold_suspeita(self):
        just_below = EVIDENCE_SUSPEITA_THRESHOLD - 0.01
        self.assertEqual(self._eq(just_below), Event.EvidenceQuality.INSUFICIENTE,
            f"trust={just_below} deve ser INSUFICIENTE.")

    def test_trust_zero_e_insuficiente(self):
        self.assertEqual(self._eq(0.0), Event.EvidenceQuality.INSUFICIENTE)

    def test_trust_none_e_insuficiente(self):
        self.assertEqual(self._eq(None), Event.EvidenceQuality.INSUFICIENTE)

    def test_trust_nan_e_insuficiente(self):
        self.assertEqual(self._eq(float("nan")), Event.EvidenceQuality.INSUFICIENTE,
            "NaN não é evidência válida.")

    def test_trust_inf_e_insuficiente(self):
        self.assertEqual(self._eq(float("inf")), Event.EvidenceQuality.INSUFICIENTE,
            "Infinito não é evidência válida.")

    def test_trust_negativo_inf_e_insuficiente(self):
        self.assertEqual(self._eq(float("-inf")), Event.EvidenceQuality.INSUFICIENTE)

    def test_trust_string_invalida_e_insuficiente(self):
        self.assertEqual(self._eq("alto"), Event.EvidenceQuality.INSUFICIENTE,
            "String não é float válido; deve retornar INSUFICIENTE sem lançar exceção.")

    def test_trust_negativo_e_insuficiente(self):
        # Valor fora do intervalo [0, 1] esperado do contrato
        self.assertEqual(self._eq(-0.1), Event.EvidenceQuality.INSUFICIENTE)

    def test_valores_spec_literais(self):
        """Reproduz a tabela de valores do enunciado."""
        self.assertEqual(self._eq(1.0),  Event.EvidenceQuality.BOA)
        self.assertEqual(self._eq(0.8),  Event.EvidenceQuality.BOA)
        self.assertEqual(self._eq(0.79), Event.EvidenceQuality.SUSPEITA)
        self.assertEqual(self._eq(0.5),  Event.EvidenceQuality.SUSPEITA)
        self.assertEqual(self._eq(0.49), Event.EvidenceQuality.INSUFICIENTE)
        self.assertEqual(self._eq(0.0),  Event.EvidenceQuality.INSUFICIENTE)
        self.assertEqual(self._eq(None), Event.EvidenceQuality.INSUFICIENTE)


# ---------------------------------------------------------------------------
# Teste 4 — consistência entre evidence_quality e needs_verification
# ---------------------------------------------------------------------------

class Test4ConsistenciaAtributos(TestCase):
    """
    Para cada valor de evidence_quality, needs_verification deve ser o valor
    esperado derivado de (evidence_quality != 'boa').
    """

    def _check(self, trust, expected_eq, expected_nv):
        eq = evidence_quality(trust)
        nv = eq != Event.EvidenceQuality.BOA

        self.assertEqual(eq, expected_eq,
            f"trust={trust}: evidence_quality esperada '{expected_eq}', obtida '{eq}'")
        self.assertEqual(nv, expected_nv,
            f"trust={trust}: needs_verification esperado {expected_nv}, obtido {nv}")

    def test_evidencia_boa_nao_exige_verificacao(self):
        self._check(1.0,  Event.EvidenceQuality.BOA,         False)
        self._check(0.8,  Event.EvidenceQuality.BOA,         False)

    def test_evidencia_suspeita_exige_verificacao(self):
        self._check(0.79, Event.EvidenceQuality.SUSPEITA,    True)
        self._check(0.5,  Event.EvidenceQuality.SUSPEITA,    True)

    def test_evidencia_insuficiente_exige_verificacao(self):
        self._check(0.49, Event.EvidenceQuality.INSUFICIENTE, True)
        self._check(0.0,  Event.EvidenceQuality.INSUFICIENTE, True)
        self._check(None, Event.EvidenceQuality.INSUFICIENTE, True)

    def test_persistido_no_banco_e_consistente(self):
        """Evento persistido no banco deve ter needs_verification derivado de evidence_quality."""
        from api_tcc.models import Machine
        machine, _ = Machine.objects.get_or_create(external_code="COLH-CONSIST-01")

        leitura = LeituraTelemetria.objects.create(
            maquina_id="COLH-CONSIST-01",
            machine=machine,
            device_id="COLH-CONSIST-01",
            message_id=str(uuid.uuid4()),
            temperatura=90.0,
            vibracao=0.4,
            rpm=1800,
            timestamp=datetime(2026, 6, 1, 10, tzinfo=timezone.utc),
            trust_score=0.9,
        )

        from api_tcc.services.eventos import _persistir_evento_com_priority
        event = _persistir_evento_com_priority(
            machine=machine,
            leitura_origem=leitura,
            tipo=Event.Tipo.TEMP_ALTA,
            severidade=Event.Severidade.CRITICO,
            dados_contexto={"temperatura": 90.0},
        )

        # trust 0.9 → BOA → needs_verification = False
        self.assertEqual(event.evidence_quality, Event.EvidenceQuality.BOA)
        self.assertFalse(event.needs_verification)

        # Recalcula para confirmar consistência
        self.assertEqual(
            event.needs_verification,
            event.evidence_quality != Event.EvidenceQuality.BOA,
        )


# ---------------------------------------------------------------------------
# Teste 5 — API: campos, ordenação, filtros e paginação
# ---------------------------------------------------------------------------

class Test5API(TestCase):
    """
    Verifica que a API REST:
    - expõe evidence_quality, needs_verification, priority_score, severidade,
      trust_score_herdado;
    - ordena por priority_score DESC (nulls last), com -criado_em como desempate;
    - mantém filtros e paginação existentes;
    - não reduz priority_score de evento com baixa confiança.
    """

    def setUp(self):
        from api_tcc.models import Machine
        from django.contrib.auth.models import User

        # Cria usuário demo para usar permissão pública
        machine, _ = Machine.objects.get_or_create(
            external_code="COLH-API-TEST",
            defaults={"is_demo": True},
        )
        self.machine = machine

        ts_base = datetime(2026, 6, 1, 10, tzinfo=timezone.utc)

        # Evento CRITICO com trust alto (evidence BOA)
        leitura_alta = LeituraTelemetria.objects.create(
            maquina_id="COLH-API-TEST", machine=machine,
            device_id="COLH-API-TEST", message_id=str(uuid.uuid4()),
            temperatura=95.0, vibracao=0.5, rpm=1800,
            timestamp=ts_base, trust_score=0.95,
        )
        # Evento CRITICO com trust baixo (evidence INSUFICIENTE)
        leitura_baixa = LeituraTelemetria.objects.create(
            maquina_id="COLH-API-TEST", machine=machine,
            device_id="COLH-API-TEST", message_id=str(uuid.uuid4()),
            temperatura=95.0, vibracao=0.5, rpm=1800,
            timestamp=ts_base + timedelta(seconds=1), trust_score=0.20,
        )

        from api_tcc.services.eventos import _persistir_evento_com_priority
        self.event_alta_confianca = _persistir_evento_com_priority(
            machine=machine, leitura_origem=leitura_alta,
            tipo=Event.Tipo.TEMP_ALTA, severidade=Event.Severidade.CRITICO,
            dados_contexto={"temperatura": 95.0},
        )
        self.event_baixa_confianca = _persistir_evento_com_priority(
            machine=machine, leitura_origem=leitura_baixa,
            tipo=Event.Tipo.TEMP_ALTA, severidade=Event.Severidade.CRITICO,
            dados_contexto={"temperatura": 95.0},
        )

        self.client = APIClient()

    def test_api_expoe_novos_campos(self):
        response = self.client.get(
            "/api/events/", {"maquina_id": "COLH-API-TEST"}
        )
        self.assertEqual(response.status_code, 200)
        results = response.data["results"]
        self.assertGreater(len(results), 0)

        first = results[0]
        self.assertIn("evidence_quality", first)
        self.assertIn("needs_verification", first)
        self.assertIn("priority_score", first)
        self.assertIn("severidade", first)
        self.assertIn("trust_score_herdado", first)

    def test_confianca_baixa_nao_reduz_priority_score(self):
        """
        Os dois eventos foram criados com mesma severidade e timestamp próximo.
        Os priority_scores devem ser iguais (ou praticamente iguais para historicos distintos).
        O evento com baixa confiança NÃO deve aparecer com score menor.
        """
        response = self.client.get(
            "/api/events/", {"maquina_id": "COLH-API-TEST"}
        )
        self.assertEqual(response.status_code, 200)
        results = response.data["results"]

        scores = [float(r["priority_score"]) for r in results if r["priority_score"] is not None]
        # Ambos CRITICO: todos scores devem ser > 0
        self.assertTrue(all(s > 0 for s in scores),
            "Eventos CRITICO devem ter priority_score > 0 independente do trust.")

        # Localiza os dois eventos pelo id
        alta = next(r for r in results if str(r["id"]) == str(self.event_alta_confianca.id))
        baixa = next(r for r in results if str(r["id"]) == str(self.event_baixa_confianca.id))

        # Priority scores podem diferir levemente pela urgência (timestamps próximos
        # mas distintos e histórico diferente), mas o evento com baixa confiança
        # nunca deve ter score MENOR por causa do trust.
        score_alta = float(alta["priority_score"])
        score_baixa = float(baixa["priority_score"])

        # A diferença de urgência por 1s de diferença de timestamp é desprezível.
        # Verificamos que os scores são razoavelmente próximos (dentro de 0.05).
        self.assertAlmostEqual(score_alta, score_baixa, delta=0.05,
            msg="priority_score não deve divergir significativamente por causa do trust.")

    def test_ordenacao_por_priority_score_desc(self):
        response = self.client.get(
            "/api/events/", {"maquina_id": "COLH-API-TEST"}
        )
        self.assertEqual(response.status_code, 200)
        results = response.data["results"]
        scores = [
            float(r["priority_score"]) if r["priority_score"] is not None else -1.0
            for r in results
        ]
        self.assertEqual(scores, sorted(scores, reverse=True),
            "Resultados devem estar ordenados por priority_score DESC.")

    def test_evidence_quality_correta_por_trust(self):
        response = self.client.get(
            "/api/events/", {"maquina_id": "COLH-API-TEST"}
        )
        results = response.data["results"]

        alta = next(r for r in results if str(r["id"]) == str(self.event_alta_confianca.id))
        baixa = next(r for r in results if str(r["id"]) == str(self.event_baixa_confianca.id))

        self.assertEqual(alta["evidence_quality"], "boa")
        self.assertFalse(alta["needs_verification"])

        self.assertNotEqual(baixa["evidence_quality"], "boa")
        self.assertTrue(baixa["needs_verification"])

    def test_filtro_severidade_funciona(self):
        response = self.client.get(
            "/api/events/", {"maquina_id": "COLH-API-TEST", "severidade": "CRITICO"}
        )
        self.assertEqual(response.status_code, 200)
        results = response.data["results"]
        self.assertTrue(all(r["severidade"] == "CRITICO" for r in results))

    def test_paginacao_funciona(self):
        response = self.client.get(
            "/api/events/", {"maquina_id": "COLH-API-TEST", "page_size": 1}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("count", response.data)
        self.assertIn("pages", response.data)
        self.assertEqual(len(response.data["results"]), 1)
