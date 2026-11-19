"""SDK e adaptadores declarativos de protocolos."""

from .base import Adapter, AdapterError, get_adapter, register, validar_param

# Registro explícito dos exemplos locais. Nenhum identificador vem do payload.
from . import examples  # noqa: F401,E402

__all__ = ["Adapter", "AdapterError", "get_adapter", "register", "validar_param"]
