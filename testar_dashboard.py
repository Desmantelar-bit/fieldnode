#!/usr/bin/env python
"""
Teste Completo do Dashboard - FieldNode
========================================

Testa TODOS os endpoints que o dashboard usa.
"""

import urllib.request
import urllib.error
import json

def test_endpoint(nome, url):
    print(f"\n{'='*60}")
    print(f"Testando: {nome}")
    print(f"URL: {url}")
    print('='*60)
    
    try:
        response = urllib.request.urlopen(url, timeout=5)
        data = json.loads(response.read().decode('utf-8'))
        
        print(f"✅ Status: {response.status}")
        print(f"✅ Content-Type: {response.headers.get('Content-Type')}")
        
        if isinstance(data, list):
            print(f"✅ Retornou lista com {len(data)} item(s)")
            if len(data) > 0:
                print(f"\n📄 Primeiro item:")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
        elif isinstance(data, dict):
            print(f"✅ Retornou objeto com {len(data)} campo(s)")
            print(f"\n📄 Dados:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        
        return True
        
    except urllib.error.HTTPError as e:
        print(f"❌ Erro HTTP {e.code}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"📄 Resposta:")
            print(error_body)
        except:
            pass
        return False
        
    except urllib.error.URLError as e:
        print(f"❌ Erro de conexão: {e.reason}")
        print(f"💡 Verifique se o Django está rodando na porta 8000")
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  🔍 TESTE COMPLETO DO DASHBOARD")
    print("="*60)
    
    endpoints = [
        ("Colheitadeiras", "http://127.0.0.1:8000/Colheitadeira/"),
        ("Temperatura Máquina", "http://127.0.0.1:8000/Temperaturamaquina/"),
        ("Combustível", "http://127.0.0.1:8000/Combustivel/"),
        ("Ambiente", "http://127.0.0.1:8000/Tempumi_ambiente/"),
        ("Movimento", "http://127.0.0.1:8000/Estadodemovimento/"),
        ("Telemetria (todas)", "http://127.0.0.1:8000/api/telemetria/"),
        ("Últimas Leituras", "http://127.0.0.1:8000/api/leituras/ultimas/"),
        ("Manutenção (CASE-TC5000-01)", "http://127.0.0.1:8000/api/manutencao/?maquina_id=CASE-TC5000-01"),
        ("Anomalias (CASE-TC5000-01)", "http://127.0.0.1:8000/api/anomalias/?maquina_id=CASE-TC5000-01"),
    ]
    
    resultados = []
    for nome, url in endpoints:
        sucesso = test_endpoint(nome, url)
        resultados.append((nome, sucesso))
    
    # Resumo
    print("\n" + "="*60)
    print("  📊 RESUMO DOS TESTES")
    print("="*60 + "\n")
    
    total = len(resultados)
    sucesso = sum(1 for _, ok in resultados if ok)
    falha = total - sucesso
    
    for nome, ok in resultados:
        status = "✅" if ok else "❌"
        print(f"{status} {nome}")
    
    print(f"\n📈 Total: {sucesso}/{total} endpoints funcionando")
    
    if falha > 0:
        print(f"\n⚠️  {falha} endpoint(s) com problema!")
        print("\n💡 Soluções:")
        print("   1. Verifique se o Django está rodando: python manage.py runserver")
        print("   2. Verifique se há dados no banco: python simular_dados.py")
        print("   3. Verifique os logs do Django no terminal")
    else:
        print("\n✅ Todos os endpoints funcionando!")
        print("\n🚀 O dashboard deve funcionar perfeitamente.")
        print("   Abra: http://127.0.0.1:5500/index.html")
        print("   Pressione Ctrl+F5 para forçar reload")

if __name__ == "__main__":
    main()
