import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from pathlib import Path

MODELO_PATH = Path(__file__).parent / 'modelos' / 'isolation_forest_v1.pkl'
COLUNAS_FEATURES = ['temperatura', 'vibracao', 'rpm']


def treinar_modelo(df_normal: pd.DataFrame) -> IsolationForest:
    """
    Treina com dados classificados como NORMAL (do simulador, cenario_normal).
    contamination baixo porque esperamos poucas anomalias no dataset de treino.
    """
    features = df_normal[COLUNAS_FEATURES]
    modelo = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    modelo.fit(features)
    MODELO_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(modelo, MODELO_PATH)
    return modelo


def carregar_modelo() -> IsolationForest:
    return joblib.load(MODELO_PATH)


def calcular_score_anomalia(temperatura: float, vibracao: float, rpm: float) -> dict:
    modelo = carregar_modelo()
    amostra = pd.DataFrame(
        [[temperatura, vibracao, rpm]], columns=COLUNAS_FEATURES
    )
    score = modelo.decision_function(amostra)[0]  # quanto mais negativo, mais anômalo
    eh_anomalia = modelo.predict(amostra)[0] == -1
    return {'score_anomalia': float(score), 'anomalia_multivariada': bool(eh_anomalia)}
