"""
api_tcc/ia/prescricoes.py

Motor prescritivo MVP: gera recomendacoes operacionais baseadas em:
- Deteccao de anomalias (Isolation Forest)
- Previsao de risco de manutencao (Random Forest)
- Regras manuais de threshold (dominio agricola)

Retorna prescricao em texto humano, nao gerada por IA generativa.
"""
from dataclasses import dataclass, asdict
from typing import Any

from django.db import transaction
from sklearn.ensemble import IsolationForest, RandomForestClassifier

from api_tcc.ia.pipeline import carregar_dados
from api_tcc.models import Colheitadeira, Prescricao


SEVERITY_ORDER = {
    "NORMAL": 0,
    "ATENCAO": 1,
    "CRITICO": 2,
}

MAX_DESCRICAO_LENGTH = 4000


@dataclass(frozen=True)
class RuleFinding:
    regra: str
    dimensao: str
    valor: Any
    limite: Any
    severidade: str
    motivo: str
    recomendacao: str
    confianca: float


def gerar_prescricao(maquina_id, limite=10):
    """
    Gera prescricao operacional para uma maquina.

    Mantem o contrato historico do retorno e adiciona campos estruturados para
    explicar quais regras dispararam e qual acao o operador deve tomar.
    """
    if not maquina_id:
        return {
            "status": "erro",
            "detalhe": "maquina_id e obrigatorio",
        }

    resultado = carregar_dados(maquina_id, limite=limite)

    if isinstance(resultado, dict) and resultado.get("status") == "dados_insuficientes":
        return {
            "status": "dados_insuficientes",
            "detalhe": f"Requer minimo de 10 leituras, atual: {resultado.get('atual', 0)}",
        }

    df = resultado
    dados_avaliados = get_latest_values(df)
    prob_risco = predict_failure_probability(df)
    eh_anomalia = detect_anomaly(df)
    findings = collect_rule_findings(dados_avaliados, prob_risco, eh_anomalia)
    prescricao_operacional = consolidate_prescription(
        dados_avaliados=dados_avaliados,
        prob_risco=prob_risco,
        eh_anomalia=eh_anomalia,
        findings=findings,
    )

    colheitadeira = Colheitadeira.objects.filter(maquina_id=maquina_id).first()
    if not colheitadeira:
        return {
            "status": "erro",
            "detalhe": f"Colheitadeira nao encontrada para maquina_id {maquina_id}",
        }

    titulo = (
        f"Prescricao {prescricao_operacional['severidade']} - "
        f"{prescricao_operacional['acao_recomendada']}"
    )
    descricao = truncate_description(prescricao_operacional["texto"])

    try:
        with transaction.atomic():
            prescricao = Prescricao.objects.create(
                colheitadeira=colheitadeira,
                titulo=titulo[:200],
                descricao=descricao,
                status="pendente",
            )
    except Exception:
        return {
            "status": "erro",
            "detalhe": "Falha ao salvar prescricao no banco.",
        }

    return {
        "status": "ok",
        "maquina_id": maquina_id,
        "prescricao": descricao,
        "acao_recomendada": prescricao_operacional["acao_recomendada"],
        "severidade": prescricao_operacional["severidade"],
        "confianca": prescricao_operacional["confianca"],
        "timestamp": str(dados_avaliados.get("timestamp")),
        "prescricao_id": prescricao.id,
        "risco": prescricao_operacional["severidade"],
        "motivos": [asdict(finding) for finding in findings],
        "recomendacoes": prescricao_operacional["recomendacoes"],
        "dados_avaliados": {
            **dados_avaliados,
            "probabilidade_risco": round(prob_risco, 3),
            "anomalia_detectada": eh_anomalia,
        },
    }


def get_latest_values(df):
    latest = df.iloc[0]
    return {
        "temperatura": safe_float(latest.get("temperatura")),
        "vibracao": safe_float(latest.get("vibracao")),
        "rpm": safe_int(latest.get("rpm")),
        "timestamp": latest.get("timestamp"),
    }


