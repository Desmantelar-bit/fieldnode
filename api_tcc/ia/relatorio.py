"""
api_tcc/ia/relatorio.py

Geração de relatórios operacionais para máquinas.

Funcionalidades:
- Cálculo de horas operadas baseado em leituras
- Identificação de picos de temperatura
- Contagem de alertas/anomalias
- Recomendações de manutenção baseadas em padrões

Usado pelo endpoint /api/relatorio/ para exportação CSV/JSON.
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from api_tcc.models import LeituraTelemetria
from api_tcc.ia.pipeline import carregar_dados

logger = logging.getLogger(__name__)


def gerar_relatorio(maquina_id: str, periodo_dias: int = 7) -> dict:
    """
    Gera relatório operacional completo para uma máquina.
    
    Args:
        maquina_id: ID da máquina
        periodo_dias: Período em dias para análise
    
    Returns:
        Dict com status e dados do relatório
    """
    try:
        # Calcula período de análise
        data_fim = timezone.now()
        data_inicio = data_fim - timedelta(days=periodo_dias)
        
        # Busca leituras no período
        leituras = LeituraTelemetria.objects.filter(
            maquina_id=maquina_id,
            timestamp__gte=data_inicio,
            timestamp__lte=data_fim
        ).order_by('timestamp')
        
        if not leituras.exists():
            return {
                'status': 'dados_insuficientes',
                'detalhe': f'Nenhuma leitura encontrada para {maquina_id} nos últimos {periodo_dias} dias'
            }
        
        # Calcula métricas
        horas_operadas = _calcular_horas_operadas(leituras)
        pico_temperatura = _calcular_pico_temperatura(leituras)
        num_alertas = _contar_alertas(leituras)
        recomendacao = _gerar_recomendacao_manutencao(leituras, horas_operadas, num_alertas)
        
        return {
            'status': 'ok',
            'maquina_id': maquina_id,
            'periodo_dias': periodo_dias,
            'data_inicio': data_inicio.isoformat(),
            'data_fim': data_fim.isoformat(),
            'total_leituras': leituras.count(),
            'dados': {
                'horas_operadas': horas_operadas,
                'pico_temperatura': pico_temperatura,
                'num_alertas': num_alertas,
                'recomendacao_manutencao': recomendacao
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório para {maquina_id}: {e}")
        return {
            'status': 'erro',
            'detalhe': f'Falha interna: {str(e)}'
        }


def _calcular_horas_operadas(leituras) -> float:
    """
    Calcula horas operadas baseado no intervalo entre leituras.
    Assume que cada leitura representa ~3 segundos de operação.
    """
    if not leituras:
        return 0.0
    
    # Método simples: conta leituras e multiplica por intervalo médio
    total_leituras = leituras.count()
    intervalo_medio_segundos = 3  # Baseado no polling do ESP32
    
    total_segundos = total_leituras * intervalo_medio_segundos
    horas = total_segundos / 3600
    
    return round(horas, 1)


def _calcular_pico_temperatura(leituras) -> float:
    """
    Encontra a maior temperatura registrada no período.
    """
    if not leituras:
        return 0.0
    
    pico = max(leitura.temperatura for leitura in leituras)
    return round(pico, 1)


def _contar_alertas(leituras) -> int:
    """
    Conta leituras que excedem limites operacionais.
    
    Critérios de alerta:
    - Temperatura > 75°C
    - Vibração > 0.5g
    - RPM < 1300 (baixa rotação)
    """
    alertas = 0
    
    for leitura in leituras:
        if (leitura.temperatura > 75 or 
            leitura.vibracao > 0.5 or 
            leitura.rpm < 1300):
            alertas += 1
    
    return alertas


def _gerar_recomendacao_manutencao(leituras, horas_operadas: float, num_alertas: int) -> str:
    """
    Gera recomendação de manutenção baseada nos dados operacionais.
    """
    total_leituras = leituras.count()
    taxa_alertas = (num_alertas / max(total_leituras, 1)) * 100
    
    # Análise de temperatura
    temp_criticas = sum(1 for l in leituras if l.temperatura > 85)
    
    # Decisão baseada em regras
    if temp_criticas > 0:
        return "URGENTE: Manutenção imediata necessária - temperaturas críticas detectadas"
    
    if taxa_alertas > 20:
        return "ALTA PRIORIDADE: Agendar manutenção preventiva - muitos alertas registrados"
    
    if horas_operadas > 50:  # Mais de 50h no período
        return "MÉDIA PRIORIDADE: Verificar componentes - alta utilização detectada"
    
    if taxa_alertas > 10:
        return "BAIXA PRIORIDADE: Monitorar de perto - alguns alertas registrados"
    
    return "NORMAL: Continuar operação - máquina dentro dos parâmetros"