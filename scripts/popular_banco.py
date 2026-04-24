"""
Script para popular o banco de dados com dados realistas de colheitadeiras.

Execução:
    python scripts/popular_banco.py

O script cria:
- 3 marcas de colheitadeiras (Case IH, John Deere, New Holland)
- 6 modelos diferentes
- 4 operários com experiências variadas
- 6 colheitadeiras completas com todos os dados de referência
- Dados de ambiente, pressão, temperatura, etc.

IDs das máquinas criadas:
- CASE-TC5000-01
- CASE-TC5000-02
- DEERE-S780-01
- DEERE-S780-02
- NH-CR9090-01
- NH-CR9090-02
"""

import os
import sys
import django

# Configura o Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from api_tcc.models import (
    UnidadedeMedida, Marca, Modelo, Combustivel, Operario,
    PressaoPneus, AlturadoCorte, PressaodoCorte, TempUmi_Ambiente,
    TemperaturaMaquina, StatusdeOperacao, EstadodeMovimento, Colheitadeira
)


def limpar_dados_existentes():
    """Remove todos os dados das tabelas para começar limpo."""
    print("🗑️  Limpando dados existentes...")
    
    # Ordem importa por causa das FKs
    Colheitadeira.objects.all().delete()
    TemperaturaMaquina.objects.all().delete()
    EstadodeMovimento.objects.all().delete()
    StatusdeOperacao.objects.all().delete()
    TempUmi_Ambiente.objects.all().delete()
    PressaodoCorte.objects.all().delete()
    AlturadoCorte.objects.all().delete()
    PressaoPneus.objects.all().delete()
    Operario.objects.all().delete()
    Combustivel.objects.all().delete()
    Modelo.objects.all().delete()
    Marca.objects.all().delete()
    UnidadedeMedida.objects.all().delete()
    
    print("✅ Dados limpos!\n")


def criar_unidades():
    """Cria unidades de medida padrão."""
    print("📏 Criando unidades de medida...")
    
    unidades = [
        'PSI',      # Pressão dos pneus
        'bar',      # Pressão hidráulica
        'cm',       # Altura de corte
        '°C',       # Temperatura
        '%',        # Umidade, combustível
        'km/h',     # Velocidade
        'RPM',      # Rotação
    ]
    
    objs = []
    for nome in unidades:
        obj = UnidadedeMedida.objects.create(Nome=nome)
        objs.append(obj)
        print(f"  ✓ {nome}")
    
    print(f"✅ {len(objs)} unidades criadas\n")
    return {u.Nome: u for u in objs}


def criar_marcas_e_modelos(unidades):
    """Cria marcas e modelos de colheitadeiras."""
    print("🏭 Criando marcas e modelos...")
    
    # Marcas
    case = Marca.objects.create(Nome='Case IH')
    deere = Marca.objects.create(Nome='John Deere')
    nh = Marca.objects.create(Nome='New Holland')
    print(f"  ✓ {case.Nome}")
    print(f"  ✓ {deere.Nome}")
    print(f"  ✓ {nh.Nome}")
    
    # Modelos
    modelos = [
        Modelo.objects.create(Nome='TC5000', Marca=case),
        Modelo.objects.create(Nome='Axial-Flow 9250', Marca=case),
        Modelo.objects.create(Nome='S780', Marca=deere),
        Modelo.objects.create(Nome='X9 1100', Marca=deere),
        Modelo.objects.create(Nome='CR9090', Marca=nh),
        Modelo.objects.create(Nome='CR10.90', Marca=nh),
    ]
    
    for m in modelos:
        print(f"  ✓ {m.Nome} ({m.Marca.Nome})")
    
    print(f"✅ {len(modelos)} modelos criados\n")
    return modelos


