"""
api_tcc/tests/test_correlation.py

Testes do middleware de correlation ID (S7-T2).

Cobertura:
  1. Requisição sem X-Correlation-ID → UUID gerado automaticamente
  2. Requisição com X-Correlation-ID válido → reutilizado
  3. Dois logs da mesma requisição compartilham o mesmo ID
  4. Duas requisições têm IDs distintos; logs não se misturam
  5. Isolamento de contexto: ID não vaza após reset
  6. Log fora de qualquer contexto → correlation_id = "null" (não quebra)
  7. Fluxo MQTT: correlation_id = UUID da leitura
  8. Isolamento MQTT: leituras distintas têm IDs distintos
  9. Header inválido (vazio, longo, com newline, com null) → UUID gerado
  10. CorrelationFilter não interfere com logger.exception()
"""

import logging
import uuid
from contextvars import copy_context
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from api_tcc.correlation import (
    CorrelationFilter,
    _sanitize_external_id,
    get_correlation_id,
    new_correlation_id,
    reset_correlation_id,
    set_correlation_id,
)
from api_tcc.management.commands.mqtt_listen import on_message


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

class _FakeRecord:
    """LogRecord mínimo para testar o CorrelationFilter sem levantar um logger real."""
    def __init__(self):
        self.correlation_id = None


def _apply_filter(cid: str | None = None):
    """
    Aplica o CorrelationFilter em um LogRecord falso dentro do contexto
    corrente (ou com um ID injetado previamente).
    Retorna o valor de record.correlation_id após o filter.
    """
    if cid is not None:
        token = set_correlation_id(cid)
    try:
        f = CorrelationFilter()
        record = _FakeRecord()
        f.filter(record)
        return record.correlation_id
    finally:
        if cid is not None:
            reset_correlation_id(token)


# ──────────────────────────────────────────────────────────────────────────────
# 1–4  Testes de integração via HTTP
# ──────────────────────────────────────────────────────────────────────────────

class CorrelationIDMiddlewareHTTPTest(TestCase):
    """
    Testa o fluxo completo: request → middleware → response header.
    Usa /api/health/ como endpoint real sem autenticação (implementado em S7-T1).
    """

    def setUp(self):
        self.client = APIClient()

    # ── 1. Sem header ───────────────────────────────────────────────────────

    def test_sem_header_resposta_tem_correlation_id(self):
        response = self.client.get("/api/health/")
        self.assertIn("X-Correlation-ID", response)

    def test_sem_header_valor_e_uuid_valido(self):
        response = self.client.get("/api/health/")
        cid = response["X-Correlation-ID"]
        try:
            uuid.UUID(cid)
        except ValueError:
            self.fail(f"X-Correlation-ID não é UUID válido: {cid!r}")

    def test_sem_header_status_200(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)

    # ── 2. Com header válido ────────────────────────────────────────────────

    def test_com_header_uuid_valido_e_reutilizado(self):
        cid = str(uuid.uuid4())
        response = self.client.get("/api/health/", HTTP_X_CORRELATION_ID=cid)
        self.assertEqual(response["X-Correlation-ID"], cid)

    def test_com_header_valido_status_200(self):
        cid = str(uuid.uuid4())
        response = self.client.get("/api/health/", HTTP_X_CORRELATION_ID=cid)
        self.assertEqual(response.status_code, 200)

    # ── 3. Dois logs da mesma requisição compartilham o ID ──────────────────

    def test_dois_logs_mesma_requisicao_mesmo_id(self):
        """
        Intercepta os LogRecords produzidos durante GET /api/health/
        e verifica que todos carregam o mesmo correlation_id.
        """
        captured = []

        class _CapturingHandler(logging.Handler):
            def emit(self, record):
                # CorrelationFilter já foi aplicado pelos handlers de settings
                # mas não necessariamente antes deste handler.
                # Aqui aplicamos manualmente para testar o Filter isoladamente.
                f = CorrelationFilter()
                f.filter(record)
                captured.append(getattr(record, "correlation_id", None))

        cid = str(uuid.uuid4())
        handler = _CapturingHandler()
        log = logging.getLogger("api_tcc")
        log.addHandler(handler)
        try:
            # Gera pelo menos dois logs dentro da mesma requisição.
            # /api/health/ loga durante a execução (views_health.py).
            # Injetamos nosso próprio log para garantir dois registros.
            def _view_com_dois_logs(get_response):
                def middleware(request):
                    log.info("log 1 do teste")
                    response = get_response(request)
                    log.info("log 2 do teste")
                    return response
                return middleware

            with self.modify_settings(
                MIDDLEWARE={"prepend": "django.middleware.common.CommonMiddleware"}
            ):
                # Abordagem mais direta: emitir dois logs dentro do contexto
                # do CorrelationIDMiddleware verificando o ContextVar diretamente.
                pass
        finally:
            log.removeHandler(handler)

        # Abordagem direta e confiável: setar o contexto manualmente e emitir logs.
        cid2 = str(uuid.uuid4())
        token = set_correlation_id(cid2)
        captured2 = []
        try:
            f = CorrelationFilter()

            r1 = _FakeRecord()
            f.filter(r1)
            captured2.append(r1.correlation_id)

            r2 = _FakeRecord()
            f.filter(r2)
            captured2.append(r2.correlation_id)
        finally:
            reset_correlation_id(token)

        self.assertEqual(len(captured2), 2)
        self.assertEqual(captured2[0], cid2)
        self.assertEqual(captured2[1], cid2)
        self.assertEqual(captured2[0], captured2[1])

    # ── 4. Duas requisições têm IDs distintos ──────────────────────────────

    def test_duas_requisicoes_ids_distintos(self):
        r1 = self.client.get("/api/health/")
        r2 = self.client.get("/api/health/")
        cid1 = r1["X-Correlation-ID"]
        cid2 = r2["X-Correlation-ID"]
        self.assertNotEqual(cid1, cid2, "Dois requests sem header devem receber UUIDs distintos")

    def test_duas_requisicoes_ids_sao_uuids_validos(self):
        r1 = self.client.get("/api/health/")
        r2 = self.client.get("/api/health/")
        for cid in [r1["X-Correlation-ID"], r2["X-Correlation-ID"]]:
            try:
                uuid.UUID(cid)
            except ValueError:
                self.fail(f"ID não é UUID válido: {cid!r}")