def detect_anomaly(df):
    required_columns = ["temperatura", "vibracao", "rpm"]
    if df.empty or any(column not in df.columns for column in required_columns):
        return False

    data = df[required_columns].fillna(0)
    if len(data) < 2:
        return False

    modelo = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
    scores = modelo.fit_predict(data)
    return bool(scores[-1] == -1)


def build_risk_features(df):
    prepared = df.copy()
    prepared["temp_media_movel"] = prepared["temperatura"].rolling(10, min_periods=1).mean()
    prepared["vib_media_movel"] = prepared["vibracao"].rolling(10, min_periods=1).mean()
    prepared["temp_tendencia"] = prepared["temperatura"].diff(5).fillna(0)

    prepared["risco"] = 0
    prepared["temp_alta_persistente"] = (
        (prepared["temperatura"] > 80).rolling(5, min_periods=1).sum()
    )
    prepared.loc[prepared["temp_alta_persistente"] >= 3, "risco"] = 1
    prepared.loc[
        (prepared["temperatura"] > 75) & (prepared["vibracao"] > 0.5),
        "risco",
    ] = 1
    prepared.loc[prepared["temp_tendencia"] > 5, "risco"] = 1
    return prepared.dropna()


def predict_failure_probability(df):
    features = [
        "temperatura",
        "vibracao",
        "rpm",
        "temp_media_movel",
        "vib_media_movel",
        "temp_tendencia",
    ]
    prepared = build_risk_features(df)
    if prepared.empty:
        return 0.1

    x = prepared[features].fillna(0)
    y = prepared["risco"]

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(x, y)

    ultima = x.iloc[[-1]]
    classes = modelo.classes_
    if len(classes) == 1:
        return 0.1 if classes[0] == 0 else 0.9

    return float(modelo.predict_proba(ultima)[0][1])


def collect_rule_findings(dados_avaliados, prob_risco, eh_anomalia):
    temp = dados_avaliados.get("temperatura")
    vib = dados_avaliados.get("vibracao")
    rpm = dados_avaliados.get("rpm")

    findings = []
    findings.extend(check_temp_vib_combinadas(temp, vib))
    findings.extend(check_temp(temp))
    findings.extend(check_vib(vib))
    findings.extend(check_rpm(rpm))
    findings.extend(check_risco_modelo(prob_risco))
    findings.extend(check_anomalia(eh_anomalia, temp, vib, rpm))
    return findings


def check_temp_vib_combinadas(temp, vib):
    if temp is None or vib is None:
        return []

    if temp > 85 and vib > 0.8:
        return [
            RuleFinding(
                regra="temperatura_e_vibracao_criticas",
                dimensao="temperatura_vibracao",
                valor={"temperatura": round(temp, 1), "vibracao": round(vib, 2)},
                limite={"temperatura": 85, "vibracao": 0.8},
                severidade="CRITICO",
                motivo=(
                    f"Temperatura {temp:.1f}C acima de 85C combinada com "
                    f"vibracao {vib:.2f} acima de 0.8."
                ),
                recomendacao=(
                    "Parar a maquina imediatamente e inspecionar arrefecimento, "
                    "correntes e rolamentos."
                ),
                confianca=0.95,
            )
        ]

    if temp > 75 and vib > 0.5:
        return [
            RuleFinding(
                regra="temperatura_e_vibracao_em_alerta",
                dimensao="temperatura_vibracao",
                valor={"temperatura": round(temp, 1), "vibracao": round(vib, 2)},
                limite={"temperatura": 75, "vibracao": 0.5},
                severidade="ATENCAO",
                motivo=(
                    f"Temperatura {temp:.1f}C acima de 75C combinada com "
                    f"vibracao {vib:.2f} acima de 0.5."
                ),
                recomendacao=(
                    "Monitorar de perto e programar inspecao preventiva nas "
                    "proximas 4 a 8 horas."
                ),
                confianca=0.80,
            )
        ]

    return []


