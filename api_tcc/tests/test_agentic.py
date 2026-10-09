from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from rest_framework.test import APIClient

from api_tcc.models import DeadLetterEntry, Decision, Event, Machine


class AgenticDecisionCommandTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.machine = Machine.objects.create(external_code="AGENTIC-DEMO-01")
        self.event = Event.objects.create(
            machine=self.machine,
            tipo=Event.Tipo.TEMP_ALTA,
            severidade=Event.Severidade.CRITICO,
            priority_score=0.93,
            dados_contexto={"temperatura": 91.2},
        )

    @override_settings(DEMO_MODE=True)
    @patch("api_tcc.api.views_prescricao.gerar_explicacao_natural")
    @patch("api_tcc.api.views_prescricao.analisar_maquina")
    def test_decisao_agentiva_pendente_entra_no_fluxo_do_dashboard(self, analisar, explicar):
        self.machine.is_demo = True
        self.machine.save(update_fields=["is_demo"])
        decision = Decision.objects.create(
            machine=self.machine,
            event=self.event,
            texto="Verificar o sistema de arrefecimento.",
            acao_recomendada="Inspecionar o radiador.",
            severidade=Event.Severidade.CRITICO,
            confianca=0.8,
            detalhes={"metodologia": "agentic_llm_poc"},
        )
        analisar.return_value = SimpleNamespace(
            maquina_id=self.machine.external_code,
            metricas={},
            status=Event.Severidade.CRITICO,
            metodologia="hibrido_regras_thresholds_e_isolation_forest",
            motivos=[],
            recomendacao="recomendacao deterministica",
        )

        response = self.client.get("/api/prescricoes/AGENTIC-DEMO-01/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["decision_id"], str(decision.id))
        self.assertEqual(response.data["decision_status"], Decision.Status.PENDENTE)
        self.assertEqual(response.data["metodologia"], "agentic_llm_poc")
        self.assertEqual(response.data["recomendacao"], decision.texto)
        self.assertEqual(response.data["recomendacao_tecnica"], decision.acao_recomendada)
        explicar.assert_not_called()

    def _gemini_response(self, text):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": text}]}}],
        }
        return response

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("api_tcc.services.agentic.requests.post")
    def test_resposta_valida_persiste_decision_pendente_agentiva(self, post):
        post.return_value = self._gemini_response(
            '{"texto":"Investigar o sistema de arrefecimento.",'
            '"acao_recomendada":"Inspecionar radiador antes de intervir.",'
            '"severidade":"CRITICO","confianca":0.82}'
        )

        call_command("gerar_decisao_agentiva")

        decision = Decision.objects.get()
        self.assertEqual(decision.status, Decision.Status.PENDENTE)
        self.assertEqual(decision.machine, self.machine)
        self.assertEqual(decision.event, self.event)
        self.assertEqual(decision.detalhes["metodologia"], "agentic_llm_poc")
        self.assertEqual(decision.detalhes["prompt_version"], "agentic_decision_v1")
        self.assertEqual(decision.confianca, 0.82)
        post.assert_called_once()

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("api_tcc.services.agentic.requests.post")
    def test_resposta_malformada_vai_para_dlq_sem_persistir_decision(self, post):
        post.return_value = self._gemini_response("não é json")

        call_command("gerar_decisao_agentiva")

        self.assertFalse(Decision.objects.exists())
        entrada = DeadLetterEntry.objects.get()
        self.assertEqual(entrada.contexto, DeadLetterEntry.Contexto.AGENTIC_LLM)
        self.assertEqual(entrada.payload_referencia["machine_external_code"], "AGENTIC-DEMO-01")
        self.assertIn("JSON válido", entrada.motivo)
