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
from datetime import datetime, timezone

BROKER = 'localhost'
PORT = 1883

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
        print(f"\n✗ Erro: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
