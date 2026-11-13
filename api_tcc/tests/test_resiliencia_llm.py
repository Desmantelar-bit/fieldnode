"""Testes de resiliência da camada de explicação generativa.

Nenhum teste deste módulo acessa o Gemini: as falhas são simuladas localmente.
"""
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

import requests
from django.test import TestCase, override_settings
from django.core.cache import cache
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from api_tcc.ia import explicacao_llm
from api_tcc.ia.pipeline import ResultadoAnalise
from api_tcc.models import Machine, Membership, Organization


class _RespostaLentaHandler(BaseHTTPRequestHandler):
    """Endpoint local que demora mais que o read timeout da aplicação."""

    def do_POST(self):
        time.sleep(5)
        try:
            self.send_response(200)
            self.end_headers()
        except BrokenPipeError:
            # O cliente já saiu por timeout, que é exatamente o comportamento esperado.
            pass

    def log_message(self, _format, *_args):
        pass


@override_settings(GEMINI_API_KEY="test-gemini-key")
class ResilienciaLLMTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="llm-teste")
        self.organization = Organization.objects.create(nome="Tenant LLM")
        Membership.objects.create(
            user=self.user,
            organization=self.organization,
            role="admin",
        )
        Machine.objects.create(
            external_code="MAQUINA-TESTE-01",
            organization=self.organization,
        )
        # O breaker é global em memória; cada cenário deve começar isolado.
        explicacao_llm._falhas_consecutivas = 0
        explicacao_llm._ultima_falha_ts = 0
        explicacao_llm._tentativa_half_open = False
        cache.clear()
        self.resultado_teste = ResultadoAnalise(
            maquina_id="maquina-teste-01",
            status="CRITICO",
            motivos=["temperatura acima de 85°C"],
            metricas={"temp_max": 90.0},
            recomendacao="Inspeção imediata recomendada.",
        )

    @patch("api_tcc.ia.explicacao_llm.requests.post")
    def test_queda_de_rede_faz_fallback_rapido(self, mock_post):
        """Queda/timeout nunca propaga exceção nem bloqueia o chamador."""
        mock_post.side_effect = requests.exceptions.Timeout("Conexão expirou")

        inicio = time.monotonic()
        resposta = explicacao_llm.gerar_explicacao_natural(self.resultado_teste)
        duracao = time.monotonic() - inicio

        self.assertEqual(resposta["fonte"], "fallback_determinístico")
        self.assertIn("Inspeção imediata", resposta["texto"])
        self.assertLess(duracao, 2.5)
        self.assertEqual(mock_post.call_args.kwargs["timeout"], 2.0)

    @patch("api_tcc.ia.explicacao_llm.requests.post")
    def test_rate_limit_abre_circuit_breaker_apos_tres_falhas(self, mock_post):
        """Depois de três 429, a quarta chamada não tenta a API pelos 120 s seguintes."""
        mock_post.side_effect = requests.exceptions.HTTPError("429 Too Many Requests")

        for _ in range(explicacao_llm.LIMITE_FALHAS):
            resposta = explicacao_llm.gerar_explicacao_natural(self.resultado_teste)
            self.assertEqual(resposta["fonte"], "fallback_determinístico")

        chamadas_antes = mock_post.call_count
        resposta = explicacao_llm.gerar_explicacao_natural(self.resultado_teste)

        self.assertEqual(resposta["fonte"], "fallback_determinístico")
        self.assertEqual(mock_post.call_count, chamadas_antes)
        self.assertTrue(explicacao_llm._circuito_aberto())
        self.assertEqual(explicacao_llm.JANELA_DEGRADADA_SEGUNDOS, 120)

    @patch("api_tcc.ia.explicacao_llm.requests.post")
    def test_half_open_permite_uma_tentativa_e_fecha_apos_sucesso(self, mock_post):
        mock_response = type("Response", (), {
            "raise_for_status": lambda self: None,
            "json": lambda self: {"candidates": [{"content": {"parts": [{"text": "Recuperado."}]}}]},
        })()
        mock_post.return_value = mock_response
        explicacao_llm._falhas_consecutivas = explicacao_llm.LIMITE_FALHAS
        explicacao_llm._ultima_falha_ts = time.time() - explicacao_llm.JANELA_DEGRADADA_SEGUNDOS - 1

        resposta = explicacao_llm.gerar_explicacao_natural(self.resultado_teste)

        self.assertEqual(resposta["fonte"], "ia_generativa")
        mock_post.assert_called_once()
        self.assertEqual(explicacao_llm._falhas_consecutivas, 0)
        self.assertFalse(explicacao_llm._tentativa_half_open)

    def test_resposta_lenta_e_interrompida_pelo_timeout(self):
        """Um servidor local que responde em 5 s é abandonado pelo timeout de 2 s."""
        servidor = ThreadingHTTPServer(("127.0.0.1", 0), _RespostaLentaHandler)
        servidor.daemon_threads = True
        thread = threading.Thread(target=servidor.serve_forever, daemon=True)
        thread.start()
        url_local = f"http://127.0.0.1:{servidor.server_port}/gemini"

        try:
            with patch.object(explicacao_llm, "GEMINI_URL", url_local):
                inicio = time.monotonic()
                resposta = explicacao_llm.gerar_explicacao_natural(self.resultado_teste)
                duracao = time.monotonic() - inicio
        finally:
            servidor.shutdown()
            servidor.server_close()
            thread.join(timeout=1)

        self.assertEqual(resposta["fonte"], "fallback_determinístico")
        self.assertIn("Inspeção imediata", resposta["texto"])
        self.assertGreaterEqual(duracao, 1.5)
        self.assertLess(duracao, 2.5)

    @patch("api_tcc.ia.explicacao_llm.requests.post")
    def test_status_normal_nao_consulta_ia_e_retorna_deterministico(self, mock_post):
        """Uma máquina normal não consome cota de IA nem exibe erro."""
        resultado_normal = ResultadoAnalise(
            maquina_id="maquina-ok",
            status="NORMAL",
            motivos=[],
            metricas={"temp_max": 65.0},
            recomendacao=None,
        )

        resposta = explicacao_llm.gerar_explicacao_natural(resultado_normal)

        self.assertEqual(resposta["fonte"], "determinístico")
        self.assertIn("parâmetros esperados", resposta["texto"])
        mock_post.assert_not_called()

    @patch("api_tcc.ia.explicacao_llm.requests.post")
    def test_chave_em_header_url_limpa_e_cache_por_decision(self, mock_post):
        mock_response = type("Response", (), {
            "raise_for_status": lambda self: None,
            "json": lambda self: {"candidates": [{"content": {"parts": [{"text": "Explicação segura."}]}}]},
        })()
        mock_post.return_value = mock_response

        first = explicacao_llm.gerar_explicacao_natural(self.resultado_teste, decision_id="decision-1")
        second = explicacao_llm.gerar_explicacao_natural(self.resultado_teste, decision_id="decision-1")
        other = explicacao_llm.gerar_explicacao_natural(self.resultado_teste, decision_id="decision-2")

        self.assertEqual(first, second)
        self.assertEqual(other["texto"], "Explicação segura.")
        self.assertEqual(mock_post.call_count, 2)
        self.assertNotIn("key=", mock_post.call_args.args[0])
        self.assertEqual(mock_post.call_args.kwargs["headers"]["x-goog-api-key"], "test-gemini-key")
        self.assertEqual(mock_post.call_args.kwargs["timeout"], 2.0)

    def test_filtro_redige_msg_args_e_excecao(self):
        import logging
        from api_tcc.middleware import RedactSecretsFilter

        record = logging.LogRecord(
            "test", logging.ERROR, __file__, 1,
            "request %s", ("https://host/path?key=gemini-secret-test",),
            (RuntimeError("x-goog-api-key: gemini-secret-test"), None, None),
        )
        RedactSecretsFilter().filter(record)
        rendered = record.getMessage() + " " + str(record.exc_text)
        self.assertNotIn("gemini-secret-test", rendered)
        self.assertIn("[REDACTED]", rendered)

    @patch("api_tcc.api.views_prescricao.gerar_explicacao_natural")
    @patch("api_tcc.api.views_prescricao.analisar_maquina")
    def test_endpoint_entrega_fallback_util_para_interface(
        self, mock_analisar_maquina, mock_gerar_explicacao
    ):
        """O contrato HTTP da tela continua 200 quando a IA entra em fallback."""
        mock_analisar_maquina.return_value = self.resultado_teste
        mock_gerar_explicacao.return_value = {
            "texto": self.resultado_teste.recomendacao,
            "fonte": "fallback_determinístico",
        }

        client = APIClient()
        client.force_authenticate(user=self.user)
        resposta = client.get("/api/prescricoes/maquina-teste-01/")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data["fonte_explicacao"], "fallback_determinístico")
        self.assertEqual(resposta.data["explicacao_operador"], "Inspeção imediata recomendada.")
        self.assertEqual(resposta.data["recomendacao_tecnica"], "Inspeção imediata recomendada.")
