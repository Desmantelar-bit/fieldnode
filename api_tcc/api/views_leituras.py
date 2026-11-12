import uuid as uuid_lib

from django.db import connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.api.serializers import LeituraTelemetriaSerializer
from api_tcc.api.views_common import (
    _filter_public_demo_leituras, _is_public_demo_request, _serializar_data_health,
)
from api_tcc.models import Colheitadeira, LeituraTelemetria, Machine, MachineDataHealth
from api_tcc.permissions import (
    IsAuthenticatedOrPublicDemo, get_machine_for_request, get_machines_for_request,
)
from api_tcc.services.telemetria import calcular_status_risco





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
