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
import math
import json
import uuid as uuid_lib

from django.conf import settings
from django.db import connection, transaction
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated
from datetime import datetime, timedelta
import csv
import io


from api_tcc.models import Decision, LeituraTelemetria, Machine, MachineDataHealth, Prescricao, SyncCursor
from api_tcc.api.serializers import (
    DecisionActionSerializer,
    DecisionSerializer,
    LeituraTelemetriaSerializer,
)
from api_tcc.api.throttles import IngestaoThrottle
from api_tcc.ia.pipeline import analisar_maquina
from api_tcc.services.decisions import aplicar_acao_decision, persistir_decision_da_analise
from api_tcc.services.telemetria import registrar_leitura, calcular_status_risco
from api_tcc.permissions import (
    MACHINE_WRITE_ROLES,
    IsAuthenticatedOrPublicDemo,
    get_machines_for_request,
    get_machine_for_request,
    request_can_access_machine,
    user_can_access_machine,
)

logger = logging.getLogger(__name__)


class HasValidIngestionAPIKey(BasePermission):
    """Permission gate shared by machine-to-machine ingestion endpoints."""
    message = 'API key inválida ou ausente.'

    def has_permission(self, request, view):
        import hmac
        supplied = request.headers.get('X-API-Key', '')
        expected = getattr(settings, 'FIELDNODE_API_KEY', '')
        return bool(supplied and expected and hmac.compare_digest(supplied, expected))


class HasIngestionCredential(BasePermission):
    """Accept device API keys or authorized members sending browser telemetry."""
    message = 'Credencial inválida ou sem acesso de escrita à máquina.'

    def has_permission(self, request, view):
        if HasValidIngestionAPIKey().has_permission(request, view):
            return True
        if not request.user.is_authenticated:
            return False

        payloads = request.data.get('leituras') if isinstance(request.data, dict) else None
        if payloads is None:
            payloads = [request.data]
        if not isinstance(payloads, list) or not payloads:
            return False

        for payload in payloads:
            if not isinstance(payload, dict):
                return False
            external_code = str(payload.get('maquina_id') or '').strip().upper()
            machine = Machine.objects.filter(external_code=external_code, ativo=True).first()
            if not machine or not user_can_access_machine(request.user, machine, write=True):
                return False
        return True


def _is_public_demo_request(request) -> bool:
    return bool(settings.DEMO_MODE and not request.user.is_authenticated)


def _filter_public_demo_leituras(queryset, request):
    if _is_public_demo_request(request):
        return queryset.filter(machine__is_demo=True)
    if request.user.is_authenticated:
        return queryset.filter(machine__in=get_machines_for_request(request))
    return queryset


def _public_demo_machine_allowed(maquina_id: str | None, request) -> bool:
    if not _is_public_demo_request(request) or not maquina_id:
        return bool(request.user.is_authenticated)
    return get_machine_for_request(request, maquina_id) is not None


def _serializar_analise(analise):
    """Converte NaN das métricas estatísticas em null válido para JSON."""
    def normalizar(valor):
        if isinstance(valor, float) and not math.isfinite(valor):
            return None
        if isinstance(valor, dict):
            return {chave: normalizar(item) for chave, item in valor.items()}
        if isinstance(valor, list):
            return [normalizar(item) for item in valor]
        return valor

    return normalizar(analise.__dict__)


def _serializar_data_health(
    machine_id,
    external_code,
    trust_score_medio,
    ultima_atualizacao,
    leituras_analisadas,
    sinais_de_alerta,
):
    if machine_id is None:
        return None

    try:
        machine_id = str(uuid_lib.UUID(str(machine_id)))
    except (TypeError, ValueError, AttributeError):
        machine_id = str(machine_id)

    if isinstance(sinais_de_alerta, str):
        try:
            sinais_de_alerta = json.loads(sinais_de_alerta)
        except json.JSONDecodeError:
            sinais_de_alerta = {}

    return {
        "machine_id": machine_id,
        "external_code": external_code,
        "status": "ok" if trust_score_medio is not None else "sem_dados",
        "trust_score_medio": trust_score_medio,
        "ultima_atualizacao": ultima_atualizacao,
        "leituras_analisadas": int(leituras_analisadas or 0),
        "sinais_de_alerta": sinais_de_alerta or {},
    }


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


