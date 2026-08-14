"""
Pipeline único de análise de telemetria.
Fluxo: leituras -> validação -> normalização -> features -> anomalia -> risco -> prescrição
Nenhum outro módulo de IA deve consultar o banco diretamente. Tudo passa por aqui.
"""
from dataclasses import dataclass
from typing import Optional
import pandas as pd
from django.db.models import QuerySet


@dataclass
class ResultadoAnalise:
    maquina_id: str
    status: str          # 'NORMAL' | 'ATENCAO' | 'CRITICO'
    motivos: list[str]
    metricas: dict
    recomendacao: Optional[str]


def carregar_janela(maquina_id: str, limite: int = 500) -> pd.DataFrame:
    """Única função autorizada a consultar LeituraTelemetria para fins de IA."""
    from api_tcc.models import LeituraTelemetria
    qs: QuerySet = (
        LeituraTelemetria.objects
        .filter(maquina_id=maquina_id)
        .order_by('-timestamp')
        .values('timestamp', 'temperatura', 'vibracao', 'rpm')[:limite]
    )
    return pd.DataFrame.from_records(qs)


def calcular_features(df: pd.DataFrame) -> dict:
    """Média móvel, delta entre leituras, tempo contínuo acima de limiar — tudo centralizado aqui."""
    if df.empty:
        return {}
    return {
        'temp_media': df['temperatura'].mean(),
        'temp_max': df['temperatura'].max(),
        'temp_tendencia': df['temperatura'].diff().mean(),
        'vib_media': df['vibracao'].mean(),
        'rpm_std': df['rpm'].std(),
    }


def detectar_anomalia(features: dict) -> tuple[bool, list[str]]:
    """Regras determinísticas documentadas — nada de threshold chutado sem justificativa."""
    motivos = []
    # LIMIARES DEFINIDOS PARA FINS DE PROTOTIPAÇÃO — documentar a origem
    # (dataset simulado de bancada, ver docs/limiares.md)
    if features.get('temp_max', 0) > 85:
        motivos.append('temperatura acima de 85°C')
    if features.get('temp_tendencia', 0) > 0.5:
        motivos.append('tendência de aumento sustentado de temperatura')
    if features.get('vib_media', 0) > 5:
        motivos.append('vibração média acima do padrão esperado')
    return (len(motivos) > 0, motivos)


def classificar_risco(motivos: list[str]) -> str:
    if len(motivos) >= 2:
        return 'CRITICO'
    if len(motivos) == 1:
        return 'ATENCAO'
    return 'NORMAL'


def gerar_recomendacao(status: str, motivos: list[str]) -> Optional[str]:
    if status == 'NORMAL':
        return None
    if status == 'ATENCAO':
        return f"Recomenda-se inspeção preventiva. Motivo: {'; '.join(motivos)}."
    return f"Inspeção imediata recomendada antes da próxima operação. Motivos: {'; '.join(motivos)}."


def analisar_maquina(maquina_id: str) -> ResultadoAnalise:
    """Ponto de entrada único. Qualquer view ou management command chama SÓ isso."""
    df = carregar_janela(maquina_id)
    features = calcular_features(df)
    tem_anomalia, motivos = detectar_anomalia(features)
    status = classificar_risco(motivos)
    recomendacao = gerar_recomendacao(status, motivos)
    return ResultadoAnalise(
        maquina_id=maquina_id,
        status=status,
        motivos=motivos,
        metricas=features,
        recomendacao=recomendacao,
    )
