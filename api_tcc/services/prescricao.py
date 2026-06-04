from api_tcc.models import LeituraTelemetria, Prescricao, Colheitadeira

def analisar_telemetria_e_gerar_prescricoes(maquina_id):
    """
    Analisa as últimas leituras de telemetria para sugerir ações de manutenção.
    """
    leituras = LeituraTelemetria.objects.filter(maquina_id=maquina_id).order_by('-timestamp')[:10]
    if not leituras.exists():
        return

    colheitadeira = Colheitadeira.objects.filter(maquina_id=maquina_id).first()
    if not colheitadeira:
        return

    # Exemplo de regra: Temperatura alta
    temp_media = sum(l.temperatura for l in leituras) / len(leituras)
    if temp_media > 95:
        Prescricao.objects.get_or_create(
            colheitadeira=colheitadeira,
            titulo="Verificar Sistema de Arrefecimento",
            descricao=f"Temperatura média elevada ({temp_media:.1f}°C) detectada nas últimas leituras.",
            status='pendente'
        )

    # Exemplo de regra: Vibração excessiva
    vibracao_max = max(l.vibracao for l in leituras)
    if vibracao_max > 8.0:
        Prescricao.objects.get_or_create(
            colheitadeira=colheitadeira,
            titulo="Manutenção de Rolamentos",
            descricao=f"Pico de vibração ({vibracao_max}) detectado. Possível desgaste em componentes móveis.",
            status='pendente'
        )