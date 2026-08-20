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
    - NH-CR8090-02: Operação normal
    - NH-CR7090-03: Atenção (temperatura elevada)
    - VALTRA-BC8800-01: Operação normal
    - VALTRA-BC6800-02: Operação normal
    - VALTRA-BC5800-03: Atenção (temperatura elevada)
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
    "CASE-TC5000-01": {
        "temp": (68, 76), "vib": (0.25, 0.45), "rpm": (1750, 1950)
    },
    "CASE-TC5070-01": {
        "temp": (74, 82), "vib": (0.40, 0.70), "rpm": (1600, 1900)
    },
    "NH-CR9000-01": {
        "temp": (85, 93), "vib": (0.75, 0.95), "rpm": (1100, 1300)
    },
    "NH-CR8090-02": {
        "temp": (70, 78), "vib": (0.30, 0.50), "rpm": (1650, 1850)
    },
    "NH-CR7090-03": {
        "temp": (76, 84), "vib": (0.45, 0.65), "rpm": (1550, 1750)
    },
    "VALTRA-BC8800-01": {
        "temp": (72, 80), "vib": (0.35, 0.55), "rpm": (1700, 1900)
    },
    "VALTRA-BC6800-02": {
        "temp": (69, 77), "vib": (0.28, 0.48), "rpm": (1750, 1950)
    },
    "VALTRA-BC5800-03": {
        "temp": (78, 86), "vib": (0.50, 0.75), "rpm": (1500, 1700)
    },
}

def gerar_leitura(maquina_id, cenario):
    return {
        "id": str(uuid.uuid4()),
        "maquina_id": maquina_id,
        "temperatura": round(random.uniform(*cenario["temp"]), 1),
        "vibracao": round(random.uniform(*cenario["vib"]), 2),
        "rpm": int(random.uniform(*cenario["rpm"])),
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
