#!/usr/bin/env python
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
import requests

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPICO = "fieldnode/COLH-01/leitura"
MAQUINA_ID = "COLH-01"
INTERVALO = 3  # segundos entre leituras


def gerar_leitura(ciclo: int) -> dict:
    t = ciclo * INTERVALO  # tempo em segundos

    if t < 40:
        # Fase 1: operação normal
        temp = 65 + (t / 40) * 7 + random.uniform(-1.5, 1.5)
        vib = random.uniform(0.05, 0.25)
        rpm = 1800 + random.randint(-200, 200)

    elif t < 80:
        # Fase 2: aquecimento progressivo — ATENÇÃO
        prog = (t - 40) / 40
        temp = 72 + prog * 13 + random.uniform(-1, 1)
        vib = 0.25 + prog * 0.35 + random.uniform(-0.05, 0.05)
        rpm = 1800 + random.randint(-300, 100)

    elif t < 120:
        # Fase 3: zona crítica — CRITICO
        prog = (t - 80) / 40
        temp = 85 + prog * 7 + random.uniform(-0.5, 0.5)
        vib = 0.60 + random.uniform(0, 0.35)  # picos de vibração
        rpm = 1500 + random.randint(-400, -100)  # RPM caindo

    else:
        # Fase 4: operador intervém, resfriamento
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
            headers={"X-API-Key": "fieldnode-demo-2024"},
            timeout=3,
        )
        return r.json() if r.status_code == 200 else None
    except:
        return None


def main():
    client = mqtt.Client()
    try:
        client.connect(BROKER_HOST, BROKER_PORT)
        client.loop_start()
        print(f"✅ Conectado ao Broker MQTT em {BROKER_HOST}:{BROKER_PORT}")
    except Exception as e:
        print(f"❌ ERRO: Não foi possível conectar ao Broker MQTT (Mosquitto).")
        print(
            f"👉 Certifique-se de que o serviço do Mosquitto está rodando na porta {BROKER_PORT}."
        )
        return

    ciclo = 0
    try:
        while True:
            leitura = gerar_leitura(ciclo)
            client.publish(TOPICO, json.dumps(leitura))
            if ciclo % 5 == 0:
                p = verificar_prescricao(MAQUINA_ID)
                if (
                    p
                    and p.get("status") == "ok"
                    and p.get("severidade", "").upper() == "CRITICO"
                ):
                    print(
                        f"!!! CRITICO {MAQUINA_ID} {p.get('confianca', 0) * 100:.0f}% !!!"
                    )
            ciclo += 1
            time.sleep(INTERVALO)
    except KeyboardInterrupt:
        client.loop_stop()


if __name__ == '__main__':
    main()