def check_temp(temp):
    if temp is None:
        return [
            RuleFinding(
                regra="temperatura_indisponivel",
                dimensao="temperatura",
                valor=None,
                limite=None,
                severidade="ATENCAO",
                motivo="Leitura de temperatura ausente ou invalida.",
                recomendacao="Verificar sensor de temperatura antes de confiar na operacao.",
                confianca=0.60,
            )
        ]

    if temp > 85:
        return [
            RuleFinding(
                regra="temperatura_critica",
                dimensao="temperatura",
                valor=round(temp, 1),
                limite=85,
                severidade="CRITICO",
                motivo=f"Temperatura critica detectada: {temp:.1f}C acima do limite 85C.",
                recomendacao="Verificar sistema de refrigeracao com urgencia.",
                confianca=0.90,
            )
        ]

    if temp > 75:
        return [
            RuleFinding(
                regra="temperatura_elevada",
                dimensao="temperatura",
                valor=round(temp, 1),
                limite=75,
                severidade="ATENCAO",
                motivo=f"Temperatura {temp:.1f}C acima da faixa recomendada de 75C.",
                recomendacao="Reduzir carga se possivel e acompanhar a proxima leitura.",
                confianca=0.75,
            )
        ]

    return []


def check_vib(vib):
    if vib is None:
        return [
            RuleFinding(
                regra="vibracao_indisponivel",
                dimensao="vibracao",
                valor=None,
                limite=None,
                severidade="ATENCAO",
                motivo="Leitura de vibracao ausente ou invalida.",
                recomendacao="Verificar sensor de vibracao e fixacao do conjunto.",
                confianca=0.60,
            )
        ]

    if vib > 0.8:
        return [
            RuleFinding(
                regra="vibracao_critica",
                dimensao="vibracao",
                valor=round(vib, 2),
                limite=0.8,
                severidade="CRITICO",
                motivo=f"Vibracao excessiva detectada: {vib:.2f} acima do limite 0.8.",
                recomendacao="Desligar maquina e verificar desbalanceamento e rolamentos.",
                confianca=0.92,
            )
        ]

    if vib > 0.5:
        return [
            RuleFinding(
                regra="vibracao_elevada",
                dimensao="vibracao",
                valor=round(vib, 2),
                limite=0.5,
                severidade="ATENCAO",
                motivo=f"Vibracao {vib:.2f} acima do limite normal 0.5.",
                recomendacao="Inspecionar alinhamento, correntes e rolamentos.",
                confianca=0.70,
            )
        ]

    return []


def check_rpm(rpm):
    if rpm is None:
        return [
            RuleFinding(
                regra="rpm_indisponivel",
                dimensao="rpm",
                valor=None,
                limite=None,
                severidade="ATENCAO",
                motivo="Leitura de RPM ausente ou invalida.",
                recomendacao="Verificar sensor de rotacao antes de continuar diagnostico.",
                confianca=0.55,
            )
        ]

    if rpm <= 0:
        return [
            RuleFinding(
                regra="rpm_invalido",
                dimensao="rpm",
                valor=rpm,
                limite="> 0",
                severidade="ATENCAO",
                motivo=f"RPM informado como {rpm}, valor incompativel com maquina em operacao.",
                recomendacao="Confirmar se a maquina esta parada ou se ha falha no sensor de RPM.",
                confianca=0.60,
            )
        ]

    return []


def check_risco_modelo(prob_risco):
    if prob_risco is None:
        return []

    if prob_risco > 0.6:
        return [
            RuleFinding(
                regra="modelo_risco_elevado",
                dimensao="risco_modelo",
                valor=round(prob_risco, 3),
                limite=0.6,
                severidade="ATENCAO",
                motivo=f"Modelo indicou probabilidade de falha de {prob_risco:.0%}.",
                recomendacao="Agendar manutencao preventiva nos proximos 1 a 2 dias.",
                confianca=prob_risco,
            )
        ]

    if prob_risco > 0.3:
        return [
            RuleFinding(
                regra="modelo_risco_baixo",
                dimensao="risco_modelo",
                valor=round(prob_risco, 3),
                limite=0.3,
                severidade="NORMAL",
                motivo=f"Modelo indicou risco baixo a moderado de {prob_risco:.0%}.",
                recomendacao="Continuar operacao normal com monitoramento de rotina.",
                confianca=1.0 - prob_risco,
            )
        ]

    return []


