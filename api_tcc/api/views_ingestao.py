import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from api_tcc.api.serializers import LeituraTelemetriaSerializer
from api_tcc.api.parsers import BoundedTelemetryJSONParser
from api_tcc.api.throttles import IngestaoThrottle
from api_tcc.api.views_common import (
    HasIngestionCredential, _filter_public_demo_leituras, _is_public_demo_request,
    _serializar_analise,
)
from api_tcc.ia.pipeline import analisar_maquina
from api_tcc.models import LeituraTelemetria, SyncCursor
from api_tcc.permissions import IsAuthenticatedOrPublicDemo
from api_tcc.services.telemetria import _computar_payload_hash, registrar_leitura

logger = logging.getLogger(__name__)





class IngestaoTelemetriaView(APIView):
    """
    POST /api/telemetria/ — recebe leitura do ESP32
    GET  /api/telemetria/ — lista últimas 50 leituras (dev/debug)

    Autenticação: credencial individual nos headers X-Device-Id/X-Device-Key.
    Idempotência: UUID duplicado retorna 200 sem reprocessar.
    Validação: payload inválido retorna 400 e é arquivado em TelemetriaInvalida.
    """
    throttle_classes = [AnonRateThrottle, UserRateThrottle, IngestaoThrottle]
    parser_classes = [BoundedTelemetryJSONParser, FormParser, MultiPartParser]

    def get_permissions(self):
        permission = HasIngestionCredential if self.request.method == 'POST' else IsAuthenticatedOrPublicDemo
        return [permission()]

    def get_throttles(self):
        if self.request.method == 'POST':
            return super().get_throttles()
        return []

    def post(self, request):
        resultado, detalhe = registrar_leitura(
            request.data,
            authenticated_device_id=getattr(request, "authenticated_ingestion_device_id", None),
        )

        if resultado == "criado":
            analise = analisar_maquina(request.data.get("maquina_id"))
            return Response({
                'status': 'ok',
                'id': detalhe,
                **self._ack_payload(detalhe, "acked"),
                'ia': _serializar_analise(analise),
            }, status=status.HTTP_201_CREATED)

        if resultado == "duplicata":
            return Response({
                'status': 'duplicata ignorada',
                'id': detalhe,
                **self._ack_payload(detalhe, "duplicate"),
            },
                            status=status.HTTP_200_OK)

        if resultado == "conflito":
            return Response({"status": "conflict", "id": detalhe,
                             **self._ack_payload(detalhe, "conflict"),
                             "payload_hash": _computar_payload_hash(request.data)}, status=status.HTTP_409_CONFLICT)

        if resultado == "invalido":
            rejected_device = request.data.get('device_id', request.data.get('maquina_id'))
            rejected_cursor = SyncCursor.objects.filter(device_id=rejected_device).values_list(
                'last_acked_sequence', flat=True
            ).first() or 0
            return Response({'status': 'rejected', 'reason': detalhe,
                             'message_id': request.data.get('message_id', request.data.get('id')),
                             'device_id': rejected_device,
                             'sequence_number': request.data.get('sequence_number'),
                             'last_acked_sequence': rejected_cursor,
                             'payload_hash': _computar_payload_hash(dict(request.data))},
                            status=status.HTTP_400_BAD_REQUEST)

        # resultado == "erro" — falha inesperada de banco
        return Response({'status': 'erro', 'detalhes': 'falha interna — verifique logs'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def _ack_payload(leitura_id: str | None, ack_status: str) -> dict:
        """Expõe apenas os dados necessários para um ACK verificável no edge."""
        if not leitura_id:
            return {}
        try:
            leitura = LeituraTelemetria.objects.get(id=leitura_id)
        except (LeituraTelemetria.DoesNotExist, ValueError, TypeError):
            logger.info("ACK omitido: leitura %s indisponível", leitura_id)
            return {}
        cursor = SyncCursor.objects.filter(device_id=leitura.device_id).first()
        return {
            'status': ack_status,
            'message_id': leitura.message_id,
            'device_id': leitura.device_id,
            'sequence_number': leitura.sequence_number,
            'payload_hash': leitura.payload_hash,
            'last_acked_sequence': cursor.last_acked_sequence if cursor else 0,
            'sync_cursor': cursor.last_acked_sequence if cursor else 0,
        }

    def get(self, request):
        if not request.user.is_authenticated and not _is_public_demo_request(request):
            return Response({'detail': 'Autenticação obrigatória.'}, status=status.HTTP_401_UNAUTHORIZED)
        maquina = request.query_params.get('maquina_id')
        leituras = _filter_public_demo_leituras(LeituraTelemetria.objects.all(), request)
        if maquina:
            leituras = leituras.filter(maquina_id=maquina)
        serializer = LeituraTelemetriaSerializer(leituras[:50], many=True)
        return Response(serializer.data)
