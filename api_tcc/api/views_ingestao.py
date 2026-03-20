from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api_tcc.models import LeituraTelemetria
from api_tcc.api.serializers import LeituraTelemetriaSerializer


class IngestaoTelemetriaView(APIView):

    def post(self, request):
        uuid_recebido = request.data.get('id')
        if uuid_recebido:
            if LeituraTelemetria.objects.filter(id=uuid_recebido).exists():
                return Response(
                    {'status': 'duplicata ignorada', 'id': uuid_recebido},
                    status=status.HTTP_200_OK
                )

        serializer = LeituraTelemetriaSerializer(data=request.data)
        if serializer.is_valid():
            maquina_id = serializer.validated_data.get('maquina_id', '').strip()
            if not maquina_id:
                return Response(
                    {'status': 'erro', 'detalhes': {'maquina_id': 'Este campo não pode ser vazio.'}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return Response(
                {'status': 'ok', 'id': str(serializer.data['id'])},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'status': 'erro', 'detalhes': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request):
        maquina = request.query_params.get('maquina_id')
        leituras = LeituraTelemetria.objects.all()
        if maquina:
            leituras = leituras.filter(maquina_id=maquina)
        serializer = LeituraTelemetriaSerializer(leituras[:50], many=True)
        return Response(serializer.data)
