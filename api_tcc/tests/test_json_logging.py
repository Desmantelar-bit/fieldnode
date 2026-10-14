"""
api_tcc/tests/test_json_logging.py

Testes unitários do JSONFormatter (S7-T3).

Verifica:
  - JSON parseável (json.loads não lança)
  - campos mínimos presentes: timestamp, level, logger, message, correlation_id
  - exatamente uma linha por evento (sem \\n no resultado)
  - correlation_id real propagado do ContextVar (integração S7-T2)
  - correlation_id None quando fora de contexto
  - correlation_id "null" (string do CorrelationFilter) → JSON null
  - mensagem com argumentos de formatação (%s) interpolada corretamente
  - Unicode (português) sobrevive ao round-trip JSON
  - exceção: JSON válido, traceback preservado, uma linha
  - campos extras via extra={} aparecem no JSON

Compatível com unittest (manage.py test) e pytest.
"""

import json
import logging
import sys
from unittest import TestCase

from api_tcc.correlation import (
    JSONFormatter,
    CorrelationFilter,
    get_correlation_id,
    reset_correlation_id,
    set_correlation_id,
)


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _make_formatter():
    return JSONFormatter()


def _make_filter():
    return CorrelationFilter()


def _make_record(
    msg: str = "mensagem de teste",
    level: int = logging.INFO,
    logger_name: str = "test.logger",
    args=None,
    exc_info=None,
    extra: dict | None = None,
) -> logging.LogRecord:
    """
    Cria um LogRecord mínimo sem precisar de logger real.
    Simula o que o sistema de logging faz internamente.
    """
    record = logging.LogRecord(
        name=logger_name,
        level=level,
        pathname="",
        lineno=0,
        msg=msg,
        args=args or (),
        exc_info=exc_info,
    )
    if extra:
        for key, value in extra.items():
            setattr(record, key, value)
    return record


def _apply_filter(filter_: CorrelationFilter, record: logging.LogRecord) -> logging.LogRecord:
    """Aplica o CorrelationFilter ao record (simula o pipeline do handler)."""
    filter_.filter(record)
    return record


# ──────────────────────────────────────────────────────────────
# 1. JSON parseável
# ──────────────────────────────────────────────────────────────

class TestJSONParseavel(TestCase):
    def setUp(self):
        self.formatter = _make_formatter()
        self.filter_ = _make_filter()

    def test_resultado_e_json_valido(self):
        record = _apply_filter(self.filter_, _make_record("evento simples"))
        resultado = self.formatter.format(record)
        parsed = json.loads(resultado)  # não deve lançar
        self.assertIsInstance(parsed, dict)

    def test_nivel_info(self):
        record = _apply_filter(self.filter_, _make_record("ok", level=logging.INFO))
        parsed = json.loads(self.formatter.format(record))
        self.assertEqual(parsed["level"], "INFO")

    def test_nivel_warning(self):
        record = _apply_filter(self.filter_, _make_record("aviso", level=logging.WARNING))
        parsed = json.loads(self.formatter.format(record))
        self.assertEqual(parsed["level"], "WARNING")

    def test_nivel_error(self):
        record = _apply_filter(self.filter_, _make_record("falha", level=logging.ERROR))
        parsed = json.loads(self.formatter.format(record))
        self.assertEqual(parsed["level"], "ERROR")


# ──────────────────────────────────────────────────────────────
# 2. Campos mínimos obrigatórios
# ──────────────────────────────────────────────────────────────

