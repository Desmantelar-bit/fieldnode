"""Detecção não supervisionada de anomalias em telemetria por máquina."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

import numpy as np
from django.utils import timezone
from sklearn.ensemble import IsolationForest

from api_tcc.ia.model_registry import ModelArtifactError, ModelNotFoundError, registry
from api_tcc.models import LeituraTelemetria

FEATURES = ("temperatura", "vibracao", "rpm")
MINIMUM_TRAINING_READINGS = 100
CONTAMINATION = 0.05
RANDOM_STATE = 42
MODEL_VERSION = "anomalia-v1"
ANOMALY_THRESHOLD = 0.70


@dataclass(frozen=True)
class AnomalyResult:
    is_anomaly: bool
    anomaly_score: float
    detection_method: str
    contributing_feature: str
    explanation: str


@dataclass
class _DetectorState:
    features: list[list[float]]
    model: IsolationForest | None = None
    training_scores: np.ndarray | None = None
    scale_mean: np.ndarray | None = None
    scale_std: np.ndarray | None = None


class AnomalyDetectorRegistry:
    """Mantém leituras em processo; o modelo treinado fica no registry em disco."""

    def __init__(self):
        self._states: dict[str, _DetectorState] = {}
        self._lock = RLock()

    def clear(self) -> None:
        with self._lock:
            self._states.clear()

    def get_or_create(self, machine_id: str) -> _DetectorState:
        key = str(machine_id)
        state = self._states.get(key)
        if state is not None:
            return state
        rows = LeituraTelemetria.objects.filter(machine__external_code=key).values(*FEATURES)
        history = [[float(row[feature]) if row[feature] is not None else 0.0 for feature in FEATURES] for row in rows.iterator()]
        state = _DetectorState(features=history)
        self._states[key] = state
        return state

    def record_reading(self, machine_id: str, reading: dict) -> None:
        with self._lock:
            state = self.get_or_create(machine_id)
            state.features.append(_feature_vector(reading, np.asarray(state.features, dtype=float)))


REGISTRY = AnomalyDetectorRegistry()


def _train_and_persist(machine_id: str, history: np.ndarray) -> tuple[IsolationForest, dict]:
    if len(history) < MINIMUM_TRAINING_READINGS:
        raise ValueError(f"amostras insuficientes: {len(history)}; mínimo: {MINIMUM_TRAINING_READINGS}")
    mean = history.mean(axis=0)
    std = np.where(history.std(axis=0) > 1e-9, history.std(axis=0), 1.0)
    model = IsolationForest(contamination=CONTAMINATION, random_state=RANDOM_STATE)
    model.fit((history - mean) / std)
    metadata = {
        "treinado_em": timezone.now().isoformat(),
        "contamination": float(model.contamination),
        "n_amostras": int(len(history)),
        "versao": MODEL_VERSION,
        "machine_id": str(machine_id),
        "features": list(FEATURES),
        "random_state": RANDOM_STATE,
        "algoritmo": "IsolationForest",
        "scale_mean": mean.tolist(),
        "scale_std": std.tolist(),
    }
    registry.save_model(machine_id, model, metadata)
    return model, metadata


def train_model_for_machine(machine_id: str) -> tuple[IsolationForest, dict]:
    rows = LeituraTelemetria.objects.filter(machine__external_code=str(machine_id)).values(*FEATURES)
    data = [[float(row[feature]) if row[feature] is not None else 0.0 for feature in FEATURES] for row in rows.iterator()]
    return _train_and_persist(str(machine_id), np.asarray(data, dtype=float))


def _load_persisted(machine_id: str, history: np.ndarray) -> tuple[IsolationForest, dict]:
    try:
        model, metadata = registry.load_latest_model(machine_id)
    except ModelNotFoundError:
        return _train_and_persist(machine_id, history)
    except ModelArtifactError:
        raise
    if tuple(metadata.get("features", FEATURES)) != FEATURES:
        raise ModelArtifactError("features do artefato não são compatíveis com o detector")
    if metadata.get("n_amostras", 0) < MINIMUM_TRAINING_READINGS:
        raise ModelArtifactError("artefato possui quantidade de amostras insuficiente")
    try:
        metadata["scale_mean"]
        metadata["scale_std"]
    except KeyError as exc:
        raise ModelArtifactError("metadata de escala ausente no artefato") from exc
    return model, metadata


def detect_anomaly(machine_id: str, current_reading: dict) -> AnomalyResult:
    with REGISTRY._lock:
        state = REGISTRY.get_or_create(machine_id)
        history = np.asarray(state.features, dtype=float)
        vector = _feature_vector(current_reading, history)
        if len(history) < MINIMUM_TRAINING_READINGS:
            return _detect_with_zscore(vector, history)
        if state.model is None:
            state.model, metadata = _load_persisted(machine_id, history)
            state.scale_mean = np.asarray(metadata["scale_mean"], dtype=float)
            state.scale_std = np.asarray(metadata["scale_std"], dtype=float)
            state.training_scores = state.model.decision_function((history - state.scale_mean) / state.scale_std)
        return _detect_with_isolation_forest(vector, history, state)


def _feature_vector(reading: dict, history: np.ndarray) -> list[float]:
    means = history.mean(axis=0) if len(history) else np.zeros(len(FEATURES))
    return [float(reading.get(feature)) if reading.get(feature) is not None else float(means[index]) for index, feature in enumerate(FEATURES)]


def _detect_with_zscore(vector: list[float], history: np.ndarray) -> AnomalyResult:
    if len(history) < 2:
        return _result(False, 0.0, "COLD_START_ZSCORE", FEATURES[0], "Sem baseline historico suficiente.")
    means = history.mean(axis=0)
    deviations = np.where(history.std(axis=0) > 1e-9, history.std(axis=0), 1.0)
    z_scores = np.abs((np.asarray(vector) - means) / deviations)
    index = int(np.argmax(z_scores))
    z_score = float(z_scores[index])
    score = min(max((z_score - 2.5) / 1.5, 0.0), 1.0)
    feature = FEATURES[index]
    direction = "acima" if vector[index] >= means[index] else "abaixo"
    explanation = f"{feature} {z_score:.1f}x {direction} do desvio padrao historico (Atual: {vector[index]:.2f}, Media: {means[index]:.2f})"
    return _result(score >= ANOMALY_THRESHOLD, score, "COLD_START_ZSCORE", feature, explanation)


def _detect_with_isolation_forest(vector: list[float], history: np.ndarray, state: _DetectorState) -> AnomalyResult:
    assert state.model is not None and state.scale_mean is not None and state.scale_std is not None
    if np.all(history.std(axis=0) < 1e-9) and np.max(np.abs(np.asarray(vector) - history[0])) < 1e-9:
        return _result(False, 0.0, "ISOLATION_FOREST", FEATURES[0], "Leitura coincide com o baseline constante.")
    scaled_vector = (np.asarray(vector) - state.scale_mean) / state.scale_std
    current_score = float(state.model.decision_function([scaled_vector])[0])
    scores = state.training_scores
    threshold = float(np.percentile(scores, 5)) if scores is not None else 0.0
    minimum = float(scores.min()) if scores is not None else threshold - 1.0
    normalized = min(max((threshold - current_score) / max(threshold - minimum, 1e-9), 0.0), 1.0)
    normalized = max(normalized, min(float(np.max(np.abs(scaled_vector))) / 6.0, 1.0))
    if state.model.predict([scaled_vector])[0] == -1:
        normalized = max(normalized, ANOMALY_THRESHOLD)
    means = history.mean(axis=0)
    deviations = np.where(history.std(axis=0) > 1e-9, history.std(axis=0), 1.0)
    index = int(np.argmax(np.abs((np.asarray(vector) - means) / deviations)))
    feature = FEATURES[index]
    explanation = f"Isolation Forest identificou padrao atipico em {feature} (Atual: {vector[index]:.2f}, Media: {means[index]:.2f})"
    return _result(normalized >= ANOMALY_THRESHOLD, normalized, "ISOLATION_FOREST", feature, explanation)


def _result(is_anomaly, score, method, feature, explanation) -> AnomalyResult:
    return AnomalyResult(bool(is_anomaly), round(float(min(max(score, 0.0), 1.0)), 4), method, feature, explanation)
