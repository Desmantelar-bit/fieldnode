"""Validação e consultas para o protótipo de telemetria CAN do motor.

As faixas abaixo são limites de plausibilidade de bancada, não especificações
validadas de um fabricante. Ausências parciais são informadas sem descartar
uma amostra que ainda contenha sinais utilizáveis.
"""
from collections import Counter, deque
import math

from api_tcc.models import LeituraCANMotor

SENSOR_RANGES = {
    "rpm": (0, 6000),
    "carga_pct": (0, 100),
    "horimetro_h": (0, 1_000_000),
    "oleo_pressao_kpa": (0, 3000),
    "oleo_temp_c": (-40, 250),
    "oleo_nivel_pct": (0, 100),
    "liquido_temp_c": (-40, 180),
    "liquido_nivel_pct": (0, 100),
    "rail_pressao_kpa": (0, 500_000),
    "combustivel_temp_c": (-40, 150),
    "consumo_lh": (0, 500),
    "turbo_pressao_kpa": (0, 1000),
    "escape_temp_c": (-40, 1200),
    "bateria_v": (0, 40),
}
def validar_leitura(leitura, historico=None):
    """Retorna validade, motivos, ausências e sinais congelados da leitura."""
    motivos = []
    ausentes = []
    maquina_id = getattr(leitura, "maquina_id", None)
    timestamp = getattr(leitura, "timestamp", None)
    if not isinstance(maquina_id, str) or not maquina_id.strip():
        motivos.append("maquina_id_ausente_ou_invalido")
    if timestamp is None:
        motivos.append("timestamp_ausente")

    presentes = 0
    for campo, (minimo, maximo) in SENSOR_RANGES.items():
        valor = getattr(leitura, campo, None)
        if valor is None:
            ausentes.append(campo)
            continue
        presentes += 1
        if isinstance(valor, bool):
            motivos.append(f"{campo}_nao_numerico")
            continue
        try:
            numero = float(valor)
        except (TypeError, ValueError, OverflowError):
            motivos.append(f"{campo}_nao_numerico")
            continue
        if not math.isfinite(numero):
            motivos.append(f"{campo}_nao_finito")
        elif not minimo <= numero <= maximo:
            motivos.append(f"{campo}_fora_faixa_fisica")

    if presentes == 0:
        motivos.append("todos_sinais_ausentes")

    congelados = []
    if historico is not None:
        amostras = list(historico)
        for campo in SENSOR_RANGES:
            valor = getattr(leitura, campo, None)
            if valor is None:
                continue
            sequencia = [getattr(item, campo, None) for item in amostras[-4:]]
            if len(sequencia) == 4 and all(item is not None and item == valor for item in sequencia):
                congelados.append(campo)
        if congelados:
            motivos.extend(f"sinal_congelado:{campo}" for campo in congelados)

    return {
        "valida": not motivos,
        "motivos": motivos,
        "campos_ausentes": ausentes,
        "sinais_congelados": congelados,
    }


def resumir_qualidade(maquina_id):
    registros = LeituraCANMotor.objects.filter(maquina_id=maquina_id).order_by("timestamp", "id")
    recebidas = 0
    validas, descartadas = 0, 0
    motivos = Counter()
    campos_ausentes = Counter()
    congelados = Counter()
    validas_recentes = deque(maxlen=120)
    anteriores = deque(maxlen=4)
    for leitura in registros.iterator(chunk_size=1000):
        recebidas += 1
        resultado = validar_leitura(leitura, anteriores)
        if resultado["valida"]:
            validas += 1
            validas_recentes.append(leitura)
        else:
            descartadas += 1
            for motivo in resultado["motivos"]:
                motivos[motivo] += 1
        for campo in resultado["campos_ausentes"]:
            campos_ausentes[campo] += 1
        for campo in resultado["sinais_congelados"]:
            congelados[campo] += 1
        anteriores.append(leitura)
    return {
        "recebidas": recebidas,
        "aceitas": validas,
        "descartadas": descartadas,
        "motivos": dict(sorted(motivos.items())),
        "campos_ausentes": dict(sorted(campos_ausentes.items())),
        "sinais_congelados": dict(sorted(congelados.items())),
        "_validas_recentes": list(validas_recentes),
    }


def estimar_horas_ate_limite(leitura_atual, leituras, campo, limite, direcao):
    """Regressão linear em horímetro. Retorna null quando não há suporte suficiente."""
    if limite is None:
        return None, "limite de referência do protótipo não definido"
    pontos = [
        (item.horimetro_h, getattr(item, campo))
        for item in leituras[-60:]
        if item.horimetro_h is not None and getattr(item, campo) is not None
    ]
    if len(pontos) < 12:
        return None, "menos de 12 observações válidas com horímetro e sinal disponíveis"
    xs, ys = zip(*pontos)
    if max(xs) - min(xs) < 0.5:
        return None, "intervalo de horímetro inferior a 0,5 h"
    if any(xs[i] <= xs[i - 1] for i in range(1, len(xs))):
        return None, "horímetro não é estritamente crescente"
    media_x, media_y = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - media_x) ** 2 for x in xs)
    if not sxx:
        return None, "variação insuficiente do horímetro"
    inclinacao = sum((x - media_x) * (y - media_y) for x, y in pontos) / sxx
    if (direcao == "baixo" and inclinacao >= 0) or (direcao == "alto" and inclinacao <= 0):
        return None, "tendência não se aproxima do limite indicado"
    intercepto = media_y - inclinacao * media_x
    previsoes = [intercepto + inclinacao * x for x in xs]
    ss_res = sum((y - p) ** 2 for y, p in zip(ys, previsoes))
    ss_tot = sum((y - media_y) ** 2 for y in ys)
    r2 = 0.0 if ss_tot == 0 else 1 - ss_res / ss_tot
    if r2 < 0.60:
        return None, "tendência inconsistente (R² abaixo de 0,60)"
    if ss_res > 0 and len(pontos) > 2:
        erro_padrao = math.sqrt((ss_res / (len(pontos) - 2)) / sxx)
        if erro_padrao and abs(inclinacao / erro_padrao) < 2:
            return None, "inclinação sem evidência suficiente frente à variabilidade observada"
    atual = getattr(leitura_atual, campo)
    horas = (limite - atual) / inclinacao
    if not math.isfinite(horas) or horas <= 0:
        return None, "projeção não cruza o limite futuro"
    return round(horas, 1), "regressão linear das últimas leituras válidas versus horímetro; estimativa de horas de motor, não tempo cronológico"
