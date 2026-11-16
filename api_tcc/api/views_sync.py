import csv
import io

from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.models import DeliveryHop


class DeliveryReportView(APIView):
    """JSON/CSV report of the delivery hops recorded for telemetry."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        hops = DeliveryHop.objects.select_related("leitura").order_by(
            "leitura__device_id", "leitura__sequence_number", "hop_index"
        )
        device_id = request.query_params.get("device_id")
        if device_id:
            hops = hops.filter(leitura__device_id=device_id)
        rows = [
            {
                "device_id": hop.leitura.device_id,
                "message_id": hop.leitura.message_id,
                "sequence_number": hop.leitura.sequence_number,
                "hop_index": hop.hop_index,
                "node_id": hop.node_id,
                "recebido_em": hop.recebido_em.isoformat(),
                "entregue_em": hop.entregue_em.isoformat() if hop.entregue_em else None,
            }
            for hop in hops[:5000]
        ]
        if request.query_params.get("format") == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=list(rows[0]) if rows else [
                "device_id", "message_id", "sequence_number", "hop_index", "node_id",
                "recebido_em", "entregue_em",
            ])
            writer.writeheader()
            writer.writerows(rows)
            return HttpResponse(output.getvalue(), content_type="text/csv; charset=utf-8")
        return Response({"count": len(rows), "hops": rows})
