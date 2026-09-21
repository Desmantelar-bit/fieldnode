#!/usr/bin/env python
import argparse
import json
import os
import random
import time
import uuid
from datetime import datetime

import requests

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPICO = "fieldnode/COLH-01/leitura"
MAQUINA_ID = "COLH-01"
INTERVALO = 3  # segundos entre leituras
API_URL = "http://127.0.0.1:8000/api/telemetria/"
API_KEY = os.environ.get("FIELDNODE_API_KEY", "fieldnode-demo-2024")


def gerar_leitura(ciclo: int) -> dict:
    t = ciclo * INTERVALO  # tempo em segundos

    if t < 40:
        # Fase 1: operacao normal
        temp = 65 + (t / 40) * 7 + random.uniform(-1.5, 1.5)
        vib = random.uniform(0.05, 0.25)
        rpm = 1800 + random.randint(-200, 200)

    elif t < 80:
        # Fase 2: aquecimento progressivo - ATENCAO
        prog = (t - 40) / 40
        temp = 72 + prog * 13 + random.uniform(-1, 1)
        vib = 0.25 + prog * 0.35 + random.uniform(-0.05, 0.05)
        rpm = 1800 + random.randint(-300, 100)

    elif t < 120:
        # Fase 3: zona critica - CRITICO
        prog = (t - 80) / 40
        temp = 85 + prog * 7 + random.uniform(-0.5, 0.5)
        vib = 0.60 + random.uniform(0, 0.35)
        rpm = 1500 + random.randint(-400, -100)

    else:
        # Fase 4: operador intervem, resfriamento
        prog = min((t - 120) / 60, 1.0)
        temp = 92 - prog * 25 + random.uniform(-1, 1)
        vib = 0.60 - prog * 0.45 + random.uniform(-0.05, 0.05)
        rpm = 1500 + int(prog * 400) + random.randint(-100, 100)

    return {
        "id": str(uuid.uuid4()),
        "maquina_id": MAQUINA_ID,
        "temperatura": round(max(40, temp), 1),
        "vibracao": round(max(0, min(1.0, vib)), 2),
        "rpm": max(800, rpm),
        "timestamp": datetime.now().isoformat(),
    }


def verificar_prescricao(maquina_id):
    try:
        r = requests.get(
            f"http://127.0.0.1:8000/api/prescricoes/?maquina_id={maquina_id}",
            headers={"X-API-Key": API_KEY},
            timeout=3,
        )
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def _enviar_http(leitura: dict) -> None:
    """Envia leitura diretamente para a API REST (modo --http)."""
    try:
        r = requests.post(
            API_URL,
            json=leitura,
            headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
            timeout=5,
        )
        status = r.json().get("status", "?")
        print(f"  -> HTTP {r.status_code} | {status}")
    except Exception as exc:
        print(f"  -> HTTP erro: {exc}")


def _loop(publish_fn, ciclos):
    ciclo = 0
    try:
        while ciclos is None or ciclo < ciclos:
            leitura = gerar_leitura(ciclo)
            t = ciclo * INTERVALO
            fase = "NORMAL" if t < 40 else "ATENCAO" if t < 80 else "CRITICO" if t < 120 else "RESFRIANDO"
            print(f"[ciclo {ciclo:03d} | {fase}] temp={leitura['temperatura']}C vib={leitura['vibracao']} rpm={leitura['rpm']}")
            publish_fn(leitura)
            if ciclo % 5 == 0:
                p = verificar_prescricao(MAQUINA_ID)
                if p and p.get("status") == "ok" and p.get("severidade", "").upper() == "CRITICO":
                    print(f"  !!! CRITICO {MAQUINA_ID} {p.get('confianca', 0) * 100:.0f}% !!!")
            ciclo += 1
            time.sleep(INTERVALO)
    except KeyboardInterrupt:
        pass


def main():
    parser = argparse.ArgumentParser(description="Demo pane FieldNode")
    parser.add_argument("--http", action="store_true", help="Envia via HTTP direto (sem Mosquitto)")
    parser.add_argument("--ciclos", type=int, default=None, help="Numero de ciclos (padrao: infinito)")
    args = parser.parse_args()

    if args.http:
        print(f"[HTTP] enviando para {API_URL}")
        _loop(_enviar_http, args.ciclos)
        return

    # Modo MQTT (padrao)
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        print("paho-mqtt nao instalado. Use --http ou: pip install paho-mqtt")
        return

    client = mqtt.Client()
    try:
        client.connect(BROKER_HOST, BROKER_PORT)
        client.loop_start()
        print(f"[OK] Conectado ao Broker MQTT em {BROKER_HOST}:{BROKER_PORT}")
    except Exception:
        print(f"[ERRO] Mosquitto inacessivel em {BROKER_HOST}:{BROKER_PORT}. Use --http para modo sem broker.")
        return

    try:
        _loop(lambda l: client.publish(TOPICO, json.dumps(l)), args.ciclos)
    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
