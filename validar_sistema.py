"""
Validação Final — FieldNode
Testa todos os componentes críticos antes da apresentação
"""
import requests
import time
import sys

API_BASE = "http://127.0.0.1:8000"
TIMEOUT = 5

def test_endpoint(name, url, expected_status=200):
    """Testa um endpoint e retorna True se passou"""
    try:
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code == expected_status:
            print(f"✅ {name}: OK ({response.status_code})")
            return True
        else:
            print(f"❌ {name}: FALHOU (esperado {expected_status}, recebeu {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: ERRO DE CONEXÃO ({e})")
        return False

def test_ia_performance(maquina_id):
    """Testa se a IA responde em tempo aceitável"""
    try:
        start = time.time()
        response = requests.get(f"{API_BASE}/api/manutencao/?maquina_id={maquina_id}", timeout=TIMEOUT)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            if elapsed < 3.0:
                print(f"✅ IA Manutenção ({maquina_id}): OK ({elapsed:.2f}s)")
                return True
            else:
                print(f"⚠️  IA Manutenção ({maquina_id}): LENTO ({elapsed:.2f}s)")
                return True
        else:
            print(f"❌ IA Manutenção ({maquina_id}): FALHOU ({response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ IA Manutenção ({maquina_id}): ERRO ({e})")
        return False

def main():
    print("=" * 60)
    print("VALIDAÇÃO FINAL — FIELDNODE")
    print("=" * 60)
    print()
    
    resultados = []
    
    # 1. Endpoints básicos
    print("📡 Testando endpoints básicos...")
    resultados.append(test_endpoint("Dashboard", f"{API_BASE}/"))
    resultados.append(test_endpoint("API Colheitadeiras", f"{API_BASE}/Colheitadeira/"))
    resultados.append(test_endpoint("API Leituras", f"{API_BASE}/api/leituras/ultimas/"))
    resultados.append(test_endpoint("API Métricas", f"{API_BASE}/api/metricas/"))
    resultados.append(test_endpoint("Swagger", f"{API_BASE}/swagger/"))
    print()
    
    # 2. IA - Anomalias
    print("🤖 Testando IA - Detecção de Anomalias...")
    resultados.append(test_endpoint("Anomalias (todas)", f"{API_BASE}/api/anomalias/"))
    print()
    
    # 3. IA - Manutenção Preditiva (performance crítica)
    print("🔧 Testando IA - Manutenção Preditiva (performance)...")
    
    # Buscar máquinas disponíveis
    try:
        response = requests.get(f"{API_BASE}/Colheitadeira/", timeout=TIMEOUT)
        if response.status_code == 200:
            maquinas = response.json()
            if maquinas:
                # Testar com até 3 máquinas
                for maquina in maquinas[:3]:
                    maquina_id = maquina.get('Modelo', {}).get('Nome', 'desconhecida')
                    resultados.append(test_ia_performance(maquina_id))
            else:
                print("⚠️  Nenhuma máquina cadastrada no banco")
        else:
            print(f"❌ Não foi possível buscar máquinas ({response.status_code})")
    except Exception as e:
        print(f"❌ Erro ao buscar máquinas: {e}")
    
    print()
    
    # 4. Resumo
    print("=" * 60)
    total = len(resultados)
    passou = sum(resultados)
    falhou = total - passou
    
    print(f"RESULTADO: {passou}/{total} testes passaram")
    
    if falhou == 0:
        print("✅ SISTEMA PRONTO PARA APRESENTAÇÃO")
        print()
        print("Próximos passos:")
        print("1. Rodar: python esp_simulator_multi.py")
        print("2. Abrir: http://127.0.0.1:8000/")
        print("3. Verificar: Dashboard atualizando em tempo real")
        return 0
    else:
        print(f"❌ {falhou} TESTE(S) FALHARAM")
        print()
        print("Ações necessárias:")
        print("1. Verificar se o servidor Django está rodando")
        print("2. Verificar se há dados no banco (rodar simular_dados.py)")
        print("3. Verificar logs em logs/fieldnode_errors.log")
        return 1

if __name__ == "__main__":
    sys.exit(main())
