# api_tcc/ia/estado.py
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from api_tcc.ia.pipeline import carregar_dados

ESTADOS = {0: "Ralenti", 1: "Operação Normal", 2: "Sobrecarga"}


def classificar_estado(maquina_id=None):
    if not maquina_id:
        return {"status": "erro", "detalhe": "maquina_id é obrigatório"}

    resultado = carregar_dados(maquina_id, limite=300, minimo=10)

    if isinstance(resultado, dict):
        return resultado

    df = resultado
    X = df[["temperatura", "vibracao", "rpm"]]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(X_scaled)

    ordem = df.groupby('cluster')['rpm'].mean().sort_values().index.tolist()
    mapa  = {cluster: ESTADOS[i] for i, cluster in enumerate(ordem)}
    df['estado'] = df['cluster'].map(mapa)

    ultima = df.iloc[0]
    contagem = df['estado'].value_counts().to_dict()

    return {
        'status':         'ok',
        'maquina_id':     maquina_id,
        'estado_atual':   ultima['estado'],
        'distribuicao':   contagem,
        'total_leituras': len(df),
    }
