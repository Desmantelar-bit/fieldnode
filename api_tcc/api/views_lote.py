from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from api_tcc.api.throttles import IngestaoThrottle
from api_tcc.api.parsers import BoundedTelemetryJSONParser
from api_tcc.api.views_common import HasIngestionCredential
from api_tcc.models import LeituraTelemetria, SyncCursor
from api_tcc.services.telemetria import _computar_payload_hash, registrar_leitura





class IngestaoLoteView(APIView):
    """
    Aceita um array de leituras acumuladas (buffer local do gateway/ESP32).
    Cada item precisa ter seu próprio UUID. Duplicatas são ignoradas individualmente:
    uma leitura ruim no meio do lote não derruba o resto.

    Nota Técnica (TCC): o processamento ocorre item a item (não bulk_create) para
    privilegiar o relatório detalhado de debug em campo sobre performance bruta.
    """
    throttle_classes = [AnonRateThrottle, UserRateThrottle, IngestaoThrottle]
    parser_classes = [BoundedTelemetryJSONParser, FormParser, MultiPartParser]

    def get_permissions(self):
        permission = HasIngestionCredential if self.request.method == 'POST' else IsAuthenticatedOrPublicDemo
        return [permission()]

    def post(self, request):
        leituras = request.data.get('leituras', [])

        if not isinstance(leituras, list) or not leituras:
            return Response(
                {'status': 'erro', 'detalhe': "corpo precisa ter uma lista 'leituras'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(leituras) > 500:
            return Response(
                {'status': 'erro', 'detalhe': 'lote máximo de 500 leituras por request'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        resultado = {'salvas': 0, 'duplicadas': 0, 'invalidas': 0, 'erros': [], 'items': []}

        for index, item in enumerate(leituras):
            if not isinstance(item, dict):
                resultado['invalidas'] += 1
                resultado['erros'].append({'id': None, 'detalhe': 'item precisa ser um objeto JSON'})
                continue

            status_item, detalhe = registrar_leitura(item)
            if status_item == "erro":
                return Response({
                    **resultado,
                    "accepted": resultado["salvas"],
                    "rejected": resultado["invalidas"],
                    "duplicates": resultado["duplicadas"],
                    "failure": {"message_id": item.get("message_id", item.get("id")),
                                "reason": "persistência não confirmada"},
                    "pending_message_ids": [
                        pending.get("message_id", pending.get("id"))
                        for pending in leituras[index + 1:]
                        if isinstance(pending, dict)
                    ],
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            ack_status = {"criado": "acked", "duplicata": "duplicate", "conflito": "conflict",
                          "invalido": "rejected"}.get(status_item, "rejected")
            entry = LeituraTelemetria.objects.filter(id=detalhe).first() if status_item in {"criado", "duplicata", "conflito"} else None
            item_device_id = entry.device_id if entry else item.get("device_id", item.get("maquina_id"))
            cursor_value = SyncCursor.objects.filter(device_id=item_device_id).values_list(
                "last_acked_sequence", flat=True
            ).first() or 0
            resultado["items"].append({
                "message_id": (entry.message_id if entry else item.get("message_id", item.get("id"))),
                "device_id": item_device_id,
                "sequence_number": (entry.sequence_number if entry else item.get("sequence_number")),
                "status": ack_status,
                "payload_hash": (entry.payload_hash if entry else _computar_payload_hash(item)),
                "last_acked_sequence": cursor_value,
                **({"reason": detalhe} if ack_status == "rejected" else {}),
            })
            if status_item == "criado":
                resultado['salvas'] += 1
            elif status_item == "duplicata":
                resultado['duplicadas'] += 1
            elif status_item == "invalido":
                resultado['invalidas'] += 1
                resultado['erros'].append({
                    'id': item.get('id'),
                    'detalhe': detalhe,
                })
            elif status_item == "conflito":
                resultado['invalidas'] += 1
                resultado['erros'].append({
                    'id': item.get('id'),
                    'detalhe': 'falha interna ao persistir a leitura',
                })
            else:
                resultado['erros'].append({
                    'id': item.get('id'),
                    'detalhe': 'falha interna ao persistir a leitura',
                })

        resultado.update(
            accepted=resultado['salvas'],
            rejected=resultado['invalidas'],
            duplicates=resultado['duplicadas'],
        )
        return Response(resultado, status=status.HTTP_200_OK)
