"""
api_tcc/ia/prescricoes.py

Motor prescritivo MVP: gera recomendações operacionais baseadas em:
- Detecção de anomalias (Isolation Forest)
- Previsão de risco de manutenção (Random Forest)
- Regras manuais de threshold (domínio agrícola)

Retorna prescrição em texto humano, não gerada por IA generativa.
"""
from django.db import transaction
from sklearn.ensemble import IsolationForest, RandomForestClassifier

from api_tcc.ia.pipeline import carregar_dados
from api_tcc.models import Colheitadeira, Prescricao


def gerar_prescricao(maquina_id, limite=10):
    """
    Gera prescrição operacional para uma máquina.

    Parâmetros:
        maquina_id (str): ID da máquina
        limite (int): número de leituras recentes a analisar (padrão 10)

    Retorna:
        {
            "status": "ok" | "dados_insuficientes" | "erro",
            "maquina_id": str,
            "prescricao": str (texto humano),
            "acao_recomendada": str,
            "severidade": "NORMAL" | "ATENCAO" | "CRITICO",
            "confianca": float (0.0 a 1.0),
            "timestamp": ISO string,
        }

    Fluxo:
        1. Carregar últimas N leituras
        2. Aplicar Isolation Forest (detecção de anomalia)
        3. Aplicar Random Forest (risco de manutenção)
        4. Combinar com regras manuais de threshold
        5. Gerar texto prescritivo programaticamente
    """
    if not maquina_id:
        return {
            "status": "erro",
            "detalhe": "maquina_id é obrigatório",
        }

    resultado = carregar_dados(maquina_id, limite=limite)

    if isinstance(resultado, dict) and resultado.get("status") == "dados_insuficientes":
        return {
            "status": "dados_insuficientes",
            "detalhe": f"Requer mínimo de 10 leituras, atual: {resultado.get('atual', 0)}",
        }

    df = resultado

    temp_atual = df.iloc[0]["temperatura"]
    vib_atual = df.iloc[0]["vibracao"]
    rpm_atual = df.iloc[0]["rpm"]

    # Detecção de anomalia (Isolation Forest)
    X_anomalia = df[["temperatura", "vibracao", "rpm"]]
    modelo_if = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
    anomalia_score = modelo_if.fit_predict(X_anomalia)
    eh_anomalia = anomalia_score[-1] == -1

    # Previsão de risco (Random Forest)
    df["temp_media_movel"] = df["temperatura"].rolling(10, min_periods=1).mean()
    df["vib_media_movel"] = df["vibracao"].rolling(10, min_periods=1).mean()
    df["temp_tendencia"] = df["temperatura"].diff(5).fillna(0)

    df["risco"] = 0
    df["temp_alta_persistente"] = (df["temperatura"] > 80).rolling(5, min_periods=1).sum()
    df.loc[df["temp_alta_persistente"] >= 3, "risco"] = 1
    df.loc[(df["temperatura"] > 75) & (df["vibracao"] > 0.5), "risco"] = 1
    df.loc[df["temp_tendencia"] > 5, "risco"] = 1

    df = df.dropna()

    FEATURES = [
        "temperatura",
        "vibracao",
        "rpm",
        "temp_media_movel",
        "vib_media_movel",
        "temp_tendencia",
    ]
    X = df[FEATURES]
    y = df["risco"]

    modelo_rf = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo_rf.fit(X, y)

    ultima = df[FEATURES].iloc[[-1]]
    
    # Verificar se o modelo tem ambas as classes (0 e 1)
    classes = modelo_rf.classes_
    if len(classes) == 1:
        # Se só tem uma classe, assumir probabilidade baixa
        prob_risco = 0.1 if classes[0] == 0 else 0.9
    else:
        # Modelo tem ambas as classes, usar predict_proba normalmente
        prob_risco = float(modelo_rf.predict_proba(ultima)[0][1])

    # Regras manuais de threshold
    severidade, confianca, acao, texto = _classificar_e_gerar_texto(
        temp_atual, vib_atual, rpm_atual, prob_risco, eh_anomalia
    )

    return {
        "status": "ok",
        "maquina_id": maquina_id,
        "prescricao": texto,
        "acao_recomendada": acao,
        "severidade": severidade,
        "confianca": confianca,
        "timestamp": str(df.iloc[0]["timestamp"]),
    }


