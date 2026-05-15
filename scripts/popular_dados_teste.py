"""
Script para popular dados de teste no banco de dados
Execute: python scripts/popular_dados_teste.py
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from api_tcc.models import (
    Operario, Marca, Modelo, UnidadedeMedida, 
    Combustivel, PressaoPneus, AlturadoCorte, PressaodoCorte,
    TempUmi_Ambiente, TemperaturaMaquina, StatusdeOperacao, EstadodeMovimento
)

def popular_dados():
    print("🌱 Populando banco de dados com dados de teste...")
    print("-" * 60)
    
    # 1. Operários
    print("\n👷 Criando operários...")
    operarios_data = [
        {'nome': 'João Silva', 'tempo_de_servico': 5, 'no_banco': True},
        {'nome': 'Maria Santos', 'tempo_de_servico': 3, 'no_banco': False},
        {'nome': 'Pedro Oliveira', 'tempo_de_servico': 8, 'no_banco': True},
        {'nome': 'Ana Costa', 'tempo_de_servico': 2, 'no_banco': True},
        {'nome': 'Carlos Souza', 'tempo_de_servico': 10, 'no_banco': False},
    ]
    
    for data in operarios_data:
        op, created = Operario.objects.get_or_create(
            nome=data['nome'],
            defaults=data
        )
        if created:
            print(f"   ✅ {op.nome} - {op.tempo_de_servico} anos")
        else:
            print(f"   ⏭️  {op.nome} já existe")
    
    # 2. Marcas
    print("\n🏭 Criando marcas...")
    marcas_data = ['John Deere', 'Case IH', 'New Holland', 'Massey Ferguson', 'Valtra']
    
    for nome in marcas_data:
        marca, created = Marca.objects.get_or_create(nome=nome)
        if created:
            print(f"   ✅ {marca.nome}")
        else:
            print(f"   ⏭️  {marca.nome} já existe")
    
    # 3. Modelos
    print("\n🚜 Criando modelos...")
    modelos_data = [
        {'nome': 'S790', 'marca': 'John Deere'},
        {'nome': 'Axial-Flow 9250', 'marca': 'Case IH'},
        {'nome': 'CR10.90', 'marca': 'New Holland'},
        {'nome': 'Ideal 9T', 'marca': 'Massey Ferguson'},
        {'nome': 'BC8800', 'marca': 'Valtra'},
    ]
    
    for data in modelos_data:
        marca = Marca.objects.get(nome=data['marca'])
        modelo, created = Modelo.objects.get_or_create(
            nome=data['nome'],
            defaults={'marca': marca}
        )
        if created:
            print(f"   ✅ {modelo.nome} ({marca.nome})")
        else:
            print(f"   ⏭️  {modelo.nome} já existe")
    
    # 4. Unidades de Medida
    print("\n📏 Criando unidades de medida...")
    unidades = ['PSI', 'Bar', 'cm', 'm', 'kg', 'L']
    
    for nome in unidades:
        unidade, created = UnidadedeMedida.objects.get_or_create(nome=nome)
        if created:
            print(f"   ✅ {unidade.nome}")
        else:
            print(f"   ⏭️  {unidade.nome} já existe")
    
    # 5. Combustíveis
    print("\n⛽ Criando combustíveis...")
    combustiveis_data = [
        {'tipo': 'Diesel S10', 'porcentagem': 100.0},
        {'tipo': 'Biodiesel B20', 'porcentagem': 80.0},
        {'tipo': 'Diesel Comum', 'porcentagem': 100.0},
    ]
    
    for data in combustiveis_data:
        comb, created = Combustivel.objects.get_or_create(
            tipo=data['tipo'],
            defaults=data
        )
        if created:
            print(f"   ✅ {comb.tipo} - {comb.porcentagem}%")
        else:
            print(f"   ⏭️  {comb.tipo} já existe")
    
    print("\n" + "=" * 60)
    print("✅ Dados de teste criados com sucesso!")
    print("=" * 60)
    
    # Resumo
    print(f"\n📊 Resumo:")
    print(f"   - Operários: {Operario.objects.count()}")
    print(f"   - Marcas: {Marca.objects.count()}")
    print(f"   - Modelos: {Modelo.objects.count()}")
    print(f"   - Unidades de Medida: {UnidadedeMedida.objects.count()}")
    print(f"   - Combustíveis: {Combustivel.objects.count()}")
    
    print("\n🌐 Acesse agora:")
    print("   - Operários: http://127.0.0.1:8000/frontend/operarios.html")
    print("   - Cadastro: http://127.0.0.1:8000/frontend/cadastro.html")
    print("   - API Operários: http://127.0.0.1:8000/api/operario/")
    print("   - API Marcas: http://127.0.0.1:8000/api/marca/")
    print("   - Swagger: http://127.0.0.1:8000/swagger/")

if __name__ == '__main__':
    try:
        popular_dados()
    except Exception as e:
        print(f"\n❌ Erro ao popular dados: {e}")
        import traceback
        traceback.print_exc()
