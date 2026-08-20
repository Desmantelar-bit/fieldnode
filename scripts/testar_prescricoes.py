#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

def testar_analises():
    print("Testando análise determinística de telemetria")
    
    # Testar com máquina existente
    maquinas = ["CASE-TC5000-01", "JOHN-DEERE-02", "NEW-HOLLAND-03"]
    
    for maquina_id in maquinas:
        print(f"\n--- Testando {maquina_id} ---")
        
        from api_tcc.ia.pipeline import analisar_maquina
        resultado = analisar_maquina(maquina_id)

        print(f"Status: {resultado.status}")
        print(f"Motivos: {resultado.motivos}")
        print(f"Métricas: {resultado.metricas}")
        print(f"Recomendação: {resultado.recomendacao}")
    
    # Testar com máquina inexistente
    print(f"\n--- Testando máquina inexistente ---")
    resultado = analisar_maquina("INEXISTENTE")
    print(f"Status: {resultado.status}")
    print(f"Recomendação: {resultado.recomendacao}")

if __name__ == "__main__":
    testar_analises()
