import csv
import io
from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.api.views_common import _filter_public_demo_leituras
from api_tcc.models import LeituraTelemetria
from api_tcc.permissions import IsAuthenticatedOrPublicDemo, get_machines_for_request





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
