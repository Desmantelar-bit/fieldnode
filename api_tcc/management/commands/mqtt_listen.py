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
import os
from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from api_tcc.services.telemetria import registrar_leitura
from api_tcc.correlation import set_correlation_id, reset_correlation_id, new_correlation_id

logger = logging.getLogger(__name__)

# S7-T4: lidos do ambiente para permitir uso em Docker (serviço "mosquitto")
# sem hardcoding de localhost. Valores padrão preservam comportamento local.
BROKER_HOST = os.environ.get('MQTT_BROKER', 'localhost')
BROKER_PORT = int(os.environ.get('MQTT_PORT', '1883'))
TOPICO      = 'fieldnode/#'   # escuta tudo que começa com fieldnode/


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info('[MQTT] Conectado ao broker. Escutando tópico: %s', TOPICO)
        client.subscribe(TOPICO)
    else:
        logger.error('[MQTT] Falha na conexão. Código: %d', rc)


def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.warning('[MQTT] Desconectado inesperadamente. Tentando reconectar...')
        try:
            client.reconnect()
        except Exception as e:
            logger.error('[MQTT] Falha na reconexão: %s', e)


def on_message(client, userdata, msg):
    """
    Processa uma mensagem MQTT.

    Correlation ID (S7-T2):
      O UUID da leitura é definido como correlation_id ANTES de chamar
      registrar_leitura, de modo que todos os logs do processamento
      daquela mensagem carregam o mesmo identificador.

      Precedência:
        1. payload["id"]         — UUID explícito enviado pelo ESP32
        2. payload["message_id"] — campo de idempotência explícito
        3. UUID gerado aqui      — fallback para payloads legados sem ID

      O contexto é resetado ao final do processamento desta mensagem,
      evitando que o ID vaze para a próxima mensagem recebida.
    """
    # Extrair o identificador da leitura antes do processamento
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
    except json.JSONDecodeError as e:
        logger.error('[MQTT] Erro ao decodificar JSON em %s: %s', msg.topic, e)
        return

    reading_id = (
        str(payload.get("id") or "").strip()
        or str(payload.get("message_id") or "").strip()
        or new_correlation_id()
    )

    token = set_correlation_id(reading_id)
    try:
        logger.info('[MQTT] Mensagem recebida em %s', msg.topic)

        resultado, detalhe = registrar_leitura(payload)

        if resultado == "criado":
            logger.info('[MQTT] Leitura salva: %s', detalhe)
        elif resultado == "duplicata":
            logger.info('[MQTT] Duplicata ignorada: %s', detalhe)
        elif resultado == "invalido":
            logger.warning('[MQTT] Payload rejeitado — %s', detalhe)
        else:
            logger.error('[MQTT] Resultado inesperado: %s — %s', resultado, detalhe)

    except Exception as e:
        logger.exception('[MQTT] Erro ao processar mensagem: %s', e)
    finally:
        reset_correlation_id(token)


class Command(BaseCommand):
    help = 'Escuta o broker MQTT e salva leituras de telemetria no banco'

    def handle(self, *args, **options):
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message

        try:
            client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
            # S7-T3: migrado de self.stdout.write para logger para manter
            # toda a saída no mesmo stream JSON estruturado.
            logger.info('worker iniciado — aguardando mensagens MQTT (Ctrl+C para parar)')
            client.loop_forever()
        except KeyboardInterrupt:
            logger.info('worker encerrado pelo operador (KeyboardInterrupt)')
        except Exception as e:
            logger.exception('erro fatal no worker MQTT: %s', e)