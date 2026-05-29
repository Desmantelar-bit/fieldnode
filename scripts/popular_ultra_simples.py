#!/usr/bin/env python
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from api_tcc.models import *

# Unidade
u, _ = UnidadedeMedida.objects.get_or_create(nome="PSI")

# Marcas e modelos
m1, _ = Marca.objects.get_or_create(nome="Case IH")
m2, _ = Marca.objects.get_or_create(nome="John Deere")
m3, _ = Marca.objects.get_or_create(nome="New Holland")

mod1, _ = Modelo.objects.get_or_create(nome="TC5000", marca=m1)
mod2, _ = Modelo.objects.get_or_create(nome="S780", marca=m2)
mod3, _ = Modelo.objects.get_or_create(nome="CR9090", marca=m3)

# Operários
op1, _ = Operario.objects.get_or_create(nome="João Silva", defaults={"tempo_de_servico": 5.0})
op2, _ = Operario.objects.get_or_create(nome="Maria Santos", defaults={"tempo_de_servico": 3.0})
op3, _ = Operario.objects.get_or_create(nome="Pedro Costa", defaults={"tempo_de_servico": 7.0})

# Auxiliares
comb = Combustivel.objects.create(porcentagem=75.0, tipo="Diesel")
pneus = PressaoPneus.objects.create(pressao=32.0, unidade_de_medida=u)
altura = AlturadoCorte.objects.create(altura=15.0, unidade_de_medida=u)
pressao = PressaodoCorte.objects.create(pressao=120.0, unidade_de_medida=u)
temp_umi = TempUmi_Ambiente.objects.create(temperatura=28.0, umidade=65.0)
temp_maq = TemperaturaMaquina.objects.create(temperatura=85.0, maquina=mod1)
status = StatusdeOperacao.objects.create(em_operacao=True, tempo_de_operacao=120.5)
movimento = EstadodeMovimento.objects.create(em_movimento=True, velocidade=12.5)

# Colheitadeiras
for mod, op in [(mod1, op1), (mod2, op2), (mod3, op3)]:
    c = Colheitadeira.objects.create(
        modelo=mod, combustivel=comb, pressao_pneus=pneus,
        altura_do_corte=altura, pressao_do_corte=pressao,
        temp_umi_ambiente=temp_umi, temperatura_maquina=temp_maq,
        operario=op, status_de_operacao=status, estado_de_movimento=movimento
    )
    print(f"✓ {c.modelo.marca.nome} {c.modelo.nome}")

print(f"\n✓ {Colheitadeira.objects.count()} colheitadeiras")
print(f"✓ {Operario.objects.count()} operários")
