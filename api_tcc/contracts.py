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


def classify(metric: str, value: float) -> str:
    contract = severity_contract()
    if metric not in contract["metrics"]:
        raise ContractError(f"métrica desconhecida: {metric}")
    if isinstance(value, bool):
        raise ContractError(f"valor não numérico para {metric}: {value!r}")
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        raise ContractError(f"valor não numérico para {metric}: {value!r}") from None
    if not math.isfinite(numeric):
        raise ContractError(f"valor não finito para {metric}: {value!r}")

    metric_contract = contract["metrics"][metric]
    minimum, maximum = metric_contract["range"]
    if not minimum <= numeric <= maximum:
        raise ContractError(
            f"{metric}={numeric} fora do range do contrato [{minimum}, {maximum}]"
        )
    if "critico" not in metric_contract:
        raise ContractError(
            f"métrica sem classificação fixa: {metric} ({metric_contract.get('severity')})"
        )
    if numeric >= metric_contract["critico"]:
        return "CRITICO"
    if numeric >= metric_contract["atencao"]:
        return "ATENCAO"
    return "NORMAL"


def transmission_class(severidade: str, evidence_quality: str, atrasado: bool) -> str:
    contract = severity_contract()
    if severidade not in {"NORMAL", "ATENCAO", "CRITICO"}:
        raise ContractError(f"severidade desconhecida: {severidade!r}")
    if evidence_quality not in set(contract["evidence_quality"]):
        raise ContractError(f"qualidade de evidência inválida: {evidence_quality!r}")
    if not isinstance(atrasado, bool):
        raise ContractError(f"atrasado deve ser booleano: {atrasado!r}")
    if severidade == "CRITICO":
        return "A"
    if severidade == "ATENCAO" or evidence_quality != "boa" or atrasado:
        return "B"
    return "C"


def metric_definition(metric: str) -> dict:
    try:
        return severity_contract()["metrics"][metric]
    except KeyError:
        raise ContractError(f"métrica desconhecida: {metric}") from None
