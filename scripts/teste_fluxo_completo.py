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

import os
import sys
import time
import uuid
import requests

API_HOST = os.environ.get("FIELDNODE_API_HOST", "http://127.0.0.1:8000")
API_BASE = os.environ.get("FIELDNODE_API_URL", f"{API_HOST}/api")
FRONTEND_URL = os.environ.get("FIELDNODE_FRONTEND_URL", "http://127.0.0.1:3000")
API_KEY = os.environ.get("FIELDNODE_API_KEY", "fieldnode-demo-2024")
TIMEOUT = 5

def print_status(msg, status="INFO"):
    symbols = {"OK": "✓", "ERRO": "✗", "INFO": "→"}
    colors = {"OK": "\033[92m", "ERRO": "\033[91m", "INFO": "\033[94m"}
    reset = "\033[0m"
    print(f"{colors.get(status, '')}{symbols.get(status, '•')} {msg}{reset}")

def testar_api_health():
    """Testa se a API está respondendo"""
    try:
        health_url = API_BASE
        if health_url.endswith("/api"):
            health_url = f"{health_url[:-4]}/api/health/"
        else:
            health_url = f"{health_url}/health/"

        resp = requests.get(health_url, timeout=TIMEOUT)
        if resp.status_code == 200:
            print_status("API está online", "OK")
            return True
        print_status(f"API retornou status {resp.status_code}", "ERRO")
        return False
    except requests.exceptions.ConnectionError:
        print_status("API não está rodando. Execute: python manage.py runserver", "ERRO")
        return False
    except Exception as e:
        print_status(f"Erro ao conectar na API: {e}", "ERRO")
        return False

def testar_endpoint(nome, url, metodo="GET", headers=None, json=None):
    """Testa um endpoint específico"""
    try:
        if metodo == "GET":
            resp = requests.get(f"{API_BASE}{url}", timeout=TIMEOUT, headers=headers)
        else:
            resp = requests.post(
                f"{API_BASE}{url}", timeout=TIMEOUT, headers=headers, json=json
            )

        if resp.status_code in [200, 201]:
            print_status(f"{nome}: OK", "OK")
            return True
        else:
            print_status(f"{nome}: Status {resp.status_code} - {resp.text}", "ERRO")
            return False
    except Exception as e:
        print_status(f"{nome}: {e}", "ERRO")
        return False


def testar_frontend_route(nome, path):
    """Testa se uma rota do frontend está acessível"""
    try:
        resp = requests.get(f"{FRONTEND_URL}{path}", timeout=TIMEOUT)
        if resp.status_code == 200:
            print_status(f"{nome}: OK", "OK")
            return True
        print_status(f"{nome}: Status {resp.status_code}", "ERRO")
        return False
    except Exception as e:
        print_status(f"{nome}: {e}", "ERRO")
        return False


def testar_dashboard():
    """Verifica se o dashboard está acessível"""
    try:
        resp = requests.get(f"{FRONTEND_URL}/dashboard", timeout=TIMEOUT)
        if resp.status_code == 200:
            print_status("Dashboard Next.js está acessível", "OK")
            return True
        print_status(f"Dashboard retornou status {resp.status_code}", "ERRO")
        return False
    except Exception as e:
        print_status(f"Erro ao acessar dashboard: {e}", "ERRO")
        return False


def testar_ingestao_telemetria():
    payload = {
        "id": str(uuid.uuid4()),
        "maquina_id": "COLH-01",
        "temperatura": 78.5,
        "vibracao": 0.42,
        "rpm": 1850,
        "timestamp": "2026-06-11T12:00:00Z",
    }
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
    }
    return testar_endpoint(
        "Ingestão de telemetria",
        "/telemetria/",
        metodo="POST",
        headers=headers,
        json=payload,
    )


def testar_prescricao():
    return testar_endpoint("Prescrição", "/prescricoes/?maquina_id=COLH-01")


def testar_relatorio():
    return testar_endpoint(
        "Relatório", "/relatorio/?maquina_id=COLH-01&periodo=7&formato=json"
    )


def main():
    print("\n" + "=" * 60)
    print("FIELDNODE — TESTE DE FLUXO COMPLETO")
    print("=" * 60 + "\n")

    resultados = []

    # 1. API Health
    print_status("Testando conectividade da API...", "INFO")
    resultados.append(testar_api_health())
    time.sleep(0.5)

    if not resultados[-1]:
        print("\n⚠ API não está rodando. Inicie com: python manage.py runserver")
        sys.exit(1)

    # 2. Endpoints críticos
    print("\n" + "-" * 60)
    print_status("Testando endpoints críticos...", "INFO")
    print("-" * 60)

    endpoints = [
        ("Métricas", "/metricas/"),
        ("Últimas leituras", "/leituras/ultimas/"),
        ("Status MQTT", "/status-mqtt/"),
        ("Anomalias", "/anomalias/"),
        ("Manutenção", "/manutencao/"),
        ("Swagger", "/swagger/"),
    ]

    for nome, url in endpoints:
        resultados.append(testar_endpoint(nome, url))
        time.sleep(0.3)

    # 3. Fluxo de prescrição e relatório
    print("\n" + "-" * 60)
    print_status("Validando fluxo de IA e relatórios...", "INFO")
    print("-" * 60)
    resultados.append(testar_ingestao_telemetria())
    time.sleep(0.3)
    resultados.append(testar_prescricao())
    time.sleep(0.3)
    resultados.append(testar_relatorio())

    # 4. Frontend
    print("\n" + "-"*60)
    print_status("Verificando frontend...", "INFO")
    print("-"*60)
    resultados.append(testar_frontend_route("Dashboard", "/dashboard"))
    resultados.append(testar_frontend_route("Relatórios", "/relatorios"))

    # Resultado final
    print("\n" + "="*60)
    total = len(resultados)
    passou = sum(resultados)
    falhou = total - passou

    if falhou == 0:
        print_status(f"TODOS OS TESTES PASSARAM ({passou}/{total})", "OK")
        print("\n✓ Sistema pronto para apresentação!")
        print(f"\nAcesse: {FRONTEND_URL}/dashboard")
    else:
        print_status(f"ALGUNS OS TESTES FALHARAM ({falhou}/{total})", "ERRO")
        print("\n⚠ Corrija os erros antes da apresentação.")
        sys.exit(1)

    print("="*60 + "\n")

if __name__ == "__main__":
    main()
