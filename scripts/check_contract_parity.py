"""Varre a paridade entre contrato Python, prioridade da borda e status do front."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from api_tcc.contracts import classify
from simulators.edge_client import classify_priority

TYPESCRIPT = ROOT / "frontend-next" / "node_modules" / "typescript"
NODE_RUNNER = r"""
const fs = require('fs');
const ts = require(process.argv[1]);
const root = process.argv[2];

function loadTypeScript(relativePath, resolveImport) {
    const source = fs.readFileSync(`${root}/frontend-next/${relativePath}`, 'utf8');
  const javascript = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
  }).outputText;
  const module = { exports: {} };
  const localRequire = (name) => resolveImport(name) ?? require(name);
  new Function('require', 'module', 'exports', javascript)(localRequire, module, module.exports);
  return module.exports;
}

const thresholds = loadTypeScript('src/lib/metricThresholds.ts', () => undefined);
const metrics = loadTypeScript('src/lib/metrics.ts', (name) =>
  name === '@/lib/metricThresholds' ? thresholds : undefined
);
const samples = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(samples.map(({ metric, value }) =>
  metrics.statusOf(value, metric)
)));
"""


def build_samples() -> list[dict[str, float | str]]:
    samples: list[dict[str, float | str]] = []
    samples.extend(
        {"metric": "temperatura", "value": step / 10}
        for step in range(1501)
    )
    samples.extend(
        {"metric": "vibracao", "value": step / 20}
        for step in range(201)
    )
    return samples


def frontend_statuses(samples: list[dict[str, float | str]]) -> list[str]:
    result = subprocess.run(
        ["node", "-e", NODE_RUNNER, str(TYPESCRIPT), str(ROOT)],
        input=json.dumps(samples),
        text=True,
        capture_output=True,
        check=False,
        cwd=ROOT,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Node falhou sem informar stderr")
    return json.loads(result.stdout)


def main() -> int:
    samples = build_samples()
    frontend = frontend_statuses(samples)
    mismatches = []
    totals = {"temperatura": 0, "vibracao": 0}

    for sample, frontend_status in zip(samples, frontend, strict=True):
        metric = str(sample["metric"])
        value = float(sample["value"])
        backend = classify(metric, value)
        edge = classify_priority(
            {
                "temperatura": value if metric == "temperatura" else 70,
                "vibracao": value if metric == "vibracao" else 0,
            }
        )
        expected_edge = {"NORMAL": "C", "ATENCAO": "B", "CRITICO": "A"}[backend]
        expected_frontend = {
            "NORMAL": "normal",
            "ATENCAO": "atencao",
            "CRITICO": "critico",
        }[backend]
        totals[metric] += 1
        if edge != expected_edge or frontend_status != expected_frontend:
            mismatches.append(
                {
                    "metric": metric,
                    "value": value,
                    "backend": backend,
                    "edge": edge,
                    "frontend": frontend_status,
                }
            )

    print(f"temperatura: {totals['temperatura']} pontos; divergências: "
          f"{sum(item['metric'] == 'temperatura' for item in mismatches)}")
    print(f"vibracao: {totals['vibracao']} pontos; divergências: "
          f"{sum(item['metric'] == 'vibracao' for item in mismatches)}")
    print(f"total: {len(samples)} pontos; divergências: {len(mismatches)}")
    if mismatches:
        print(json.dumps(mismatches[:20], ensure_ascii=False, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())