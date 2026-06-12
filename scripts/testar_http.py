#!/usr/bin/env python
import requests
import json
import time
import subprocess
import sys
import os

def iniciar_servidor():
    """Inicia o servidor Django em background"""
    print("Iniciando servidor Django...")
    return subprocess.Popen([
        sys.executable, "manage.py", "runserver", "8000"
    ], cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def testar_endpoint_http():
    """Testa o endpoint via HTTP"""
    base_url = "http://127.0.0.1:8000"
    
    # Aguardar servidor iniciar
    print("Aguardando servidor inicializar...")
    time.sleep(3)
    
    # Testar endpoint de prescrições
    maquinas = ["CASE-TC5000-01", "JOHN-DEERE-02", "NEW-HOLLAND-03"]
    
    for maquina_id in maquinas:
        print(f"\n--- Testando {maquina_id} via HTTP ---")
        
        try:
            response = requests.get(f"{base_url}/api/prescricoes/", 
                                  params={"maquina_id": maquina_id},
                                  timeout=10)
            
            print(f"Status HTTP: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Status: {data.get('status')}")
                print(f"Severidade: {data.get('severidade')}")
                print(f"Confiança: {data.get('confianca')}")
                print(f"Ação: {data.get('acao_recomendada')}")
                print(f"Prescrição: {data.get('prescricao', '')[:100]}...")
            else:
                print(f"Erro HTTP: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão: {e}")
    
    # Testar sem maquina_id
    print(f"\n--- Testando sem maquina_id ---")
    try:
        response = requests.get(f"{base_url}/api/prescricoes/", timeout=10)
        print(f"Status HTTP: {response.status_code}")
        if response.status_code != 200:
            data = response.json()
            print(f"Erro esperado: {data}")
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão: {e}")

if __name__ == "__main__":
    servidor = None
    try:
        servidor = iniciar_servidor()
        testar_endpoint_http()
    finally:
        if servidor:
            print("\nFinalizando servidor...")
            servidor.terminate()
            servidor.wait()