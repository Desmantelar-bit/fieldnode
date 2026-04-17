#!/usr/bin/env python
"""
FieldNode — Script de Demo de Pane para a Banca

Simula uma colheitadeira aquecendo gradualmente até atingir
zona crítica em ~2 minutos, depois se recuperando.

Como rodar (com Django e mqtt_listen rodando):
    python scripts/demo_pane.py

O que você vai ver:
    → temperatura subindo de 65°C até 92°C
    → nível mudando de NORMAL → ATENCAO → CRITICO
    → dashboard atualizando automaticamente
    → vibração com picos de anomalia no trecho crítico
"""
import json
import math
import random
import time
import uuid
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("❌ Erro: paho-mqtt não está instalado.")
    print("Execute: pip install paho-mqtt")
    exit(1)

BROKER_HOST = 'localhost'
BROKER_PORT  = 1883
TOPICO       = 'fieldnode/COLH-01/leitura'
MAQUINA_ID   = 'COLH-01'
INTERVALO    = 3  # segundos entre leituras

# ─────────────────────────────────────────────────────────────
# SCRIPT DE PANE
# Fase 1 (0-40s):   temperatura normal, 65-72°C, vibracao baixa
# Fase 2 (40-80s):  temperatura subindo, 72-85°C, vibracao média
# Fase 3 (80-120s): zona critica, 85-92°C, vibracao alta com picos
# Fase 4 (120s+):   resfriamento, simula intervenção do operador
# ─────────────────────────────────────────────────────────────

def gerar_leitura(ciclo: int) -> dict:
    t = ciclo * INTERVALO  # tempo em segundos

    if t < 40:
        # Fase 1: operação normal
        temp = 65 + (t / 40) * 7 + random.uniform(-1.5, 1.5)
        vib  = random.uniform(0.05, 0.25)
        rpm  = 1800 + random.randint(-200, 200)

    elif t < 80:
        # Fase 2: aquecimento progressivo — ATENÇÃO
        prog = (t - 40) / 40
        temp = 72 + prog * 13 + random.uniform(-1, 1)
        vib  = 0.25 + prog * 0.35 + random.uniform(-0.05, 0.05)
        rpm  = 1800 + random.randint(-300, 100)

    elif t < 120:
        # Fase 3: zona crítica — CRITICO
        prog = (t - 80) / 40
        temp = 85 + prog * 7 + random.uniform(-0.5, 0.5)
        vib  = 0.60 + random.uniform(0, 0.35)   # picos de vibração
        rpm  = 1500 + random.randint(-400, -100)  # RPM caindo

    else:
        # Fase 4: operador intervém, resfriamento
        prog = min((t - 120) / 60, 1.0)
        temp = 92 - prog * 25 + random.uniform(-1, 1)
        vib  = 0.60 - prog * 0.45 + random.uniform(-0.05, 0.05)
        rpm  = 1500 + int(prog * 400) + random.randint(-100, 100)

    return {
        'id':          str(uuid.uuid4()),
        'maquina_id':  MAQUINA_ID,
        'temperatura': round(max(40, temp), 1),
        'vibracao':    round(max(0, min(1.0, vib)), 2),
        'rpm':         max(800, rpm),
        'timestamp':   datetime.now().isoformat(),
    }


def main():
    print()
    print('=' * 42)
    print('  FIELDNODE - DEMO DE PANE')
    print('  Simulacao de falha progressiva em campo')
    print('=' * 42)
    print()
    print(f'  Broker: {BROKER_HOST}:{BROKER_PORT}')
    print(f'  Topico: {TOPICO}')
    print(f'  Maquina: {MAQUINA_ID}')
    print()
    print('  Fases:')
    print('  00-40s  -> NORMAL (65-72°C)')
    print('  40-80s  -> ATENCAO (72-85°C)')
    print('  80-120s -> CRITICO (85-92°C)')
    print('  120s+   -> Recuperacao (operador intervem)')
    print()

    client = mqtt.Client()
    client.connect(BROKER_HOST, BROKER_PORT)
    client.loop_start()

    ciclo = 0
    try:
        while True:
            leitura  = gerar_leitura(ciclo)
            payload  = json.dumps(leitura)
            t_seg    = ciclo * INTERVALO

            fase = (
                'CRITICO' if leitura['temperatura'] > 85 else
                'ATENCAO' if leitura['temperatura'] > 75 else
                'NORMAL'
            )

            print(f'[{t_seg:>4}s] {fase}  '
                  f'{leitura["temperatura"]:>5.1f}°C  '
                  f'vib={leitura["vibracao"]:.2f}  '
                  f'rpm={leitura["rpm"]}')

            client.publish(TOPICO, payload)
            ciclo += 1
            time.sleep(INTERVALO)

    except KeyboardInterrupt:
        print('\n[Demo] Encerrado.')
        client.loop_stop()


if __name__ == '__main__':
    main()