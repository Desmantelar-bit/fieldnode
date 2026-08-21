"""Testes de resiliência da camada de explicação generativa.

Nenhum teste deste módulo acessa o Gemini: as falhas são simuladas localmente.
"""
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

import requests
from django.test import TestCase
from rest_framework.test import APIClient

from api_tcc.ia import explicacao_llm
from api_tcc.ia.pipeline import ResultadoAnalise


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


class ResilienciaLLMTestCase(TestCase):
    def setUp(self):
        # O breaker é global em memória; cada cenário deve começar isolado.
        explicacao_llm._falhas_consecutivas = 0
        explicacao_llm._ultima_falha_ts = 0
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

        resposta = APIClient().get("/api/prescricoes/maquina-teste-01/")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data["fonte_explicacao"], "fallback_determinístico")
        self.assertEqual(resposta.data["explicacao_operador"], "Inspeção imediata recomendada.")
        self.assertEqual(resposta.data["recomendacao_tecnica"], "Inspeção imediata recomendada.")