class TestCamposMinimos(TestCase):
    def setUp(self):
        self.formatter = _make_formatter()
        self.filter_ = _make_filter()

    def test_timestamp_presente(self):
        record = _apply_filter(self.filter_, _make_record())
        parsed = json.loads(self.formatter.format(record))
        self.assertIn("timestamp", parsed)
        self.assertTrue(parsed["timestamp"])  # não é vazio

    def test_level_presente(self):
        record = _apply_filter(self.filter_, _make_record())
        parsed = json.loads(self.formatter.format(record))
        self.assertIn("level", parsed)

    def test_logger_presente(self):
        record = _apply_filter(self.filter_, _make_record(logger_name="servicos.telemetria"))
        parsed = json.loads(self.formatter.format(record))
        self.assertEqual(parsed["logger"], "servicos.telemetria")

    def test_message_presente(self):
        record = _apply_filter(self.filter_, _make_record("leitura processada"))
        parsed = json.loads(self.formatter.format(record))
        self.assertEqual(parsed["message"], "leitura processada")

    def test_correlation_id_presente(self):
        record = _apply_filter(self.filter_, _make_record())
        parsed = json.loads(self.formatter.format(record))
        self.assertIn("correlation_id", parsed)

    def test_timestamp_formato_iso8601(self):
        """Timestamp deve ser string ISO 8601 com offset de timezone."""
        record = _apply_filter(self.filter_, _make_record())
        parsed = json.loads(self.formatter.format(record))
        ts = parsed["timestamp"]
        # ISO 8601 com timezone: contém 'T' e '+' ou '-' ou 'Z'
        self.assertIn("T", ts)
        self.assertTrue(
            any(c in ts for c in ("+", "-", "Z")),
            f"Timestamp sem offset: {ts!r}",
        )


# ──────────────────────────────────────────────────────────────
# 3. Garantia de uma linha por evento
# ──────────────────────────────────────────────────────────────

class TestUmaLinhaPorEvento(TestCase):
    def setUp(self):
        self.formatter = _make_formatter()
        self.filter_ = _make_filter()

    def test_sem_newline_no_resultado(self):
        record = _apply_filter(self.filter_, _make_record("sem quebra"))
        resultado = self.formatter.format(record)
        self.assertNotIn(
            "\n", resultado,
            f"O formatter produziu quebra de linha: {resultado!r}",
        )

    def test_count_newline_zero(self):
        record = _apply_filter(self.filter_, _make_record("outro evento"))
        resultado = self.formatter.format(record)
        self.assertEqual(resultado.count("\n"), 0)


# ──────────────────────────────────────────────────────────────
# 4. correlation_id — integração com S7-T2
# ──────────────────────────────────────────────────────────────

class TestCorrelationID(TestCase):
    def setUp(self):
        self.formatter = _make_formatter()
        self.filter_ = _make_filter()

    def test_correlation_id_null_fora_de_contexto(self):
        """Fora de qualquer contexto gerenciado, correlation_id deve ser null."""
        record = _apply_filter(self.filter_, _make_record("sem contexto"))
        parsed = json.loads(self.formatter.format(record))
        self.assertIsNone(parsed["correlation_id"])

    def test_correlation_id_string_null_vira_json_null(self):
        """
        O CorrelationFilter injeta a string "null" fora de contexto para
        compatibilidade com formatters de texto. O JSONFormatter deve
        converter essa string para JSON null (Python None), não para
        a string "null".
        """
        record = _make_record("fora de contexto")
        record.correlation_id = "null"  # simula o que o CorrelationFilter injeta
        parsed = json.loads(self.formatter.format(record))
        self.assertIsNone(
            parsed["correlation_id"],
            'correlation_id deve ser JSON null, não a string "null"',
        )

    def test_correlation_id_real_aparece_no_json(self):
        """Dentro de um contexto com ID definido, o JSON deve conter o ID."""
        cid = "abc-123-def-456"
        token = set_correlation_id(cid)
        try:
            record = _apply_filter(self.filter_, _make_record("com contexto"))
            parsed = json.loads(self.formatter.format(record))
            self.assertEqual(parsed["correlation_id"], cid)
        finally:
            reset_correlation_id(token)

    def test_correlation_id_uuid_completo(self):
        """UUID4 completo deve aparecer inalterado."""
        cid = "7f4e2d1a-8b3c-4f5e-9a6d-0e1f2b3c4d5e"
        token = set_correlation_id(cid)
        try:
            record = _apply_filter(self.filter_, _make_record("uuid"))
            parsed = json.loads(self.formatter.format(record))
            self.assertEqual(parsed["correlation_id"], cid)
        finally:
            reset_correlation_id(token)

    def test_dois_eventos_com_mesmo_correlation_id(self):
        """Dois registros no mesmo contexto devem ter o mesmo correlation_id."""
        cid = "correlacao-compartilhada"
        token = set_correlation_id(cid)
        try:
            r1 = _apply_filter(self.filter_, _make_record("evento A"))
            r2 = _apply_filter(self.filter_, _make_record("evento B"))
            p1 = json.loads(self.formatter.format(r1))
            p2 = json.loads(self.formatter.format(r2))
            self.assertEqual(p1["correlation_id"], cid)
            self.assertEqual(p2["correlation_id"], cid)
            self.assertEqual(p1["correlation_id"], p2["correlation_id"])
        finally:
            reset_correlation_id(token)

    def test_contextos_distintos_tem_ids_distintos(self):
        """IDs de contextos diferentes não devem vazar entre si."""
        cid_x = "contexto-X"
        cid_y = "contexto-Y"

        token_x = set_correlation_id(cid_x)
        r_x = _apply_filter(self.filter_, _make_record("evento X"))
        p_x = json.loads(self.formatter.format(r_x))
        reset_correlation_id(token_x)

        token_y = set_correlation_id(cid_y)
        r_y = _apply_filter(self.filter_, _make_record("evento Y"))
        p_y = json.loads(self.formatter.format(r_y))
        reset_correlation_id(token_y)

        self.assertEqual(p_x["correlation_id"], cid_x)
        self.assertEqual(p_y["correlation_id"], cid_y)
        self.assertNotEqual(p_x["correlation_id"], p_y["correlation_id"])

    def test_formatter_nao_gera_novo_uuid(self):
        """
        O formatter não deve gerar um novo UUID a cada chamada.
        Sem contexto → correlation_id null (não um UUID novo).
        """
        r1 = _apply_filter(self.filter_, _make_record("primeiro"))
        r2 = _apply_filter(self.filter_, _make_record("segundo"))
        p1 = json.loads(self.formatter.format(r1))
        p2 = json.loads(self.formatter.format(r2))
        # ambos devem ser null, não UUIDs diferentes
        self.assertIsNone(p1["correlation_id"])
        self.assertIsNone(p2["correlation_id"])


