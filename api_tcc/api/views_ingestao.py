from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError, connection
from api_tcc.models import LeituraTelemetria
from api_tcc.api.serializers import LeituraTelemetriaSerializer
from api_tcc.ia.anomalias import detectar_anomalias
from api_tcc.ia.manutencao import prever_manutencao


class AnomaliaView(APIView):
    """
    GET /api/anomalias/
    GET /api/anomalias/?maquina_id=COLH-01

    Detecta leituras fora do padrão usando Isolation Forest.
    Precisa de pelo menos 20 leituras no banco para funcionar.
    """
    def get(self, request):
        maquina = request.query_params.get('maquina_id')
        resultado = detectar_anomalias(maquina_id=maquina)
        return Response(resultado)

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
            try:
                serializer.save()
            except IntegrityError:
                return Response(
                    {'status': 'duplicata ignorada', 'id': str(serializer.validated_data.get('id', ''))},
                    status=status.HTTP_200_OK
                )
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


class UltimaLeituraView(APIView):
    """
    Retorna a leitura mais recente de cada máquina ativa.
    Opcionalmente filtra por maquina_id.

    GET /api/leituras/ultimas/
    GET /api/leituras/ultimas/?maquina_id=COLH-01

    Resposta:
    [
        {
            "maquina_id": "COLH-01",
            "temperatura": 87.3,
            "vibracao": 0.45,
            "rpm": 1850,
            "timestamp": "2026-04-10T14:32:01",
            "nivel_risco": "CRITICO",
            "total_leituras": 124
        }
    ]
    """

    def get(self, request):
        maquina = request.query_params.get('maquina_id')

        # SQL raw para pegar apenas a última leitura de cada máquina
        with connection.cursor() as cursor:
            if maquina:
                cursor.execute("""
                    SELECT t1.maquina_id, t1.temperatura, t1.vibracao, t1.rpm, t1.timestamp, t2.total_leituras
                    FROM api_tcc_leituratelemetria t1
                    INNER JOIN (
                        SELECT maquina_id, MAX(timestamp) as max_ts
                        FROM api_tcc_leituratelemetria
                        WHERE maquina_id = %s
                    ) t_max ON t1.maquina_id = t_max.maquina_id AND t1.timestamp = t_max.max_ts
                    INNER JOIN (
                        SELECT maquina_id, COUNT(*) as total_leituras
                        FROM api_tcc_leituratelemetria
                        WHERE maquina_id = %s
                    ) t_count ON t1.maquina_id = t_count.maquina_id
                    WHERE t1.maquina_id = %s
                """, [maquina, maquina, maquina])
            else:
                cursor.execute("""
                    SELECT t1.maquina_id, t1.temperatura, t1.vibracao, t1.rpm, t1.timestamp, t3.total_leituras
                    FROM api_tcc_leituratelemetria t1
                    INNER JOIN (
                        SELECT maquina_id, MAX(timestamp) as max_ts
                        FROM api_tcc_leituratelemetria
                        GROUP BY maquina_id
                    ) t2 ON t1.maquina_id = t2.maquina_id AND t1.timestamp = t2.max_ts
                    INNER JOIN (
                        SELECT maquina_id, COUNT(*) as total_leituras
                        FROM api_tcc_leituratelemetria
                        GROUP BY maquina_id
                    ) t3 ON t1.maquina_id = t3.maquina_id
                    ORDER BY t1.maquina_id
                    LIMIT 10
                """)
            
            rows = cursor.fetchall()
        
        resultado = []
        for row in rows:
            mid, temp, vib, rpm, ts, total = row
            
            if temp > 85 or vib > 0.8:
                nivel = 'CRITICO'
            elif temp > 75 or vib > 0.5:
                nivel = 'ATENCAO'
            else:
                nivel = 'NORMAL'
                
            resultado.append({
                'maquina_id': mid,
                'temperatura': temp,
                'vibracao': vib,
                'rpm': rpm,
                'timestamp': ts,
                'nivel_risco': nivel,
                'total_leituras': total,
            })

        return Response(resultado)


class ManutencaoView(APIView):
    """
    GET /api/manutencao/?maquina_id=COLH-01

    Prevê probabilidade de necessidade de manutenção.
    Precisa de pelo menos 30 leituras da máquina especificada.
    """
    def get(self, request):
        maquina = request.query_params.get('maquina_id')
        if not maquina:
            return Response(
                {'status': 'erro', 'detalhe': 'maquina_id é obrigatório'},
                status=400
            )
        resultado = prever_manutencao(maquina_id=maquina)
        return Response(resultado)
