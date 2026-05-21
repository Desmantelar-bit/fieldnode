import pandas as pd
from sklearn.ensemble import IsolationForest
from api_tcc.ia.pipeline import carregar_dados


def detectar_anomalias(maquina_id=None, contamination=0.05):
    """
    Detecta leituras anômalas usando Isolation Forest.

    Parâmetros:
        maquina_id    — filtra por máquina; None = retorna erro (não suportado)
        contamination — fração esperada de anomalias (5% padrão)

    Retorna dict com:
        anomalias  — lista de leituras classificadas como fora do padrão
        total      — total de anomalias encontradas
        analisadas — total de leituras analisadas
        status     — 'ok' | 'dados_insuficientes'
    """
    if not maquina_id:
        return {
            "status": "erro",
            "detalhe": "maquina_id é obrigatório",
        }

    resultado = carregar_dados(maquina_id, limite=500)

    if isinstance(resultado, dict) and resultado.get("status") == "dados_insuficientes":
        resultado["anomalias"] = []
        resultado["total"] = 0
        resultado["analisadas"] = 0
        return resultado

    df = resultado
    X = df[['temperatura', 'vibracao', 'rpm']]
    modelo = IsolationForest(contamination=contamination, random_state=42, n_estimators=100)
    df["score"] = modelo.fit_predict(X)
    df['anomalia'] = df['score'] == -1

    anomalias = df[df['anomalia']].copy()
    anomalias['timestamp'] = anomalias['timestamp'].astype(str)
    anomalias['id'] = anomalias['id'].astype(str)

    return {
        "status": "ok",
        "anomalias": anomalias[
            ["id", "maquina_id", "temperatura", "vibracao", "rpm", "timestamp"]
        ].to_dict("records"),
        "total": int(anomalias.shape[0]),
        "analisadas": int(df.shape[0]),
    }