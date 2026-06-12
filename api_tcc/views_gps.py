from django.http import JsonResponse
from .models import LeituraTelemetria, Colheitadeira
from django.utils import timezone
from datetime import timedelta

def get_maquinas_posicao(request):
    """
    Retorna a última localização e status de todas as colheitadeiras ou de uma específica.
    Parâmetro GET opcional: maquina_id (ID da colheitadeira)
    """
    maquina_id_param = request.GET.get('maquina_id')
    if maquina_id_param:
        try:
            # Filtragem robusta pelo ID primário para evitar confusão com nomes de modelos
            maquinas = Colheitadeira.objects.filter(id=maquina_id_param).select_related('modelo', 'status_de_operacao')
        except ValueError:
            maquinas = Colheitadeira.objects.none()
    else:
        maquinas = Colheitadeira.objects.select_related('modelo', 'status_de_operacao').all()

    agora = timezone.now()
    resultado = []

    for maquina in maquinas:
        # Busca a última leitura de telemetria desta máquina
        # Nota: Assume-se que maquina_id na telemetria corresponde ao ID da Colheitadeira
        ultima_leitura = LeituraTelemetria.objects.filter(
            maquina_id=str(maquina.id)
        ).order_by('-timestamp').first()

        if ultima_leitura and ultima_leitura.latitude and ultima_leitura.longitude:
            # Lógica simples de status
            # Usamos 'recebido_em' como fallback de segurança caso o relógio do ESP32 esteja errado
            referencia_tempo = ultima_leitura.recebido_em
            esta_online = referencia_tempo > (agora - timedelta(minutes=10))

            status = "operando" if (esta_online and maquina.status_de_operacao.em_operacao) else \
                     "parada" if esta_online else "offline"

            resultado.append({
                "id": maquina.id,
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