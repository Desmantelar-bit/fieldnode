"""Registro persistente de falhas inesperadas do pipeline."""

import logging
from collections.abc import Mapping

from api_tcc.models import DeadLetterEntry

logger = logging.getLogger(__name__)


def registrar_falha_dlq(*, contexto: str, payload_referencia: Mapping, motivo: str) -> DeadLetterEntry | None:
    """Persiste uma falha sem mascarar a exceção que originou a chamada.

    O primeiro registro sempre representa uma única tentativa. Se o banco da
    aplicação estiver indisponível, a DLQ não consegue persistir localmente;
    nesse caso registramos a falha do mecanismo e devolvemos ``None``.
    """
    try:
        return DeadLetterEntry.objects.create(
            contexto=contexto,
            payload_referencia=dict(payload_referencia),
            motivo=str(motivo)[:500],
            tentativas=1,
            resolvido=False,
        )
    except Exception:
        logger.exception(
            "Falha ao persistir entrada na DLQ. contexto=%s",
            contexto,
        )
        return None
