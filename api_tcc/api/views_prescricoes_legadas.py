from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.api.views_common import _public_demo_machine_allowed, _serializar_analise
from api_tcc.ia.pipeline import analisar_maquina
from api_tcc.models import Decision
from api_tcc.permissions import IsAuthenticatedOrPublicDemo, get_machine_for_request
from api_tcc.services.decisions import persistir_decision_da_analise


def _legacy_decision_payload(decision):
    return {
        "id": str(decision.id),
        "maquina_id": decision.machine.external_code,
        "titulo": decision.acao_recomendada,
        "descricao": decision.texto,
        "status": decision.status,
        "data_geracao": decision.criado_em,
        "decision_id": str(decision.id),
        "severidade": decision.severidade,
        "event_id": str(decision.event_id) if decision.event_id else None,
        "outcome_texto": decision.outcome_texto,
    }





class LegacyDecisionListView(APIView):
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

        decisions = Decision.objects.filter(machine=machine).order_by("-criado_em")
        response = Response([_legacy_decision_payload(item) for item in decisions])
        response["Deprecation"] = "true"
        return response


class LegacyDecisionTestView(APIView):
    """View simplificada para testar prescrições"""
    permission_classes = [IsAuthenticatedOrPublicDemo]

    
    def get(self, request):
        response = Response(
            {"status": "erro", "detalhe": "rota de teste desativada; use Event/Decision"},
            status=status.HTTP_410_GONE,
        )
        response["Deprecation"] = "true"
        return response


class LegacyDecisionView(APIView):
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
        response = Response(payload)
        response["Deprecation"] = "true"
        return response

    def get(self, request):
        return self._executar(request, forcar_persistencia=False)

    def post(self, request):
        return self._executar(request, forcar_persistencia=True)
