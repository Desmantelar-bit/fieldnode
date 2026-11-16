"""Detecção não supervisionada de anomalias em telemetria por máquina."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from datetime import timedelta
from threading import RLock

import numpy as np
import joblib
import hashlib
from django.utils import timezone
from sklearn.ensemble import IsolationForest

from api_tcc.ia.model_registry import ModelArtifactError, ModelNotFoundError, registry
from api_tcc.models import Event, LeituraTelemetria, Machine
from api_tcc.services.regime import inferir_regime

FEATURES = ("temperatura", "vibracao", "rpm")
MINIMUM_TRAINING_READINGS = 100
CONTAMINATION = 0.05
RANDOM_STATE = 42
MODEL_VERSION = "anomalia-v1"
ANOMALY_THRESHOLD = 0.70

TRAINING_POLICY = {
    "minimum_readings": MINIMUM_TRAINING_READINGS,
    "minimum_coverage_hours": 8.0,
    "minimum_regimes": 2,
    "minimum_average_trust": 0.8,
    "training_regime": "trabalhando",
}


@dataclass(frozen=True)
class AnomalyResult:
    is_anomaly: bool
    anomaly_score: float
    detection_method: str
    contributing_feature: str | None
    explanation: str
    model_version: str | None = None
    detection_status: str = "concluido"
    data_quality: dict[str, Any] | None = None


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

    def get_or_create(self, machine_id: str, regime: str = "trabalhando") -> _DetectorState:
        key = f"{machine_id}|{regime}"
        state = self._states.get(key)
        if state is not None:
            return state
        rows = LeituraTelemetria.objects.filter(machine__external_code=str(machine_id), regime=regime).values(*FEATURES)
        # Leituras históricas anteriores à S5-T3 não possuíam regime; o
        # fallback mantém compatibilidade sem misturar regimes novos.
        if not rows.exists() and regime == "trabalhando":
            rows = LeituraTelemetria.objects.filter(
                machine__external_code=str(machine_id), regime="desconhecido"
            ).values(*FEATURES)
        history = [[float(row[feature]) if row[feature] is not None else 0.0 for feature in FEATURES] for row in rows.iterator()]
        state = _DetectorState(features=history)
        self._states[key] = state
        return state

    def record_reading(self, machine_id: str, reading: dict) -> None:
        with self._lock:
            regime = reading.get("regime") or inferir_regime(reading.get("rpm"), reading.get("velocidade_kmh"))
            state = self.get_or_create(machine_id, regime)
            state.features.append(_feature_vector(reading, np.asarray(state.features, dtype=float)))


REGISTRY = AnomalyDetectorRegistry()


def _training_readings(machine):
    """Retorna somente leituras rastreáveis e com qualidade conhecida."""
    return LeituraTelemetria.objects.filter(
        machine=machine,
        timestamp__isnull=False,
        trust_score__isnull=False,
        evidence_quality="boa",
    ).order_by("timestamp")


def resumo_elegibilidade(machine) -> dict[str, Any]:
    readings = list(_training_readings(machine))
    timestamps = [r.timestamp for r in readings if r.timestamp is not None]
    coverage_hours = 0.0
    if len(timestamps) >= 2:
        coverage_hours = max(0.0, (max(timestamps) - min(timestamps)).total_seconds() / 3600.0)
    regimes = sorted({r.regime for r in readings if r.regime != "desconhecido"})
    trusts = [float(r.trust_score) for r in readings if r.trust_score is not None]
    avg_trust = sum(trusts) / len(trusts) if trusts else None
    critical_open = Event.objects.filter(
        machine=machine,
        severidade=Event.Severidade.CRITICO,
        status=Event.Status.ABERTO,
        criado_em__gte=(timezone.now() - timedelta(hours=max(coverage_hours, 1.0))),
    ).exists()
    return {
        "eligible_readings": len(readings),
        "coverage_hours": round(coverage_hours, 4),
        "regimes": regimes,
        "average_trust": None if avg_trust is None else round(avg_trust, 4),
        "critical_event_open": critical_open,
    }


def pode_treinar(machine) -> tuple[bool, list[str]]:
    """Decide se há evidência suficiente para um modelo individual.

    A diversidade de regimes valida a cobertura operacional, mas o treino do
    modelo ``trabalhando`` usa apenas esse regime e ``evidence_quality=boa``.
    """
    summary = resumo_elegibilidade(machine)
    reasons: list[str] = []
    if summary["eligible_readings"] < TRAINING_POLICY["minimum_readings"]:
        reasons.append("INSUFFICIENT_READINGS")
    if summary["coverage_hours"] < TRAINING_POLICY["minimum_coverage_hours"]:
        reasons.append("COVERAGE_BELOW_MINIMUM")
    if len(summary["regimes"]) < TRAINING_POLICY["minimum_regimes"]:
        reasons.append("INSUFFICIENT_REGIMES")
    if summary["average_trust"] is None:
        reasons.append("TRUST_UNAVAILABLE")
    elif summary["average_trust"] < TRAINING_POLICY["minimum_average_trust"]:
        reasons.append("AVERAGE_TRUST_BELOW_MINIMUM")
    if summary["critical_event_open"]:
        reasons.append("OPEN_CRITICAL_EVENT")
    if not any(r.regime == TRAINING_POLICY["training_regime"] for r in _training_readings(machine)):
        reasons.append("TRAINING_REGIME_UNAVAILABLE")
    return not reasons, reasons


def selecionar_fonte_modelo(machine, regime: str = "trabalhando") -> dict[str, Any]:
    """Seleciona individual, grupo, estatístico ou inconclusivo, sem cruzar tenants."""
    eligible, reasons = pode_treinar(machine)
    if eligible:
        return {"model_source": "individual", "machine_id": machine.external_code, "regime": regime, "reasons": []}
    if machine.modelo_id:
        peers = Machine.objects.filter(modelo_id=machine.modelo_id).exclude(pk=machine.pk)
        if machine.organization_id:
            peers = peers.filter(organization_id=machine.organization_id)
        peers = [peer for peer in peers if pode_treinar(peer)[0]]
        if peers:
            return {"model_source": "group_baseline", "group_model_id": machine.modelo_id, "machines": len(peers) + 1, "regime": regime, "reasons": reasons}
    if summary := resumo_elegibilidade(machine):
        if summary["eligible_readings"] >= 2 and summary["average_trust"] is not None:
            return {"model_source": "statistical_baseline", "regime": regime, "reasons": reasons}
    return {"model_source": "none", "regime": regime, "reasons": reasons + ["NO_COMPATIBLE_BASELINE"]}


def aprovar_challenger(
    champion_metrics: dict[str, float | None] | None,
    challenger_metrics: dict[str, float | None] | None,
    *,
    minimum_f1: float = 0.0,
) -> tuple[bool, str]:
    """Regra pequena e pré-declarada para não trocar champion às cegas.

    Sem validação independente ou métricas definidas, a resposta é rejeição.
    O empate mantém o champion, evitando troca de artefato sem ganho claro.
    """
    if not champion_metrics or not challenger_metrics:
        return False, "VALIDATION_INSUFFICIENT"
    champion_f1 = champion_metrics.get("f1")
    challenger_f1 = challenger_metrics.get("f1")
    if champion_f1 is None or challenger_f1 is None:
        return False, "METRIC_UNDEFINED"
    if challenger_f1 < minimum_f1:
        return False, "CHALLENGER_BELOW_MINIMUM"
    if challenger_f1 <= champion_f1:
        return False, "CHALLENGER_NOT_BETTER"
    return True, "CHALLENGER_APPROVED"


def _train_and_persist(machine_id: str, history: np.ndarray, *, regime: str = "trabalhando") -> tuple[IsolationForest, dict]:
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
        "model_version": MODEL_VERSION,
        "machine_id": str(machine_id),
        "regime": regime,
        "features": list(FEATURES),
        "random_state": RANDOM_STATE,
        "algoritmo": "IsolationForest",
        "algorithm": "IsolationForest",
        "training_status": "trained",
        "dataset_hash": hashlib.sha256(history.tobytes()).hexdigest(),
        "scale_mean": mean.tolist(),
        "scale_std": std.tolist(),
    }
    registry.save_model(machine_id, model, metadata)
    return model, metadata


def train_model_for_machine(machine_id: str, *, regime: str = "trabalhando") -> tuple[IsolationForest, dict]:
    machine = Machine.objects.get(external_code=str(machine_id))
    eligible, reasons = pode_treinar(machine)
    if not eligible:
        raise ValueError("treinamento recusado: " + ", ".join(reasons))
    rows = LeituraTelemetria.objects.filter(machine=machine, regime=regime, evidence_quality="boa").values(*FEATURES)
    data = [[float(row[feature]) if row[feature] is not None else 0.0 for feature in FEATURES] for row in rows.iterator()]
    return _train_and_persist(str(machine_id), np.asarray(data, dtype=float), regime=regime)


def _load_persisted(machine_id: str, history: np.ndarray, *, regime: str = "trabalhando") -> tuple[IsolationForest, dict]:
    try:
        model, metadata = registry.load_latest_model(machine_id, regime=regime)
    except ModelNotFoundError:
        try:
            model, metadata = registry.load_latest_model(machine_id)
        except ModelNotFoundError:
            return _train_and_persist(machine_id, history, regime=regime)
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
        regime = current_reading.get("regime") or inferir_regime(current_reading.get("rpm"), current_reading.get("velocidade_kmh"))
        if regime == "desconhecido":
            return _result(False, 0.0, "regime_contextual", None, "Regime desconhecido; observabilidade sem alerta mecânico.", status="inconclusivo")
        state = REGISTRY.get_or_create(machine_id, regime)
        history = np.asarray(state.features, dtype=float)
        vector = _feature_vector(current_reading, history)
        if len(history) < MINIMUM_TRAINING_READINGS:
            return _detect_with_zscore(vector, history)
        if state.model is None:
            state.model, metadata = _load_persisted(machine_id, history, regime=regime)
            state.scale_mean = np.asarray(metadata["scale_mean"], dtype=float)
            state.scale_std = np.asarray(metadata["scale_std"], dtype=float)
            state.training_scores = state.model.decision_function((history - state.scale_mean) / state.scale_std)
        return _detect_with_isolation_forest(vector, history, state)


def detect_from_history(
    history: np.ndarray | list[list[float]],
    current_reading: dict | list[float],
    *,
    model: IsolationForest | None = None,
    metadata: dict[str, Any] | None = None,
) -> AnomalyResult:
    """Executa o mesmo detector da API sem depender do banco.

    O harness de avaliação usa esta função. Rótulos e geração de cenários ficam
    fora do serviço, mas o algoritmo e o contrato permanecem únicos.
    """
    values = np.asarray(history, dtype=float)
    if values.ndim != 2 or values.shape[1] != len(FEATURES):
        raise ValueError(f"histórico deve possuir as features {FEATURES}")
    vector = np.asarray(current_reading, dtype=float) if not isinstance(current_reading, dict) else np.asarray(
        _feature_vector(current_reading, values), dtype=float
    )
    if model is None:
        return _detect_with_zscore(vector.tolist(), values)
    meta = metadata or {}
    state = _DetectorState(
        features=values.tolist(),
        model=model,
        scale_mean=np.asarray(meta.get("scale_mean", values.mean(axis=0)), dtype=float),
        scale_std=np.asarray(meta.get("scale_std", np.where(values.std(axis=0) > 1e-9, values.std(axis=0), 1.0)), dtype=float),
    )
    state.training_scores = np.asarray(meta.get("training_scores"), dtype=float) if meta.get("training_scores") is not None else model.decision_function((values - state.scale_mean) / state.scale_std)
    return _detect_with_isolation_forest(vector, values, state)


def detect_many_from_history(history, readings, *, model, metadata=None, feature_names=None) -> list[AnomalyResult]:
    """Versão em lote do detector oficial, para avaliações reprodutíveis."""
    values = np.asarray(history, dtype=float)
    names = tuple(feature_names or FEATURES)
    if len(names) != values.shape[1]:
        raise ValueError("feature_names deve possuir um nome por coluna")
    meta = metadata or {}
    mean = np.asarray(meta.get("scale_mean", values.mean(axis=0)), dtype=float)
    std = np.asarray(meta.get("scale_std", np.where(values.std(axis=0) > 1e-9, values.std(axis=0), 1.0)), dtype=float)
    vectors = np.asarray(readings, dtype=float)
    scaled = (vectors - mean) / std
    scores = model.decision_function(scaled)
    predicted = model.predict(scaled)
    training_scores = np.asarray(meta.get("training_scores", model.decision_function((values - mean) / std)), dtype=float)
    threshold = float(np.percentile(training_scores, 5))
    minimum = float(training_scores.min())
    result = []
    feature_means = values.mean(axis=0)
    deviations = np.where(values.std(axis=0) > 1e-9, values.std(axis=0), 1.0)
    for vector, score, prediction in zip(vectors, scores, predicted):
        normalized = min(max((threshold - float(score)) / max(threshold - minimum, 1e-9), 0.0), 1.0)
        normalized = max(normalized, min(float(np.max(np.abs((vector - mean) / std))) / 6.0, 1.0))
        if prediction == -1:
            normalized = max(normalized, ANOMALY_THRESHOLD)
        index = int(np.argmax(np.abs((vector - feature_means) / deviations)))
        result.append(_result(normalized >= ANOMALY_THRESHOLD, normalized, "ISOLATION_FOREST", names[index], f"Isolation Forest identificou padrao atipico em {names[index]}", model_version=meta.get("model_version", MODEL_VERSION)))
    return result


def detect_compatibility_artifact(temperatura: float, vibracao: float, rpm: float) -> AnomalyResult:
    """Fachada temporária; consumidores legados usam o contrato oficial."""
    from api_tcc.ia.deteccao_multivariada import MODELO_PATH

    if not MODELO_PATH.exists():
        return _result(False, 0.0, "indisponivel", None, "Artefato ausente.", status="indisponivel")
    model = joblib.load(MODELO_PATH)
    rng = np.random.default_rng(42)
    baseline = np.column_stack((rng.uniform(60, 80, 1000), rng.uniform(0.2, 2.0, 1000), rng.uniform(1400, 1900, 1000)))
    sample = np.asarray([[temperatura, vibracao, rpm]], dtype=float)
    raw_score = float(model.decision_function(sample)[0])
    is_anomaly = bool(model.predict(sample)[0] == -1)
    normalized = max(0.0, min((0.5 - raw_score) / 1.0, 1.0))
    if is_anomaly:
        normalized = max(normalized, ANOMALY_THRESHOLD)
    return _result(is_anomaly, normalized, "ISOLATION_FOREST", None,
                   "Artefato global de bancada encaminhado pelo serviço oficial.",
                   model_version="legacy-bench-v1")


def train_legacy_compatibility_model(data) -> IsolationForest:
    """Gera o artefato histórico apenas para compatibilidade de bancada."""
    model = IsolationForest(n_estimators=100, contamination=CONTAMINATION, random_state=RANDOM_STATE)
    model.fit(data[["temperatura", "vibracao", "rpm"]])
    import joblib
    MODELO_PATH = __import__("api_tcc.ia.deteccao_multivariada", fromlist=["MODELO_PATH"]).MODELO_PATH
    MODELO_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODELO_PATH)
    return model


def _feature_vector(reading: dict, history: np.ndarray) -> list[float]:
    means = history.mean(axis=0) if len(history) else np.zeros(len(FEATURES))
    return [float(reading.get(feature)) if reading.get(feature) is not None else float(means[index]) for index, feature in enumerate(FEATURES)]


def _detect_with_zscore(vector: list[float], history: np.ndarray) -> AnomalyResult:
    if len(history) < 2:
        return _result(False, 0.0, "baseline_estatistico", None, "Sem baseline historico suficiente.", status="inconclusivo")
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
        return _result(False, 0.0, "ISOLATION_FOREST", None, "Leitura coincide com o baseline constante.", model_version=MODEL_VERSION)
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
    return _result(normalized >= ANOMALY_THRESHOLD, normalized, "ISOLATION_FOREST", feature, explanation, model_version=MODEL_VERSION)


def _result(is_anomaly, score, method, feature, explanation, *, model_version=None, status="concluido") -> AnomalyResult:
    return AnomalyResult(
        bool(is_anomaly),
        round(float(min(max(score, 0.0), 1.0)), 4),
        method,
        feature,
        explanation,
        model_version=model_version,
        detection_status=status,
        data_quality={"n_historico": None},
    )
