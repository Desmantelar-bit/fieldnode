"""Compatibilidade para o antigo módulo global de Isolation Forest."""

from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest

MODELO_PATH = Path(__file__).parent / "modelos" / "isolation_forest_v1.pkl"
COLUNAS_FEATURES = ["temperatura", "vibracao", "rpm"]


def treinar_modelo(df_normal: pd.DataFrame) -> IsolationForest:
    """Compatibilidade; o comando oficial é ``treinar_modelo_anomalia``."""
    from api_tcc.services.anomaly_detection import train_legacy_compatibility_model

    return train_legacy_compatibility_model(df_normal)


def carregar_modelo() -> IsolationForest:
    import joblib

    return joblib.load(MODELO_PATH)


def calcular_score_anomalia(temperatura: float, vibracao: float, rpm: float) -> dict:
    from api_tcc.services.anomaly_detection import detect_compatibility_artifact

    resultado = detect_compatibility_artifact(temperatura, vibracao, rpm)
    return {
        "score_anomalia": resultado.anomaly_score,
        "anomalia_multivariada": resultado.is_anomaly,
        "detection_method": resultado.detection_method,
        "model_version": resultado.model_version,
    }