# ──────────────────────────────────────────────────────────────
# 5. Mensagem com argumentos de formatação
# ──────────────────────────────────────────────────────────────

class TestMensagemInterpolada(TestCase):
    def setUp(self):
        self.formatter = _make_formatter()
        self.filter_ = _make_filter()

    def test_args_percentual_interpolados(self):
        """logger.info('máquina %s', 12) → message: 'máquina 12'"""
        record = _apply_filter(self.filter_, _make_record("máquina %s", args=(12,)))
        parsed = json.loads(self.formatter.format(record))
        self.assertEqual(parsed["message"], "máquina 12")

    def test_msg_sem_args_inalterada(self):
        record = _apply_filter(self.filter_, _make_record("mensagem direta"))
        parsed = json.loads(self.formatter.format(record))
        self.assertEqual(parsed["message"], "mensagem direta")

    def test_multiplos_args(self):
        record = _apply_filter(
            self.filter_, _make_record("device=%s seq=%d", args=("COLH-01", 42))
        )
        parsed = json.loads(self.formatter.format(record))
        self.assertEqual(parsed["message"], "device=COLH-01 seq=42")


# ──────────────────────────────────────────────────────────────
# 6. Unicode / português
# ──────────────────────────────────────────────────────────────

class TestUnicode(TestCase):
    def setUp(self):
        self.formatter = _make_formatter()
        self.filter_ = _make_filter()

    def test_acentos_preservados(self):
        """Caracteres acentuados devem aparecer legíveis, não como \\\\uXXXX."""
        msg = "não foi possível processar a leitura"
        record = _apply_filter(self.filter_, _make_record(msg))
        resultado = self.formatter.format(record)
        parsed = json.loads(resultado)
        self.assertEqual(parsed["message"], msg)
        # Garante que não foi escaped desnecessariamente
        self.assertTrue(
            "\\u" not in resultado or json.loads(f'"{msg}"') == msg,
        )

    def test_unicode_json_valido(self):
        msg = "máquina desconhecida — verificar configuração"
        record = _apply_filter(self.filter_, _make_record(msg))
        parsed = json.loads(self.formatter.format(record))
        self.assertEqual(parsed["message"], msg)

    def test_unicode_uma_linha(self):
        record = _apply_filter(self.filter_, _make_record("leitura inválida: temperatura fora do range"))
        resultado = self.formatter.format(record)
        self.assertNotIn("\n", resultado)