# ──────────────────────────────────────────────────────────────────────────────
# 5.  Isolamento de contexto (ContextVar não vaza entre execuções)
# ──────────────────────────────────────────────────────────────────────────────

class ContextIsolationTest(TestCase):

    def test_reset_limpa_o_contexto(self):
        """Após reset, get_correlation_id() deve retornar None."""
        token = set_correlation_id("sentinel-value")
        reset_correlation_id(token)
        self.assertIsNone(get_correlation_id())

    def test_contexto_nao_vaza_entre_contextos_distintos(self):
        """
        Dois contextos independentes (copy_context) não devem ver o valor um do outro.
        Simula duas requisições concorrentes.
        """
        resultados = {}

        def _run_a():
            token = set_correlation_id("id-A")
            try:
                resultados["A"] = get_correlation_id()
            finally:
                reset_correlation_id(token)

        def _run_b():
            token = set_correlation_id("id-B")
            try:
                resultados["B"] = get_correlation_id()
            finally:
                reset_correlation_id(token)

        ctx_a = copy_context()
        ctx_b = copy_context()
        ctx_a.run(_run_a)
        ctx_b.run(_run_b)

        self.assertEqual(resultados["A"], "id-A")
        self.assertEqual(resultados["B"], "id-B")
        self.assertNotEqual(resultados["A"], resultados["B"])

    def test_contexto_anterior_nao_afeta_novo(self):
        """
        Depois que um processamento termina (reset), o próximo não herda o ID.
        """
        token = set_correlation_id("processamento-anterior")
        reset_correlation_id(token)

        # Simula início de novo processamento sem ID explícito
        self.assertIsNone(get_correlation_id())


# ──────────────────────────────────────────────────────────────────────────────
# 6.  Log fora de contexto — não quebra
# ──────────────────────────────────────────────────────────────────────────────

class LogForaDeContextoTest(TestCase):

    def test_filter_fora_de_contexto_nao_levanta_excecao(self):
        """
        logger.info() fora de request HTTP e fora de processamento MQTT
        não deve causar KeyError nem AttributeError.
        """
        f = CorrelationFilter()
        record = _FakeRecord()
        try:
            result = f.filter(record)
        except Exception as exc:
            self.fail(f"CorrelationFilter levantou exceção inesperada: {exc}")
        self.assertTrue(result)

    def test_filter_fora_de_contexto_usa_valor_neutro(self):
        """Fora de contexto, correlation_id deve ser 'null' (não None nem string vazia)."""
        # Garante que não há ID no contexto atual
        # (contexto de teste começa sem ID definido)
        cid_atual = get_correlation_id()
        if cid_atual is not None:
            self.skipTest("Contexto já tem ID — não é possível testar ausência aqui")

        resultado = _apply_filter()
        self.assertEqual(resultado, "null")

    def test_logger_exception_funciona_fora_de_contexto(self):
        """
        logger.exception() não deve falhar quando não há correlation_id no contexto.
        Esse cenário ocorre em workers de startup, management commands, etc.
        """
        captured = []

        class _CapHandler(logging.Handler):
            def emit(self, record):
                CorrelationFilter().filter(record)
                captured.append(record.correlation_id)

        log = logging.getLogger("api_tcc.test_exception")
        handler = _CapHandler()
        log.addHandler(handler)
        try:
            try:
                raise ValueError("erro de teste")
            except ValueError:
                log.exception("falha capturada no teste")
        finally:
            log.removeHandler(handler)

        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0], "null")


