"""Contrato pequeno para fontes de telemetria, sem dependência de Django."""

from abc import ABC, abstractmethod
import math

from api_tcc.services.j1939 import Param
from api_tcc.services.sensor_limits import LIMITES


ORIGENS = {"medido", "calculado", "estimado", "simulado"}
CANONICAL_METRICS = {
    "engine.temperature": "temperatura",
    "engine.coolant_temp": "temperatura",
    "engine.vibration": "vibracao",
    "engine.rpm": "rpm",
}
CANONICAL_UNITS = {
    "engine.temperature": {"C"},
    "engine.coolant_temp": {"C"},
    "engine.vibration": {"g", "indice_0_10"},
    "engine.rpm": {"rpm"},
}
_REGISTRY = {}


class AdapterError(ValueError):
    """Erro de contrato ou resolução de adaptador."""


def register(manufacturer_id: str):
    """Registra uma classe sob identificador controlado pelo código."""
    if not isinstance(manufacturer_id, str) or not manufacturer_id.strip():
        raise AdapterError("manufacturer_id vazio")

    def decorator(adapter_cls):
        if manufacturer_id in _REGISTRY:
            raise AdapterError(f"adaptador já registrado: {manufacturer_id}")
        _REGISTRY[manufacturer_id] = adapter_cls
        adapter_cls.manufacturer_id = manufacturer_id
        return adapter_cls

    return decorator


def get_adapter(manufacturer_id: str) -> "Adapter":
    try:
        adapter_cls = _REGISTRY[manufacturer_id]
    except KeyError as exc:
        raise AdapterError(f"adaptador inexistente: {manufacturer_id}") from exc
    return adapter_cls()


def validar_param(param: Param) -> Param:
    """Valida a saída sem apagar estados Raw/unsupported/invalid."""
    if param.status != "decoded":
        return param
    if param.canonical not in CANONICAL_METRICS:
        return Param(**{**param.__dict__, "status": "unsupported"})
    if param.origem not in ORIGENS:
        return Param(**{**param.__dict__, "status": "invalid", "quality": "invalid_origin"})
    if param.unit not in CANONICAL_UNITS[param.canonical]:
        return Param(**{**param.__dict__, "status": "invalid", "quality": "invalid_unit"})
    try:
        value = float(param.value)
    except (TypeError, ValueError, OverflowError):
        return Param(**{**param.__dict__, "status": "invalid", "quality": "invalid_value"})
    if not math.isfinite(value):
        return Param(**{**param.__dict__, "status": "invalid", "quality": "invalid_value"})
    metric = CANONICAL_METRICS[param.canonical]
    minimum, maximum = LIMITES[metric]
    if not minimum <= value <= maximum:
        return Param(**{**param.__dict__, "status": "invalid", "quality": "out_of_physical_range"})
    return param


class Adapter(ABC):
    """Implementação deve fornecer somente parsing específico da fonte."""

    @abstractmethod
    def _parse(self, payload: dict) -> list[Param]:
        raise NotImplementedError

    @abstractmethod
    def fingerprint(self) -> str:
        raise NotImplementedError

    def parse(self, payload: dict) -> list[Param]:
        if not isinstance(payload, dict):
            raise AdapterError("payload do adaptador deve ser objeto JSON")
        return [validar_param(param) for param in self._parse(payload)]


def _unknown(field: str, value, source: str) -> Param:
    return Param(None, None, None, status="unsupported", origem="simulado", fonte=source, raw_value=value, raw_field=field)
