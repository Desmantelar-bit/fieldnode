"""
Script de teste do fluxo completo do FieldNode.

Valida:
1. Banco de dados migrado
2. API respondendo
3. Endpoints críticos funcionando
4. Dashboard acessível

Uso:
    python scripts/teste_fluxo_completo.py
"""

import sys
import time
import requests
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 5

def print_status(msg, status="INFO"):
    symbols = {"OK": "✓", "ERRO": "✗", "INFO": "→"}
    colors = {"OK": "\033[92m", "ERRO": "\033[91m", "INFO": "\033[94m"}
    reset = "\033[0m"
    print(f"{colors.get(status, '')}{symbols.get(status, '•')} {msg}{reset}")

def testar_api_health():
    """Testa se a API está respondendo"""
    try:
        resp = requests.get(f"{BASE_URL}/api/health/", timeout=TIMEOUT)
        if resp.status_code == 200:
            print_status("API está online", "OK")
            return True
        else:
            print_status(f"API retornou status {resp.status_code}", "ERRO")
            return False
    except requests.exceptions.ConnectionError:
        print_status("API não está rodando. Execute: python manage.py runserver", "ERRO")
        return False
    except Exception as e:
        print_status(f"Erro ao conectar na API: {e}", "ERRO")
        return False

def testar_endpoint(nome, url, metodo="GET"):
    """Testa um endpoint específico"""
    try:
        if metodo == "GET":
            resp = requests.get(f"{BASE_URL}{url}", timeout=TIMEOUT)
        else:
            resp = requests.post(f"{BASE_URL}{url}", timeout=TIMEOUT)
        
        if resp.status_code in [200, 201]:
            print_status(f"{nome}: OK", "OK")
            return True
        else:
            print_status(f"{nome}: Status {resp.status_code}", "ERRO")
            return False
    except Exception as e:
        print_status(f"{nome}: {e}", "ERRO")
        return False

def testar_dashboard():
    """Verifica se o dashboard está acessível"""
    dashboard_path = Path("frontend/dashboard.html")
    if dashboard_path.exists():
        print_status("Dashboard HTML encontrado", "OK")
        return True
    else:
        print_status("Dashboard HTML não encontrado", "ERRO")
        return False

def main():
    print("\n" + "="*60)
    print("FIELDNODE — TESTE DE FLUXO COMPLETO")
    print("="*60 + "\n")
    
    resultados = []
    
    # 1. API Health
    print_status("Testando conectividade da API...", "INFO")
    resultados.append(testar_api_health())
    time.sleep(0.5)
    
    if not resultados[-1]:
        print("\n⚠ API não está rodando. Inicie com: python manage.py runserver")
        sys.exit(1)
    
    # 2. Endpoints críticos
    print("\n" + "-"*60)
    print_status("Testando endpoints críticos...", "INFO")
    print("-"*60)
    
    endpoints = [
        ("Métricas", "/api/metricas/"),
        ("Últimas leituras", "/api/leituras/ultimas/"),
        ("Status MQTT", "/api/status-mqtt/"),
        ("Anomalias", "/api/anomalias/"),
        ("Manutenção", "/api/manutencao/"),
        ("Swagger", "/swagger/"),
    ]
    
    for nome, url in endpoints:
        resultados.append(testar_endpoint(nome, url))
        time.sleep(0.3)
    
    # 3. Dashboard
    print("\n" + "-"*60)
    print_status("Verificando frontend...", "INFO")
    print("-"*60)
    resultados.append(testar_dashboard())
    
    # Resultado final
    print("\n" + "="*60)
    total = len(resultados)
    passou = sum(resultados)
    falhou = total - passou
    
    if falhou == 0:
        print_status(f"TODOS OS TESTES PASSARAM ({passou}/{total})", "OK")
        print("\n✓ Sistema pronto para apresentação!")
        print(f"\nAcesse: {BASE_URL}/frontend/dashboard.html")
    else:
        print_status(f"ALGUNS TESTES FALHARAM ({falhou}/{total})", "ERRO")
        print("\n⚠ Corrija os erros antes da apresentação.")
        sys.exit(1)
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
