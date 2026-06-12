#!/usr/bin/env python
"""
Teste rápido do sistema de busca
Envia dados de todas as máquinas para testar o autocomplete
"""
import paho.mqtt.client as mqtt
import json
import uuid
import time
from datetime import datetime

BROKER = 'localhost'
PORT = 1883

MAQUINAS = [
    "CASE-TC5000-01",
    "CASE-TC5070-01", 
    "NH-CR9000-01",
    "NH-CR8090-02",
    "NH-CR7090-03",
    "VALTRA-BC8800-01",
    "VALTRA-BC6800-02",
    "VALTRA-BC5800-03"
]

def enviar_leitura_teste(client, maquina_id):
    leitura = {
        "id": str(uuid.uuid4()),
        "maquina_id": maquina_id,
        "temperatura": 75.0,
        "vibracao": 0.45,
        "rpm": 1800,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    topico = f"fieldnode/{maquina_id}/leitura"
    client.publish(topico, json.dumps(leitura))
    print(f"✓ {maquina_id}")

def main():
    print("\n=== TESTE DE BUSCA - FIELDNODE ===\n")
    print("Enviando leitura inicial para todas as máquinas...\n")
    
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    
    for maquina in MAQUINAS:
        enviar_leitura_teste(client, maquina)
        time.sleep(0.2)
    
    print("\n✓ Todas as máquinas foram registradas!")
    print("\nAgora você pode testar a busca no dashboard:")
    print("  - Digite 'CASE' para ver as máquinas CASE")
    print("  - Digite 'NH' para ver as New Holland")
    print("  - Digite 'VALTRA' para ver as Valtra")
    print("\nIniciando simulador contínuo...\n")
    
    client.disconnect()

if __name__ == "__main__":
    main()
