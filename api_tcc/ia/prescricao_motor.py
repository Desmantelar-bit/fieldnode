"""Motor de regras determinísticas CAN; não utiliza machine learning.

Os limites são referências ilustrativas de protótipo e exigem validação por
fabricante/modelo e dados de campo antes de qualquer uso operacional.
"""
from api_tcc.services.can_motor import estimar_horas_ate_limite

# Limites de demonstração, não calibrados. Ver docs/can_motor.md.
LIMITES_PROTOCOLO = {
    "liquido_temp_c": {"atencao": 105.0, "critico": 112.0},
    "oleo_pressao_kpa": {"atencao_baixo": 180.0, "critico_baixo": 120.0},
    "oleo_temp_c": {"atencao": 115.0, "critico": 130.0},
    "rail_pressao_kpa": {"atencao_baixo": 100_000.0, "critico_baixo": 70_000.0},
    "turbo_pressao_kpa": {"atencao_baixo": 100.0, "critico_baixo": 70.0},
    "escape_temp_c": {"atencao": 650.0, "critico": 800.0},
}

# Referências de fabricante para descrever códigos neste protótipo; não são
# universais e não substituem a tabela SAE/J1939 aplicável ao motor instalado.
DTC_REFERENCIAS = {
    (110, 0): "Temperatura do líquido de arrefecimento alta; referência de aplicação consultada.",
    (100, 1): "Pressão do óleo muito baixa; referência de aplicação consultada.",
    (157, 16): "Pressão de rail baixa; descrição varia por fabricante/aplicação.",
    (102, 18): "Pressão do coletor de admissão baixa; referência de aplicação consultada.",
}
SUBSISTEMAS = {
    "arrefecimento": "Arrefecimento",
    "lubrificacao": "Lubrificação",
    "combustivel_alta_pressao": "Combustível de alta pressão",
    "admissao": "Admissão",
}


def _nivel_evidencia(sinais):
    """Conta canais físicos distintos concordantes; não estima independência estatística."""
    grupos = {item["grupo"] for item in sinais if item.get("concorda")}
    if len(grupos) >= 3:
        return "ALTA"
    if len(grupos) == 2:
        return "MEDIA"
    return "BAIXA"


