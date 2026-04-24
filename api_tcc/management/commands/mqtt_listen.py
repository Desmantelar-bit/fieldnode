# ============================================================
# MQTT Listener - FieldNode Telemetria
# 
# Este comando Django escuta mensagens MQTT do broker local e
# salva as leituras de telemetria no banco de dados MySQL.
#
# Como usar:
#   python manage.py mqtt_listen
#
# Estrutura da mensagem JSON esperada:
# {
#   "id": "550e8400-e29b-41d4-a716-446655440000",
#   "maquina_id": "COLH-01", 
#   "temperatura": 78.5,
#   "vibracao": 0.42,
#   "rpm": 1850,
#   "timestamp": "2026-04-10T10:30:00Z"
# }
#
# Exemplo de envio via mosquitto_pub:
#   mosquitto_pub -h localhost -p 1883 -t "fieldnode/COLH-01/leitura" -m '{"id":"uuid-aqui","maquina_id":"COLH-01","temperatura":85.5,"vibracao":0.65,"rpm":1750,"timestamp":"2026-04-17T10:00:00"}'
#
# ============================================================

import json
import logging
from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from api_tcc.services.telemetria import registrar_leitura

logger = logging.getLogger(__name__)

BROKER_HOST = 'localhost'
BROKER_PORT = 1883 
TOPICO      = 'fieldnode/#'   # escuta tudo que começa com fieldnode/


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f'[MQTT] Conectado ao broker. Escutando tópico: {TOPICO}')
        client.subscribe(TOPICO)
    else:
        print(f'[MQTT] Falha na conexão. Código: {rc}')


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        print(f'[MQTT] Mensagem recebida em {msg.topic}: {payload}')

        # Usa o service layer para registrar a leitura
        # Isso garante deduplicação, validação de range e logging consistente
        resultado, detalhe = registrar_leitura(payload)
        
        if resultado == "criado":
            print(f'[MQTT] Salvo: {detalhe}')
        elif resultado == "duplicata":
            print(f'[MQTT] Duplicata ignorada: {detalhe}')
        elif resultado == "invalido":
            print(f'[MQTT] Rejeitado — {detalhe}')
        else:
            print(f'[MQTT] Resultado: {resultado} - {detalhe}')
            
    except json.JSONDecodeError as e:
        print(f'[MQTT] Erro ao decodificar JSON: {e}')
    except Exception as e:
        print(f'[MQTT] Erro ao processar mensagem: {e}')


class Command(BaseCommand):
    help = 'Escuta o broker MQTT e salva leituras de telemetria no banco'

    def handle(self, *args, **options):
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        try:
            client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
            self.stdout.write('[MQTT] Iniciando loop... (Ctrl+C para parar)')
            client.loop_forever()
        except KeyboardInterrupt:
            self.stdout.write('[MQTT] Encerrado.')
        except Exception as e:
            self.stderr.write(f'[MQTT] Erro fatal: {e}')