#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script Django para popular dados de teste direto no banco
Bypass da validação de máquina cadastrada
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from api_tcc.models import LeituraTelemetria
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
import uuid
import random

MAQUINAS = ['COLH-01', 'COLH-02', 'COLH-03', 'TRAT-01', 'TRAT-02', 'PULV-01']

def gerar_leitura(maquina_id, timestamp):
    """Gera uma leitura sintética"""
    base_temp = random.uniform(65, 90)
    base_vib = random.uniform(0.1, 0.7)
    base_rpm = random.randint(1400, 2000)
    
    return LeituraTelemetria(
        id=uuid.uuid4(),
        maquina_id=maquina_id,
        temperatura=round(base_temp, 1),
        vibracao=round(base_vib, 2),
        rpm=base_rpm,
        timestamp=make_aware(timestamp)
    )

def popular_dados():
    print('=' * 50)
    print('  POPULANDO DADOS DE TESTE (Django ORM)')
    print('=' * 50)
    print(f'Máquinas: {", ".join(MAQUINAS)}')
    print()
    
    agora = datetime.now()
    leituras = []
    
    for maquina in MAQUINAS:
        print(f'Gerando leituras para {maquina}...')
        
        # Gera 10 leituras espaçadas de 5 minutos
        for i in range(10):
            timestamp = agora - timedelta(minutes=5 * (9 - i))
            leitura = gerar_leitura(maquina, timestamp)
            leituras.append(leitura)
            print(f'  {leitura.temperatura}C | {leitura.vibracao}g | {leitura.rpm} RPM')
        
        print()
    
    # Bulk insert
    print('Salvando no banco...')
    LeituraTelemetria.objects.bulk_create(leituras)
    
    print('=' * 50)
    print(f'Total de leituras criadas: {len(leituras)}')
    print('=' * 50)
    print()
    print('Acesse: http://127.0.0.1:8000/frontend/dashboard.html')

if __name__ == '__main__':
    popular_dados()
