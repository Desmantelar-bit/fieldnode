#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para popular dados de teste via API HTTP
Não depende de MQTT - envia direto para /api/telemetria/
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import uuid
from datetime import datetime, timedelta, timezone
import random

API_URL = 'http://127.0.0.1:8000/api/telemetria/'
API_KEY = 'fieldnode-prod-2024-secure-key'

MAQUINAS = ['COLH-01', 'COLH-02', 'COLH-03']

def gerar_leitura(maquina_id, timestamp):
    """Gera uma leitura sintética"""
    base_temp = random.uniform(65, 90)
    base_vib = random.uniform(0.1, 0.7)
    base_rpm = random.randint(1400, 2000)
    
    return {
        'id': str(uuid.uuid4()),
        'maquina_id': maquina_id,
        'temperatura': round(base_temp, 1),
        'vibracao': round(base_vib, 2),
        'rpm': base_rpm,
        'timestamp': timestamp.isoformat()
    }

def popular_dados():
    print('=' * 50)
    print('  POPULANDO DADOS DE TESTE')
    print('=' * 50)
    print(f'API: {API_URL}')
    print(f'Máquinas: {", ".join(MAQUINAS)}')
    print()
    
    agora = datetime.now(timezone.utc)
    total_enviadas = 0
    
    for maquina in MAQUINAS:
        print(f'Enviando leituras para {maquina}...')
        
        # Envia 10 leituras espaçadas de 5 minutos
        for i in range(10):
            timestamp = agora - timedelta(minutes=5 * (9 - i))
            leitura = gerar_leitura(maquina, timestamp)
            
            try:
                resp = requests.post(
                    API_URL,
                    json=leitura,
                    headers={'X-API-Key': API_KEY},
                    timeout=5
                )
                
                if resp.status_code in [200, 201]:
                    total_enviadas += 1
                    print(f'  OK {leitura["temperatura"]}C | {leitura["vibracao"]}g | {leitura["rpm"]} RPM')
                else:
                    print(f'  ERRO {resp.status_code}: {resp.text[:100]}')
                    
            except Exception as e:
                print(f'  FALHA na requisicao: {e}')
                break
        
        print()
    
    print('=' * 50)
    print(f'Total de leituras enviadas: {total_enviadas}')
    print('=' * 50)
    print()
    print('Acesse: http://127.0.0.1:8000/frontend/dashboard.html')

if __name__ == '__main__':
    popular_dados()
