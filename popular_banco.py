import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
sys.path.append('.')
django.setup()

from api_tcc.models import Prescricao, Colheitadeira, LeituraTelemetria
from api_tcc.models import Modelo, Marca, Combustivel, PressaoPneus, AlturadoCorte, PressaodoCorte, TempUmi_Ambiente, TemperaturaMaquina, Operario, StatusdeOperacao, EstadodeMovimento, UnidadedeMedida

# dependências mínimas sem colunas fantasmas
unidade, _ = UnidadedeMedida.objects.get_or_create(nome='°C')
marca, _ = Marca.objects.get_or_create(nome='Case IH')
modelo, _ = Modelo.objects.get_or_create(nome='Axial-Flow 9240', defaults={'marca': marca})
combustivel, _ = Combustivel.objects.get_or_create(tipo='Diesel', porcentagem=100.0)

# criando operário sem o campo tempo_de_servico que bugou o banco antes
operario, _ = Operario.objects.get_or_create(nome='João Silva', defaults={'tempo_de_servico': 5})

pressao_pneus, _ = PressaoPneus.objects.get_or_create(pressao=32.0, unidade_de_medida=unidade)
altura_corte, _ = AlturadoCorte.objects.get_or_create(altura=15.0, unidade_de_medida=unidade)
pressao_corte, _ = PressaodoCorte.objects.get_or_create(pressao=8.5, unidade_de_medida=unidade)
temp_ambiente, _ = TempUmi_Ambiente.objects.get_or_create(temperatura=25.0, umidade=65.0)
temp_maquina, _ = TemperaturaMaquina.objects.get_or_create(temperatura=85.0, maquina=modelo)
status_op, _ = StatusdeOperacao.objects.get_or_create(em_operacao=True, tempo_de_operacao=8.5)
movimento, _ = EstadodeMovimento.objects.get_or_create(em_movimento=True, velocidade=12.0)

# garante a máquina exata que o front ou o curl vai buscar
colheitadeira, _ = Colheitadeira.objects.get_or_create(
    maquina_id='CASE-TC5000-01',
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

# injetando as duas prescrições reais com os campos corretos mapeados pelo zod no front
Prescricao.objects.create(
    colheitadeira=colheitadeira,
    titulo='Verificar Sistema de Arrefecimento',
    descricao='Temperatura média elevada (98.2°C) detectada nas últimas leituras. Recomenda-se verificar radiador, nível de fluido de arrefecimento e funcionamento da ventoinha.',
    status='pendente'
)

Prescricao.objects.create(
    colheitadeira=colheitadeira,
    titulo='Manutenção Preventiva do Motor', 
    descricao='Análise dos dados indica necessidade de verificação dos filtros de ar e óleo. Temperatura operacional ligeiramente acima do normal.',
    status='pendente'
)

print("banco populado de verdade, caralho!")