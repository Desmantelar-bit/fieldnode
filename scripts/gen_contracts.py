"""Gera artefatos de contrato determinísticos para as linguagens consumidoras."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "contracts" / "severity.v1.json"
TARGET = ROOT / "frontend-next/src/lib/metricThresholds.ts"


def load_contract():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    if data.get("schema") != "severity.v1" or set(data.get("metrics", {})) != {"temperatura", "vibracao", "rpm"}:
        raise ValueError("contrato inválido: schema ou métricas obrigatórias incorretas")
    for key, metric in data["metrics"].items():
        bounds = metric.get("range")
        if not isinstance(bounds, list) or len(bounds) != 2 or bounds[0] >= bounds[1]:
            raise ValueError(f"range inválido para {key}")
        if "critico" in metric and not (bounds[0] <= metric["atencao"] < metric["critico"] <= bounds[1]):
            raise ValueError(f"limiares inválidos para {key}")
    return data


def render(data):
    metrics = data["metrics"]
    rows = []
    for name in ("temperatura", "vibracao", "rpm"):
        m = metrics[name]
        alert = json.dumps(m.get("atencao"))
        critical = json.dumps(m.get("critico"))
        rows.append(f"  {name}: {{ alert: {alert}, critical: {critical}, unit: {json.dumps(m['unit'])}, higherIsWorse: true, min: {m['range'][0]}, max: {m['range'][1]} }},")
    return ("""/** Generated from contracts/severity.v1.json. Do not edit by hand. */
export type MetricKey = 'temperatura' | 'vibracao' | 'rpm';
export type MetricThresholds = { alert: number | null; critical: number | null; unit: string; higherIsWorse: boolean; min: number; max: number };
export const METRIC_THRESHOLDS: Record<MetricKey, MetricThresholds> = {
""" + "\n".join(rows) + "\n};\n" + """
export function visibleThresholds(values: number[], key: MetricKey) {
  const config = METRIC_THRESHOLDS[key];
  const finite = values.filter(Number.isFinite);
  if (!finite.length) return { config, alert: null as number | null, critical: null as number | null };
  const min = Math.min(...finite), max = Math.max(...finite);
  const span = max - min || Math.abs(max) * 0.2 || 1, window = span * 1.5;
  const inWindow = (value: number | null) => value !== null && value >= min - window && value <= max + window;
  return { config, alert: inWindow(config.alert) ? config.alert : null, critical: inWindow(config.critical) ? config.critical : null };
}

export function classifyMetric(key: MetricKey, value: number): 'NORMAL' | 'ATENCAO' | 'CRITICO' {
  const metric = METRIC_THRESHOLDS[key];
  if (!Number.isFinite(value) || value < metric.min || value > metric.max) throw new RangeError(`Valor inválido para ${key}`);
  if (metric.critical !== null && value >= metric.critical) return 'CRITICO';
  if (metric.alert !== null && value >= metric.alert) return 'ATENCAO';
  return 'NORMAL';
}
"""
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="falha se o artefato TypeScript estiver desatualizado")
    args = parser.parse_args()
    expected = render(load_contract())
    if args.check:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"artefato desatualizado: {TARGET.relative_to(ROOT)}")
        print(f"verificado: {TARGET.relative_to(ROOT)}")
    else:
        TARGET.write_text(expected, encoding="utf-8")
        print(f"gerado: {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
