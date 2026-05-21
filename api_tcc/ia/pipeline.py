"""
api_tcc/ia/pipeline.py

Pipeline centralizado de carregamento e pré-processamento de dados de telemetria.

Todos os módulos de IA (anomalias, estado, manutenção, prescrições) usam esta
função para obter dados do banco, garantindo:
- Uma query por chamada (não 3 queries redundantes)
- Escalabilidade com múltiplos workers (sem cache em dicionário global)
- Validação consistente de dados
- Interface simples: (maquina_id, limite) -> DataFrame
"""
import pandas as pd
from api_tcc.models import LeituraTelemetria


def carregar_dados(maquina_id, limite=300):
    """
    Carrega as últimas N leituras de telemetria de uma máquina.

    Parâmetros:
        maquina_id (str): ID da máquina a filtrar
        limite (int): número máximo de leituras a retornar (padrão 300)

    Retorna:
        DataFrame Pandas com colunas ['id', 'maquina_id', 'temperatura', 'vibracao', 'rpm', 'timestamp']
        se houver dados suficientes, ordenado por timestamp decrescente (mais recente primeiro).

        Caso contrário, retorna um dicionário de erro:
        {
            'status': 'dados_insuficientes',
            'minimo': N,
            'atual': M,
        }

    Decisão de design:
        - Usa ORM Django para aproveitar índices compostos (maquina_id, -timestamp)
        - Converte para DataFrame apenas uma vez (eficiência)
        - Não realiza cache aqui — cache é responsabilidade do framework/Redis
        - Não treina modelos aqui — apenas carrega e valida dados
    """
    qs = LeituraTelemetria.objects.filter(maquina_id=maquina_id).order_by('-timestamp')[:limite]

    if qs.count() < 10:
        return {
            'status': 'dados_insuficientes',
            'minimo': 10,
            'atual': qs.count(),
        }

    df = pd.DataFrame(list(qs.values(
        'id', 'maquina_id', 'temperatura', 'vibracao', 'rpm', 'timestamp'
    )))

    df = df.dropna()

    if len(df) < 10:
        return {
            'status': 'dados_insuficientes',
            'minimo': 10,
            'atual': len(df),
        }

    return df
