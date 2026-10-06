"""
api_tcc/middleware.py

Middleware Django de correlation ID (S7-T2).

Responsabilidades:
  1. Ler X-Correlation-ID do request (se presente e válido)
  2. Gerar UUID4 se ausente/inválido
  3. Definir o valor no ContextVar para toda a duração da requisição
  4. Restaurar o contexto ao final (via token — evita vazamento)
  5. Adicionar X-Correlation-ID à resposta (sucesso e erro)

O que este middleware NÃO faz:
  - Não captura exceções da aplicação
  - Não altera status HTTP
  - Não modifica regra de negócio
  - Não loga o header bruto antes de sanitizá-lo

Uso:
    MIDDLEWARE = [
        ...
        'api_tcc.middleware.CorrelationIDMiddleware',
        ...
    ]
"""

import logging

from api_tcc.correlation import (
    _sanitize_external_id,
    new_correlation_id,
    reset_correlation_id,
    set_correlation_id,
)

logger = logging.getLogger(__name__)

_HEADER_IN = "HTTP_X_CORRELATION_ID"   # Django transforma X-Correlation-ID → HTTP_X_CORRELATION_ID
_HEADER_OUT = "X-Correlation-ID"


class CorrelationIDMiddleware:
    """
    Middleware Django (new-style, non-class-based middleware).

    Posicionamento recomendado: logo após CorsMiddleware, antes dos demais.
    Isso garante que o ID esteja disponível desde o início do processamento.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ── 1. Extrair header externo ──────────────────────────────────────
        raw_header = request.META.get(_HEADER_IN, "")

        # ── 2. Validar/sanitizar — não registrar raw antes de sanitizar ────
        external_id = _sanitize_external_id(raw_header) if raw_header else None

        # ── 3. Definir correlation ID: reutiliza externo ou gera novo ──────
        correlation_id = external_id if external_id is not None else new_correlation_id()

        # ── 4. Injetar no ContextVar e preservar token para reset ──────────
        token = set_correlation_id(correlation_id)

        try:
            response = self.get_response(request)
        finally:
            # ── 5. Restaurar contexto — garante isolamento entre requests ──
            reset_correlation_id(token)

        # ── 6. Adicionar header à resposta ─────────────────────────────────
        # Acontece após o reset intencional — o ID já foi capturado em variável local.
        response[_HEADER_OUT] = correlation_id

        return response
