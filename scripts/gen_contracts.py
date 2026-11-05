"""Gera artefatos derivados do contrato v1, sem rede ou dependências externas."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "contracts" / "severity.v1.json"
TS_TARGET = ROOT / "frontend-next" / "src" / "lib" / "metricThresholds.ts"


def load_contract() -> dict:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    if data.get("schema") != "severity.v1" or set(data.get("metrics", {})) != {"temperatura", "vibracao", "rpm"}:
        raise ValueError("contrato inválido: schema ou métricas obrigatórias ausentes")
    for name, metric in data["metrics"].items():
        if not isinstance(metric.get("range"), list) or len(metric["range"]) != 2:
            raise ValueError(f"contrato inválido: range de {name}")
        if "critico" not in metric and metric.get("severity") != "dependente_de_regime":
            raise ValueError(f"contrato inválido: regra de severidade de {name}")
    return data


def render_ts(data: dict) -> str:
    metrics = data["metrics"]
    rows = []
    for name in ("temperatura", "vibracao", "rpm"):
        metric = metrics[name]
        alert = json.dumps(metric.get("atencao")) if "atencao" in metric else "null"
        critical = json.dumps(metric.get("critico")) if "critico" in metric else "null"
        unit = json.dumps(metric["unit"])
        severity = "'fixed'" if "critico" in metric else "'dependente_de_regime'"
        rows.append(f"  {name}: {{ alert: {alert}, critical: {critical}, unit: {unit}, higherIsWorse: true, min: {metric['range'][0]}, max: {metric['range'][1]}, severity: {severity} }},")
    return ("""/** Generated from contracts/severity.v1.json. Do not edit by hand. */
export type MetricKey = 'temperatura' | 'vibracao' | 'rpm';
export type MetricThresholds = {
  alert: number | null;
  critical: number | null;
  unit: string;
  higherIsWorse: boolean;
  min: number;
  max: number;
  severity: 'fixed' | 'dependente_de_regime';
};
export const METRIC_THRESHOLDS: Record<MetricKey, MetricThresholds> = {
""" + "\n".join(rows) + "\n};\n"
    + """
export function visibleThresholds(values: number[], key: MetricKey) {
  const config = METRIC_THRESHOLDS[key];
  const finite = values.filter(Number.isFinite);
  if (!finite.length) return { config, alert: null as number | null, critical: null as number | null };
  const min = Math.min(...finite), max = Math.max(...finite);
  const span = max - min || Math.abs(max) * 0.2 || 1;
  const inWindow = (value: number | null) => value !== null && value >= min - span * 1.5 && value <= max + span * 1.5;
  return { config, alert: inWindow(config.alert) ? config.alert : null, critical: inWindow(config.critical) ? config.critical : null };
}
""")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = load_contract()
    expected = render_ts(data)
    current = TS_TARGET.read_text(encoding="utf-8") if TS_TARGET.exists() else ""
    if args.check:
        if current != expected:
            print(f"desatualizado: {TS_TARGET}")
            return 1
        print(f"ok: {TS_TARGET}")
        return 0
    TS_TARGET.write_text(expected, encoding="utf-8", newline="\n")
    print(f"gerado: {TS_TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
