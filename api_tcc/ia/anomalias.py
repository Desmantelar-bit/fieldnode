import pandas as pd
import time
from sklearn.ensemble import IsolationForest
from api_tcc.models import LeituraTelemetria

_cache = {}  # {chave: (resultado, timestamp)}

def detectar_anomalias(maquina_id=None, contamination=0.05):
    """
    Parâmetros:
        maquina_id    — filtra por máquina; None = usa todas
        contamination — fração esperada de anomalias (5% padrão)

    Retorna dict com:
        anomalias  — lista de leituras classificadas como fora do padrão
        total      — total de anomalias encontradas
        analisadas — total de leituras analisadas
        status     — 'ok' | 'dados_insuficientes'
    """
    agora = time.time()
    chave = maquina_id or '_todas'
    if chave in _cache and agora - _cache[chave][1] < 30:
        return _cache[chave][0]
    qs = LeituraTelemetria.objects.all()
    if maquina_id:
        qs = qs.filter(maquina_id=maquina_id)

    qs = qs.order_by('-timestamp')[:500]

    if qs.count() < 20:
        resultado = {
            'status':    'dados_insuficientes',
            'minimo':    20,
            'atual':     qs.count(),
            'anomalias': [],
            'total':     0,
        }
        _cache[chave] = (resultado, agora)
        return resultado

    df = pd.DataFrame(list(qs.values(
        'id', 'maquina_id', 'temperatura', 'vibracao', 'rpm', 'timestamp'
    )))

    X = df[['temperatura', 'vibracao', 'rpm']]
    modelo = IsolationForest(contamination=contamination, random_state=42, n_estimators=100)
    df['score'] = modelo.fit_predict(X)   # -1 = anomalia, 1 = normal
    df['anomalia'] = df['score'] == -1

    anomalias = df[df['anomalia']].copy()
    anomalias['timestamp'] = anomalias['timestamp'].astype(str)
    anomalias['id'] = anomalias['id'].astype(str)

    resultado = {
        'status':    'ok',
        'anomalias': anomalias[['id', 'maquina_id', 'temperatura', 'vibracao', 'rpm', 'timestamp']].to_dict('records'),
        'total':     int(anomalias.shape[0]),
        'analisadas': int(df.shape[0]),
    }
    _cache[chave] = (resultado, agora)
    return resultado