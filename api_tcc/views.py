from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api_tcc.models import Prescricao, Colheitadeira


class PrescricaoListView(APIView):
    """
    GET /api/prescricoes/lista/
    Retorna lista de prescrições cadastradas.
    """
    def get(self, request):
        prescricoes = Prescricao.objects.all().select_related('colheitadeira').order_by('-data_geracao')
        resultado = []
        for p in prescricoes:
            resultado.append({
                'id': p.id,
                'titulo': p.titulo,
                'descricao': p.descricao,
                'data_geracao': p.data_geracao,
                'status': p.status,
                'colheitadeira_id': p.colheitadeira.maquina_id,
                'modelo': p.colheitadeira.modelo.nome,
                'marca': p.colheitadeira.modelo.marca.nome,
            })
        return Response(resultado)
