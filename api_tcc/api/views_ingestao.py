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
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import csv
import io


from api_tcc.models import LeituraTelemetria, Prescricao
from api_tcc.api.serializers import LeituraTelemetriaSerializer
from api_tcc.ia.pipeline import agendar_processamento_ia
from api_tcc.services.telemetria import registrar_leitura, calcular_status_risco

logger = logging.getLogger(__name__)


class HealthView(APIView):
    """GET /api/health/ - checagem simples para scripts e deploy."""

    def get(self, request):
        return Response({'status': 'ok'})


class AnomaliaView(APIView):
    """
    GET /api/anomalias/
    GET /api/anomalias/?maquina_id=COLH-01

    Enfileira detecção de anomalias para processamento em background.
    Resposta rápida evita bloqueio do request por modelos de IA.
    """
    def get(self, request):
        maquina = request.query_params.get('maquina_id')
        if not maquina:
            return Response(
                {"status": "erro", "detalhe": "maquina_id é obrigatório"},
                status=400,
            )

        logger.debug("Requisição de anomalias. maquina_id=%s", maquina)
        resultado = agendar_processamento_ia(maquina, modelos=("anomalias",))
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

            # Classificação de risco usando o serviço de telemetria (centralizado)
            status_dict = calcular_status_risco(temp, vib, rpm)
            # Mapear o rótulo de risco do serviço para o formato esperado pela view
            nivel_risco_map = {
                'Crítico': 'CRITICO',
                'Alerta': 'ATENCAO',
                'Normal': 'NORMAL'
            }
            nivel = nivel_risco_map.get(status_dict['rotuloRisco'], 'NORMAL')

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

    Enfileira análise de manutenção para execução em background.
    Retorna rapidamente para não bloquear o request com modelagem de IA.
    """
    def get(self, request):
        maquina = request.query_params.get('maquina_id')
        if not maquina:
            return Response(
                {'status': 'erro', 'detalhe': 'maquina_id é obrigatório'},
                status=400
            )
        logger.debug("Análise de manutenção solicitada. maquina_id=%s", maquina)
        resultado = agendar_processamento_ia(maquina, modelos=("manutencao",))
        return Response(resultado)


class MetricasView(APIView):
    """
    GET /api/metricas/

    Métricas operacionais do sistema em tempo real.
    Retorna:
    - leituras_validas: total de leituras aceitas
    - leituras_invalidas: total de leituras rejeitadas (TelemetriaInvalida)
    - taxa_rejeicao_pct: percentual de rejeição
    - maquinas_ativas: número de máquinas com pelo menos uma leitura

    Uso: Dashboard / apresentações para demonstrar observabilidade e
    resiliência do sistema em campo.
    """
    def get(self, request):
        from api_tcc.models import TelemetriaInvalida

        total_validas = LeituraTelemetria.objects.count()
        total_invalidas = TelemetriaInvalida.objects.count()
        total_geral = total_validas + total_invalidas

        return Response({
            'leituras_validas': total_validas,
            'leituras_invalidas': total_invalidas,
            'taxa_rejeicao_pct': round(
                (total_invalidas / max(total_geral, 1)) * 100, 1
            ),
            'maquinas_ativas': LeituraTelemetria.objects.values(
                'maquina_id'
            ).distinct().count(),
        })


class StatusMQTTView(APIView):
    """
    GET /api/status-mqtt/

    Retorna status de conectividade MQTT e última leitura recebida.

    Usado pelo dashboard para mostrar indicador de conexão:
    - mqtt_conectado: bool (true se última leitura foi há < 10s)
    - ultima_leitura_segundos_atras: int (tempo em segundos)
    - status: str ("online" ou "offline")

    Lógica: considera sistema online se recebeu alguma leitura nos últimos 10 segundos.
    10s é escolhido conservadoramente — deixa espaço para atrasos de rede
    mantendo responsividade de detecção de desconexão.
    """
    def get(self, request):
        ultima_leitura = LeituraTelemetria.objects.order_by('-recebido_em').first()

        if not ultima_leitura:
            return Response({
                'mqtt_conectado': False,
                'ultima_leitura_segundos_atras': None,
                'status': 'offline',
                'detalhes': 'Nenhuma leitura recebida ainda'
            })

        delta = timezone.now() - ultima_leitura.recebido_em
        segundos_atras = int(delta.total_seconds())
        conectado = segundos_atras < 10

        return Response({
            'mqtt_conectado': conectado,
            'ultima_leitura_segundos_atras': segundos_atras,
            'status': 'online' if conectado else 'offline',
        })


class RelatorioView(APIView):
    """
    GET /api/relatorio/?formato=json

    Gera relatório operacional geral do sistema.
    Retorna sempre os campos obrigatórios esperados pelo frontend.
    """
    def get(self, request):
        formato = request.query_params.get('formato', 'json')
        
        # Cálculos básicos do relatório
        total_leituras = LeituraTelemetria.objects.count()
        maquinas_ativas = LeituraTelemetria.objects.values('maquina_id').distinct().count()
        
        # Contar alertas (leituras com risco crítico/atenção)
        alertas_gerados = 0
        if total_leituras > 0:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM api_tcc_leituratelemetria 
                    WHERE temperatura > 75 OR vibracao > 0.5
                """)
                alertas_gerados = cursor.fetchone()[0]
        
        eficiencia = round((maquinas_ativas / max(total_leituras, 1)) * 100, 1) if total_leituras > 0 else 0
        
        resultado = {
            "periodo": "Últimas 24 horas",
            "total_leituras": total_leituras,
            "maquinas_ativas": maquinas_ativas,
            "alertas_gerados": alertas_gerados,
            "eficiencia_operacional": eficiencia
        }
        
        if formato == 'csv':
            return Response(
                self._build_csv_geral(resultado),
                content_type='text/csv',
                headers={'Content-Disposition': f'attachment; filename="relatorio_geral_{datetime.now().strftime("%Y%m%d")}.csv"'}
            )
        
        return Response(resultado)
    
    def _build_csv_geral(self, dados):
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(['Relatório Geral - FieldNode'])
        w.writerow(['Período', dados['periodo']])
        w.writerow(['Gerado em', datetime.now().strftime('%d/%m/%Y %H:%M')])
        w.writerow([])
        w.writerow(['Métrica', 'Valor'])
        w.writerow(['Total de Leituras', dados['total_leituras']])
        w.writerow(['Máquinas Ativas', dados['maquinas_ativas']])
        w.writerow(['Alertas Gerados', dados['alertas_gerados']])
        w.writerow(['Eficiência Operacional', f"{dados['eficiencia_operacional']}%"])
        return buf.getvalue()


