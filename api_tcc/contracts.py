"""Leitura e semântica do contrato versionado de severidade."""

import json
import math
from functools import lru_cache
from pathlib import Path


class ContractError(ValueError):
    """Entrada incompatível com o contrato de severidade."""


@lru_cache(maxsize=1)
def severity_contract() -> dict:
    path = Path(__file__).resolve().parent.parent / "contracts" / "severity.v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def metric_definition(metric: str) -> dict:
    try:
        return severity_contract()["metrics"][metric]
    except KeyError:
        raise ContractError(f"métrica desconhecida: {metric}") from None


def classify(metric: str, value: float) -> str:
    definition = metric_definition(metric)
    if isinstance(value, bool):
        raise ContractError(f"valor não numérico para {metric}: {value!r}")
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        raise ContractError(f"valor não numérico para {metric}: {value!r}") from None
    if not math.isfinite(numeric):
        raise ContractError(f"valor não finito para {metric}: {value!r}")
    minimum, maximum = definition["range"]
    if not minimum <= numeric <= maximum:
        raise ContractError(f"{metric}={numeric} fora do range [{minimum}, {maximum}]")
    if "critico" not in definition:
        raise ContractError(f"métrica sem classificação fixa: {metric}")
    if numeric >= definition["critico"]:
        return "CRITICO"
    if numeric >= definition["atencao"]:
        return "ATENCAO"
    return "NORMAL"


def transmission_class(severidade: str, evidence_quality: str, atrasado: bool) -> str:
    if severidade not in {"NORMAL", "ATENCAO", "CRITICO"}:
        raise ContractError(f"severidade desconhecida: {severidade!r}")
    if evidence_quality not in set(severity_contract()["evidence_quality"]):
        raise ContractError(f"qualidade de evidência inválida: {evidence_quality!r}")
    if not isinstance(atrasado, bool):
        raise ContractError("atrasado deve ser booleano")
    if severidade == "CRITICO":
        return "A"
    if severidade == "ATENCAO" or evidence_quality != "boa" or atrasado:
        return "B"
    return "C"
