"""Inferência determinística do regime operacional da máquina.

Os cortes são heurísticas de bancada. Eles não representam calibração por
modelo de máquina e não devem ser tratados como diagnóstico mecânico.
"""

from __future__ import annotations

from typing import Any

REGIMES = ("desligada", "marcha_lenta", "trabalhando", "deslocamento", "desconhecido")


def inferir_regime(rpm: float | None, velocidade_kmh: float | None = None) -> str:
    """Classifica uma leitura sem inventar estado quando RPM não existe."""
    if rpm is None:
        return "desconhecido"
    try:
        rpm_value = float(rpm)
        speed_value = 0.0 if velocidade_kmh is None else float(velocidade_kmh)
    except (TypeError, ValueError):
        return "desconhecido"
    if rpm_value < 300:
        return "desligada"
    if rpm_value < 1000 and speed_value < 1:
        return "marcha_lenta"
    if speed_value > 8 and rpm_value < 1800:
        return "deslocamento"
    return "trabalhando"


def regime_de_leitura(leitura: Any) -> str:
    return inferir_regime(
        leitura.get("rpm") if isinstance(leitura, dict) else getattr(leitura, "rpm", None),
        leitura.get("velocidade_kmh") if isinstance(leitura, dict) else getattr(leitura, "velocidade_kmh", None),
    )
