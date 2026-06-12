#!/usr/bin/env python
"""Script oficial para popular o banco com dados de teste.

Cria 3 colheitadeiras completas com maquina_id, operários e dependências.
Use: python scripts/popular_banco.py
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from api_tcc.models import *

print("🔧 Populando banco de dados...\n")

# 1. Unidades de medida
print("📏 Criando unidades de medida...")
u_psi, _ = UnidadedeMedida.objects.get_or_create(nome="PSI")
u_cm, _ = UnidadedeMedida.objects.get_or_create(nome="cm")
print("  ✓ PSI, cm\n")

# 2. Marcas e modelos
print("🏭 Criando marcas e modelos...")
m1, _ = Marca.objects.get_or_create(nome="Case IH")
m2, _ = Marca.objects.get_or_create(nome="John Deere")
m3, _ = Marca.objects.get_or_create(nome="New Holland")

mod1, _ = Modelo.objects.get_or_create(nome="TC5000", marca=m1)
mod2, _ = Modelo.objects.get_or_create(nome="S780", marca=m2)
mod3, _ = Modelo.objects.get_or_create(nome="CR9090", marca=m3)
print(f"  ✓ {m1.nome} {mod1.nome}")
print(f"  ✓ {m2.nome} {mod2.nome}")
print(f"  ✓ {m3.nome} {mod3.nome}\n")

# 3. Operários
print("👷 Criando operários...")
op1, _ = Operario.objects.get_or_create(nome="João Silva", defaults={"tempo_de_servico": 5, "no_banco": False})
op2, _ = Operario.objects.get_or_create(nome="Maria Santos", defaults={"tempo_de_servico": 3, "no_banco": False})
op3, _ = Operario.objects.get_or_create(nome="Pedro Costa", defaults={"tempo_de_servico": 7, "no_banco": True})
op4, _ = Operario.objects.get_or_create(nome="Ana Oliveira", defaults={"tempo_de_servico": 4, "no_banco": False})
op5, _ = Operario.objects.get_or_create(nome="Carlos Mendes", defaults={"tempo_de_servico": 6, "no_banco": False})
op6, _ = Operario.objects.get_or_create(nome="Juliana Alves", defaults={"tempo_de_servico": 2, "no_banco": False})
op7, _ = Operario.objects.get_or_create(nome="Roberto Souza", defaults={"tempo_de_servico": 8, "no_banco": True})
op8, _ = Operario.objects.get_or_create(nome="Fernanda Lima", defaults={"tempo_de_servico": 3, "no_banco": False})
op9, _ = Operario.objects.get_or_create(nome="Lucas Martins", defaults={"tempo_de_servico": 5, "no_banco": False})

for op in [op1, op2, op3, op4, op5, op6, op7, op8, op9]:
    print(f"  ✓ {op.nome} - {op.tempo_de_servico} anos")
print()

# 4. Colheitadeiras
print("🚜 Criando colheitadeiras...")

maquinas = [
    {"maquina_id": "COLH-01", "modelo": mod1, "operario": op1, "em_op": True, "em_mov": True, "tempo": 120.5, "vel": 12.5, "comb": 75.0},
    {"maquina_id": "COLH-02", "modelo": mod2, "operario": op2, "em_op": True, "em_mov": False, "tempo": 85.0, "vel": 0.0, "comb": 45.0},
    {"maquina_id": "COLH-03", "modelo": mod3, "operario": op3, "em_op": False, "em_mov": False, "tempo": 200.0, "vel": 0.0, "comb": 20.0},
    {"maquina_id": "COLH-04", "modelo": mod1, "operario": op4, "em_op": True, "em_mov": True, "tempo": 95.0, "vel": 10.0, "comb": 60.0},
    {"maquina_id": "COLH-05", "modelo": mod2, "operario": op5, "em_op": True, "em_mov": True, "tempo": 150.0, "vel": 14.0, "comb": 80.0},
    {"maquina_id": "COLH-06", "modelo": mod3, "operario": op6, "em_op": True, "em_mov": False, "tempo": 110.0, "vel": 0.0, "comb": 35.0},
    {"maquina_id": "COLH-07", "modelo": mod1, "operario": op7, "em_op": False, "em_mov": False, "tempo": 250.0, "vel": 0.0, "comb": 15.0},
    {"maquina_id": "COLH-08", "modelo": mod2, "operario": op8, "em_op": True, "em_mov": True, "tempo": 75.0, "vel": 11.5, "comb": 55.0},
    {"maquina_id": "COLH-09", "modelo": mod3, "operario": op9, "em_op": True, "em_mov": False, "tempo": 130.0, "vel": 0.0, "comb": 40.0},
]

for m in maquinas:
    comb = Combustivel.objects.create(porcentagem=m["comb"], tipo="Diesel")
    pneus = PressaoPneus.objects.create(pressao=32.0, unidade_de_medida=u_psi)
    altura = AlturadoCorte.objects.create(altura=15.0, unidade_de_medida=u_cm)
    pressao = PressaodoCorte.objects.create(pressao=120.0, unidade_de_medida=u_psi)
    temp_umi = TempUmi_Ambiente.objects.create(temperatura=28.0, umidade=65.0)
    temp_maq = TemperaturaMaquina.objects.create(temperatura=85.0, maquina=m["modelo"])
    status = StatusdeOperacao.objects.create(em_operacao=m["em_op"], tempo_de_operacao=m["tempo"])
    movimento = EstadodeMovimento.objects.create(em_movimento=m["em_mov"], velocidade=m["vel"])
    
    c = Colheitadeira.objects.create(
        maquina_id=m["maquina_id"],
        modelo=m["modelo"],
        combustivel=comb,
        pressao_pneus=pneus,
        altura_do_corte=altura,
        pressao_do_corte=pressao,
        temp_umi_ambiente=temp_umi,
        temperatura_maquina=temp_maq,
        operario=m["operario"],
        status_de_operacao=status,
        estado_de_movimento=movimento
    )
    print(f"  ✓ {c.maquina_id} - {c.modelo.marca.nome} {c.modelo.nome} - Operador: {c.operario.nome}")

print(f"\n✅ Banco populado com sucesso!")
print(f"   • {Colheitadeira.objects.count()} colheitadeiras")
print(f"   • {Operario.objects.count()} operários")
print(f"   • {Modelo.objects.count()} modelos")