def criar_operarios():
    """Cria operários com experiências variadas."""
    print("👷 Criando operários...")
    
    operarios = [
        Operario.objects.create(Nome='João Silva', TempodeServico=8, Nobanco=True),
        Operario.objects.create(Nome='Maria Santos', TempodeServico=12, Nobanco=True),
        Operario.objects.create(Nome='Pedro Costa', TempodeServico=5, Nobanco=True),
        Operario.objects.create(Nome='Ana Oliveira', TempodeServico=15, Nobanco=True),
    ]
    
    for op in operarios:
        print(f"  ✓ {op.Nome} ({op.TempodeServico} anos)")
    
    print(f"✅ {len(operarios)} operários criados\n")
    return operarios


def criar_combustiveis():
    """Cria tipos de combustível."""
    print("⛽ Criando combustíveis...")
    
    combustiveis = [
        Combustivel.objects.create(Tipo='Diesel S10', Porcentagem=85.0),
        Combustivel.objects.create(Tipo='Diesel S10', Porcentagem=92.0),
        Combustivel.objects.create(Tipo='Diesel S10', Porcentagem=78.0),
        Combustivel.objects.create(Tipo='Diesel S500', Porcentagem=88.0),
    ]
    
    for c in combustiveis:
        print(f"  ✓ {c.Tipo} ({c.Porcentagem}%)")
    
    print(f"✅ {len(combustiveis)} combustíveis criados\n")
    return combustiveis


def criar_dados_operacionais(unidades):
    """Cria dados operacionais (pressão, altura, temperatura, etc)."""
    print("⚙️  Criando dados operacionais...")
    
    # Pressão dos pneus (PSI)
    pneus = [
        PressaoPneus.objects.create(Pressao=32.0, UnidadedeMedida=unidades['PSI']),
        PressaoPneus.objects.create(Pressao=34.0, UnidadedeMedida=unidades['PSI']),
        PressaoPneus.objects.create(Pressao=30.0, UnidadedeMedida=unidades['PSI']),
    ]
    print(f"  ✓ {len(pneus)} pressões de pneus")
    
    # Altura de corte (cm)
    alturas = [
        AlturadoCorte.objects.create(Altura=15.0, UnidadedeMedida=unidades['cm']),
        AlturadoCorte.objects.create(Altura=18.0, UnidadedeMedida=unidades['cm']),
        AlturadoCorte.objects.create(Altura=20.0, UnidadedeMedida=unidades['cm']),
    ]
    print(f"  ✓ {len(alturas)} alturas de corte")
    
    # Pressão de corte (bar)
    pressoes_corte = [
        PressaodoCorte.objects.create(Pressao=120.0, UnidadedeMedida=unidades['bar']),
        PressaodoCorte.objects.create(Pressao=125.0, UnidadedeMedida=unidades['bar']),
        PressaodoCorte.objects.create(Pressao=115.0, UnidadedeMedida=unidades['bar']),
    ]
    print(f"  ✓ {len(pressoes_corte)} pressões de corte")
    
    # Temperatura e umidade ambiente
    ambientes = [
        TempUmi_Ambiente.objects.create(Temperatura=28.5, Umidade=65.0),
        TempUmi_Ambiente.objects.create(Temperatura=31.2, Umidade=58.0),
        TempUmi_Ambiente.objects.create(Temperatura=26.8, Umidade=72.0),
    ]
    print(f"  ✓ {len(ambientes)} leituras de ambiente")
    
    # Status de operação
    status_ops = [
        StatusdeOperacao.objects.create(Em_Operacao=True, Tempo_de_Operacao=4.5),
        StatusdeOperacao.objects.create(Em_Operacao=True, Tempo_de_Operacao=6.2),
        StatusdeOperacao.objects.create(Em_Operacao=True, Tempo_de_Operacao=3.8),
        StatusdeOperacao.objects.create(Em_Operacao=False, Tempo_de_Operacao=0.0),
    ]
    print(f"  ✓ {len(status_ops)} status de operação")
    
    # Estado de movimento
    movimentos = [
        EstadodeMovimento.objects.create(Em_Movimento=True, Velocidade=8.5),
        EstadodeMovimento.objects.create(Em_Movimento=True, Velocidade=12.3),
        EstadodeMovimento.objects.create(Em_Movimento=True, Velocidade=6.7),
        EstadodeMovimento.objects.create(Em_Movimento=False, Velocidade=0.0),
    ]
    print(f"  ✓ {len(movimentos)} estados de movimento")
    
    print(f"✅ Dados operacionais criados\n")
    
    return {
        'pneus': pneus,
        'alturas': alturas,
        'pressoes_corte': pressoes_corte,
        'ambientes': ambientes,
        'status_ops': status_ops,
        'movimentos': movimentos,
    }