class IngestaoTelemetriaView(APIView):
    """
    POST /api/telemetria/ — recebe leitura do ESP32
    GET  /api/telemetria/ — lista últimas 50 leituras (dev/debug)

    Autenticação: API key via header X-API-Key.
    Idempotência: UUID duplicado retorna 200 sem reprocessar.
    Validação: payload inválido retorna 400 e é arquivado em TelemetriaInvalida.
    """
    throttle_classes = [IngestaoThrottle]

    def get_permissions(self):
        permission = HasIngestionCredential if self.request.method == 'POST' else IsAuthenticatedOrPublicDemo
        return [permission()]

    def get_throttles(self):
        if self.request.method == 'POST':
            return super().get_throttles()
        return []

    def post(self, request):
        resultado, detalhe = registrar_leitura(request.data)

        if resultado == "criado":
            analise = analisar_maquina(request.data.get("maquina_id"))
            return Response({
                'status': 'ok',
                'id': detalhe,
                **self._ack_payload(detalhe),
                'ia': _serializar_analise(analise),
            }, status=status.HTTP_201_CREATED)

        if resultado == "duplicata":
            return Response({
                'status': 'duplicata ignorada',
                'id': detalhe,
                **self._ack_payload(detalhe),
            },
                            status=status.HTTP_200_OK)

        if resultado == "invalido":
            return Response({'status': 'erro', 'detalhes': detalhe},
                            status=status.HTTP_400_BAD_REQUEST)

        # resultado == "erro" — falha inesperada de banco
        return Response({'status': 'erro', 'detalhes': 'falha interna — verifique logs'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def _ack_payload(leitura_id: str | None) -> dict:
        """Expõe apenas os dados necessários para um ACK verificável no edge."""
        if not leitura_id:
            return {}
        try:
            leitura = LeituraTelemetria.objects.get(id=leitura_id)
        except (LeituraTelemetria.DoesNotExist, ValueError, TypeError):
            logger.info("ACK omitido: leitura %s indisponível", leitura_id)
            return {}
        cursor = SyncCursor.objects.filter(device_id=leitura.device_id).first()
        return {
            'message_id': leitura.message_id,
            'device_id': leitura.device_id,
            'sequence_number': leitura.sequence_number,
            'payload_hash': leitura.payload_hash,
            'sync_cursor': cursor.last_acked_sequence if cursor else 0,
        }

    def get(self, request):
        if not request.user.is_authenticated and not _is_public_demo_request(request):
            return Response({'detail': 'Autenticação obrigatória.'}, status=status.HTTP_401_UNAUTHORIZED)
        maquina = request.query_params.get('maquina_id')
        leituras = _filter_public_demo_leituras(LeituraTelemetria.objects.all(), request)
        if maquina:
            leituras = leituras.filter(maquina_id=maquina)
        serializer = LeituraTelemetriaSerializer(leituras[:50], many=True)
        return Response(serializer.data)


class MachineDataHealthView(APIView):
    """
    GET /api/machines/<id>/health/

    Retorna o estado agregado persistido da qualidade da telemetria da Machine.
    Nao recalcula historico de leituras durante a consulta.
    """

    def get(self, request, machine_id):
        machine = get_machine_for_request(request, machine_id)
        if machine is None:
            try:
                uuid_val = uuid_lib.UUID(str(machine_id))
                m_exists = Machine.objects.filter(id=uuid_val).exists()
            except (ValueError, AttributeError):
                m_exists = Machine.objects.filter(external_code=str(machine_id).strip().upper()).exists()

            if m_exists:
                return Response(
                    {"status": "erro", "detalhe": "machine nao disponivel no dataset demo"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(
                {"status": "erro", "detalhe": "machine nao encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        health = MachineDataHealth.objects.filter(machine=machine).first()
        if health is None:
            return Response({
                "machine_id": str(machine.id),
                "external_code": machine.external_code,
                "status": "sem_dados",
                "trust_score_medio": None,
                "ultima_atualizacao": None,
                "leituras_analisadas": 0,
                "sinais_de_alerta": {},
            })

        return Response({
            "machine_id": str(machine.id),
            "external_code": machine.external_code,
            "status": "ok",
            "trust_score_medio": health.trust_score_medio,
            "ultima_atualizacao": health.ultima_atualizacao,
            "leituras_analisadas": health.leituras_analisadas,
            "sinais_de_alerta": health.sinais_de_alerta,
        })


class IngestaoLoteView(APIView):
    """
    Aceita um array de leituras acumuladas (buffer local do gateway/ESP32).
    Cada item precisa ter seu próprio UUID. Duplicatas são ignoradas individualmente:
    uma leitura ruim no meio do lote não derruba o resto.

    Nota Técnica (TCC): o processamento ocorre item a item (não bulk_create) para
    privilegiar o relatório detalhado de debug em campo sobre performance bruta.
    """
    throttle_classes = [IngestaoThrottle]

    def get_permissions(self):
        permission = HasIngestionCredential if self.request.method == 'POST' else IsAuthenticatedOrPublicDemo
        return [permission()]

    def post(self, request):
        leituras = request.data.get('leituras', [])

        if not isinstance(leituras, list) or not leituras:
            return Response(
                {'status': 'erro', 'detalhe': "corpo precisa ter uma lista 'leituras'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(leituras) > 500:
            return Response(
                {'status': 'erro', 'detalhe': 'lote máximo de 500 leituras por request'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        resultado = {'salvas': 0, 'duplicadas': 0, 'invalidas': 0, 'erros': []}

        for item in leituras:
            if not isinstance(item, dict):
                resultado['invalidas'] += 1
                resultado['erros'].append({'id': None, 'detalhe': 'item precisa ser um objeto JSON'})
                continue

            status_item, detalhe = registrar_leitura(item)
            if status_item == "criado":
                resultado['salvas'] += 1
            elif status_item == "duplicata":
                resultado['duplicadas'] += 1
            elif status_item == "invalido":
                resultado['invalidas'] += 1
                resultado['erros'].append({
                    'id': item.get('id'),
                    'detalhe': detalhe,
                })
            else:
                resultado['erros'].append({
                    'id': item.get('id'),
                    'detalhe': 'falha interna ao persistir a leitura',
                })

        return Response(resultado, status=status.HTTP_200_OK)


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

    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request):
        if not request.user.is_authenticated and not _is_public_demo_request(request):
            return Response({'detail': 'Autenticação obrigatória.'}, status=status.HTTP_401_UNAUTHORIZED)
        maquina = request.query_params.get('maquina_id')
        demo_publico = _is_public_demo_request(request)

        user_id = request.user.id if request.user.is_authenticated else -1
        with connection.cursor() as cursor:
            if maquina:
                cursor.execute("""
                    SELECT t1.maquina_id, t1.temperatura, t1.vibracao, t1.rpm,
                           t1.timestamp, t2.total_leituras,
                           t1.machine_id, m_health.external_code,
                           h.trust_score_medio, h.ultima_atualizacao,
                           h.leituras_analisadas, h.sinais_de_alerta
                    FROM api_tcc_leituratelemetria t1
                    INNER JOIN api_tcc_machine m ON t1.machine_id = m.id
                    LEFT JOIN api_tcc_machine m_health ON t1.machine_id = m_health.id
                    LEFT JOIN api_tcc_machinedatahealth h ON h.machine_id = t1.machine_id
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
                      AND ((%s = TRUE AND m.is_demo = TRUE)
                        OR (%s = FALSE AND m.organization_id IN (
                            SELECT organization_id FROM api_tcc_membership WHERE user_id = %s
                        ) AND m.ativo = TRUE))
                """, [maquina, maquina, maquina, demo_publico, demo_publico, user_id])
            else:
                cursor.execute("""
                    SELECT t1.maquina_id, t1.temperatura, t1.vibracao, t1.rpm,
                           t1.timestamp, t3.total_leituras,
                           t1.machine_id, m_health.external_code,
                           h.trust_score_medio, h.ultima_atualizacao,
                           h.leituras_analisadas, h.sinais_de_alerta
                    FROM api_tcc_leituratelemetria t1
                    INNER JOIN api_tcc_machine m ON t1.machine_id = m.id
                    LEFT JOIN api_tcc_machine m_health ON t1.machine_id = m_health.id
                    LEFT JOIN api_tcc_machinedatahealth h ON h.machine_id = t1.machine_id
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
                    WHERE ((%s = TRUE AND m.is_demo = TRUE)
                        OR (%s = FALSE AND m.organization_id IN (
                            SELECT organization_id FROM api_tcc_membership WHERE user_id = %s
                        ) AND m.ativo = TRUE))
                    ORDER BY t1.maquina_id
                """, [demo_publico, demo_publico, user_id])

            rows = cursor.fetchall()

        # Paginação configurável e suporte a frotas com mais de 10 máquinas
        try:
            limit = int(request.query_params.get('limit') or request.query_params.get('page_size') or 50)
            limit = max(1, min(limit, 200))
        except (TypeError, ValueError):
            limit = 50

        try:
            if 'page' in request.query_params:
                page = max(1, int(request.query_params.get('page', 1)))
                offset = (page - 1) * limit
            else:
                offset = max(0, int(request.query_params.get('offset', 0)))
        except (TypeError, ValueError):
            offset = 0

        # Soft delete é respeitado também nesta rota de leitura rápida. Assim,
        # uma máquina inativada não reaparece no dashboard por ter histórico.
        from api_tcc.models import Colheitadeira, Machine
        maquinas_ativas = set(
            Colheitadeira.objects.filter(ativo=True).values_list("maquina_id", flat=True)
        ) | set(
            Machine.objects.filter(ativo=True).values_list("external_code", flat=True)
        )
        rows = [
            row for row in rows
            if row[0] in maquinas_ativas or (len(row) > 7 and row[7] in maquinas_ativas)
        ]
        total_maquinas_ativas = len(rows)

        if not maquina:
            rows = rows[offset:offset + limit]

        resultado = []
        for row in rows:
            (
                mid,
                temp,
                vib,
                rpm,
                ts,
                total,
                machine_id,
                external_code,
                trust_score_medio,
                health_updated_at,
                leituras_analisadas,
                sinais_de_alerta,
            ) = row

            # Classificação de risco usando o serviço de telemetria (centralizado)
            status_dict = calcular_status_risco(temp, vib, rpm)
            # Mantém o formato estruturado retornado pelos demais endpoints.
            # nivel_risco continua por compatibilidade com consumidores antigos.
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
                'status_risco':  status_dict,
                'nivel_risco':   nivel,
                'total_leituras': total,
                'data_health': _serializar_data_health(
                    machine_id,
                    external_code,
                    trust_score_medio,
                    health_updated_at,
                    leituras_analisadas,
                    sinais_de_alerta,
                ),
            })

        response = Response(resultado)
        response['X-Total-Count'] = str(total_maquinas_ativas)
        response['X-Limit'] = str(limit)
        response['X-Offset'] = str(offset)
        return response


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
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request):
        from api_tcc.models import TelemetriaInvalida

        leituras = _filter_public_demo_leituras(LeituraTelemetria.objects.all(), request)
        total_validas = leituras.count()
        total_invalidas = 0 if _is_public_demo_request(request) else TelemetriaInvalida.objects.count()
        total_geral = total_validas + total_invalidas

        return Response({
            'leituras_validas': total_validas,
            'leituras_invalidas': total_invalidas,
            'taxa_rejeicao_pct': round(
                (total_invalidas / max(total_geral, 1)) * 100, 1
            ),
            'maquinas_ativas': leituras.values(
                'maquina_id'
            ).distinct().count(),
        })


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


class RelatorioView(APIView):
    """
    GET /api/relatorio/?formato=json

    Gera relatório operacional geral do sistema.
    Retorna sempre os campos obrigatórios esperados pelo frontend.
    """
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request):
        formato = request.query_params.get('formato', 'json')
        periodo_inicio = timezone.now() - timedelta(hours=24)
        leituras = _filter_public_demo_leituras(
            LeituraTelemetria.objects.filter(timestamp__gte=periodo_inicio), request
        )
        
        # Cálculos básicos do relatório
        total_leituras = leituras.count()
        maquinas_ativas = leituras.values('maquina_id').distinct().count()
        
        # Contar alertas (leituras com risco crítico/atenção)
        alertas_gerados = (
            leituras.filter(temperatura__gt=75).count()
            + leituras.filter(temperatura__lte=75, vibracao__gt=0.5).count()
        )
        
        total_maquinas = get_machines_for_request(request).filter(ativo=True).count()
        maquinas_com_leituras = leituras.values('machine_id').distinct().count()
        eficiencia = round((maquinas_com_leituras / total_maquinas) * 100, 1) if total_maquinas else 0
        
        resultado = {
            "periodo": "Últimas 24 horas",
            "total_leituras": total_leituras,
            "maquinas_ativas": maquinas_ativas,
            "alertas_gerados": alertas_gerados,
            "eficiencia_operacional": eficiencia
        }
        
        if formato == 'csv':
            resposta = Response(
                "\ufeff" + self._build_csv_geral(resultado),
                content_type='text/csv; charset=utf-8',
                headers={'Content-Disposition': f'attachment; filename="relatorio_geral_{datetime.now().strftime("%Y%m%d")}.csv"'}
            )
            return resposta
        
        return Response(resultado)
    
    def _build_csv_geral(self, dados):
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=';', lineterminator='\n')
        w.writerow(['Relatório Geral - FieldNode'])
        w.writerow(['Período', dados['periodo']])
        w.writerow(['Gerado em', datetime.now().strftime('%d/%m/%Y %H:%M')])
        w.writerow([])
        w.writerow(['Métrica', 'Valor'])
        w.writerow(['Total de Leituras', dados['total_leituras']])
        w.writerow(['Máquinas Ativas', dados['maquinas_ativas']])
        w.writerow(['Alertas Gerados', dados['alertas_gerados']])
        w.writerow(['Cobertura Operacional', f"{dados['eficiencia_operacional']}%"])
        return buf.getvalue()


# Unificado em api_tcc.api.views_relatorio para suportar XLSX e CSV sem conflito
from api_tcc.api.views_relatorio import RelatorioExportarView


def _serializar_prescricao(p) -> dict:
    if isinstance(p, dict):
        return p
    return {
        'id': p.id,
        'maquina_id': p.colheitadeira.maquina_id,
        'titulo': p.titulo,
        'descricao': p.descricao,
        'status': p.status,
        'data_geracao': p.data_geracao,
    }


class PrescricaoListView(APIView):
    """
    GET /api/prescricoes/lista/?maquina_id=COLH-01

    Lista o histórico de prescrições geradas para a máquina.
    Mantida temporariamente como leitura histórica; novas decisões usam Event/Decision.
    """
    permission_classes = [IsAuthenticatedOrPublicDemo]


    def get(self, request):
        maquina_id = request.query_params.get("maquina_id")
        if not maquina_id:
            return Response(
                {"status": "erro", "detalhe": "maquina_id é obrigatório"}, status=400
            )
        machine = get_machine_for_request(request, maquina_id)
        if machine is None:
            return Response([], status=200)

        prescricoes = list(
            Prescricao.objects.filter(
                colheitadeira_id=machine.colheitadeira_id,
            ).order_by("-data_geracao")
        )
        response = Response([_serializar_prescricao(p) for p in prescricoes])
        response["Deprecation"] = "true"
        response["Sunset"] = "2026-12-31"
        return response


class PrescricaoTesteView(APIView):
    """View simplificada para testar prescrições"""
    permission_classes = [IsAuthenticatedOrPublicDemo]

    
    def get(self, request):
        return Response(
            {"status": "erro", "detalhe": "rota de teste desativada; use Event/Decision"},
            status=status.HTTP_410_GONE,
        )


class DecisionActionView(APIView):
    """
    GET /api/decisions/<id>/   — consulta detalhes da Decision
    PATCH /api/decisions/<id>/ — registra acao humana sobre uma Decision
    """

    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request, decision_id):
        try:
            decision = (
                Decision.objects
                .select_related("machine", "event", "decidido_por")
                .get(id=decision_id)
            )
        except Decision.DoesNotExist:
            return Response(
                {"status": "erro", "detalhe": "Decision nao encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request_can_access_machine(request, decision.machine):
            return Response(
                {"status": "erro", "detalhe": "Decision nao disponivel para este usuario"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(DecisionSerializer(decision).data, status=status.HTTP_200_OK)

    def patch(self, request, decision_id):
        serializer = DecisionActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        novo_status = serializer.validated_data["status"]
        outcome_fornecido = "outcome_texto" in serializer.validated_data
        outcome_texto = serializer.validated_data.get("outcome_texto")

        try:
            with transaction.atomic():
                decision = Decision.objects.select_for_update().get(id=decision_id)
                if not user_can_access_machine(
                    request.user,
                    decision.machine,
                    write=True,
                ):
                    return Response(
                        {"status": "erro", "detalhe": "sem permissao para esta machine"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                aplicar_acao_decision(
                    decision,
                    usuario=request.user,
                    novo_status=novo_status,
                    outcome_texto_fornecido=outcome_fornecido,
                    outcome_texto=outcome_texto,
                )
        except Decision.DoesNotExist:
            return Response(
                {"status": "erro", "detalhe": "Decision nao encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as exc:
            return Response(
                {"status": "erro", "detalhe": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(DecisionSerializer(decision).data, status=status.HTTP_200_OK)


class PrescricaoView(APIView):
    """
    GET /api/prescricoes/?maquina_id=COLH-01
    POST /api/prescricoes/ (com maquina_id)

    GET analisa sem persistir; POST analisa e persiste explicitamente uma Decision.
    """
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def _executar(self, request, forcar_persistencia: bool = False):
        maquina_id = request.data.get('maquina_id') or request.query_params.get('maquina_id')
        if not maquina_id:
            return Response(
                {"status": "erro", "detalhe": "maquina_id é obrigatório"},
                status=400,
            )
        if not _public_demo_machine_allowed(maquina_id, request):
            return Response(
                {"status": "erro", "detalhe": "máquina não disponível no dataset demo"},
                status=404,
            )

        deve_persistir = forcar_persistencia

        analise = analisar_maquina(maquina_id)
        if deve_persistir:
            decision = persistir_decision_da_analise(analise)
            decision_id = str(decision.id)
            decision_status = decision.status
        else:
            machine = get_machine_for_request(request, maquina_id)
            existing = (
                Decision.objects.filter(machine=machine, status=Decision.Status.PENDENTE)
                .order_by("-criado_em")
                .first()
                if machine else None
            )
            decision_id = str(existing.id) if existing else None
            decision_status = existing.status if existing else None

        payload = _serializar_analise(analise)
        payload["decision_id"] = decision_id
        payload["decision_status"] = decision_status
        payload["preview"] = not deve_persistir
        return Response(payload)

    def get(self, request):
        return self._executar(request, forcar_persistencia=False)

    def post(self, request):
        return self._executar(request, forcar_persistencia=True)
