"""
Script de teste rápido para verificar o endpoint de operários
"""
import requests

API_BASE = 'http://127.0.0.1:8000'

def testar_operarios():
    print("🔍 Testando endpoint /api/operario/")
    print("-" * 50)
    
    try:
        response = requests.get(f'{API_BASE}/api/operario/')
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dados recebidos: {len(data)} operários")
            
            if len(data) > 0:
                print("\n📋 Primeiro operário:")
                print(f"   - ID: {data[0].get('id')}")
                print(f"   - Nome: {data[0].get('nome')}")
                print(f"   - Tempo de Serviço: {data[0].get('tempo_de_servico')} anos")
                print(f"   - No Banco: {data[0].get('no_banco')}")
            else:
                print("⚠️  Nenhum operário cadastrado no banco")
                print("\n💡 Para cadastrar um operário, use:")
                print("   python manage.py shell")
                print("   >>> from api_tcc.models import Operario")
                print("   >>> Operario.objects.create(nome='João Silva', tempo_de_servico=5, no_banco=True)")
        else:
            print(f"❌ Erro: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar à API")
        print("   Certifique-se de que o servidor Django está rodando:")
        print("   python manage.py runserver")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == '__main__':
    testar_operarios()
