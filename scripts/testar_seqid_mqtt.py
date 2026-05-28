#!/usr/bin/env python
"""
Script de teste para validar que seq_id é atribuído via MQTT.

Simula o fluxo completo:
1. Publica mensagem MQTT
2. Aguarda processamento
3. Verifica se seq_id foi atribuído

Uso:
    python scripts/testar_seqid_mqtt.py
"""
import json
import time
import uuid
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("❌ Erro: paho-mqtt não está instalado.")
    print("Execute: pip install paho-mqtt")
    exit(1)

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from api_tcc.models import LeituraTelemetria

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPICO = "fieldnode/TEST-SEQID/leitura"

def testar_mqtt_seqid():
    """Testa se inserções via MQTT recebem seq_id."""
    
    # Gerar UUID único para este teste
    test_uuid = str(uuid.uuid4())
    
    print("=" * 60)
    print("TESTE: seq_id via MQTT")
    print("=" * 60)
    print(f"UUID do teste: {test_uuid}")
    print()
    
    # Criar payload de teste
    payload = {
        "id": test_uuid,
        "maquina_id": "TEST-SEQID-MQTT",
        "temperatura": 76.5,
        "vibracao": 0.38,
        "rpm": 1830,
        "timestamp": datetime.now().isoformat()
    }
    
    # Conectar ao broker MQTT
    print("[1/4] Conectando ao broker MQTT...")
    client = mqtt.Client()
    try:
        client.connect(BROKER_HOST, BROKER_PORT, keepalive=10)
        print(f"      ✅ Conectado a {BROKER_HOST}:{BROKER_PORT}")
    except Exception as e:
        print(f"      ❌ Erro ao conectar: {e}")
        print()
        print("DICA: Certifique-se de que:")
        print("  1. O Mosquitto está rodando")
        print("  2. O mqtt_listen está ativo: python manage.py mqtt_listen")
        return False
    
    # Publicar mensagem
    print()
    print("[2/4] Publicando mensagem MQTT...")
    print(f"      Tópico: {TOPICO}")
    print(f"      Payload: {json.dumps(payload, indent=2)}")
    
    result = client.publish(TOPICO, json.dumps(payload))
    if result.rc == 0:
        print("      ✅ Mensagem publicada")
    else:
        print(f"      ❌ Erro ao publicar: {result.rc}")
        return False
    
    client.disconnect()
    
    # Aguardar processamento
    print()
    print("[3/4] Aguardando processamento (3 segundos)...")
    time.sleep(3)
    
    # Verificar no banco
    print()
    print("[4/4] Verificando no banco de dados...")
    
    try:
        leitura = LeituraTelemetria.objects.get(id=test_uuid)
        print(f"      ✅ Registro encontrado")
        print()
        print("RESULTADO:")
        print(f"  UUID:        {leitura.id}")
        print(f"  seq_id:      {leitura.seq_id}")
        print(f"  maquina_id:  {leitura.maquina_id}")
        print(f"  temperatura: {leitura.temperatura}°C")
        print(f"  vibracao:    {leitura.vibracao}")
        print(f"  rpm:         {leitura.rpm}")
        print()
        
        if leitura.seq_id is not None:
            print("=" * 60)
            print("✅ TESTE PASSOU: seq_id foi atribuído via MQTT!")
            print("=" * 60)
            return True
        else:
            print("=" * 60)
            print("❌ TESTE FALHOU: seq_id está None")
            print("=" * 60)
            print()
            print("POSSÍVEIS CAUSAS:")
            print("  1. A correção não foi aplicada em services/telemetria.py")
            print("  2. O mqtt_listen não foi reiniciado após a correção")
            print("  3. Há um problema no método save() do model")
            return False
            
    except LeituraTelemetria.DoesNotExist:
        print("      ❌ Registro não encontrado no banco")
        print()
        print("POSSÍVEIS CAUSAS:")
        print("  1. O mqtt_listen não está rodando")
        print("  2. Houve erro na validação do payload")
        print("  3. O broker MQTT não está funcionando")
        print()
        print("DICA: Verifique os logs do mqtt_listen")
        return False
    except Exception as e:
        print(f"      ❌ Erro ao consultar banco: {e}")
        return False

if __name__ == '__main__':
    sucesso = testar_mqtt_seqid()
    sys.exit(0 if sucesso else 1)
