# api_tcc/ia/estado.py
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from api_tcc.models import LeituraTelemetria

ESTADOS = {0: 'Ralenti',
           1: 'Operação Normal',
           2: 'Sobrecarga'}

def classificar_estado(maquina_id=None):
    qs = LeituraTelemetria.objects.all()
    if maquina_id:
        qs = qs.filter(maquina_id=maquina_id)
    qs = qs.order_by('-timestamp')[:300]

    if qs.count() < 15:
        return {'status': 'dados_insuficientes'}

    df = pd.DataFrame(list(qs.values(
        'id', 'maquina_id', 'temperatura', 'vibracao', 'rpm', 'timestamp'
    )))

    X = df[['temperatura', 'vibracao', 'rpm']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)

    # Ordena clusters por RPM médio pra mapear pro nome
    ordem = df.groupby('cluster')['rpm'].mean().sort_values().index.tolist()
    mapa  = {cluster: ESTADOS[i] for i, cluster in enumerate(ordem)}
    df['estado'] = df['cluster'].map(mapa)

    ultima = df.iloc[0]
    contagem = df['estado'].value_counts().to_dict()

    return {
        'maquina_id':     maquina_id,
        'estado_atual':   ultima['estado'],
        'distribuicao':   contagem,
        'total_leituras': len(df),
    }