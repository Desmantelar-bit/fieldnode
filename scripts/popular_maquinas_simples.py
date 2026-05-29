#!/usr/bin/env python
"""Script simplificado para criar máquinas"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from api_tcc.models import *

# Criar dados básicos
marca1, _ = Marca.objects.get_or_create(nome="Case IH")
marca2, _ = Marca.objects.get_or_create(nome="John Deere")
marca3, _ = Marca.objects.get_or_create(nome="New Holland")

modelo1, _ = Modelo.objects.get_or_create(nome="TC5000", marca=marca1)
modelo2, _ = Modelo.objects.get_or_create(nome="S780", marca=marca2)
modelo3, _ = Modelo.objects.get_or_create(nome="CR9090", marca=marca3)

op1, _ = Operario.objects.get_or_create(nome="João Silva", defaults={"tempo_de_servico": 5.0})
op2, _ = Operario.objects.get_or_create(nome="Maria Santos", defaults={"tempo_de_servico": 3.0})
op3, _ = Operario.objects.get_or_create(nome="Pedro Costa", defaults={"tempo_de_servico": 7.0})

# Criar objetos auxiliares com valores mínimos
comb = Combustivel.objects.create(porcentagem=75.0, tipo="Diesel")
pneus = PressaoPneus.objects.create(dianteiro_esquerdo=32.0, dianteiro_direito=32.0, traseiro_esquerdo=28.0, traseiro_direito=28.0)
altura = AlturadoCorte.objects.create(altura=15.0)
pressao = PressaodoCorte.objects.create(pressao=120.0)
temp_umi = TempUmi_Ambiente.objects.create(temperatura=28.0, umidade=65.0)
temp_maq = TemperaturaMaquina.objects.create(motor=85.0, oleo=75.0, transmissao=70.0)
status = StatusdeOperacao.objects.create(em_operacao=True, tempo_de_operacao=120.5)
movimento = EstadodeMovimento.objects.create(em_movimento=True, velocidade=12.5)

# Criar colheitadeiras
c1 = Colheitadeira.objects.create(
    modelo=modelo1, combustivel=comb, pressao_pneus=pneus,
    altura_do_corte=altura, pressao_do_corte=pressao,
    temp_umi_ambiente=temp_umi, temperatura_maquina=temp_maq,
    operario=op1, status_de_operacao=status, estado_de_movimento=movimento
)
print(f"✓ Criada: {c1.modelo.marca.nome} {c1.modelo.nome}")

c2 = Colheitadeira.objects.create(
    modelo=modelo2, combustivel=comb, pressao_pneus=pneus,
    altura_do_corte=altura, pressao_do_corte=pressao,
    temp_umi_ambiente=temp_umi, temperatura_maquina=temp_maq,
    operario=op2, status_de_operacao=status, estado_de_movimento=movimento
)
print(f"✓ Criada: {c2.modelo.marca.nome} {c2.modelo.nome}")

c3 = Colheitadeira.objects.create(
    modelo=modelo3, combustivel=comb, pressao_pneus=pneus,
    altura_do_corte=altura, pressao_do_corte=pressao,
    temp_umi_ambiente=temp_umi, temperatura_maquina=temp_maq,
    operario=op3, status_de_operacao=status, estado_de_movimento=movimento
)
print(f"✓ Criada: {c3.modelo.marca.nome} {c3.modelo.nome}")

print(f"\n✓ Total: {Colheitadeira.objects.count()} colheitadeiras")
