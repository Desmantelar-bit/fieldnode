"""Busca global restrita às entidades e aos limites visíveis na operação."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from api_tcc.models import Decision, Machine, Operario
from api_tcc.permissions import IsAuthenticatedOrPublicDemo, get_machines_for_request


class GlobalSearchView(APIView):
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if len(query) < 2:
            return Response({"query": query, "results": {"machines": [], "operators": [], "decisions": []}})
        if len(query) > 80:
            return Response({"status": "erro", "detalhe": "A busca deve ter no máximo 80 caracteres."}, status=status.HTTP_400_BAD_REQUEST)

        machines = get_machines_for_request(request)
        machine_rows = machines.filter(
            Q(external_code__icontains=query) | Q(modelo__nome__icontains=query)
        ).select_related("modelo")[:8]
        operators = Operario.objects.filter(
            Q(nome__icontains=query),
            colheitadeira__machine__in=machines,
        ).distinct()[:8]
        decisions = Decision.objects.filter(
            Q(texto__icontains=query)
            | Q(acao_recomendada__icontains=query)
            | Q(machine__external_code__icontains=query),
            machine__in=machines,
        ).select_related("machine").order_by("-criado_em")[:8]

        return Response({
            "query": query,
            "results": {
                "machines": [{
                    "id": str(machine.id),
                    "label": machine.external_code,
                    "description": machine.modelo.nome if machine.modelo_id else "Máquina cadastrada",
                    "href": f"/detalhes?id={machine.external_code}",
                } for machine in machine_rows],
                "operators": [{
                    "id": str(operator.id),
                    "label": operator.nome,
                    "description": "Operário cadastrado",
                    "href": "/operarios",
                } for operator in operators],
                "decisions": [{
                    "id": str(decision.id),
                    "label": decision.machine.external_code,
                    "description": decision.texto[:120],
                    "href": f"/decisoes?decision={decision.id}",
                } for decision in decisions],
            },
        })