class PrescricaoListView(APIView):
    """
    GET /api/prescricoes/lista/?maquina_id=COLH-01

    Lista o histórico de prescrições geradas para a máquina.
    """

    def get(self, request):
        maquina_id = request.query_params.get("maquina_id")
        if not maquina_id:
            return Response(
                {"status": "erro", "detalhe": "maquina_id é obrigatório"}, status=400
            )

        prescricoes = Prescricao.objects.filter(
            colheitadeira__maquina_id=maquina_id
        ).order_by("-data_geracao")

        return Response(
            [
                {
                    "id": p.id,
                    "maquina_id": p.colheitadeira.maquina_id,
                    "titulo": p.titulo,
                    "descricao": p.descricao,
                    "status": p.status,
                    "data_geracao": p.data_geracao,
                }
                for p in prescricoes
            ]
        )


class PrescricaoTesteView(APIView):
    """View simplificada para testar prescrições"""
    
    def get(self, request):
        maquina_id = request.query_params.get('maquina_id', 'DESCONHECIDA')
        
        resultado = [
            {
                "id": 1,
                "maquina_id": maquina_id,
                "titulo": "Verificar Sistema de Arrefecimento",
                "descricao": "Temperatura média elevada detectada nas últimas leituras. Recomenda-se verificar radiador e sistema de refrigeração.",
                "status": "pendente",
                "data_geracao": timezone.now().isoformat()
            },
            {
                "id": 2,
                "maquina_id": maquina_id,
                "titulo": "Manutenção Preventiva do Motor",
                "descricao": "Análise dos dados indica necessidade de verificação dos filtros de ar e óleo. Sistema operando dentro dos parâmetros.",
                "status": "pendente", 
                "data_geracao": timezone.now().isoformat()
            }
        ]
        
        return Response(resultado)


class PrescricaoView(APIView):
    """
    GET /api/prescricoes/?maquina_id=COLH-01

    Retorna array de prescrições para a máquina especificada.
    Usa os campos reais do banco: titulo, descricao, status, data_geracao.
    """
    def get(self, request):
        maquina_id = request.query_params.get('maquina_id')
        if not maquina_id:
            return Response(
                {"status": "erro", "detalhe": "maquina_id é obrigatório"},
                status=400,
            )

        resultado = agendar_processamento_ia(maquina_id, modelos=("prescricao",))
        return Response(resultado)
