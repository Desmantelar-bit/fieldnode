"""
api_tcc/correlation.py

Infraestrutura mínima de correlation ID para observabilidade.

Responsabilidades separadas:
  - ContextVar: mantém o ID isolado por contexto de execução (thread/async-safe)
  - CorrelationFilter: injeta o ID em todo LogRecord automaticamente
  - set_correlation_id / get_correlation_id: API pública para o middleware e o worker MQTT

Arquitetura (S7-T2):
  HTTP:  CorrelationIDMiddleware → ContextVar → LogRecord
  MQTT:  on_message → set_correlation_id(uuid_leitura) → LogRecord

Por que contextvars e não threading.local:
  threading.local isola por thread mas não por corrotina (asyncio) nem por
  task de um executor. ContextVar isola por contexto de execução em ambos os
  modelos, sem comportamento surpresa em workers concorrentes.

Por que não global simples:
  Uma variável global compartilhada entre requisições concorrentes misturaria
  correlation IDs de operações distintas, tornando os logs inúteis para
  diagnóstico.

Preparado para S7-T3 (JSON logging):
  record.correlation_id já está disponível no LogRecord — o formatter JSON
  pode consumir esse campo sem alterar o middleware.
"""

import json
import logging
import traceback
import uuid
from contextvars import ContextVar
from datetime import timezone
from typing import Optional

# ──────────────────────────────────────────────────────────────
# ContextVar
# Cada contexto de execução (requisição HTTP, worker MQTT, etc.)
# tem seu próprio valor sem interferência dos demais.
# default=None significa: fora de qualquer contexto gerenciado.
# ──────────────────────────────────────────────────────────────
_correlation_id_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id",
    default=None,
)


def get_correlation_id() -> Optional[str]:
    """Retorna o correlation ID do contexto atual, ou None se não definido."""
    return _correlation_id_var.get()


def set_correlation_id(value: str):
    """
    Define o correlation ID para o contexto atual.

    Retorna o token necessário para reset posterior:

        token = set_correlation_id("abc-123")
        try:
            ...
        finally:
            reset_correlation_id(token)
    """
    return _correlation_id_var.set(value)


def reset_correlation_id(token) -> None:
    """
    Restaura o contexto ao estado anterior ao set_correlation_id.
    Evita vazamento do ID para o próximo processamento no mesmo contexto.
    """
    _correlation_id_var.reset(token)


# ──────────────────────────────────────────────────────────────
# Logging Filter
# Injetado automaticamente em todos os handlers via settings.LOGGING.
# Não exige extra={"correlation_id": ...} em cada logger.info().
# Funciona também fora de request — retorna "null" como valor neutro.
# ──────────────────────────────────────────────────────────────
class CorrelationFilter(logging.Filter):
    """
    Injeta ``correlation_id`` em cada LogRecord.

    Comportamento:
      - Dentro de request HTTP: valor do X-Correlation-ID da requisição
      - Dentro de processamento MQTT: UUID da leitura
      - Fora de qualquer contexto: "null"

    O valor "null" (string) é escolhido deliberadamente:
      - Compatível com formatters de string (não causa KeyError)
      - Distinguível de um UUID real nos logs
      - Substituível por None no formatter JSON (S7-T3)
    """

    def filter(self, record: logging.LogRecord) -> bool:
        cid = get_correlation_id()
        record.correlation_id = cid if cid is not None else "null"
        return True


# ──────────────────────────────────────────────────────────────
# Validação do header externo
# ──────────────────────────────────────────────────────────────
_MAX_CORRELATION_ID_LEN = 64
_SAFE_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "-_"
)


def _sanitize_external_id(raw: str) -> Optional[str]:
    """
    Valida e sanitiza um correlation ID recebido de fonte externa.

    Regras:
      1. Vazio ou só espaços → rejeita (retorna None → gera UUID novo)
      2. Tamanho > _MAX_CORRELATION_ID_LEN → rejeita
      3. Contém caractere fora do conjunto seguro → rejeita
         (previne injeção de newline e de sequências ANSI em logs)

    Por que aceitar apenas [a-zA-Z0-9-_]:
      Qualquer sistema razoável de tracing gera IDs nesse charset.
      Caracteres fora dele não têm valor operacional e representam
      superfície de ataque: um cliente malicioso poderia inserir \n
      para fabricar linhas falsas no log.

    Retorna o valor original (não transforma) se passar na validação,
    ou None se precisar gerar um novo UUID.
    """
    if not raw or not raw.strip():
        return None
    raw = raw.strip()
    if len(raw) > _MAX_CORRELATION_ID_LEN:
        return None
    if not all(c in _SAFE_CHARS for c in raw):
        return None
    return raw


