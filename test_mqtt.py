#!/usr/bin/env python
"""
Script para testar envio de mensagem MQTT
"""
import json
import uuid
from datetime import datetime
import paho.mqtt.client as mqtt

# Configuração
BROKER_HOST = 'localhost'
BROKER_PORT = 1883
TOPICO = 'fieldnode/COLH-01/leitura'

# Mensagem de teste
mensagem = {
    'id': str(uuid.uuid4()),
    'maquina_id': 'COLH-01',
    'temperatura': 85.5,
    'vibracao': 0.65,
    'rpm': 1750,
    'timestamp': datetime.now().isoformat()
}

def enviar_teste():
    client = mqtt.Client()
    
    try:
        print(f"Conectando ao broker {BROKER_HOST}:{BROKER_PORT}...")
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        
        payload = json.dumps(mensagem)
        print(f"Enviando para tópico: {TOPICO}")
        print(f"Payload: {payload}")
        
        result = client.publish(TOPICO, payload)
        
        if result.rc == 0:
            print("✅ Mensagem enviada com sucesso!")
        else:
            print(f"❌ Erro ao enviar: {result.rc}")
            
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    enviar_teste()