def criar_temperaturas_maquina(modelos):
    """Cria leituras de temperatura para cada modelo."""
    print("🌡️  Criando temperaturas das máquinas...")
    
    temps = [
        TemperaturaMaquina.objects.create(Temperatura=72.5, Maquina=modelos[0]),  # TC5000
        TemperaturaMaquina.objects.create(Temperatura=68.3, Maquina=modelos[0]),  # TC5000
        TemperaturaMaquina.objects.create(Temperatura=75.8, Maquina=modelos[2]),  # S780
        TemperaturaMaquina.objects.create(Temperatura=71.2, Maquina=modelos[2]),  # S780
        TemperaturaMaquina.objects.create(Temperatura=69.5, Maquina=modelos[4]),  # CR9090
        TemperaturaMaquina.objects.create(Temperatura=73.1, Maquina=modelos[4]),  # CR9090
    ]
    
    for t in temps:
        print(f"  ✓ {t.Temperatura}°C ({t.Maquina.Nome})")
    
    print(f"✅ {len(temps)} temperaturas criadas\n")
    return temps


def criar_colheitadeiras(modelos, operarios, combustiveis, dados_ops, temps):
    """Cria as colheitadeiras completas."""
    print("🚜 Criando colheitadeiras...")
    
    colheitadeiras = [
        # CASE TC5000 #1 - João Silva
        Colheitadeira.objects.create(
            Modelo=modelos[0],              # TC5000
            Combustivel=combustiveis[0],    # 85%
            Operario=operarios[0],          # João Silva
            PressaoPneus=dados_ops['pneus'][0],
            AlturadoCorte=dados_ops['alturas'][0],
            PressaodoCorte=dados_ops['pressoes_corte'][0],
            TempUmi_Ambiente=dados_ops['ambientes'][0],
            TemperaturaMaquina=temps[0],
            StatusdeOperacao=dados_ops['status_ops'][0],
            EstadodeMovimento=dados_ops['movimentos'][0],
        ),
        
        # CASE TC5000 #2 - Maria Santos
        Colheitadeira.objects.create(
            Modelo=modelos[0],              # TC5000
            Combustivel=combustiveis[1],    # 92%
            Operario=operarios[1],          # Maria Santos
            PressaoPneus=dados_ops['pneus'][1],
            AlturadoCorte=dados_ops['alturas'][1],
            PressaodoCorte=dados_ops['pressoes_corte'][1],
            TempUmi_Ambiente=dados_ops['ambientes'][1],
            TemperaturaMaquina=temps[1],
            StatusdeOperacao=dados_ops['status_ops'][1],
            EstadodeMovimento=dados_ops['movimentos'][1],
        ),
        
        # John Deere S780 #1 - Pedro Costa
        Colheitadeira.objects.create(
            Modelo=modelos[2],              # S780
            Combustivel=combustiveis[2],    # 78%
            Operario=operarios[2],          # Pedro Costa
            PressaoPneus=dados_ops['pneus'][2],
            AlturadoCorte=dados_ops['alturas'][2],
            PressaodoCorte=dados_ops['pressoes_corte'][2],
            TempUmi_Ambiente=dados_ops['ambientes'][2],
            TemperaturaMaquina=temps[2],
            StatusdeOperacao=dados_ops['status_ops'][2],
            EstadodeMovimento=dados_ops['movimentos'][2],
        ),
        
        # John Deere S780 #2 - Ana Oliveira
        Colheitadeira.objects.create(
            Modelo=modelos[2],              # S780
            Combustivel=combustiveis[3],    # 88%
            Operario=operarios[3],          # Ana Oliveira
            PressaoPneus=dados_ops['pneus'][0],
            AlturadoCorte=dados_ops['alturas'][0],
            PressaodoCorte=dados_ops['pressoes_corte'][0],
            TempUmi_Ambiente=dados_ops['ambientes'][0],
            TemperaturaMaquina=temps[3],
            StatusdeOperacao=dados_ops['status_ops'][0],
            EstadodeMovimento=dados_ops['movimentos'][0],
        ),
        
        # New Holland CR9090 #1 - João Silva
        Colheitadeira.objects.create(
            Modelo=modelos[4],              # CR9090
            Combustivel=combustiveis[0],    # 85%
            Operario=operarios[0],          # João Silva
            PressaoPneus=dados_ops['pneus'][1],
            AlturadoCorte=dados_ops['alturas'][1],
            PressaodoCorte=dados_ops['pressoes_corte'][1],
            TempUmi_Ambiente=dados_ops['ambientes'][1],
            TemperaturaMaquina=temps[4],
            StatusdeOperacao=dados_ops['status_ops'][1],
            EstadodeMovimento=dados_ops['movimentos'][1],
        ),
        
        # New Holland CR9090 #2 - Maria Santos
        Colheitadeira.objects.create(
            Modelo=modelos[4],              # CR9090
            Combustivel=combustiveis[1],    # 92%
            Operario=operarios[1],          # Maria Santos
            PressaoPneus=dados_ops['pneus'][2],
            AlturadoCorte=dados_ops['alturas'][2],
            PressaodoCorte=dados_ops['pressoes_corte'][2],
            TempUmi_Ambiente=dados_ops['ambientes'][2],
            TemperaturaMaquina=temps[5],
            StatusdeOperacao=dados_ops['status_ops'][2],
            EstadodeMovimento=dados_ops['movimentos'][2],
        ),
    ]
    
    for i, c in enumerate(colheitadeiras, 1):
        print(f"  ✓ #{i} {c.Modelo.Nome} ({c.Modelo.Marca.Nome}) - {c.Operario.Nome}")
    
    print(f"✅ {len(colheitadeiras)} colheitadeiras criadas\n")
    return colheitadeiras


