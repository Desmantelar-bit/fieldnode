#!/usr/bin/env python
"""
Script para criar máquinas de teste no banco de dados
"""
import os
import sys
import django

# Configura Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from api_tcc.models import (
    Marca, Modelo, Operario, Colheitadeira,
    Combustivel, PressaoPneus, AlturadoCorte, PressaodoCorte,
    TempUmi_Ambiente, TemperaturaMaquina, StatusdeOperacao, EstadodeMovimento
)

def criar_maquinas():
    print("Criando marcas...")
    case, _ = Marca.objects.get_or_create(nome="Case IH")
    john_deere, _ = Marca.objects.get_or_create(nome="John Deere")
    new_holland, _ = Marca.objects.get_or_create(nome="New Holland")
    
    print("Criando modelos...")
    modelo_case, _ = Modelo.objects.get_or_create(nome="TC5000", marca=case)
    modelo_jd, _ = Modelo.objects.get_or_create(nome="S780", marca=john_deere)
    modelo_nh, _ = Modelo.objects.get_or_create(nome="CR9090", marca=new_holland)
    
    print("Criando operários...")
    op1, _ = Operario.objects.get_or_create(nome="João Silva", defaults={"tempo_de_servico": 5.0})
    op2, _ = Operario.objects.get_or_create(nome="Maria Santos", defaults={"tempo_de_servico": 3.0})
    op3, _ = Operario.objects.get_or_create(nome="Pedro Costa", defaults={"tempo_de_servico": 7.0})
    
    print("Criando dados auxiliares...")
    combustivel, _ = Combustivel.objects.get_or_create(nivel=75.0, capacidade_total=500.0)
    pressao_pneus, _ = PressaoPneus.objects.get_or_create(dianteiro_esquerdo=32.0, dianteiro_direito=32.0, traseiro_esquerdo=28.0, traseiro_direito=28.0)
    altura_corte, _ = AlturadoCorte.objects.get_or_create(altura=15.0)
    pressao_corte, _ = PressaodoCorte.objects.get_or_create(pressao=120.0)
    temp_umi, _ = TempUmi_Ambiente.objects.get_or_create(temperatura=28.0, umidade=65.0)
    temp_maq, _ = TemperaturaMaquina.objects.get_or_create(motor=85.0, oleo=75.0, transmissao=70.0)
    status_op, _ = StatusdeOperacao.objects.get_or_create(em_operacao=True, tempo_de_operacao=120.5)
    estado_mov, _ = EstadodeMovimento.objects.get_or_create(em_movimento=True, velocidade=12.5)
    
    print("Criando colheitadeiras...")
    
    # CASE-TC5000-01
    colh1, created = Colheitadeira.objects.get_or_create(
        modelo=modelo_case,
        defaults={
            'combustivel': combustivel,
            'pressao_pneus': pressao_pneus,
            'altura_do_corte': altura_corte,
            'pressao_do_corte': pressao_corte,
            'temp_umi_ambiente': temp_umi,
            'temperatura_maquina': temp_maq,
            'operario': op1,
            'status_de_operacao': status_op,
            'estado_de_movimento': estado_mov,
        }
    )
    print(f"  {'Criada' if created else 'Já existe'}: {colh1.modelo.marca.nome} {colh1.modelo.nome}")
    
    # JOHN-DEERE-02
    colh2, created = Colheitadeira.objects.get_or_create(
        modelo=modelo_jd,
        defaults={
            'combustivel': combustivel,
            'pressao_pneus': pressao_pneus,
            'altura_do_corte': altura_corte,
            'pressao_do_corte': pressao_corte,
            'temp_umi_ambiente': temp_umi,
            'temperatura_maquina': temp_maq,
            'operario': op2,
            'status_de_operacao': status_op,
            'estado_de_movimento': estado_mov,
        }
    )
    print(f"  {'Criada' if created else 'Já existe'}: {colh2.modelo.marca.nome} {colh2.modelo.nome}")
    
    # NEW-HOLLAND-03
    colh3, created = Colheitadeira.objects.get_or_create(
        modelo=modelo_nh,
        defaults={
            'combustivel': combustivel,
            'pressao_pneus': pressao_pneus,
            'altura_do_corte': altura_corte,
            'pressao_do_corte': pressao_corte,
            'temp_umi_ambiente': temp_umi,
            'temperatura_maquina': temp_maq,
            'operario': op3,
            'status_de_operacao': status_op,
            'estado_de_movimento': estado_mov,
        }
    )
    print(f"  {'Criada' if created else 'Já existe'}: {colh3.modelo.marca.nome} {colh3.modelo.nome}")
    
    total = Colheitadeira.objects.count()
    print(f"\n✓ Total de colheitadeiras no banco: {total}")

if __name__ == '__main__':
    criar_maquinas()
