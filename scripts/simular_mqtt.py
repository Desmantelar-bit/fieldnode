"""
Simulador MQTT - FieldNode
===========================

Envia dados variados de telemetria via MQTT para o broker local.
Use enquanto o mqtt_listen.py está rodando.

Uso:
    python scripts/simular_mqtt.py

Cenários simulados:
    - CASE-TC5000-01: Operação normal
    - CASE-TC5070-01: Atenção (temperatura elevada)
    - NH-CR9000-01: Crítico (superaquecimento)
    - JD-S780-01: Normal com variação
"""

import paho.mqtt.client as mqtt
import json
import uuid
import time
import random
from datetime import datetime

BROKER = 'localhost'
PORT = 1883

# Cenários de operação
CENARIOS = {
    "CASE-TC5000-01": {
        "temp": (68, 76), "vib": (0.25, 0.45), "rpm": (1750, 1950)
    },
    "CASE-TC5070-01": {
        "temp": (74, 82), "vib": (0.40, 0.70), "rpm": (1600, 1900)
    },
    "NH-CR9000-01": {
        "temp": (85, 93), "vib": (0.75, 0.95), "rpm": (1100, 1300)
    },
    "JD-S780-01": {
        "temp": (68, 78), "vib": (0.30, 0.54), "rpm": (1700, 1940)
    },
}

def gerar_leitura(maquina_id, cenario):
    return {
        "id": str(uuid.uuid4()),
        "maquina_id": maquina_id,
        "temperatura": round(random.uniform(*cenario["temp"]), 1),
        "vibracao": round(random.uniform(*cenario["vib"]), 2),
        "rpm": int(random.uniform(*cenario["rpm"])),
        "timestamp": datetime.utcnow().isoformat() + "Z"
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
