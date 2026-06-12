import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fieldnode.settings')
django.setup()

from api_tcc.models import *
from django.utils import timezone

def criar_dados_teste():
    # Criar dependências básicas
    unidade, _ = UnidadedeMedida.objects.get_or_create(nome='°C')
    marca, _ = Marca.objects.get_or_create(nome='Case IH')
    modelo, _ = Modelo.objects.get_or_create(nome='Axial-Flow 9240', defaults={'marca': marca})
    combustivel, _ = Combustivel.objects.get_or_create(tipo='Diesel', porcentagem=100.0)
    operario, _ = Operario.objects.get_or_create(nome='João Silva', tempo_de_servico=5)

    pressao_pneus, _ = PressaoPneus.objects.get_or_create(pressao=32.0, unidade_de_medida=unidade)
    altura_corte, _ = AlturadoCorte.objects.get_or_create(altura=15.0, unidade_de_medida=unidade)
    pressao_corte, _ = PressaodoCorte.objects.get_or_create(pressao=8.5, unidade_de_medida=unidade)
    temp_ambiente, _ = TempUmi_Ambiente.objects.get_or_create(temperatura=25.0, umidade=65.0)
    temp_maquina, _ = TemperaturaMaquina.objects.get_or_create(temperatura=85.0, maquina=modelo)
    status_op, _ = StatusdeOperacao.objects.get_or_create(em_operacao=True, tempo_de_operacao=8.5)
    movimento, _ = EstadodeMovimento.objects.get_or_create(em_movimento=True, velocidade=12.0)

    # Criar colheitadeira
    colheitadeira, created = Colheitadeira.objects.get_or_create(
        maquina_id='COLH-01',
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

    # Limpar prescrições antigas
    Prescricao.objects.filter(colheitadeira=colheitadeira).delete()

    # Criar prescrições de teste
    p1 = Prescricao.objects.create(
        colheitadeira=colheitadeira,
        titulo='Verificar Sistema de Arrefecimento',
        descricao='Temperatura média elevada (98.2°C) detectada nas últimas leituras. Recomenda-se verificar radiador, nível de fluido de arrefecimento e funcionamento da ventoinha.',
        status='pendente'
    )

    p2 = Prescricao.objects.create(
        colheitadeira=colheitadeira,
        titulo='Manutenção Preventiva do Motor', 
        descricao='Análise dos dados indica necessidade de verificação dos filtros de ar e óleo. Temperatura operacional ligeiramente acima do normal.',
        status='pendente'
    )

    print(f'Colheitadeira criada: {colheitadeira.maquina_id}')
    print(f'Prescrições criadas: {p1.id}, {p2.id}')
    print('Dados de teste criados com sucesso!')

if __name__ == '__main__':
    criar_dados_teste()