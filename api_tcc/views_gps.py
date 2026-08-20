import random
from django.http import JsonResponse
from .models import LeituraTelemetria, Colheitadeira
from django.views.decorators.http import require_GET
from django.utils import timezone
from datetime import timedelta

DEMO_ROUTE = [
    {"lat": -15.793889, "lng": -47.882778, "status": "operando"},
    {"lat": -15.795500, "lng": -47.885000, "status": "parada"},
    {"lat": -15.798000, "lng": -47.888500, "status": "operando"},
    {"lat": -15.801000, "lng": -47.892000, "status": "parada"},
    {"lat": -15.803500, "lng": -47.889500, "status": "operando"},
    {"lat": -15.802000, "lng": -47.885000, "status": "offline"},
    {"lat": -15.799000, "lng": -47.881500, "status": "parada"},
    {"lat": -15.796000, "lng": -47.879000, "status": "operando"},
    {"lat": -15.794000, "lng": -47.881000, "status": "parada"},
    {"lat": -15.793889, "lng": -47.882778, "status": "operando"},
]

MODELS_DEMO = ['TC5000', 'CR9000', 'BC8800', 'TX7000', 'AF9000', 'W5000', 'MX3000', 'FH7800']

@require_GET
def gps_demo(request):
    maquina_id_param = request.GET.get('maquina_id')
    route = []
    now = timezone.now().isoformat()

    pontos = [DEMO_ROUTE[0]] if maquina_id_param else DEMO_ROUTE

    for idx, ponto in enumerate(pontos):
        lat_drift = (random.random() - 0.5) * 0.0001
        lng_drift = (random.random() - 0.5) * 0.0001
        route.append({
            "id": idx + 1,
            "maquina_id": maquina_id_param or f"COLH-{str(idx + 1).zfill(2)}",
            "modelo": MODELS_DEMO[idx] if idx < len(MODELS_DEMO) else "TC5000",
            "lat": round(ponto["lat"] + lat_drift, 6),
            "lng": round(ponto["lng"] + lng_drift, 6),
            "status": ponto["status"],
            "telemetria": {
                "temperatura": round(68 + random.random() * 20, 1),
                "rpm": round(1500 + random.random() * 500),
                "timestamp": now
            }
        })

    return JsonResponse(route, safe=False)

def get_maquinas_posicao(request):
    """
    Retorna a última localização e status de todas as colheitadeiras ou de uma específica.

    Parâmetro GET opcional: maquina_id (ID textual da colheitadeira, ex: COLH-01)

    A busca usa o identificador textual (maquina_id) para filtrar tanto a máquina
    quanto a telemetria relacionada. O status online/offline é determinado pela
    data de recebimento da última leitura (recebido_em).
    """
    maquina_id_param = request.GET.get('maquina_id')
    if maquina_id_param:
        maquinas = Colheitadeira.objects.filter(
            maquina_id=maquina_id_param, ativo=True
        ).select_related('modelo', 'status_de_operacao')
    else:
        maquinas = Colheitadeira.objects.filter(ativo=True).select_related('modelo', 'status_de_operacao')

    agora = timezone.now()
    resultado = []

    for maquina in maquinas:
        ultima_leitura = LeituraTelemetria.objects.filter(
            maquina_id=maquina.maquina_id
        ).order_by('-recebido_em').first()

        if (
            ultima_leitura
            and ultima_leitura.latitude is not None
            and ultima_leitura.longitude is not None
        ):
            referencia_tempo = ultima_leitura.recebido_em or ultima_leitura.timestamp
            esta_online = referencia_tempo > (agora - timedelta(minutes=10))

            if esta_online and maquina.status_de_operacao.em_operacao:
                status = "operando"
            elif esta_online:
                status = "parada"
            else:
                status = "offline"

            resultado.append({
                "id": maquina.id,
                "maquina_id": maquina.maquina_id,
                "modelo": maquina.modelo.nome,
                "lat": ultima_leitura.latitude,
                "lng": ultima_leitura.longitude,
                "status": status,
                "telemetria": {
                    "temperatura": ultima_leitura.temperatura,
                    "rpm": ultima_leitura.rpm,
                    "timestamp": ultima_leitura.timestamp.isoformat()
                }
            })

    return JsonResponse(resultado, safe=False)
