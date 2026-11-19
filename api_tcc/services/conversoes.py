"""Conversoes de unidade declarativas e restritas por grandeza fisica."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ConversionRule:
    dimension: str
    source_unit: str
    target_unit: str
    factor: float
    offset: float = 0.0
    version: str = "v1"

    def apply(self, value: float) -> float:
        return value * self.factor + self.offset


CONVERSION_TABLE = {
    ("temperature", "F", "C"): ConversionRule(
        "temperature", "F", "C", 5 / 9, -32 * 5 / 9, "temperature-f-c-v1"
    ),
    ("pressure", "psi", "kPa"): ConversionRule(
        "pressure", "psi", "kPa", 6.894757293168, 0.0, "pressure-psi-kpa-v1"
    ),
}

CANONICAL_UNITS = {
    "engine.temperature": ("temperature", "C"),
    "engine.coolant_temp": ("temperature", "C"),
    "engine.oil_pressure": ("pressure", "kPa"),
    "engine.rpm": ("speed", "rpm"),
    "engine.vibration": ("acceleration", "g"),
}
IDENTITY_UNITS = {
    "engine.vibration": {"g", "indice_0_10"},
}


def convert_value(value, source_unit: str, canonical_parameter: str):
    """Retorna (valor, unidade, fator, offset) ou levanta ValueError."""
    try:
        numeric_value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("valor nao numerico") from exc
    if not math.isfinite(numeric_value):
        raise ValueError("valor nao finito")

    expected = CANONICAL_UNITS.get(canonical_parameter)
    if expected is None:
        if not source_unit:
            raise ValueError("unidade de origem desconhecida")
        return numeric_value, source_unit, None, None

    dimension, target_unit = expected
    source_unit = (source_unit or "").strip()
    if not source_unit:
        raise ValueError("unidade de origem desconhecida")
    if source_unit in IDENTITY_UNITS.get(canonical_parameter, set()):
        return numeric_value, source_unit, None, None
    if source_unit == target_unit:
        return numeric_value, target_unit, None, None
    rule = CONVERSION_TABLE.get((dimension, source_unit, target_unit))
    if rule is None:
        raise ValueError(
            f"conversao nao cadastrada ou grandeza incompativel: {source_unit} -> {target_unit}"
        )
    return rule.apply(numeric_value), target_unit, rule.factor, rule.offset
