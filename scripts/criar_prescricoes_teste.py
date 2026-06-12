#!/usr/bin/env python3
"""
Script para criar prescrições de teste no banco de dados.
"""

import os
import sys
import django
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fieldnode.settings')
django.setup()

from api_tcc.models import Prescricao, Colheitadeira, LeituraTelemetria
from api_tcc.services.prescricao import analisar_telemetria_e_gerar_prescricoes

def criar_colheitadeira_teste():
    """Garante que existe uma colheitadeira de teste"""
    from api_tcc.models import (Modelo, Marca, Combustivel, PressaoPneus, 
                               AlturadoCorte, PressaodoCorte, TempUmi_Ambiente,
                               TemperaturaMaquina, Operario, StatusdeOperacao, 
                               EstadodeMovimento, UnidadedeMedida)
    
    # Criar dependências básicas
    unidade, _ = UnidadedeMedida.objects.get_or_create(nome="°C")
    marca, _ = Marca.objects.get_or_create(nome="Case IH")
    modelo, _ = Modelo.objects.get_or_create(nome="Axial-Flow 9240", marca=marca)
    combustivel, _ = Combustivel.objects.get_or_create(tipo="Diesel", porcentagem=100.0)
    operario, _ = Operario.objects.get_or_create(nome="João Silva", tempo_de_servico=5)
    
    pressao_pneus, _ = PressaoPneus.objects.get_or_create(pressao=32.0, unidade_de_medida=unidade)
    altura_corte, _ = AlturadoCorte.objects.get_or_create(altura=15.0, unidade_de_medida=unidade)
    pressao_corte, _ = PressaodoCorte.objects.get_or_create(pressao=8.5, unidade_de_medida=unidade)
    temp_ambiente, _ = TempUmi_Ambiente.objects.get_or_create(temperatura=25.0, umidade=65.0)
    temp_maquina, _ = TemperaturaMaquina.objects.get_or_create(temperatura=85.0, maquina=modelo)
    status_op, _ = StatusdeOperacao.objects.get_or_create(em_operacao=True, tempo_de_operacao=8.5)
    movimento, _ = EstadodeMovimento.objects.get_or_create(em_movimento=True, velocidade=12.0)
    
    # Criar colheitadeira
    colheitadeira, created = Colheitadeira.objects.get_or_create(
        maquina_id="COLH-01",
        defaults={
            'modelo': modelo,
            'combustivel': combustivel,
            'pressao_pneus': pressao_pneus,
            'altura_do_corte': altura_corte,
            'pressao_do_corte': pressao_corte,
            'temp_umi_ambiente': temp_ambiente,
            'temperatura_maquina': temp_maquina,
            'operario': operario,
            'status_de_operacao': status_op,
            'estado_de_movimento': movimento,
        }
    )
    
    return colheitadeira

def criar_telemetria_teste(maquina_id="COLH-01"):
    """Cria dados de telemetria para gerar prescrições"""
    import uuid
    from django.utils import timezone
    
    # Cria leituras com temperatura alta para gerar prescrição
    for i in range(5):
        LeituraTelemetria.objects.create(
            id=uuid.uuid4(),
            maquina_id=maquina_id,
            temperatura=98.0 + i,  # Temperatura alta para trigger
            vibracao=0.3,
            rpm=1800,
            timestamp=timezone.now()
        )
    
    print(f"Criadas 5 leituras de teste para {maquina_id}")

def criar_prescricoes_diretas():
    """Cria prescrições diretamente no banco"""
    colheitadeira = criar_colheitadeira_teste()
    
    # Limpa prescrições antigas
    Prescricao.objects.filter(colheitadeira=colheitadeira).delete()
    
    # Cria prescrições de teste
    prescricoes = [
        {
            'titulo': 'Verificar Sistema de Arrefecimento',
            'descricao': 'Temperatura média elevada (98.2°C) detectada nas últimas leituras. Recomenda-se verificar radiador, nível de fluido de arrefecimento e funcionamento da ventoinha.',
            'status': 'pendente'
        },
        {
            'titulo': 'Manutenção Preventiva do Motor',
            'descricao': 'Análise dos dados indica necessidade de verificação dos filtros de ar e óleo. Temperatura operacional ligeiramente acima do normal.',
            'status': 'pendente'
        },
        {
            'titulo': 'Inspeção de Correias',
            'descricao': 'Dados de vibração sugerem possível folga em correias do sistema de transmissão. Verificar tensionamento.',
            'status': 'concluida'
        }
    ]
    
    for dados in prescricoes:
        Prescricao.objects.create(
            colheitadeira=colheitadeira,
            **dados
        )
    
    print(f"Criadas {len(prescricoes)} prescrições para {colheitadeira.maquina_id}")
    return prescricoes

def testar_servico_prescricao():
    """Testa o serviço de análise e geração de prescrições"""
    colheitadeira = criar_colheitadeira_teste()
    criar_telemetria_teste(colheitadeira.maquina_id)
    
    # Executa análise automática
    analisar_telemetria_e_gerar_prescricoes(colheitadeira.maquina_id)
    
    # Verifica se prescrições foram criadas
    prescricoes = Prescricao.objects.filter(colheitadeira=colheitadeira)
    print(f"Prescrições geradas automaticamente: {prescricoes.count()}")
    
    for p in prescricoes:
        print(f"  - {p.titulo}: {p.descricao[:50]}...")

def main():
    print("Criando dados de teste para prescrições...")
    print("=" * 50)
    
    # Cria colheitadeira e prescrições
    prescricoes = criar_prescricoes_diretas()
    
    # Testa também o serviço automático
    print("\nTestando geração automática...")
    testar_servico_prescricao()
    
    print("\n" + "=" * 50)
    print("Dados de teste criados com sucesso!")
    print("Agora você pode testar:")
    print("  curl 'http://127.0.0.1:8000/api/prescricoes/?maquina_id=COLH-01'")

if __name__ == "__main__":
    main()