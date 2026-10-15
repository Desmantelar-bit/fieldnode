"""
api_tcc/api/views_decisions.py

Endpoints de listagem e consulta para o modelo Decision.
Complementa a DecisionActionView (mutação via PATCH).
"""
import logging
from django.core.paginator import InvalidPage, Paginator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.api.serializers import DecisionSerializer
from api_tcc.models import Decision
from api_tcc.permissions import (
    IsAuthenticatedOrPublicDemo,
    get_machine_for_request,
    get_machines_for_request,
)

logger = logging.getLogger(__name__)

PAGE_SIZE_DEFAULT = 20
PAGE_SIZE_MAX = 100


class DecisionListView(APIView):
    """
    GET /api/decisions/

    Lista decisões/recomendações com filtros e paginação.
    Filtros suportados:
        maquina_id (opcional) — ID textual ou UUID da máquina. Se omitido, lista de todas as máquinas autorizadas.
        status (opcional) — filtra por Decision.Status (PENDENTE, APROVADA, REJEITADA, EXECUTADA, EXPIRADA)
        severidade (opcional) — filtra por severidade (NORMAL, ATENCAO, CRITICO)
        page (opcional) — número da página (padrão: 1)
        page_size (opcional) — itens por página (padrão: 20, máximo: 100)
    """

    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request):
        maquina_id = request.query_params.get("maquina_id")
        if maquina_id:
            machine = get_machine_for_request(request, maquina_id)
            if machine is None:
                return Response(
                    {"status": "erro", "detalhe": "máquina não disponível para este usuário"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            qs = Decision.objects.filter(machine=machine)
        else:
            accessible_machines = get_machines_for_request(request)
            qs = Decision.objects.filter(machine__in=accessible_machines)

        qs = qs.select_related("machine", "event", "decidido_por").order_by("-criado_em")

        filtro_status = request.query_params.get("status")
        if filtro_status:
            qs = qs.filter(status=filtro_status)

        severidade = request.query_params.get("severidade")
        if severidade:
            qs = qs.filter(severidade=severidade)

        try:
            page_size = int(request.query_params.get("page_size", PAGE_SIZE_DEFAULT))
            page_size = max(1, min(page_size, PAGE_SIZE_MAX))
        except (TypeError, ValueError):
            page_size = PAGE_SIZE_DEFAULT

        paginator = Paginator(qs, page_size)

        try:
            page_num = int(request.query_params.get("page", 1))
        except (TypeError, ValueError):
            page_num = 1

        try:
            page_obj = paginator.page(page_num)
        except InvalidPage:
            return Response(
                {"status": "erro", "detalhe": f"Página {page_num} não existe."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DecisionSerializer(page_obj.object_list, many=True)

        def _build_page_url(num):
            params = request.query_params.copy()
            params["page"] = num
            params["page_size"] = page_size
            return request.build_absolute_uri(request.path) + "?" + params.urlencode()

        return Response({
            "count": paginator.count,
            "page": page_obj.number,
            "page_size": page_size,
            "pages": paginator.num_pages,
            "next": _build_page_url(page_obj.next_page_number()) if page_obj.has_next() else None,
            "previous": _build_page_url(page_obj.previous_page_number()) if page_obj.has_previous() else None,
            "results": serializer.data,
        })