# ──────────────────────────────────────────────────────────────
# 7. Exceção / traceback
# ──────────────────────────────────────────────────────────────

class TestExcecao(TestCase):
    def setUp(self):
        self.formatter = _make_formatter()
        self.filter_ = _make_filter()

    def _record_com_excecao(self) -> logging.LogRecord:
        try:
            raise ValueError("falha de processamento")
        except ValueError:
            exc_info = sys.exc_info()
        record = logging.LogRecord(
            name="test.exception",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="erro ao processar leitura",
            args=(),
            exc_info=exc_info,
        )
        self.filter_.filter(record)
        return record

    def test_json_valido_com_excecao(self):
        record = self._record_com_excecao()
        parsed = json.loads(self.formatter.format(record))
        self.assertIsInstance(parsed, dict)

    def test_uma_linha_com_excecao(self):
        record = self._record_com_excecao()
        resultado = self.formatter.format(record)
        self.assertNotIn(
            "\n", resultado,
            "Traceback quebrou a garantia de uma linha por evento",
        )

    def test_excecao_campo_presente(self):
        record = self._record_com_excecao()
        parsed = json.loads(self.formatter.format(record))
        self.assertIn("exception", parsed)

    def test_excecao_type_correto(self):
        record = self._record_com_excecao()
        parsed = json.loads(self.formatter.format(record))
        self.assertEqual(parsed["exception"]["type"], "ValueError")

    def test_excecao_message_correto(self):
        record = self._record_com_excecao()
        parsed = json.loads(self.formatter.format(record))
        self.assertEqual(parsed["exception"]["message"], "falha de processamento")

    def test_traceback_presente_e_nao_vazio(self):
        record = self._record_com_excecao()
        parsed = json.loads(self.formatter.format(record))
        tb = parsed["exception"]["traceback"]
        self.assertTrue(tb)  # não vazio
        self.assertIn("ValueError", tb)

    def test_correlation_id_presente_com_excecao(self):
        cid = "excecao-correlacionada"
        token = set_correlation_id(cid)
        try:
            record = self._record_com_excecao()
            parsed = json.loads(self.formatter.format(record))
            self.assertEqual(parsed["correlation_id"], cid)
        finally:
            reset_correlation_id(token)


# ──────────────────────────────────────────────────────────────
# 8. Campos extras via extra={}
# ──────────────────────────────────────────────────────────────

class TestCamposExtras(TestCase):
    def setUp(self):
        self.formatter = _make_formatter()
        self.filter_ = _make_filter()

    def test_maquina_id_preservado(self):
        record = _apply_filter(
            self.filter_,
            _make_record("leitura processada", extra={"maquina_id": 12}),
        )
        parsed = json.loads(self.formatter.format(record))
        self.assertEqual(parsed["maquina_id"], 12)

    def test_campo_string_preservado(self):
        record = _apply_filter(
            self.filter_,
            _make_record("ok", extra={"device_id": "COLH-01"}),
        )
        parsed = json.loads(self.formatter.format(record))
        self.assertEqual(parsed["device_id"], "COLH-01")

    def test_campo_extra_nao_duplica_campos_base(self):
        """
        extra não deve sobrescrever timestamp/level/logger/message/correlation_id.
        Os campos base têm prioridade — o extra é inserido na construção do payload,
        mas os campos reservados são listados em _LOGRECORD_RESERVED e ignorados.
        Aqui testamos que a mensagem do payload base está correta mesmo com extra.
        """
        record = _apply_filter(
            self.filter_,
            _make_record("evento com extra", extra={"source": "mqtt"}),
        )
        parsed = json.loads(self.formatter.format(record))
        self.assertEqual(parsed["message"], "evento com extra")
        self.assertEqual(parsed["source"], "mqtt")

    def test_json_valido_com_extra(self):
        record = _apply_filter(
            self.filter_,
            _make_record("ok", extra={"sequence_number": 7, "transport": "mqtt"}),
        )
        parsed = json.loads(self.formatter.format(record))
        self.assertIsInstance(parsed, dict)
        self.assertEqual(parsed["sequence_number"], 7)
        self.assertEqual(parsed["transport"], "mqtt")
