"""Avaliação independente do detector em sinais reais do CWRU Bearing Data Center.

Os arquivos CWRU não são distribuídos pelo repositório. O operador deve baixá-los
da fonte oficial e informar os caminhos explicitamente. O experimento usa o
detector oficial do FieldNode, com um adaptador de features de vibração.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.io import loadmat
from scipy.stats import kurtosis
from sklearn.ensemble import IsolationForest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
try:
    import django
    django.setup()
except Exception:
    pass

from api_tcc.services.anomaly_detection import detect_many_from_history
from .metrics import metricas

FEATURE_NAMES = ("rms", "pico", "curtose_pearson")
RANDOM_STATE = 42
WINDOW_SIZE = 4096
OVERLAP = 0
IF_CONTAMINATION = 0.05
BASELINE_Z_THRESHOLD = 3.0


@dataclass(frozen=True)
class SignalFile:
    path: Path
    label: int


def _numeric_signal(mat: dict) -> np.ndarray:
    candidates = []
    for name, value in mat.items():
        if name.startswith("__"):
            continue
        array = np.asarray(value).squeeze()
        if array.ndim == 1 and array.size > 1000 and np.issubdtype(array.dtype, np.number):
            priority = 0 if name.endswith("_DE_time") else 1 if name.endswith("_FE_time") else 2
            candidates.append((priority, name, array.astype(float)))
    if not candidates:
        raise ValueError("arquivo .mat não contém uma série de vibração numérica reconhecível")
    return min(candidates, key=lambda item: (item[0], item[1]))[2]


def extract_window_features(signal: np.ndarray, *, window_size: int = WINDOW_SIZE, overlap: int = OVERLAP) -> np.ndarray:
    """Extrai RMS, pico e curtose de Pearson; descarta janela incompleta."""
    values = np.asarray(signal, dtype=float).reshape(-1)
    if window_size <= 0 or not 0 <= overlap < window_size:
        raise ValueError("window_size deve ser positivo e overlap deve estar em [0, window_size)")
    step = window_size - overlap
    rows = []
    for start in range(0, len(values) - window_size + 1, step):
        window = values[start:start + window_size]
        if not np.isfinite(window).all():
            continue
        pearson_kurtosis = 3.0 if np.all(window == window[0]) else float(kurtosis(window, fisher=False, bias=False))
        rows.append((np.sqrt(np.mean(window ** 2)), np.max(np.abs(window)), pearson_kurtosis))
    if not rows:
        raise ValueError("sinal não possui uma janela completa e finita")
    return np.asarray(rows, dtype=float)


def load_cwru_files(files: list[SignalFile], *, window_size: int = WINDOW_SIZE, overlap: int = OVERLAP) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Carrega arquivos CWRU, preservando o rótulo fornecido pelo nome do grupo."""
    feature_rows, labels, groups = [], [], []
    for item in files:
        if not item.path.is_file():
            raise FileNotFoundError(f"arquivo CWRU não encontrado: {item.path}")
        features = extract_window_features(_numeric_signal(loadmat(item.path)), window_size=window_size, overlap=overlap)
        feature_rows.append(features)
        labels.extend([item.label] * len(features))
        groups.extend([item.path.name] * len(features))
    return np.vstack(feature_rows), np.asarray(labels, dtype=int), groups


def _fit_if(training: np.ndarray) -> tuple[IsolationForest, dict]:
    mean = training.mean(axis=0)
    std = np.where(training.std(axis=0) > 1e-12, training.std(axis=0), 1.0)
    model = IsolationForest(contamination=IF_CONTAMINATION, random_state=RANDOM_STATE)
    model.fit((training - mean) / std)
    return model, {"scale_mean": mean.tolist(), "scale_std": std.tolist(), "training_scores": model.decision_function((training - mean) / std).tolist(), "model_version": "public-cwru-adapter-v1", "random_state": RANDOM_STATE}


def _baseline(training: np.ndarray, test: np.ndarray) -> np.ndarray:
    mean = training.mean(axis=0)
    std = np.where(training.std(axis=0) > 1e-12, training.std(axis=0), 1.0)
    return (np.abs((test - mean) / std).max(axis=1) >= BASELINE_Z_THRESHOLD)


def evaluate(training: np.ndarray, test: np.ndarray, labels: np.ndarray) -> dict:
    model, metadata = _fit_if(training)
    if_results = detect_many_from_history(training, test, model=model, metadata=metadata, feature_names=FEATURE_NAMES)
    if_pred = [result.is_anomaly for result in if_results]
    baseline_pred = _baseline(training, test).tolist()
    observed_seconds = float(len(test))
    return {"isolation_forest": metricas(if_pred, labels, observed_seconds), "limiar_simples": metricas(baseline_pred, labels, observed_seconds), "config": {"features": FEATURE_NAMES, "window_size": WINDOW_SIZE, "overlap": OVERLAP, "kurtosis": "Pearson, bias=False", "random_state": RANDOM_STATE, "if_contamination": IF_CONTAMINATION, "baseline_z_threshold": BASELINE_Z_THRESHOLD}}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-normal", nargs="+", type=Path, required=True)
    parser.add_argument("--test-normal", nargs="+", type=Path, required=True)
    parser.add_argument("--test-fault", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("docs/evidence/s5/S5-T5_PUBLIC_CWRU_RESULTS.json"))
    args = parser.parse_args()
    train, _, _ = load_cwru_files([SignalFile(path, 0) for path in args.train_normal])
    test_normal, normal_labels, _ = load_cwru_files([SignalFile(path, 0) for path in args.test_normal])
    test_fault, fault_labels, _ = load_cwru_files([SignalFile(path, 1) for path in args.test_fault])
    test = np.vstack([test_normal, test_fault])
    result = evaluate(train, test, np.concatenate([normal_labels, fault_labels]))
    result.update({"dataset": "CWRU Bearing Data Center", "source": "https://engineering.case.edu/bearingdatacenter/download-data-file", "training_files": [{"path": str(p), "sha256": _sha256(p)} for p in args.train_normal], "test_normal_files": [{"path": str(p), "sha256": _sha256(p)} for p in args.test_normal], "test_fault_files": [{"path": str(p), "sha256": _sha256(p)} for p in args.test_fault], "n_training_windows": len(train), "n_test_windows": len(test), "label_definition": "0 normal, 1 bearing fault according to CWRU file group"})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
