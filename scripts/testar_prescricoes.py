#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

def testar_prescricoes():
    print("Testando endpoint /api/prescricoes/")
    
    # Testar com máquina existente
    maquinas = ["CASE-TC5000-01", "JOHN-DEERE-02", "NEW-HOLLAND-03"]
    
    for maquina_id in maquinas:
        print(f"\n--- Testando {maquina_id} ---")
        
        # Importar e testar diretamente a função
        from api_tcc.ia.prescricoes import gerar_prescricao
        resultado = gerar_prescricao(maquina_id, limite=10)
        
        print(f"Status: {resultado.get('status')}")
        if resultado.get('status') == 'ok':
            print(f"Severidade: {resultado.get('severidade')}")
            print(f"Confiança: {resultado.get('confianca')}")
            print(f"Ação: {resultado.get('acao_recomendada')}")
            print(f"Prescrição: {resultado.get('prescricao')[:100]}...")
        else:
            print(f"Erro: {resultado}")
    
    # Testar com máquina inexistente
    print(f"\n--- Testando máquina inexistente ---")
    resultado = gerar_prescricao("INEXISTENTE", limite=10)
    print(f"Status: {resultado.get('status')}")
    print(f"Detalhe: {resultado.get('detalhe', 'N/A')}")

if __name__ == "__main__":
    testar_prescricoes()