from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.api.serializers import DecisionActionSerializer, DecisionSerializer
from api_tcc.models import Decision
from api_tcc.permissions import IsAuthenticatedOrPublicDemo, request_can_access_machine, user_can_access_machine
from api_tcc.services.decisions import aplicar_acao_decision





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
