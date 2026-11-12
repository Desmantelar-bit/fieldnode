#!/usr/bin/env python3
"""Simulador didático de leituras CAN de motor; toda gravação é SIMULADA."""
import argparse
import math
import os
import random
import signal
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
import django  # noqa: E402

django.setup()
from django.db import IntegrityError  # noqa: E402
from django.utils import timezone  # noqa: E402
from api_tcc.models import DTCMotor, LeituraCANMotor  # noqa: E402

CENARIOS = ("normal", "arrefecimento", "lubrificacao", "combustivel", "admissao")
PARAR = False


def _sinal_parar(signum, frame):
    global PARAR
    PARAR = True


def _suavizar(t, inicio, fim):
    x = max(0.0, min(1.0, (t - inicio) / (fim - inicio)))
    return x * x * (3 - 2 * x)


def gerar_leitura(maquina, cenario, fase, inicio, rng, sequencia, intervalo):
    """Gera um snapshot dependente do tempo e de sinais correlacionados."""
    instante = timezone.now()
    horas_desde_inicio = (instante - inicio).total_seconds() / 3600
    carga_base = 35 + 8 * math.sin(sequencia / 23)
    carga = max(15, min(85, carga_base + rng.gauss(0, 2.0)))
    rpm = max(700, 1050 + carga * 13 + rng.gauss(0, 18))
    graduacao = fase
    deterioracao = _suavizar(graduacao, 0.45, 1.0) if cenario != "normal" else 0.0
    oscilacao = math.sin(sequencia / 7) * 0.8 + rng.gauss(0, 0.3)

    liquido_temp = 82 + carga * 0.13 + oscilacao
    liquido_nivel = 92 + rng.gauss(0, 0.4)
    oleo_temp = 88 + carga * 0.10 + rng.gauss(0, 0.6)
    oleo_pressao = 410 - max(0, oleo_temp - 90) * 1.1 + rng.gauss(0, 3)
    oleo_nivel = 91 + rng.gauss(0, 0.3)
    rail = 155_000 + carga * 160 + rng.gauss(0, 1200)
    consumo = max(4, 12 + carga * 0.55 + rng.gauss(0, 0.8))
    turbo = 175 + carga * 1.8 + rng.gauss(0, 2.0)
    escape = 390 + carga * 2.4 + rng.gauss(0, 5)
    combustivel_temp = 42 + rng.gauss(0, 0.5)

    if cenario == "arrefecimento":
        liquido_temp += 29 * deterioracao
        liquido_nivel -= 83 * deterioracao
        carga += 7 * deterioracao
    elif cenario == "lubrificacao":
        oleo_pressao -= 315 * deterioracao
        oleo_temp += 43 * deterioracao
        oleo_nivel -= 7 * deterioracao
    elif cenario == "combustivel":
        rail -= 104_000 * deterioracao
        rail += rng.gauss(0, 3000 * deterioracao)
        consumo += 10 * deterioracao
        combustivel_temp += 16 * deterioracao
    elif cenario == "admissao":
        turbo -= 155 * deterioracao
        escape += 390 * deterioracao + carga * 1.4 * deterioracao

    leitura = {
        "maquina_id": maquina,
        "timestamp": instante,
        "rpm": round(max(0, rpm), 2),
        "carga_pct": round(max(0, min(100, carga)), 2),
        "horimetro_h": round(1200 + horas_desde_inicio, 6),
        "oleo_pressao_kpa": round(oleo_pressao, 2),
        "oleo_temp_c": round(oleo_temp, 2),
        "oleo_nivel_pct": round(oleo_nivel, 2),
        "liquido_temp_c": round(liquido_temp, 2),
        "liquido_nivel_pct": round(liquido_nivel, 2),
        "rail_pressao_kpa": round(max(0, rail), 2),
        "combustivel_temp_c": round(combustivel_temp, 2),
        "consumo_lh": round(consumo, 2),
        "turbo_pressao_kpa": round(max(0, turbo), 2),
        "escape_temp_c": round(escape, 2),
        "bateria_v": round(13.8 + rng.gauss(0, 0.1), 2),
        "simulado": True,
    }
    # 1,5% de leituras com falha explícita: campo ausente, fora de faixa ou congelado.
    if rng.random() < 0.015:
        tipo = rng.choice(("ausente", "fora_faixa", "congelado"))
        campo = rng.choice(("oleo_pressao_kpa", "liquido_temp_c", "rail_pressao_kpa", "turbo_pressao_kpa"))
        if tipo == "ausente":
            leitura[campo] = None
        elif tipo == "fora_faixa":
            leitura["bateria_v"] = 55.0
        else:
            leitura[campo] = 0.0
    return leitura


