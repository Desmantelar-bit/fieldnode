import json
from datetime import timedelta
from uuid import uuid4

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from api_tcc.models import Event, LeituraTelemetria, Machine, Membership, Organization
from api_tcc.services.agentic import AgenticOutputError, validar_explicacao
from api_tcc.services.assistant_tools import execute_tool


class ExplanationGuardrailTest(TestCase):
    def setUp(self):
        now = timezone.now()
        self.context = {
            "schema": "decision.v1", "observado": "temperatura", "evidencias": [{"leitura_id": "reading-1", "campo": "temperatura", "valor": 91.2, "limiar": 85, "event_time": now.isoformat()}],
            "janela_analisada": {"inicio": (now - timedelta(minutes=1)).isoformat(), "fim": now.isoformat(), "n_leituras": 1},
            "qualidade_dado": {"evidence_quality": "boa", "fatores": []}, "regra": {"id": "R1", "versao": "1"},
            "modelo": {"id": "M1", "score": None, "contribuinte": None}, "dados_faltantes": [], "horizonte_minutos": None, "alternativas": [],
        }

    def test_numero_inventado_e_rejeitado(self):
        with self.assertRaises(AgenticOutputError):
            validar_explicacao(json.dumps({"texto": "Temperatura 92 C", "evidencias_citadas": ["reading-1"]}), self.context)

    def test_id_inexistente_e_rejeitado(self):
        with self.assertRaises(AgenticOutputError):
            validar_explicacao(json.dumps({"texto": "Há evidência registrada.", "evidencias_citadas": ["other"]}), self.context)

    def test_resposta_valida(self):
        resposta = validar_explicacao(json.dumps({"texto": "Temperatura 91,2 registrada.", "evidencias_citadas": ["reading-1"]}), self.context)
        self.assertEqual(resposta["evidencias_citadas"], ["reading-1"])


class AssistantIsolationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("operator", password="x")
        org_a = Organization.objects.create(nome="A")
        org_b = Organization.objects.create(nome="B")
        Membership.objects.create(user=self.user, organization=org_a, role="viewer")
        self.machine_a = Machine.objects.create(external_code="A-1", organization=org_a)
        self.machine_b = Machine.objects.create(external_code="B-1", organization=org_b)

    def test_machine_de_outra_organizacao_e_oculta(self):
        resposta = execute_tool(self.user, "saude_da_maquina", {"id": str(self.machine_b.id)})
        self.assertEqual(resposta["mensagem"], "Não encontrada.")

    def test_tool_fora_da_allowlist_e_rejeitada(self):
        with self.assertRaises(ValueError):
            execute_tool(self.user, "aprovar_decisao", {"id": str(uuid4())})
