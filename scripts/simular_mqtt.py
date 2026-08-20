"""
Simulador MQTT - FieldNode
===========================

Envia dados variados de telemetria via MQTT para o broker local.
Use enquanto o mqtt_listen.py está rodando.

Uso:
    python scripts/simular_mqtt.py

Cenários simulados:
    - COLH-01 a COLH-08: IDs compatíveis com scripts/popular_banco.py
    - Cada máquina recebe uma posição-base e pequeno deslocamento GPS simulado.
"""

import paho.mqtt.client as mqtt
import json
import uuid
import time
import random
import os
import requests
from datetime import datetime, timezone

BROKER = os.getenv('MQTT_BROKER', 'localhost')
PORT = int(os.getenv('MQTT_PORT', '1883'))
API_URL = os.getenv('FIELDNODE_API_URL', 'http://127.0.0.1:8000/api/telemetria/')
API_KEY = os.getenv('FIELDNODE_API_KEY', '00000000-0000-4000-8000-000000000000')
DEMO_CYCLES = int(os.getenv('DEMO_CYCLES', '0'))

DEMO_ROUTE = [
    {"lat": -15.793889, "lng": -47.882778, "status": "operando"},
    {"lat": -15.795500, "lng": -47.885000, "status": "parada"},
    {"lat": -15.798000, "lng": -47.888500, "status": "operando"},
    {"lat": -15.801000, "lng": -47.892000, "status": "parada"},
    {"lat": -15.803500, "lng": -47.889500, "status": "operando"},
    {"lat": -15.802000, "lng": -47.885000, "status": "offline"},
    {"lat": -15.799000, "lng": -47.881500, "status": "parada"},
    {"lat": -15.796000, "lng": -47.879000, "status": "operando"},
    {"lat": -15.794000, "lng": -47.881000, "status": "parada"},
    {"lat": -15.793889, "lng": -47.882778, "status": "operando"},
]

# Cenários de operação
CENARIOS = {
    "COLH-01": {
        "temp": (68, 76), "vib": (0.25, 0.45), "rpm": (1750, 1950),
        "lat": -15.793889, "lng": -47.882778
    },
    "COLH-02": {
        "temp": (74, 82), "vib": (0.40, 0.70), "rpm": (1600, 1900),
        "lat": -15.800000, "lng": -47.890000
    },
    "COLH-03": {
        "temp": (85, 93), "vib": (0.75, 0.95), "rpm": (1100, 1300),
        "lat": -15.810000, "lng": -47.870000
    },
    "COLH-04": {
        "temp": (70, 78), "vib": (0.30, 0.50), "rpm": (1650, 1850),
        "lat": -15.775000, "lng": -47.905000
    },
    "COLH-05": {
        "temp": (76, 84), "vib": (0.45, 0.65), "rpm": (1550, 1750),
        "lat": -15.820000, "lng": -47.860000
    },
    "COLH-06": {
        "temp": (72, 80), "vib": (0.35, 0.55), "rpm": (1700, 1900),
        "lat": -15.785000, "lng": -47.875000
    },
    "COLH-07": {
        "temp": (69, 77), "vib": (0.28, 0.48), "rpm": (1750, 1950),
        "lat": -15.798000, "lng": -47.895000
    },
    "COLH-08": {
        "temp": (78, 86), "vib": (0.50, 0.75), "rpm": (1500, 1700),
        "lat": -15.812000, "lng": -47.865000
    },
}

def gerar_leitura(maquina_id, cenario):
    lat_base = cenario.get("lat", -15.793889)
    lng_base = cenario.get("lng", -47.882778)
    lat_drift = random.uniform(-0.0005, 0.0005)
    lng_drift = random.uniform(-0.0005, 0.0005)
    return {
        "id": str(uuid.uuid4()),
        "maquina_id": maquina_id,
        "temperatura": round(random.uniform(*cenario["temp"]), 1),
        "vibracao": round(random.uniform(*cenario["vib"]), 2),
        "rpm": int(random.uniform(*cenario["rpm"])),
        "latitude": round(lat_base + lat_drift, 6),
        "longitude": round(lng_base + lng_drift, 6),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def gerar_leitura_demo(maquina_id, ponto):
    lat_drift = random.uniform(-0.0001, 0.0001)
    lng_drift = random.uniform(-0.0001, 0.0001)
    if ponto["status"] == "offline":
        temp_range, vib_range, rpm_range = (65, 72), (0.20, 0.35), (0, 800)
    elif ponto["status"] == "parada":
        temp_range, vib_range, rpm_range = (70, 80), (0.25, 0.50), (900, 1400)
    else:
        temp_range, vib_range, rpm_range = (68, 88), (0.30, 0.75), (1500, 2000)

    return {
        "id": str(uuid.uuid4()),
        "maquina_id": maquina_id,
        "temperatura": round(random.uniform(*temp_range), 1),
        "vibracao": round(random.uniform(*vib_range), 2),
        "rpm": int(random.uniform(*rpm_range)),
        "latitude": round(ponto["lat"] + lat_drift, 6),
        "longitude": round(ponto["lng"] + lng_drift, 6),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

def enviar_para_api(leitura):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Key": API_KEY,
    }
    response = requests.post(API_URL, headers=headers, json=leitura, timeout=10)
    response.raise_for_status()
    return response

def loop_fallback_api():
    print("Modo demo GPS ativo: enviando rota simulada diretamente para a API Django.")
    print(f"API: {API_URL}\n")

    ciclo = 0
    while True:
        for idx, ponto in enumerate(DEMO_ROUTE):
            maquina_id = f"COLH-{str(idx + 1).zfill(2)}"
            leitura = gerar_leitura_demo(maquina_id, ponto)

            try:
                enviar_para_api(leitura)
                print(
                    f"DEMO {maquina_id}: {leitura['latitude']}, {leitura['longitude']} | "
                    f"{leitura['temperatura']}°C | {leitura['rpm']} RPM"
                )
            except Exception as api_error:
                print(f"Falha ao enviar demo para API ({maquina_id}): {api_error}")

            time.sleep(0.5)

        ciclo += 1
        print(f"\n--- Ciclo demo {ciclo} concluído ---\n")
        if DEMO_CYCLES and ciclo >= DEMO_CYCLES:
            print("Modo demo encerrado por DEMO_CYCLES.")
            return
        time.sleep(2)

def main():
    client = mqtt.Client()
    
    try:
        client.connect(BROKER, PORT, 60)
        print(f"✓ Conectado ao broker MQTT em {BROKER}:{PORT}")
        print("Enviando leituras variadas... (Ctrl+C para parar)\n")
        
        contador = 0
        while True:
            for maquina_id, cenario in CENARIOS.items():
                leitura = gerar_leitura(maquina_id, cenario)
                topico = f"fieldnode/{maquina_id}/leitura"
                
                client.publish(topico, json.dumps(leitura))
                
                status = "🔴 CRÍTICO" if leitura["temperatura"] > 85 else \
                         "🟡 ATENÇÃO" if leitura["temperatura"] > 75 else "🟢 NORMAL"
                
                print(f"{status} {maquina_id}: {leitura['temperatura']}°C | "
                      f"{leitura['vibracao']}g | {leitura['rpm']} RPM")
                
                time.sleep(0.5)
            
            contador += 1
            print(f"\n--- Ciclo {contador} concluído ---\n")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n✓ Simulação encerrada")
    except Exception as e:
        print(f"\n✗ MQTT indisponível: {e}")
        loop_fallback_api()
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
