"""Cached, unsupervised anomaly detection for machine telemetry."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

import numpy as np
from sklearn.ensemble import IsolationForest

from api_tcc.models import LeituraTelemetria


FEATURES = ("temperatura", "vibracao", "rpm")
MINIMUM_TRAINING_READINGS = 100
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
    """Process-local registry; models are trained once per machine lifecycle."""

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

        rows = LeituraTelemetria.objects.filter(
            machine__external_code=key,
        ).values(*FEATURES)
        history = [
            [float(row[feature]) if row[feature] is not None else 0.0 for feature in FEATURES]
            for row in rows.iterator()
        ]
        state = _DetectorState(features=history)
        self._states[key] = state
        return state

    def record_reading(self, machine_id: str, reading: dict) -> None:
        with self._lock:
            state = self.get_or_create(machine_id)
            history = np.asarray(state.features, dtype=float)
            state.features.append(_feature_vector(reading, history))


REGISTRY = AnomalyDetectorRegistry()


def detect_anomaly(machine_id: str, current_reading: dict) -> AnomalyResult:
    """Return a normalized anomaly result without loading models from disk."""
    with REGISTRY._lock:
        state = REGISTRY.get_or_create(machine_id)
        history = np.asarray(state.features, dtype=float)
        vector = _feature_vector(current_reading, history)

        if len(history) < MINIMUM_TRAINING_READINGS:
            result = _detect_with_zscore(vector, history)
        else:
            result = _detect_with_isolation_forest(vector, history, state)

        return result


def _feature_vector(reading: dict, history: np.ndarray) -> list[float]:
    means = history.mean(axis=0) if len(history) else np.zeros(len(FEATURES))
    return [
        float(reading.get(feature))
        if reading.get(feature) is not None
        else float(means[index])
        for index, feature in enumerate(FEATURES)
    ]


def _detect_with_zscore(vector: list[float], history: np.ndarray) -> AnomalyResult:
    if len(history) < 2:
        return _result(False, 0.0, "COLD_START_ZSCORE", FEATURES[0], "Sem baseline historico suficiente.")

    means = history.mean(axis=0)
    deviations = history.std(axis=0)
    deviations = np.where(deviations > 1e-9, deviations, 1.0)
    z_scores = np.abs((np.asarray(vector) - means) / deviations)
    index = int(np.argmax(z_scores))
    z_score = float(z_scores[index])
    score = min(max((z_score - 2.5) / 1.5, 0.0), 1.0)
    feature = FEATURES[index]
    direction = "acima" if vector[index] >= means[index] else "abaixo"
    explanation = (
        f"{feature} {z_score:.1f}x {direction} do desvio padrão histórico "
        f"(Atual: {vector[index]:.2f}, Média: {means[index]:.2f})"
    )
    return _result(score >= ANOMALY_THRESHOLD, score, "COLD_START_ZSCORE", feature, explanation)


def _detect_with_isolation_forest(
    vector: list[float], history: np.ndarray, state: _DetectorState
) -> AnomalyResult:
    if state.model is None:
        state.scale_mean = history.mean(axis=0)
        state.scale_std = np.where(history.std(axis=0) > 1e-9, history.std(axis=0), 1.0)
        scaled_history = (history - state.scale_mean) / state.scale_std
        state.model = IsolationForest(contamination=0.05, random_state=42)
        state.model.fit(scaled_history)
        state.training_scores = state.model.decision_function(scaled_history)

    if np.all(history.std(axis=0) < 1e-9):
        distance = float(np.max(np.abs(np.asarray(vector) - history[0])))
        if distance < 1e-9:
            return _result(False, 0.0, "ISOLATION_FOREST", FEATURES[0], "Leitura coincide com o baseline constante.")

    scaled_vector = (np.asarray(vector) - state.scale_mean) / state.scale_std
    current_score = float(state.model.decision_function([scaled_vector])[0])
    scores = state.training_scores
    threshold = float(np.percentile(scores, 5)) if scores is not None else 0.0
    minimum = float(scores.min()) if scores is not None else threshold - 1.0
    denominator = max(threshold - minimum, 1e-9)
    normalized = min(max((threshold - current_score) / denominator, 0.0), 1.0)
    distance_score = min(float(np.max(np.abs(scaled_vector))) / 6.0, 1.0)
    normalized = max(normalized, distance_score)
    if state.model.predict([scaled_vector])[0] == -1:
        normalized = max(normalized, ANOMALY_THRESHOLD)

    means = history.mean(axis=0)
    deviations = np.where(history.std(axis=0) > 1e-9, history.std(axis=0), 1.0)
    index = int(np.argmax(np.abs((np.asarray(vector) - means) / deviations)))
    feature = FEATURES[index]
    explanation = (
        f"Isolation Forest identificou padrão atípico em {feature} "
        f"(Atual: {vector[index]:.2f}, Média: {means[index]:.2f})"
    )
    return _result(
        normalized >= ANOMALY_THRESHOLD,
        normalized,
        "ISOLATION_FOREST",
        feature,
        explanation,
    )


def _result(is_anomaly, score, method, feature, explanation) -> AnomalyResult:
    return AnomalyResult(
        is_anomaly=bool(is_anomaly),
        anomaly_score=round(float(min(max(score, 0.0), 1.0)), 4),
        detection_method=method,
        contributing_feature=feature,
        explanation=explanation,
    )
