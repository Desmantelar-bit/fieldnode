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
# Publicação de dispositivo usa username=COLH-01, tópico
# fieldnode/COLH-01/telemetria e payload contendo device_id=COLH-01.
#
# ============================================================

import json
import logging
import os
import re
from django.utils import timezone
from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from api_tcc.services.telemetria import registrar_leitura
from api_tcc.correlation import set_correlation_id, reset_correlation_id, new_correlation_id
from api_tcc.models import DeviceCredential
from api_tcc.services.dlq import registrar_falha_dlq

logger = logging.getLogger(__name__)

# S7-T4: lidos do ambiente para permitir uso em Docker (serviço "mosquitto")
# sem hardcoding de localhost. Valores padrão preservam comportamento local.
BROKER_HOST = os.environ.get('MQTT_BROKER', 'localhost')
BROKER_PORT = int(os.environ.get('MQTT_PORT', '1883'))
TOPICOS = (('fieldnode/+/telemetria', 1), ('fieldnode/+/status', 1))
DEVICE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info('[MQTT] Conectado ao broker. Escutando tópicos: %s', TOPICOS)
        client.subscribe(TOPICOS)
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
    parts = str(msg.topic).split('/')
    if (len(parts) != 3 or parts[0] != 'fieldnode'
            or parts[2] not in {'telemetria', 'status'}
            or not DEVICE_ID_RE.fullmatch(parts[1])):
        logger.warning('[MQTT] Tópico rejeitado por formato inválido: %s', msg.topic)
        return
    topic_device = parts[1]
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.warning('[MQTT] Payload MQTT inválido em tópico de dispositivo')
        return
    if not isinstance(payload, dict):
        logger.warning('[MQTT] Payload MQTT deve ser um objeto JSON')
        return

    declared_device = str(payload.get('device_id') or '').strip()
    credential = DeviceCredential.objects.filter(
        device_id=topic_device, username=topic_device, active=True,
        provisioning_state='active', revoked_at__isnull=True,
    ).first()
    reason = None
    if not credential:
        reason = 'dispositivo sem credencial ativa associada ao tópico'
    elif declared_device != topic_device:
        reason = 'device_id declarado diverge do tópico'
    if reason:
        registrar_falha_dlq(
            contexto='MQTT_SPOOF',
            payload_referencia={
                'topic': str(msg.topic)[:300],
                'topic_device_id': topic_device,
                'declared_device_id': declared_device[:100],
                'credential_device_id': credential.device_id if credential else None,
                'received_at': timezone.now().isoformat(),
            },
            motivo=reason,
        )
        logger.warning('[MQTT] Mensagem rejeitada; contexto=MQTT_SPOOF; motivo=%s', reason)
        return
    if parts[2] == 'status':
        logger.info('[MQTT] Status autenticado recebido para dispositivo %s', topic_device)
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
        mqtt_username = os.environ.get('MQTT_WORKER_USERNAME', 'fieldnode-worker').strip()
        password_file = os.environ.get('MQTT_WORKER_PASSWORD_FILE', '/run/secrets/mqtt_worker_password')
        try:
            with open(password_file, encoding='utf-8') as secret_file:
                mqtt_password = secret_file.read().strip()
        except OSError:
            mqtt_password = ''
        if mqtt_username != 'fieldnode-worker' or not mqtt_password:
            raise RuntimeError('Credenciais MQTT do worker ausentes ou inválidas; conexão não iniciada.')
        client = mqtt.Client()
        client.username_pw_set(mqtt_username, mqtt_password)
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
            logger.exception('erro fatal no worker MQTT: %s', type(e).__name__)
            raise
