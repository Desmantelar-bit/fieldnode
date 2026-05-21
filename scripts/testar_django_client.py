#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.test import Client
import json

def testar_endpoint_django():
    """Testa o endpoint usando Django Test Client"""
    client = Client()
    
    print("=== Testando endpoint /api/prescricoes/ ===")
    
    # Testar com máquina existente
    maquinas = ["CASE-TC5000-01", "JOHN-DEERE-02", "NEW-HOLLAND-03"]
    
    for maquina_id in maquinas:
        print(f"\n--- Testando {maquina_id} ---")
        
        response = client.get('/api/prescricoes/', {'maquina_id': maquina_id})
        
        print(f"Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Severidade: {data.get('severidade')}")
            print(f"Confiança: {data.get('confianca')}")
            print(f"Ação: {data.get('acao_recomendada')}")
            print(f"Prescrição: {data.get('prescricao', '')[:100]}...")
            
            # Verificar se foi persistido no banco
            from api_tcc.models import Prescricao
            ultima_prescricao = Prescricao.objects.filter(maquina_id=maquina_id).first()
            if ultima_prescricao:
                print(f"✓ Prescrição persistida no banco (ID: {ultima_prescricao.id})")
            else:
                print("✗ Prescrição não foi persistida no banco")
        else:
            print(f"Erro HTTP: {response.content.decode()}")
    
    # Testar sem maquina_id
    print(f"\n--- Testando sem maquina_id ---")
    response = client.get('/api/prescricoes/')
    print(f"Status HTTP: {response.status_code}")
    if response.status_code != 200:
        data = response.json()
        print(f"Erro esperado: {data}")
    
    # Testar com máquina inexistente
    print(f"\n--- Testando máquina inexistente ---")
    response = client.get('/api/prescricoes/', {'maquina_id': 'INEXISTENTE'})
    print(f"Status HTTP: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data.get('status')}")
        print(f"Detalhe: {data.get('detalhe', 'N/A')}")

if __name__ == "__main__":
    testar_endpoint_django()