def simular(maquina="COLH-01", cenario="normal", intervalo=5, duracao=5):
    if intervalo <= 0 or duracao <= 0:
        raise ValueError("intervalo e duracao devem ser positivos")
    inicio = timezone.now()
    total = max(1, math.ceil(duracao * 60 / intervalo))
    rng = random.Random(f"{maquina}:{cenario}:{inicio.isoformat()}")
    DTCMotor.objects.filter(maquina_id=maquina, simulado=True, ativo=True).update(ativo=False)
    gravadas = 0
    dtc_emitido = False
    print(f"Iniciando simulação SIMULADA: máquina={maquina}, cenário={cenario}, duração={duracao} min")
    for i in range(total):
        if PARAR:
            break
        agora = timezone.now()
        fase = i / max(1, total - 1)
        leitura = gerar_leitura(maquina, cenario, fase, inicio, rng, i, intervalo)
        try:
            LeituraCANMotor.objects.create(**leitura)
            gravadas += 1
            codigo = {
                "arrefecimento": (110, 0),
                "lubrificacao": (100, 1),
                "combustivel": (157, 16),
                "admissao": (102, 18),
            }.get(cenario)
            if codigo and fase >= 0.82 and not dtc_emitido:
                spn, fmi = codigo
                dtc, criado = DTCMotor.objects.get_or_create(
                    maquina_id=maquina,
                    spn=spn,
                    fmi=fmi,
                    defaults={
                        "ocorrencias": 1,
                        "ativo": True,
                        "simulado": True,
                        "primeira_vez": leitura["timestamp"],
                        "ultima_vez": leitura["timestamp"],
                    },
                )
                if not criado and not dtc.ativo:
                    dtc.ocorrencias += 1
                    dtc.ativo = True
                    dtc.simulado = True
                    dtc.ultima_vez = leitura["timestamp"]
                    dtc.save(update_fields=["ocorrencias", "ativo", "simulado", "ultima_vez"])
                dtc_emitido = True
        except IntegrityError:
            print("Leitura duplicada para máquina/timestamp ignorada.", file=sys.stderr)
        if (i + 1) % 12 == 0:
            print(f"{i + 1}/{total} amostras geradas; gravações: {gravadas}")
        restante = intervalo - (timezone.now() - agora).total_seconds()
        if i + 1 < total and restante > 0:
            time.sleep(restante)
    print(f"Fim. Gravações SIMULADAS: {gravadas}; encerramento={('Ctrl+C' if PARAR else 'duração concluída')}.")
    return gravadas


def main():
    parser = argparse.ArgumentParser(description="Simulador SIMULADO CAN de motor do FieldNode")
    parser.add_argument("--maquina", default="COLH-01")
    parser.add_argument("--cenario", choices=CENARIOS, default="normal")
    parser.add_argument("--intervalo", type=float, default=5, help="Intervalo em segundos")
    parser.add_argument("--duracao", type=float, default=5, help="Duração em minutos")
    args = parser.parse_args()
    signal.signal(signal.SIGINT, _sinal_parar)
    signal.signal(signal.SIGTERM, _sinal_parar)
    simular(args.maquina.strip().upper(), args.cenario, args.intervalo, args.duracao)


if __name__ == "__main__":
    main()
