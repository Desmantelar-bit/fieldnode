# api_tcc/ia/manutencao.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from api_tcc.models import LeituraTelemetria

def prever_manutencao(maquina_id):
    """
    Retorna:
        prob_risco   — float 0.0 a 1.0
        nivel        — 'NORMAL' | 'ATENCAO' | 'CRITICO'
        features_usadas — quais variáveis influenciaram mais
        status       — 'ok' | 'dados_insuficientes'
    """
    qs = LeituraTelemetria.objects.filter(
        maquina_id=maquina_id
    ).order_by('timestamp')[:300]

    if qs.count() < 30:
        return {
            'status':  'dados_insuficientes',
            'minimo':  30,
            'atual':   qs.count(),
        }

    df = pd.DataFrame(list(qs.values(
        'temperatura', 'vibracao', 'rpm', 'timestamp'
    )))

    # Feature: tendência nos últimos 10 registros
    df['temp_media_movel'] = df['temperatura'].rolling(10, min_periods=1).mean()
    df['vib_media_movel']  = df['vibracao'].rolling(10, min_periods=1).mean()
    df['temp_tendencia']   = df['temperatura'].diff(5).fillna(0)

    # Label baseado em padrões operacionais documentados de máquinas agrícolas
    # Referência: limites térmicos de motores diesel e análise de vibração mecânica
    df['risco'] = 0

    # Risco 1: Temperatura sustentada acima do limite operacional
    # Motores diesel: 80°C+ por >3 leituras indica falha de arrefecimento
    df['temp_alta_persistente'] = (df['temperatura'] > 80).rolling(5, min_periods=1).sum()
    df.loc[df['temp_alta_persistente'] >= 3, 'risco'] = 1

    # Risco 2: Combinação de sinais indica sobrecarga
    # Temp elevada + vibração alta = desbalanceamento ou desgaste de rolamentos
    df.loc[(df['temperatura'] > 75) & (df['vibracao'] > 0.5), 'risco'] = 1

    # Risco 3: Variação térmica rápida indica instabilidade
    # Subida >5°C em 5 leituras = possível falha de injeção ou refrigeração
    df.loc[df['temp_tendencia'] > 5, 'risco'] = 1

    df = df.dropna()
    if len(df) < 20:
        return {'status': 'dados_insuficientes', 'minimo': 20, 'atual': len(df)}

    FEATURES = ['temperatura', 'vibracao', 'rpm', 'temp_media_movel', 'vib_media_movel', 'temp_tendencia']
    X = df[FEATURES]
    y = df['risco']

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X, y)

    ultima = df[FEATURES].iloc[[-1]]
    prob_risco = float(modelo.predict_proba(ultima)[0][1])
    importancia = dict(zip(FEATURES, modelo.feature_importances_.round(3)))

    return {
        'status':         'ok',
        'maquina_id':     maquina_id,
        'prob_risco':     round(prob_risco, 3),
        'nivel':          'CRITICO' if prob_risco > 0.7 else 'ATENCAO' if prob_risco > 0.4 else 'NORMAL',
        'features':       importancia,
        'total_leituras': len(df),
    }