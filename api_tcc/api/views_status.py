import logging

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.api.views_common import (
    _filter_public_demo_leituras, _public_demo_machine_allowed, _serializar_analise,
)
from api_tcc.ia.pipeline import analisar_maquina
from api_tcc.models import LeituraTelemetria
from api_tcc.permissions import IsAuthenticatedOrPublicDemo

logger = logging.getLogger(__name__)





class AnomaliaView(APIView):
    """
    GET /api/anomalias/
    GET /api/anomalias/?maquina_id=COLH-01

    Enfileira detecção de anomalias para processamento em background.
    Resposta rápida evita bloqueio do request por modelos de IA.
    """
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request):
        maquina = request.query_params.get('maquina_id')
        if not maquina:
            return Response(
                {"status": "erro", "detalhe": "maquina_id é obrigatório"},
                status=400,
            )
        if not _public_demo_machine_allowed(maquina, request):
            return Response(
                {"status": "erro", "detalhe": "máquina não disponível no dataset demo"},
                status=404,
            )

        logger.debug("Requisição de anomalias. maquina_id=%s", maquina)
        analise = analisar_maquina(maquina)
        return Response(_serializar_analise(analise))


class ManutencaoView(APIView):
    """
    GET /api/manutencao/?maquina_id=COLH-01

    Enfileira análise de manutenção para execução em background.
    Retorna rapidamente para não bloquear o request com modelagem de IA.
    """
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request):
        maquina = request.query_params.get('maquina_id')
        if not maquina:
            return Response(
                {'status': 'erro', 'detalhe': 'maquina_id é obrigatório'},
                status=400
            )
        if not _public_demo_machine_allowed(maquina, request):
            return Response(
                {'status': 'erro', 'detalhe': 'máquina não disponível no dataset demo'},
                status=404,
            )
        logger.debug("Análise de manutenção solicitada. maquina_id=%s", maquina)
        analise = analisar_maquina(maquina)
        return Response(_serializar_analise(analise))


class StatusMQTTView(APIView):
    """
    GET /api/status-mqtt/

    Retorna a atualidade da última leitura recebida. Não mede a conexão do broker.

    Usado pelo dashboard para mostrar indicador de conexão:
    - telemetria_atualizada: bool (true se última leitura foi há < 10s)
    - ultima_leitura_segundos_atras: int (tempo em segundos)
    - status: str ("recente" ou "desatualizada")

    O intervalo é apenas uma indicação de frescor da telemetria; não comprova
    conectividade do broker ou do worker MQTT.
    """
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request):
        ultima_leitura = _filter_public_demo_leituras(
            LeituraTelemetria.objects.all(), request
        ).order_by('-recebido_em').first()

        if not ultima_leitura:
            return Response({
                'telemetria_atualizada': False,
                'ultima_leitura_segundos_atras': None,
                'status': 'sem_dados',
                'detalhes': 'Nenhuma leitura recebida ainda'
            })

        delta = timezone.now() - ultima_leitura.recebido_em
        segundos_atras = int(delta.total_seconds())
        atualizada = segundos_atras < 10

        return Response({
            'telemetria_atualizada': atualizada,
            'ultima_leitura_segundos_atras': segundos_atras,
            'status': 'recente' if atualizada else 'desatualizada',
        })
