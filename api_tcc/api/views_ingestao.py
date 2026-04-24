"""
api_tcc/api/views_ingestao.py

Views de ingestão de telemetria.

Arquitetura: views são finas — apenas traduzem HTTP para chamadas de serviço.
Regra de negócio (deduplicação, validação, persistência) vive em
api_tcc/services/telemetria.py, reutilizável pelo worker MQTT.

Decisão de não usar autenticação complexa no protótipo:
O ESP32 não suporta JWT nativamente sem biblioteca adicional que
consome ~30% da memória flash disponível. API key simples via header
é o equilíbrio correto entre segurança e limitação de hardware.
"""
import logging

from django.conf import settings
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api_tcc.models import LeituraTelemetria
from api_tcc.api.serializers import LeituraTelemetriaSerializer
from api_tcc.ia.anomalias import detectar_anomalias
from api_tcc.ia.manutencao import prever_manutencao
from api_tcc.services.telemetria import registrar_leitura

logger = logging.getLogger(__name__)


class AnomaliaView(APIView):
    """
    GET /api/anomalias/
    GET /api/anomalias/?maquina_id=COLH-01

    Detecta leituras fora do padrão usando Isolation Forest.
    Requer mínimo de 20 leituras no banco para funcionar.

    Limitação conhecida: modelo retreinado a cada requisição —
    aceitável para protótipo, mas em produção usar cache com TTL.
    """
    def get(self, request):
        maquina = request.query_params.get('maquina_id')
        logger.debug("Requisição de anomalias. maquina_id=%s", maquina)
        resultado = detectar_anomalias(maquina_id=maquina)
        return Response(resultado)


class IngestaoTelemetriaView(APIView):
    """
    POST /api/telemetria/ — recebe leitura do ESP32
    GET  /api/telemetria/ — lista últimas 50 leituras (dev/debug)

    Autenticação: API key via header X-API-Key.
    Idempotência: UUID duplicado retorna 200 sem reprocessar.
    Validação: payload inválido retorna 400 e é arquivado em TelemetriaInvalida.
    """

    def _verificar_api_key(self, request) -> bool:
        api_key = request.headers.get('X-API-Key')
        return bool(api_key and api_key == settings.FIELDNODE_API_KEY)

    def post(self, request):
        if not self._verificar_api_key(request):
            logger.warning("Tentativa de ingestão com API key inválida. IP: %s",
                           request.META.get('REMOTE_ADDR'))
            return Response(
                {'status': 'erro', 'detalhes': 'API key inválida ou ausente'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        resultado, detalhe = registrar_leitura(request.data)

        if resultado == "criado":
            return Response({'status': 'ok', 'id': detalhe},
                            status=status.HTTP_201_CREATED)

        if resultado == "duplicata":
            return Response({'status': 'duplicata ignorada', 'id': detalhe},
                            status=status.HTTP_200_OK)

        if resultado == "invalido":
            return Response({'status': 'erro', 'detalhes': detalhe},
                            status=status.HTTP_400_BAD_REQUEST)

        # resultado == "erro" — falha inesperada de banco
        return Response({'status': 'erro', 'detalhes': 'falha interna — verifique logs'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        maquina = request.query_params.get('maquina_id')
        leituras = LeituraTelemetria.objects.all()
        if maquina:
            leituras = leituras.filter(maquina_id=maquina)
        serializer = LeituraTelemetriaSerializer(leituras[:50], many=True)
        return Response(serializer.data)


class UltimaLeituraView(APIView):
    """
    GET /api/leituras/ultimas/
    GET /api/leituras/ultimas/?maquina_id=COLH-01

    Retorna a leitura mais recente de cada máquina ativa.

    Implementação: SQL raw em vez de ORM para evitar N+1 queries.
    O ORM geraria uma subquery por máquina; aqui resolvemos tudo em 1 query
    com window functions (MAX + COUNT em JOIN).

    Limitação: retorna máximo 10 máquinas distintas por vez.
    Para frotas maiores, implementar paginação.
    """

    def get(self, request):
        maquina = request.query_params.get('maquina_id')

        with connection.cursor() as cursor:
            if maquina:
                cursor.execute("""
                    SELECT t1.maquina_id, t1.temperatura, t1.vibracao, t1.rpm,
                           t1.timestamp, t2.total_leituras
                    FROM api_tcc_leituratelemetria t1
                    INNER JOIN (
                        SELECT maquina_id, MAX(timestamp) as max_ts
                        FROM api_tcc_leituratelemetria
                        WHERE maquina_id = %s
                    ) t_max ON t1.maquina_id = t_max.maquina_id AND t1.timestamp = t_max.max_ts
                    INNER JOIN (
                        SELECT maquina_id, COUNT(*) as total_leituras
                        FROM api_tcc_leituratelemetria
                        WHERE maquina_id = %s
                    ) t2 ON t1.maquina_id = t2.maquina_id
                    WHERE t1.maquina_id = %s
                """, [maquina, maquina, maquina])
            else:
                cursor.execute("""
                    SELECT t1.maquina_id, t1.temperatura, t1.vibracao, t1.rpm,
                           t1.timestamp, t3.total_leituras
                    FROM api_tcc_leituratelemetria t1
                    INNER JOIN (
                        SELECT maquina_id, MAX(timestamp) as max_ts
                        FROM api_tcc_leituratelemetria
                        GROUP BY maquina_id
                    ) t2 ON t1.maquina_id = t2.maquina_id AND t1.timestamp = t2.max_ts
                    INNER JOIN (
                        SELECT maquina_id, COUNT(*) as total_leituras
                        FROM api_tcc_leituratelemetria
                        GROUP BY maquina_id
                    ) t3 ON t1.maquina_id = t3.maquina_id
                    ORDER BY t1.maquina_id
                    LIMIT 10
                """)

            rows = cursor.fetchall()

        resultado = []
        for row in rows:
            mid, temp, vib, rpm, ts, total = row

            # Classificação de risco baseada em limites operacionais documentados
            # (mesmos thresholds usados pela IA para consistência de UI)
            if temp > 85 or vib > 0.8:
                nivel = 'CRITICO'
            elif temp > 75 or vib > 0.5:
                nivel = 'ATENCAO'
            else:
                nivel = 'NORMAL'

            resultado.append({
                'maquina_id':    mid,
                'temperatura':   temp,
                'vibracao':      vib,
                'rpm':           rpm,
                'timestamp':     ts,
                'nivel_risco':   nivel,
                'total_leituras': total,
            })

        return Response(resultado)


class ManutencaoView(APIView):
    """
    GET /api/manutencao/?maquina_id=COLH-01

    Prevê probabilidade de necessidade de manutenção.
    Requer mínimo de 30 leituras da máquina especificada.

    Limitação conhecida: modelo treinado a cada requisição com dados
    sintéticos (labels baseados em padrões operacionais, não falhas reais).
    Em produção: retreinar mensalmente com histórico de manutenções confirmadas.
    """
    def get(self, request):
        maquina = request.query_params.get('maquina_id')
        if not maquina:
            return Response(
                {'status': 'erro', 'detalhe': 'maquina_id é obrigatório'},
                status=400
            )
        logger.debug("Análise de manutenção solicitada. maquina_id=%s", maquina)
        resultado = prever_manutencao(maquina_id=maquina)
        return Response(resultado)