def new_correlation_id() -> str:
    """Gera um UUID4 como correlation ID."""
    return str(uuid.uuid4())


# ──────────────────────────────────────────────────────────────
# JSON Formatter (S7-T3)
# Produz exatamente uma linha JSON por evento de log.
#
# Contrato:
#   - campos mínimos: timestamp, level, logger, message, correlation_id
#   - correlation_id: None (JSON null) quando fora de contexto gerenciado
#   - message: record.getMessage() — interpola argumentos de formatação
#   - exception: incluída como objeto estruturado quando presente,
#                serializada como string para não quebrar a garantia
#                de uma linha por evento
#   - campos extras: qualquer chave adicionada via extra={} é preservada
#                    desde que não conflite com campos reservados do LogRecord
#   - ensure_ascii=False: preserva caracteres Unicode (português) legíveis
#
# Campos reservados do LogRecord que são omitidos intencionalmente:
#   args, exc_info, exc_text, stack_info, msg, created, relativeCreated,
#   msecs, thread, threadName, processName, pathname, lineno, filename,
#   funcName, module, process, levelno, name (exposto como "logger").
# ──────────────────────────────────────────────────────────────

# Atributos nativos do LogRecord — não devem ser copiados cegamente para o JSON.
_LOGRECORD_RESERVED = frozenset({
    "args", "created", "exc_info", "exc_text", "filename", "funcName",
    "levelname", "levelno", "lineno", "message", "module", "msecs", "msg",
    "name", "pathname", "process", "processName", "relativeCreated",
    "stack_info", "taskName", "thread", "threadName",
    # campos injetados pelo CorrelationFilter — tratados explicitamente
    "correlation_id",
})


class JSONFormatter(logging.Formatter):
    """
    Formata cada LogRecord como uma linha JSON válida.

    Integra com S7-T2: lê ``record.correlation_id`` já injetado pelo
    CorrelationFilter — nunca gera um novo UUID.

    O campo ``correlation_id`` vem do CorrelationFilter como string ``"null"``
    quando fora de contexto (compatibilidade com o formatter de texto).
    Este formatter converte ``"null"`` → ``None`` para produzir JSON null real.

    Campos adicionais definidos via ``extra={"maquina_id": 12}`` são
    preservados desde que não conflitem com os campos reservados acima.
    """

    def format(self, record: logging.LogRecord) -> str:
        # ── Timestamp ISO 8601 com timezone ───────────────────────────────
        # datetime.fromtimestamp com tz=timezone.utc garante timezone-aware,
        # depois convertemos para o timezone local do processo via astimezone().
        from datetime import datetime
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc).astimezone()
        timestamp = ts.isoformat(timespec="milliseconds")

        # ── correlation_id: "null" (string do CorrelationFilter) → None ───
        raw_cid = getattr(record, "correlation_id", None)
        correlation_id = None if (raw_cid is None or raw_cid == "null") else raw_cid

        # ── Mensagem: interpola argumentos de formatação ───────────────────
        # record.getMessage() resolve "máquina %s" % (12,) → "máquina 12"
        message = record.getMessage()

        payload: dict = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "correlation_id": correlation_id,
        }

        # ── Campos extras definidos via extra={} ───────────────────────────
        # Preserva apenas chaves que não conflitem com campos reservados
        # e que sejam JSON-serializáveis de forma razoável.
        for key, value in vars(record).items():
            if key not in _LOGRECORD_RESERVED and not key.startswith("_"):
                try:
                    # Testa serializabilidade sem incluir no payload ainda
                    json.dumps(value, ensure_ascii=False)
                    payload[key] = value
                except (TypeError, ValueError):
                    # Valor não serializável: inclui como string
                    payload[key] = str(value)

        # ── Exceção: estruturada, serializada como string para manter 1 linha
        if record.exc_info:
            exc_type, exc_value, exc_tb = record.exc_info
            tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            payload["exception"] = {
                "type": exc_type.__name__ if exc_type else None,
                "message": str(exc_value) if exc_value else None,
                # Traceback como string única — garante 1 linha JSON por evento
                "traceback": tb_str.rstrip("\n"),
            }
        elif record.exc_text:
            # exc_text já foi formatado (ex: via formatException anterior)
            payload["exception"] = {"traceback": record.exc_text}

        # ── Serialização: uma linha, Unicode legível ───────────────────────
        return json.dumps(payload, ensure_ascii=False, default=str)