def main():
    """Executa o script de população do banco."""
    print("\n" + "="*60)
    print("  FIELDNODE — POPULAÇÃO DO BANCO DE DADOS")
    print("="*60 + "\n")
    
    # Limpa dados existentes
    limpar_dados_existentes()
    
    # Cria dados em ordem de dependência
    unidades = criar_unidades()
    modelos = criar_marcas_e_modelos(unidades)
    operarios = criar_operarios()
    combustiveis = criar_combustiveis()
    dados_ops = criar_dados_operacionais(unidades)
    temps = criar_temperaturas_maquina(modelos)
    colheitadeiras = criar_colheitadeiras(modelos, operarios, combustiveis, dados_ops, temps)
    
    # Resumo final
    print("\n" + "="*60)
    print("  RESUMO FINAL")
    print("="*60)
    print(f"  ✅ {UnidadedeMedida.objects.count()} unidades de medida")
    print(f"  ✅ {Marca.objects.count()} marcas")
    print(f"  ✅ {Modelo.objects.count()} modelos")
    print(f"  ✅ {Operario.objects.count()} operários")
    print(f"  ✅ {Combustivel.objects.count()} combustíveis")
    print(f"  ✅ {Colheitadeira.objects.count()} colheitadeiras")
    print("="*60)
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("  1. Rode o simulador para gerar telemetria:")
    print("     python esp_simulator_multi.py")
    print("\n  2. Ou use o demo de pane para apresentação:")
    print("     python scripts/demo_pane.py")
    print("\n  3. Acesse o dashboard:")
    print("     Abra frontend/index.html no navegador")
    print("\n✅ Banco de dados populado com sucesso!\n")


if __name__ == '__main__':
    main()