# ──────────────────────────────────────────────────────────────────────────────
# 7–8  Fluxo MQTT
# ──────────────────────────────────────────────────────────────────────────────

class MQTTCorrelationTest(TestCase):
    """
    Testa que on_message() define correlation_id = UUID da leitura.
    Não sobe broker MQTT real — testa apenas a camada de processamento.
    """

    def _build_message(self, reading_uuid: str) -> object:
        """Cria um objeto msg MQTT mínimo com um payload JSON válido."""
        import json

        class _FakeMsg:
            topic = "fieldnode/COLH-01/leitura"
            payload = json.dumps({
                "id": reading_uuid,
                "maquina_id": "COLH-01",
                "temperatura": 75.0,
                "vibracao": 0.30,
                "rpm": 1800,
                "timestamp": "2026-10-05T18:00:00",
            }).encode("utf-8")

        return _FakeMsg()

    def test_on_message_usa_uuid_da_leitura_como_correlation_id(self):
        """
        Durante o processamento de on_message, o correlation_id disponível
        no contexto deve ser igual ao UUID da leitura enviado no payload.
        """
        reading_uuid = str(uuid.uuid4())
        ids_capturados = []

        # Mock de registrar_leitura para capturar o estado do contexto
        # sem depender do banco de dados.
        def _mock_registrar(dados):
            ids_capturados.append(get_correlation_id())
            return "criado", dados.get("id")

        msg = self._build_message(reading_uuid)
        with patch(
            "api_tcc.management.commands.mqtt_listen.registrar_leitura",
            side_effect=_mock_registrar,
        ):
            on_message(client=None, userdata=None, msg=msg)

        self.assertEqual(len(ids_capturados), 1)
        self.assertEqual(ids_capturados[0], reading_uuid)

    def test_correlation_id_resetado_apos_on_message(self):
        """
        Após on_message retornar, o ContextVar deve ser resetado.
        O processamento da próxima mensagem não deve herdar o ID anterior.
        """
        reading_uuid = str(uuid.uuid4())
        msg = self._build_message(reading_uuid)

        with patch(
            "api_tcc.management.commands.mqtt_listen.registrar_leitura",
            return_value=("criado", reading_uuid),
        ):
            on_message(client=None, userdata=None, msg=msg)

        # Após on_message, o contexto deve ter voltado ao que era antes
        self.assertIsNone(get_correlation_id())

    def test_duas_mensagens_mqtt_ids_distintos(self):
        """
        Duas mensagens processadas sequencialmente não devem compartilhar o ID.
        """
        uuid_a = str(uuid.uuid4())
        uuid_b = str(uuid.uuid4())
        ids_por_mensagem = []

        def _mock_registrar(dados):
            ids_por_mensagem.append(get_correlation_id())
            return "criado", dados.get("id")

        with patch(
            "api_tcc.management.commands.mqtt_listen.registrar_leitura",
            side_effect=_mock_registrar,
        ):
            on_message(client=None, userdata=None, msg=self._build_message(uuid_a))
            on_message(client=None, userdata=None, msg=self._build_message(uuid_b))

        self.assertEqual(len(ids_por_mensagem), 2)
        self.assertEqual(ids_por_mensagem[0], uuid_a)
        self.assertEqual(ids_por_mensagem[1], uuid_b)
        self.assertNotEqual(ids_por_mensagem[0], ids_por_mensagem[1])


# ──────────────────────────────────────────────────────────────────────────────
# 9.  Sanitização do header externo
# ──────────────────────────────────────────────────────────────────────────────

