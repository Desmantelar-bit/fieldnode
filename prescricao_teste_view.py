from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone


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