def _classificar_e_gerar_texto(temp, vib, rpm, prob_risco, eh_anomalia):
    """
    Classifica estado e gera prescrição em texto humano.

    Retorna: (severidade, confianca, acao_recomendada, texto_prescricao)
    """

    # Regra 1: Crítico — temperatura muito elevada + vibração alta
    if temp > 85 and vib > 0.8:
        return (
            "CRITICO",
            0.95,
            "Parar máquina imediatamente. Verificar arrefecimento e rolamentos.",
            f"ALERTA CRÍTICO: Máquina operando em temperatura {temp:.1f}°C (limite 85°C) "
            f"com vibração {vib:.2f} (limite 0.8). Possível falha de arrefecimento ou "
            f"desgaste mecânico. Inspecione imediatamente: radiador, correntes, rolamentos.",
        )

    # Regra 2: Crítico — temperatura crítica sozinha
    if temp > 85:
        return (
            "CRITICO",
            0.90,
            "Verificar sistema de refrigeração com urgência.",
            f"ALERTA: Temperatura crítica {temp:.1f}°C (limite 85°C). "
            f"Sistema de arrefecimento pode estar comprometido. "
            f"Verifique nível de coolant, radiador limpo e ventilador operacional.",
        )

    # Regra 3: Crítico — vibração muito alta
    if vib > 0.8:
        return (
            "CRITICO",
            0.92,
            "Desligar máquina. Verificar desbalanceamento e rolamentos.",
            f"ALERTA CRÍTICO: Vibração excessiva {vib:.2f} (limite 0.8) detectada. "
            f"Possível desbalanceamento, desgaste de rolamentos ou falha mecânica. "
            f"Máquina requer inspeção técnica urgente.",
        )

    # Regra 4: Atenção — temperatura elevada + vibração moderada
    if temp > 75 and vib > 0.5:
        return (
            "ATENCAO",
            0.80,
            "Monitorar temperatura. Inspecionar sistema de refrigeração.",
            f"AVISO: Temperatura elevada ({temp:.1f}°C) combinada com vibração elevada ({vib:.2f}) "
            f"indica possível sobrecarga ou falha incipiente. "
            f"Recomenda-se monitoramento próximo e inspeção preventiva em 4-8 horas.",
        )

    # Regra 5: Atenção — temperatura moderadamente elevada
    if temp > 75:
        return (
            "ATENCAO",
            0.75,
            "Aumentar monitoramento. Verificar carga de trabalho.",
            f"AVISO: Temperatura {temp:.1f}°C está próxima ao limite operacional (75-85°C). "
            f"Máquina pode estar sobrecarregada. Recomenda-se reduzir carga ou "
            f"permitir repouso até temperatura normalizar.",
        )

    # Regra 6: Atenção — vibração moderada
    if vib > 0.5:
        return (
            "ATENCAO",
            0.70,
            "Inspecionar alinhamento e rolamentos.",
            f"AVISO: Vibração {vib:.2f} está acima do normal (limite 0.5). "
            f"Possível desalinhamento, desgaste de correntes ou rolamentos. "
            f"Agende inspeção para validar condição mecânica.",
        )

    # Regra 7: Atenção — probabilidade de risco elevada
    if prob_risco > 0.6:
        return (
            "ATENCAO",
            prob_risco,
            "Agendar manutenção preventiva em curto prazo.",
            f"AVISO: Padrões operacionais indicam risco elevado de falha (probabilidade {prob_risco:.0%}). "
            f"Recomenda-se manutenção preventiva nos próximos 1-2 dias para evitar parada não planejada.",
        )

    # Regra 8: Atenção — anomalia detectada
    if eh_anomalia:
        return (
            "ATENCAO",
            0.65,
            "Investigar comportamento anômalo.",
            f"AVISO: Leitura atual apresenta comportamento anômalo em relação ao histórico. "
            f"Temperatura {temp:.1f}°C, Vibração {vib:.2f}, RPM {rpm}. "
            f"Pode indicar falha de sensor ou mudança operacional. Verifique manualmente.",
        )

    # Regra 9: Normal — tudo dentro dos limites
    if prob_risco > 0.3:
        return (
            "NORMAL",
            1.0 - prob_risco,
            "Continuar operação normal. Monitoramento de rotina.",
            f"Máquina operando dentro dos limites normais (Temp: {temp:.1f}°C, Vibração: {vib:.2f}, RPM: {rpm}). "
            f"Risco baixo. Mantenha monitoramento de rotina e siga cronograma de manutenção preventiva.",
        )

    # Padrão: tudo normal
    return (
        "NORMAL",
        1.0,
        "Continuar operação. Sem ações imediatas necessárias.",
        f"Máquina operando normalmente (Temp: {temp:.1f}°C, Vibração: {vib:.2f}, RPM: {rpm}). "
        f"Nenhuma ação imediata necessária. Continue com manutenção de rotina.",
    )