def check_anomalia(eh_anomalia, temp, vib, rpm):
    if not eh_anomalia:
        return []

    return [
        RuleFinding(
            regra="anomalia_historica",
            dimensao="padrao_operacional",
            valor={"temperatura": temp, "vibracao": vib, "rpm": rpm},
            limite="historico_recente",
            severidade="ATENCAO",
            motivo="Leitura atual destoou do historico recente da maquina.",
            recomendacao=(
                "Investigar comportamento anomalo e validar se houve mudanca de operacao "
                "ou falha de sensor."
            ),
            confianca=0.65,
        )
    ]


def consolidate_prescription(dados_avaliados, prob_risco, eh_anomalia, findings):
    principal = choose_primary_finding(findings)
    severidade = principal.severidade if principal else "NORMAL"
    confianca = principal.confianca if principal else 1.0
    acao = principal.recomendacao if principal else "Continuar operacao. Sem acoes imediatas necessarias."
    recomendacoes = unique_recommendations(findings) or [acao]
    texto = build_prescription_text(
        severidade=severidade,
        acao=acao,
        dados_avaliados=dados_avaliados,
        prob_risco=prob_risco,
        eh_anomalia=eh_anomalia,
        findings=findings,
        recomendacoes=recomendacoes,
    )

    return {
        "severidade": severidade,
        "confianca": round(float(confianca), 3),
        "acao_recomendada": acao,
        "texto": texto,
        "recomendacoes": recomendacoes,
    }


def choose_primary_finding(findings):
    if not findings:
        return None

    return sorted(
        findings,
        key=lambda finding: (SEVERITY_ORDER.get(finding.severidade, 0), finding.confianca),
        reverse=True,
    )[0]


def unique_recommendations(findings):
    recommendations = []
    for finding in findings:
        if finding.recomendacao not in recommendations:
            recommendations.append(finding.recomendacao)
    return recommendations


def build_prescription_text(
    severidade,
    acao,
    dados_avaliados,
    prob_risco,
    eh_anomalia,
    findings,
    recomendacoes,
):
    temp = format_value(dados_avaliados.get("temperatura"), "C", decimals=1)
    vib = format_value(dados_avaliados.get("vibracao"), "", decimals=2)
    rpm = format_value(dados_avaliados.get("rpm"), "rpm", decimals=0)

    lines = [
        f"Status operacional: {severidade}.",
        f"Acao sugerida: {acao}",
        (
            "Dados avaliados: "
            f"temperatura {temp}, vibracao {vib}, RPM {rpm}, "
            f"risco estimado {prob_risco:.0%}, "
            f"anomalia historica {'sim' if eh_anomalia else 'nao'}."
        ),
    ]

    if findings:
        lines.append("Motivos identificados:")
        for finding in findings:
            limite = finding.limite if finding.limite is not None else "nao aplicavel"
            lines.append(
                "- "
                f"{finding.regra}: {finding.motivo} "
                f"Valor detectado: {finding.valor}. Limite: {limite}. "
                f"Severidade: {finding.severidade}."
            )
    else:
        lines.append(
            "Motivos identificados: nenhuma regra critica ou de alerta foi disparada."
        )

    lines.append("Recomendacoes:")
    for recomendacao in recomendacoes:
        lines.append(f"- {recomendacao}")

    return "\n".join(lines)


def truncate_description(text):
    if len(text) <= MAX_DESCRICAO_LENGTH:
        return text

    suffix = "\n[Texto encurtado para caber no campo de descricao.]"
    return f"{text[:MAX_DESCRICAO_LENGTH - len(suffix)]}{suffix}"


def safe_float(value):
    if is_missing(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value):
    if is_missing(value):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def is_missing(value):
    return value is None or value != value


def format_value(value, suffix="", decimals=1):
    if value is None:
        return "indisponivel"

    if isinstance(value, int):
        formatted = f"{value:d}"
    else:
        formatted = f"{value:.{decimals}f}"

    return f"{formatted}{suffix}"
