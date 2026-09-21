import logging
import math

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from api_tcc.ia.pipeline import analisar_maquina
from api_tcc.ia.explicacao_llm import gerar_explicacao_natural
from api_tcc.models import Machine

logger = logging.getLogger("api_tcc.api")


def _is_demo_publico(request) -> bool:
    return bool(settings.DEMO_MODE and not request.user.is_authenticated)


def _demo_machine_allowed(maquina_id: str, request) -> bool:
    if not _is_demo_publico(request):
        return True
    return Machine.objects.filter(external_code=maquina_id.strip().upper(), is_demo=True).exists()


def _valor_json_seguro(valor):
    """Converte escalares pandas/numpy e NaN para valores JSON seguros."""
    if hasattr(valor, "item"):
        valor = valor.item()

    if isinstance(valor, float):
        if not math.isfinite(valor):
            return None
        return valor

    if isinstance(valor, dict):
        return {chave: _valor_json_seguro(item) for chave, item in valor.items()}

    if isinstance(valor, list):
        return [_valor_json_seguro(item) for item in valor]

    return valor


class PrescricaoView(APIView):
    """
    Ponto crítico de honestidade técnica (TCC):
    O campo status retorna NORMAL / ATENCAO / CRITICO com base em comportamento anômalo.
    O sistema NAO afirma prever o momento exato da falha, pois isso exigiria dataset histórico
    de quebras reais que não está disponível. O objetivo é a recomendação preditiva/preventiva.
    """

    def get(self, request, maquina_id):
        if not _demo_machine_allowed(maquina_id, request):
            return Response(
                {"status": "erro", "detalhe": "máquina não disponível no dataset demo"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            resultado = analisar_maquina(maquina_id)
            metricas_seguras = _valor_json_seguro(resultado.metricas)
        except Exception as exc:
            logger.exception(
                "Erro ao processar prescricao para maquina %s: %s",
                maquina_id,
                exc,
            )
            return Response(
                {"status": "erro", "detalhe": "não foi possível processar a análise"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        explicacao = gerar_explicacao_natural(resultado)

        return Response(
            {
                "maquina_id": resultado.maquina_id,
                "status": resultado.status,
                "motivos": resultado.motivos,
                "metricas": metricas_seguras,
                "recomendacao": resultado.recomendacao,
                "recomendacao_tecnica": resultado.recomendacao,
                "explicacao_operador": explicacao["texto"],
                "fonte_explicacao": explicacao["fonte"],
                "gerado_em": timezone.now().isoformat(),
            }
        )
