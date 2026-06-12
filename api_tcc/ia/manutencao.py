# api_tcc/ia/manutencao.py
from sklearn.ensemble import RandomForestClassifier
from api_tcc.ia.pipeline import carregar_dados


def prever_manutencao(maquina_id):
    """
    Prevê probabilidade de necessidade de manutenção.

    Retorna:
        prob_risco   — float 0.0 a 1.0
        nivel        — 'NORMAL' | 'ATENCAO' | 'CRITICO'
        features_usadas — quais variáveis influenciaram mais
        status       — 'ok' | 'dados_insuficientes'
    """
    if not maquina_id:
        return {"status": "erro", "detalhe": "maquina_id é obrigatório"}

    resultado = carregar_dados(maquina_id, limite=300, minimo=20)

    if isinstance(resultado, dict):
        return resultado

    df = resultado

    df['temp_media_movel'] = df['temperatura'].rolling(10, min_periods=1).mean()
    df['vib_media_movel']  = df['vibracao'].rolling(10, min_periods=1).mean()
    df['temp_tendencia']   = df['temperatura'].diff(5).fillna(0)

    df["risco"] = 0

    df['temp_alta_persistente'] = (df['temperatura'] > 80).rolling(5, min_periods=1).sum()
    df.loc[df['temp_alta_persistente'] >= 3, 'risco'] = 1

    df.loc[(df["temperatura"] > 75) & (df["vibracao"] > 0.5), "risco"] = 1

    df.loc[df['temp_tendencia'] > 5, 'risco'] = 1

    df = df.dropna()
    if len(df) < 20:
        return {"status": "dados_insuficientes", "minimo": 20, "atual": len(df)}

    FEATURES = ['temperatura', 'vibracao', 'rpm', 'temp_media_movel', 'vib_media_movel', 'temp_tendencia']
    X = df[FEATURES]
    y = df['risco']

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X, y)

    ultima = df[FEATURES].iloc[[-1]]
    
    # Verificar se o modelo tem ambas as classes (0 e 1)
    classes = modelo.classes_
    if len(classes) == 1:
        # Se só tem uma classe, assumir probabilidade baixa
        prob_risco = 0.1 if classes[0] == 0 else 0.9
    else:
        # Modelo tem ambas as classes, usar predict_proba normalmente
        prob_risco = float(modelo.predict_proba(ultima)[0][1])
    
    importancia = dict(zip(FEATURES, modelo.feature_importances_.round(3)))

    return {
        "status": "ok",
        "maquina_id": maquina_id,
        "prob_risco": round(prob_risco, 3),
        "nivel": "CRITICO"
        if prob_risco > 0.7
        else "ATENCAO"
        if prob_risco > 0.4
        else "NORMAL",
        "features": importancia,
        "total_leituras": len(df),
    }
