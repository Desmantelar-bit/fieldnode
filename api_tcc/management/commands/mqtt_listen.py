# ============================================================
# Exemplos de publicação de mensagens JSON no Mosquitto
#
# 1. Usando CMD (Prompt de Comando do Windows):
#    mosquitto_pub -h localhost -t "fieldnode/teste" -m "{\"id\":\"550e8400-e29b-41d4-a716-446655440000\",\"maquina_id\":\"COLH-01\",\"temperatura\":78.5,\"vibracao\":0.42,\"rpm\":1850,\"timestamp\":\"2026-04-10T10:30:00Z\"}"
#
#    -> No CMD, é necessário escapar as aspas internas com \"
#
# 2. Usando PowerShell:
#    mosquitto_pub -h localhost -t "fieldnode/teste" -m '{"id":"550e8400-e29b-41d4-a716-446655440000","maquina_id":"COLH-01","temperatura":78.5,"vibracao":0.42,"rpm":1850,"timestamp":"2026-04-10T10:30:00Z"}'
#
#    -> No PowerShell, basta usar aspas simples externas e aspas duplas internas
#
# 3. Usando arquivo JSON (funciona em ambos):
#    Crie um arquivo msg.json com:
#    {
#      "id": "550e8400-e29b-41d4-a716-446655440000",
#      "maquina_id": "COLH-01",
#      "temperatura": 78.5,
#      "vibracao": 0.42,
#      "rpm": 1850,
#      "timestamp": "2026-04-10T10:30:00Z"
#    }
#
#    E publique com:
#    mosquitto_pub -h localhost -t "fieldnode/teste" -f msg.json
#
# ============================================================

import json
import logging
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
import paho.mqtt.client as mqtt
from api_tcc.models import LeituraTelemetria

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

        uuid_recebido = payload.get('id')

        # Deduplicação — ignora se já existe no banco
        if uuid_recebido and LeituraTelemetria.objects.filter(id=uuid_recebido).exists():
            print(f'[MQTT] Duplicata ignorada: {uuid_recebido}')
            return

        LeituraTelemetria.objects.create(
            id          = uuid_recebido,
            maquina_id  = payload['maquina_id'],
            temperatura = payload['temperatura'],
            vibracao    = payload['vibracao'],
            rpm         = payload['rpm'],
            timestamp   = parse_datetime(payload['timestamp']),
        )
        print(f'[MQTT] Salvo no banco: {uuid_recebido}')

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