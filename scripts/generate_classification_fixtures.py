"""Generate or check shared severity golden files from severity.v1.json."""

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts/severity.v1.json"
FIXTURE_PATH = ROOT / "contracts/fixtures/classificacao.json"
def metric_severity(metric: dict, value: float) -> str:
    if value >= metric["critico"]:
        return "CRITICO"
    if value >= metric["atencao"]:
        return "ATENCAO"
    return "NORMAL"


def expected_class(contract: dict, severity: str, quality: str, delayed: bool) -> str:
    rules = contract["transmission_class"]
    if rules != {
        "A": "severidade == CRITICO",
        "B": "severidade == ATENCAO OR evidence_quality != boa OR dado_atrasado",
        "C": "caso contrario",
    }:
        raise ValueError("Regras de transmission_class não reconhecidas pelo gerador")
    if severity == "CRITICO":
        return "A"
    if severity == "ATENCAO" or quality != "boa" or delayed:
        return "B"
    return "C"


def build_case(contract: dict, case_id: str, temperature: float, vibration: float,
               quality: str = "boa", delayed: bool = False) -> dict:
    metrics = contract["metrics"]
    temperature_severity = metric_severity(metrics["temperatura"], temperature)
    vibration_severity = metric_severity(metrics["vibracao"], vibration)
    severity_order = contract["severity_order"]
    ranks = {severity: index for index, severity in enumerate(severity_order)}
    severity = max((temperature_severity, vibration_severity), key=ranks.__getitem__)
    return {
        "id": case_id,
        "temperatura": temperature,
        "vibracao": vibration,
        "vibracao_unit": contract["metrics"]["vibracao"]["unit"],
        "evidence_quality": quality,
        "atrasado": delayed,
        "severidade_temperatura": temperature_severity,
        "severidade_vibracao": vibration_severity,
        "severidade": severity,
        "classe": expected_class(contract, severity, quality, delayed),
    }


def generate(contract: dict) -> list[dict]:
    cases = []
    metrics = contract["metrics"]
    adjacent = Decimal("0.001")  # Explicit three-decimal JSON step, stable around one-decimal thresholds.
    for metric_name in ("temperatura", "vibracao"):
        metric = metrics[metric_name]
        other_name = "vibracao" if metric_name == "temperatura" else "temperatura"
        other_normal = float(metrics[other_name]["range"][0])
        for threshold_name in ("atencao", "critico"):
            threshold = Decimal(str(metric[threshold_name]))
            for label, delta in (("abaixo", -adjacent), ("limite", Decimal(0)), ("acima", adjacent)):
                boundary_value = float(threshold + delta)
                values = {metric_name: boundary_value, other_name: other_normal}
                cases.append(build_case(
                    contract,
                    f"{metric_name}_{threshold_name}_{label}",
                    values["temperatura"],
                    values["vibracao"],
                ))

    for metric_name in ("temperatura", "vibracao"):
        metric = metrics[metric_name]
        other_name = "vibracao" if metric_name == "temperatura" else "temperatura"
        other_normal = float(metrics[other_name]["range"][0])
        for bound_name, bound_value in zip(("minimo", "maximo"), metric["range"]):
            values = {metric_name: float(bound_value), other_name: other_normal}
            cases.append(build_case(contract, f"{metric_name}_{bound_name}",
                                    values["temperatura"], values["vibracao"]))

    cases.extend([
        build_case(contract, "temperatura_critica_vibracao_normal",
                   metrics["temperatura"]["critico"], metrics["vibracao"]["range"][0]),
        build_case(contract, "vibracao_critica_temperatura_normal",
                   metrics["temperatura"]["range"][0], metrics["vibracao"]["critico"]),
        build_case(contract, "ambas_atencao", metrics["temperatura"]["atencao"], metrics["vibracao"]["atencao"]),
        build_case(contract, "ambas_criticas", metrics["temperatura"]["critico"], metrics["vibracao"]["critico"]),
    ])
    for quality in contract["evidence_quality"]:
        cases.append(build_case(contract, f"qualidade_{quality}", 0.0, 0.0, quality))
    cases.append(build_case(contract, "normal_atrasado", 0.0, 0.0, delayed=True))

    for metric_name in ("temperatura", "vibracao"):
        metric = metrics[metric_name]
        other_name = "vibracao" if metric_name == "temperatura" else "temperatura"
        other_normal = float(metrics[other_name]["range"][0])
        invalid_value = float(metric["range"][0]) - 0.001
        values = {metric_name: invalid_value, other_name: other_normal}
        cases.append({
            "id": f"{metric_name}_fora_do_range",
            "temperatura": values["temperatura"],
            "vibracao": values["vibracao"],
            "vibracao_unit": metrics["vibracao"]["unit"],
            "evidence_quality": "boa",
            "atrasado": False,
            "expected_error": "range",
        })
    return cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the versioned fixture is stale")
    args = parser.parse_args()
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    serialized = json.dumps(generate(contract), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not FIXTURE_PATH.exists() or FIXTURE_PATH.read_text(encoding="utf-8") != serialized:
            print("classificacao.json está desatualizado; execute o gerador localmente e revise o diff", file=sys.stderr)
            return 1
        print(f"Fixture verificada: {FIXTURE_PATH.relative_to(ROOT)}")
        return 0
    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.write_text(serialized, encoding="utf-8")
    print(f"Fixture gerada: {FIXTURE_PATH.relative_to(ROOT)} ({len(generate(contract))} casos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
