"""Executa o benchmark sintético fixado sem usar seus rótulos no treino."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
from sklearn.ensemble import IsolationForest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
try:
    import django
    django.setup()
except Exception:
    pass

from api_tcc.services.anomaly_detection import detect_many_from_history
from .scenarios import SCENARIO_FACTORIES, _base
from .metrics import metricas, tempo_ate_deteccao

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "ml" / "eval" / "fixtures" / "benchmark_v1.json"
REPORT = ROOT / "docs" / "AVALIACAO_ANOMALIA.md"
SEEDS = tuple(range(20))


def _train(seed):
    training = _base(10_000 + seed, 500)
    values = training[["temperatura", "vibracao", "rpm"]].to_numpy(float)
    mean = values.mean(axis=0)
    std = np.where(values.std(axis=0) > 1e-9, values.std(axis=0), 1.0)
    model = IsolationForest(n_estimators=20, contamination=0.05, random_state=42)
    model.fit((values - mean) / std)
    dataset_hash = hashlib.sha256(values.tobytes()).hexdigest()
    scores = model.decision_function((values - mean) / std)
    return values, model, {"scale_mean": mean.tolist(), "scale_std": std.tolist(), "training_scores": scores.tolist(),
                           "model_version": "synthetic-if-v1", "dataset_hash": dataset_hash}


def evaluate_one(factory, seed):
    scenario = factory(seed)
    history, model, metadata = _train(seed)
    readings = scenario.serie[["temperatura", "vibracao", "rpm"]].to_numpy(float)
    detected = detect_many_from_history(history, readings, model=model, metadata=metadata)
    results = []
    for row, result in zip(scenario.serie.itertuples(index=False), detected):
        results.append({"event_time": row.event_time, "is_anomaly": result.is_anomaly,
                        "score": result.anomaly_score, "method": result.detection_method,
                        "model_version": metadata["model_version"]})
    observed = (scenario.serie.event_time.max() - scenario.serie.event_time.min()).total_seconds()
    values = metricas([r["is_anomaly"] for r in results], scenario.rotulo, observed)
    values["tempo_ate_deteccao_s"] = tempo_ate_deteccao(results, scenario.rotulo)
    values.update(nome=scenario.nome, esperado=scenario.esperado,
                  detection_method=results[0]["method"], model_version=metadata["model_version"])
    return values


def _fmt(value):
    return "n/d" if value is None else f"{value:.3f}"


def main():
    results = [evaluate_one(factory, seed) for factory in SCENARIO_FACTORIES for seed in SEEDS]
    groups = {}
    for item in results:
        groups.setdefault(item["nome"], []).append(item)
    lines = ["# Avaliação de anomalias", "", "**Métrica de teste sintético, não de campo.**", "",
             "Benchmark fixado: `benchmark_v1`; 8 cenários × 20 sementes.",
             "O treino usa uma série normal independente por semente e não lê os rótulos de avaliação.", "",
             "| Cenário | Execuções | TP | FP | FN | TN | Precisão média | Recall médio | F1 médio | FP/h média | Método | Versão |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|"]
    for name, items in groups.items():
        def avg(key):
            values = [x[key] for x in items if x[key] is not None]
            return None if not values else float(np.mean(values))
        lines.append(f"| {name} | {len(items)} | {sum(x['tp'] for x in items)} | {sum(x['fp'] for x in items)} | {sum(x['fn'] for x in items)} | {sum(x['tn'] for x in items)} | {_fmt(avg('precision'))} | {_fmt(avg('recall'))} | {_fmt(avg('f1'))} | {_fmt(avg('false_positive_per_hour'))} | {items[0]['detection_method']} | {items[0]['model_version']} |")
    lines.extend(["", "## Limitações", "", "Os dados são sintéticos e servem para verificar determinismo, contrato e cálculo das métricas. Não são validação de campo, não medem falha mecânica e não autorizam afirmar previsão de falhas.", "", "A lacuna de comunicação é tratada como caso de observabilidade; ausência de leitura não é convertida silenciosamente em normalidade."])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Relatório escrito em {REPORT}")


if __name__ == "__main__":
    main()