def _prescricao(chave, leituras):
    atual = leituras[-1] if leituras else None
    indisponiveis = []
    sinais = []
    status = "NORMAL"
    diagnostico = "Os sinais disponíveis não cruzaram as regras de referência deste protótipo."
    acao = "Manter monitoramento conforme o plano de manutenção do fabricante."
    prazo = "Monitoramento"
    estimativa = None
    limite_referencia = None
    motivo_estimativa = "Sem condição em tendência que permita projetar um limite."
    referencias = LIMITES_PROTOCOLO

    if atual is None:
        return {
            "subsistema": chave,
            "status": None,
            "evidencia_nivel": "BAIXA",
            "sinais_usados": [],
            "sinais_indisponiveis": ["nenhuma leitura válida disponível"],
            "horas_ate_limite": None,
            "limite_referencia": None,
            "motivo_estimativa": "estimativa indisponível: não há leituras válidas",
            "diagnostico": "Prescrição indisponível: ausência de dados não significa condição normal.",
            "acao": "Verificar conectividade e qualidade da telemetria antes de decidir manutenção.",
            "prazo": "Monitoramento",
            "dtcs_relacionados": [],
        }

    def valor(campo, titulo, grupo, predicate):
        dado = getattr(atual, campo)
        if dado is None:
            indisponiveis.append(titulo)
            return False
        concorda = bool(predicate(dado))
        sinais.append({
            "sinal": campo,
            "valor": dado,
            "unidade": _unidade(campo),
            "concorda": concorda,
            "grupo": grupo,
        })
        return concorda

    codigo = None
    campo_estimativa = None
    limite = None
    direcao = None

    if chave == "arrefecimento":
        temp = valor(
            "liquido_temp_c", "temperatura do líquido", "temperatura",
            lambda v: v >= referencias["liquido_temp_c"]["atencao"],
        )
        nivel_baixo = valor(
            "liquido_nivel_pct", "nível do líquido", "nível", lambda v: v <= 10,
        )
        temp_critica = (
            atual.liquido_temp_c is not None
            and atual.liquido_temp_c >= referencias["liquido_temp_c"]["critico"]
        )
        if temp and nivel_baixo and temp_critica:
            status = "CRITICO"
            diagnostico = "Temperatura acima da referência crítica e nível baixo concordam; investigar o arrefecimento sem presumir uma causa específica."
        elif temp or nivel_baixo:
            status = "ATENCAO"
            diagnostico = "Um sinal cruzou a referência do protótipo; confirmar a condição com inspeção e outra evidência independente."
        if status != "NORMAL":
            acao = "Inspecionar nível, vazamentos, radiador e fluxo de ar; seguir limites do fabricante."
            prazo = "Imediata" if status == "CRITICO" else "Monitoramento"
            codigo = (110, 0) if temp else None
            campo_estimativa, limite, direcao = (
                "liquido_temp_c", referencias["liquido_temp_c"]["critico"], "alto"
            )

    elif chave == "lubrificacao":
        pressao_baixa = valor(
            "oleo_pressao_kpa", "pressão do óleo", "pressão",
            lambda v: v <= referencias["oleo_pressao_kpa"]["atencao_baixo"],
        )
        temp_alta = valor(
            "oleo_temp_c", "temperatura do óleo", "temperatura",
            lambda v: v >= referencias["oleo_temp_c"]["atencao"],
        )
        nivel_baixo = valor(
            "oleo_nivel_pct", "nível do óleo", "nível", lambda v: v <= 10,
        )
        pressao_critica = (
            atual.oleo_pressao_kpa is not None
            and atual.oleo_pressao_kpa <= referencias["oleo_pressao_kpa"]["critico_baixo"]
        )
        temp_critica = (
            atual.oleo_temp_c is not None
            and atual.oleo_temp_c >= referencias["oleo_temp_c"]["critico"]
        )
        nivel_critico = atual.oleo_nivel_pct is not None and atual.oleo_nivel_pct <= 5
        condicao_critica = pressao_baixa and (
            temp_critica
            or nivel_critico
            or (pressao_critica and (temp_alta or nivel_baixo))
            or (temp_alta and nivel_baixo)
        )
        if condicao_critica:
            status = "CRITICO"
            diagnostico = "Pressão baixa concorda com um sinal severo de temperatura ou nível; investigar imediatamente, sem atribuir causa apenas à telemetria."
        elif pressao_baixa or temp_alta or nivel_baixo:
            status = "ATENCAO"
            diagnostico = "Um sinal de lubrificação cruzou a referência do protótipo; confirmar regime, sensor e especificação do motor."
        if status != "NORMAL":
            acao = "Verificar nível, pressão com instrumento adequado, filtro e condição do óleo; seguir procedimento do fabricante."
            prazo = "Imediata" if status == "CRITICO" else "Monitoramento"
            codigo = (100, 1) if pressao_baixa else None
            campo_estimativa, limite, direcao = (
                "oleo_pressao_kpa", referencias["oleo_pressao_kpa"]["critico_baixo"], "baixo"
            )

    elif chave == "combustivel_alta_pressao":
        rail_baixo = valor(
            "rail_pressao_kpa", "pressão do rail", "pressão",
            lambda v: v <= referencias["rail_pressao_kpa"]["atencao_baixo"],
        )
        if rail_baixo:
            status = "ATENCAO"
            diagnostico = "Pressão de rail cruzou a referência do protótipo; confirmar pressão-alvo, carga e documentação do fabricante."
        if status != "NORMAL":
            acao = "Verificar filtros, alimentação e sistema de alta pressão conforme procedimento autorizado do fabricante."
            prazo = "Monitoramento"
            codigo = (157, 16) if rail_baixo else None
            campo_estimativa, limite, direcao = (
                "rail_pressao_kpa", referencias["rail_pressao_kpa"]["critico_baixo"], "baixo"
            )

    elif chave == "admissao":
        turbo_baixo = valor(
            "turbo_pressao_kpa", "pressão do turbo", "pressão",
            lambda v: v <= referencias["turbo_pressao_kpa"]["atencao_baixo"],
        )
        escape_alto = valor(
            "escape_temp_c", "temperatura de escape", "temperatura",
            lambda v: v >= referencias["escape_temp_c"]["atencao"],
        )
        turbo_critico = (
            atual.turbo_pressao_kpa is not None
            and atual.turbo_pressao_kpa <= referencias["turbo_pressao_kpa"]["critico_baixo"]
        )
        escape_critico = (
            atual.escape_temp_c is not None
            and atual.escape_temp_c >= referencias["escape_temp_c"]["critico"]
        )
        if turbo_baixo and escape_alto:
            status = "CRITICO" if turbo_critico and escape_critico else "ATENCAO"
            diagnostico = "Pressão de admissão reduzida e temperatura de escape elevada justificam inspeção; a hipótese não confirma falha do turbo."
        elif turbo_baixo or escape_alto:
            status = "ATENCAO"
            diagnostico = "Um sinal cruzou a referência do protótipo; verificar carga e qualidade dos sensores antes de concluir."
        if status != "NORMAL":
            acao = "Inspecionar filtro e dutos de admissão, vazamentos e turbocompressor conforme manual do fabricante."
            prazo = "Imediata" if status == "CRITICO" else "Monitoramento"
            codigo = (102, 18) if turbo_baixo else None
            campo_estimativa, limite, direcao = (
                "turbo_pressao_kpa", referencias["turbo_pressao_kpa"]["critico_baixo"], "baixo"
            )

    evidencia = _nivel_evidencia(sinais)
    if status == "ATENCAO" and evidencia == "BAIXA":
        diagnostico += " Evidência baixa: há apenas um grupo de medição concordante."

    if campo_estimativa:
        estimativa, motivo_estimativa = estimar_horas_ate_limite(
            atual, leituras, campo_estimativa, limite, direcao,
        )
        limite_referencia = {
            "sinal": campo_estimativa,
            "valor": limite,
            "unidade": _unidade(campo_estimativa),
            "direcao": "acima" if direcao == "alto" else "abaixo",
            "origem": "Referência ilustrativa do protótipo; validar para o fabricante e modelo.",
        }

    relacionados = []
    if codigo:
        relacionados = [{
            "spn": codigo[0],
            "fmi": codigo[1],
            "descricao_referencia": DTC_REFERENCIAS[codigo],
        }]

    return {
        "subsistema": chave,
        "status": status,
        "evidencia_nivel": evidencia,
        "sinais_usados": [{k: v for k, v in item.items() if k != "grupo"} for item in sinais],
        "sinais_indisponiveis": indisponiveis,
        "horas_ate_limite": estimativa,
        "limite_referencia": limite_referencia,
        "motivo_estimativa": motivo_estimativa,
        "diagnostico": diagnostico,
        "acao": acao,
        "prazo": prazo,
        "dtcs_relacionados": relacionados,
    }


def _unidade(campo):
    if campo.endswith("_kpa"):
        return "kPa"
    if campo.endswith("_temp_c") or campo.endswith("_c"):
        return "°C"
    if campo.endswith("_pct"):
        return "%"
    if campo == "consumo_lh":
        return "L/h"
    return "h" if campo == "horimetro_h" else "rpm"


def gerar_prescricoes(leituras):
    """Gera recomendações determinísticas sem persistir efeitos colaterais."""
    return [_prescricao(chave, leituras) for chave in SUBSISTEMAS]
