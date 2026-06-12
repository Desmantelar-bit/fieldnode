from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api_tcc.models import Prescricao
from api_tcc.services.relatorios import gerar_relatorio_csv, gerar_relatorio_completo, preparar_dados_relatorio
from api_tcc.services.prescricao import analisar_telemetria_e_gerar_prescricoes
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GerarRelatorioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        maquina_id = request.query_params.get('maquina_id')
        tipo = request.query_params.get('tipo', 'csv')
        formato = request.query_params.get('formato', 'csv')  # csv ou txt
        data_inicio_str = request.query_params.get('data_inicio')
        data_fim_str = request.query_params.get('data_fim')

        if not maquina_id:
            return Response({"error": "maquina_id é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

        # Converter strings de data para objetos datetime se fornecidas
        data_inicio = None
        data_fim = None

        if data_inicio_str:
            try:
                data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
            except ValueError:
                return Response({"error": "Formato de data_inicio inválido. Use YYYY-MM-DD"},
                              status=status.HTTP_400_BAD_REQUEST)

        if data_fim_str:
            try:
                data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
            except ValueError:
                return Response({"error": "Formato de data_fim inválido. Use YYYY-MM-DD"},
                              status=status.HTTP_400_BAD_REQUEST)

        # Hardening: Try/Except robusto para evitar 500 sem tratamento
        try:
            if tipo == 'simple' and formato == 'csv':
                return gerar_relatorio_csv(maquina_id)
            else:
                return gerar_relatorio_completo(
                    maquina_id=maquina_id,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    formato=formato
                )
        except Exception as e:
            logger.error(f"Erro ao gerar relatório para máquina {maquina_id}: {str(e)}")
            return Response(
                {"error": "Ocorreu um erro interno ao processar o relatório. Por favor, tente um período menor."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RelatorioResumoView(APIView):
    """
    Dica de Ouro: Endpoint para pré-visualização JSON antes do download.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        maquina_id = request.query_params.get('maquina_id')
        if not maquina_id:
            return Response({"error": "maquina_id é obrigatório"}, status=400)

        dados, _, _ = preparar_dados_relatorio(maquina_id)

        if not dados:
            return Response({"message": "Nenhum dado encontrado para o período."}, status=404)

        # Retorna apenas o resumo estatístico e títulos das prescrições
        resumo = {
            "maquina": maquina_id,
            "periodo": {
                "inicio": dados['data_inicio'],
                "fim": dados['data_fim']
            },
            "estatisticas": dados['stats'],
            "total_prescricoes": len(dados['prescricoes']),
            "prescricoes_recentes": [
                {"titulo": p.titulo, "status": p.status}
                for p in dados['prescricoes'][:3]
            ]
        }

        return Response(resumo)