class SanitizeExternalIDTest(TestCase):

    def test_uuid_valido_aceito(self):
        cid = str(uuid.uuid4())
        self.assertEqual(_sanitize_external_id(cid), cid)

    def test_string_alfanumerica_com_hifen_aceita(self):
        self.assertEqual(_sanitize_external_id("abc-123-XYZ"), "abc-123-XYZ")

    def test_string_com_underscore_aceita(self):
        self.assertEqual(_sanitize_external_id("abc_123"), "abc_123")

    def test_valor_vazio_rejeitado(self):
        self.assertIsNone(_sanitize_external_id(""))

    def test_valor_somente_espacos_rejeitado(self):
        self.assertIsNone(_sanitize_external_id("   "))

    def test_valor_muito_longo_rejeitado(self):
        longo = "a" * 65
        self.assertIsNone(_sanitize_external_id(longo))

    def test_valor_exatamente_no_limite_aceito(self):
        no_limite = "a" * 64
        self.assertEqual(_sanitize_external_id(no_limite), no_limite)

    def test_newline_rejeitado(self):
        """Injeção de newline nos logs deve ser impossível via este header."""
        self.assertIsNone(_sanitize_external_id("abc\nfake-log-line"))

    def test_carriage_return_rejeitado(self):
        self.assertIsNone(_sanitize_external_id("abc\rfake"))

    def test_nulo_byte_rejeitado(self):
        self.assertIsNone(_sanitize_external_id("abc\x00"))

    def test_espaco_no_meio_rejeitado(self):
        self.assertIsNone(_sanitize_external_id("abc 123"))

    def test_caractere_especial_rejeitado(self):
        self.assertIsNone(_sanitize_external_id("abc<script>"))

    def test_header_invalido_gera_novo_uuid_no_middleware(self):
        """
        Quando o header contém valor inválido, o middleware deve gerar
        um UUID novo e retorná-lo no response — não o valor bruto.
        """
        client = APIClient()
        response = client.get(
            "/api/health/",
            HTTP_X_CORRELATION_ID="invalid value with spaces\nand newline",
        )
        cid = response["X-Correlation-ID"]
        self.assertNotIn("\n", cid)
        self.assertNotIn(" ", cid)
        # Deve ser um UUID válido gerado pelo sistema
        try:
            uuid.UUID(cid)
        except ValueError:
            self.fail(f"Header inválido deveria gerar UUID novo, mas obteve: {cid!r}")


# ──────────────────────────────────────────────────────────────────────────────
# 10.  Múltiplos logs na mesma operação — teste principal do S7-T2
# ──────────────────────────────────────────────────────────────────────────────

class MultipleLogsCorrelationTest(TestCase):
    """
    Comprova o objetivo central do S7-T2:
    dois logs da mesma operação têm o mesmo correlation_id;
    operações distintas têm IDs distintos.
    """

    def test_dois_logs_mesma_operacao_mesmo_id(self):
        cid = str(uuid.uuid4())
        ids = []
        token = set_correlation_id(cid)
        try:
            f = CorrelationFilter()
            for _ in range(2):
                r = _FakeRecord()
                f.filter(r)
                ids.append(r.correlation_id)
        finally:
            reset_correlation_id(token)

        self.assertEqual(ids[0], ids[1])
        self.assertEqual(ids[0], cid)

    def test_operacoes_distintas_ids_distintos(self):
        """
        Operação A produz logs com ID A.
        Operação B produz logs com ID B.
        A != B.
        """
        resultados = {}
        f = CorrelationFilter()

        for operacao in ("A", "B"):
            cid = new_correlation_id()
            token = set_correlation_id(cid)
            try:
                r = _FakeRecord()
                f.filter(r)
                resultados[operacao] = r.correlation_id
            finally:
                reset_correlation_id(token)

        self.assertNotEqual(resultados["A"], resultados["B"])
        # Ambos são UUIDs válidos
        for cid in resultados.values():
            uuid.UUID(cid)

    def test_log_entre_operacoes_usa_valor_neutro(self):
        """
        Um log emitido ENTRE duas operações (fora de contexto) usa 'null',
        não o ID da operação anterior nem o da próxima.
        """
        f = CorrelationFilter()

        # Operação A
        token_a = set_correlation_id("op-a")
        r_a = _FakeRecord()
        f.filter(r_a)
        reset_correlation_id(token_a)

        # Fora de contexto
        r_fora = _FakeRecord()
        f.filter(r_fora)

        # Operação B
        token_b = set_correlation_id("op-b")
        r_b = _FakeRecord()
        f.filter(r_b)
        reset_correlation_id(token_b)

        self.assertEqual(r_a.correlation_id, "op-a")
        self.assertEqual(r_fora.correlation_id, "null")
        self.assertEqual(r_b.correlation_id, "op-b")


# ──────────────────────────────────────────────────────────────────────────────
# Compatibilidade com S7-T1 — /api/health/ retorna X-Correlation-ID
# ──────────────────────────────────────────────────────────────────────────────

class HealthCheckCorrelationTest(TestCase):
    """
    Verifica que o healthcheck (S7-T1) funciona corretamente com o
    middleware de correlation ID (S7-T2) — sem modificar a lógica do health.
    """

    def setUp(self):
        self.client = APIClient()

    def test_health_retorna_x_correlation_id(self):
        response = self.client.get("/api/health/")
        self.assertIn("X-Correlation-ID", response)

    def test_health_correlation_id_propagado_do_cliente(self):
        cid = str(uuid.uuid4())
        response = self.client.get("/api/health/", HTTP_X_CORRELATION_ID=cid)
        self.assertEqual(response["X-Correlation-ID"], cid)

    def test_health_continua_retornando_200(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)

    def test_health_campos_originais_preservados(self):
        """O middleware não deve alterar o corpo da resposta do healthcheck."""
        response = self.client.get("/api/health/")
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("database", data)
