from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.api.views_common import _filter_public_demo_leituras, _is_public_demo_request
from api_tcc.models import LeituraTelemetria, TelemetriaInvalida
from api_tcc.permissions import IsAuthenticatedOrPublicDemo





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
