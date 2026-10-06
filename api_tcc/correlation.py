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

import logging
import uuid
from contextvars import ContextVar
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
