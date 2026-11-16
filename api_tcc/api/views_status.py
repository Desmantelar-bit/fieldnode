import logging

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.api.views_common import (
    _filter_public_demo_leituras, _is_public_demo_request, _public_demo_machine_allowed, _serializar_analise,
)
from api_tcc.ia.pipeline import analisar_maquina
from api_tcc.models import DeadLetterEntry, LeituraTelemetria, SyncCursor
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
                'detalhes': 'Nenhuma leitura recebida ainda',
                'sincronizacao': {'dispositivos': [], 'perdas_registradas': 0, 'backlog_total': 0},
            })

        delta = timezone.now() - ultima_leitura.recebido_em
        segundos_atras = int(delta.total_seconds())
        atualizada = segundos_atras < 10

        scoped_leituras = _filter_public_demo_leituras(LeituraTelemetria.objects.all(), request)
        devices = set(scoped_leituras.values_list('device_id', flat=True).distinct())
        reports = []
        for device_id in sorted(devices):
            cursor = SyncCursor.objects.filter(device_id=device_id).first()
            ack = cursor.last_acked_sequence if cursor else 0
            pending = scoped_leituras.filter(
                device_id=device_id, sequence_number__gt=ack,
            )
            counts = {value: pending.filter(priority_class=value).count() for value in ('A', 'B', 'C')}
            oldest_pending = pending.order_by('recebido_em').first()
            delay = (
                max(0, int((timezone.now() - oldest_pending.recebido_em).total_seconds()))
                if oldest_pending else None
            )
            reports.append({
                'device_id': device_id,
                'ultimo_ack': ack,
                'pendentes_por_classe': counts,
                'backlog': sum(counts.values()),
                'atraso_maximo_segundos': delay,
            })
        loss_query = DeadLetterEntry.objects.filter(
            contexto=DeadLetterEntry.Contexto.SYNC, resolvido=False,
        )
        if _is_public_demo_request(request):
            losses = loss_query.filter(payload_referencia__device_id__in=list(devices)).count()
        else:
            losses = loss_query.count()
        backlog_total = sum(report['backlog'] for report in reports)

        return Response({
            'telemetria_atualizada': atualizada,
            'ultima_leitura_segundos_atras': segundos_atras,
            'status': 'recente' if atualizada else 'desatualizada',
            'sincronizacao': {
                'dispositivos': reports,
                'perdas_registradas': losses,
                'backlog_total': backlog_total,
                'alerta_backlog': backlog_total > 0 or losses > 0,
            },
        })
