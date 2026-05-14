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
        obj = UnidadedeMedida.objects.create(nome=nome)
        objs.append(obj)
        print(f"  ✓ {nome}")
    
    print(f"✅ {len(objs)} unidades criadas\n")
    return {u.nome: u for u in objs}


def criar_marcas_e_modelos(unidades):
    """Cria marcas e modelos de colheitadeiras."""
    print("🏭 Criando marcas e modelos...")
    
    # Marcas
    case = Marca.objects.create(nome='Case IH')
    deere = Marca.objects.create(nome='John Deere')
    nh = Marca.objects.create(nome='New Holland')
    print(f"  ✓ {case.nome}")
    print(f"  ✓ {deere.nome}")
    print(f"  ✓ {nh.nome}")

    # Modelos
    modelos = [
        Modelo.objects.create(nome='TC5000', marca=case),
        Modelo.objects.create(nome='Axial-Flow 9250', marca=case),
        Modelo.objects.create(nome='S780', marca=deere),
        Modelo.objects.create(nome='X9 1100', marca=deere),
        Modelo.objects.create(nome='CR9090', marca=nh),
        Modelo.objects.create(nome='CR10.90', marca=nh),
    ]

    for m in modelos:
        print(f"  ✓ {m.nome} ({m.marca.nome})")
    
    print(f"✅ {len(modelos)} modelos criados\n")
    return modelos


def criar_operarios():
    """Cria operários com experiências variadas."""
    print("👷 Criando operários...")

    operarios = [
        Operario.objects.create(nome='João Silva', tempo_de_servico=8, no_banco=True),
        Operario.objects.create(nome='Maria Santos', tempo_de_servico=12, no_banco=True),
        Operario.objects.create(nome='Pedro Costa', tempo_de_servico=5, no_banco=True),
        Operario.objects.create(nome='Ana Oliveira', tempo_de_servico=15, no_banco=True),
    ]

    for op in operarios:
        print(f"  ✓ {op.nome} ({op.tempo_de_servico} anos)")

    print(f"✅ {len(operarios)} operários criados\n")
    return operarios


def criar_combustiveis():
    """Cria tipos de combustível."""
    print("⛽ Criando combustíveis...")

    combustiveis = [
        Combustivel.objects.create(tipo='Diesel S10', porcentagem=85.0),
        Combustivel.objects.create(tipo='Diesel S10', porcentagem=92.0),
        Combustivel.objects.create(tipo='Diesel S10', porcentagem=78.0),
        Combustivel.objects.create(tipo='Diesel S500', porcentagem=88.0),
    ]

    for c in combustiveis:
        print(f"  ✓ {c.tipo} ({c.porcentagem}%)")

    print(f"✅ {len(combustiveis)} combustíveis criados\n")
    return combustiveis


def criar_dados_operacionais(unidades):
    """Cria dados operacionais (pressão, altura, temperatura, etc)."""
    print("⚙️  Criando dados operacionais...")

    # Pressão dos pneus (PSI)
    pneus = [
        PressaoPneus.objects.create(pressao=32.0, unidade_de_medida=unidades['PSI']),
        PressaoPneus.objects.create(pressao=34.0, unidade_de_medida=unidades['PSI']),
        PressaoPneus.objects.create(pressao=30.0, unidade_de_medida=unidades['PSI']),
    ]
    print(f"  ✓ {len(pneus)} pressões de pneus")

    # Altura de corte (cm)
    alturas = [
        AlturadoCorte.objects.create(altura=15.0, unidade_de_medida=unidades['cm']),
        AlturadoCorte.objects.create(altura=18.0, unidade_de_medida=unidades['cm']),
        AlturadoCorte.objects.create(altura=20.0, unidade_de_medida=unidades['cm']),
    ]
    print(f"  ✓ {len(alturas)} alturas de corte")

    # Pressão de corte (bar)
    pressoes_corte = [
        PressaodoCorte.objects.create(pressao=120.0, unidade_de_medida=unidades['bar']),
        PressaodoCorte.objects.create(pressao=125.0, unidade_de_medida=unidades['bar']),
        PressaodoCorte.objects.create(pressao=115.0, unidade_de_medida=unidades['bar']),
    ]
    print(f"  ✓ {len(pressoes_corte)} pressões de corte")

    # Temperatura e umidade ambiente
    ambientes = [
        TempUmi_Ambiente.objects.create(temperatura=28.5, umidade=65.0),
        TempUmi_Ambiente.objects.create(temperatura=31.2, umidade=58.0),
        TempUmi_Ambiente.objects.create(temperatura=26.8, umidade=72.0),
    ]
    print(f"  ✓ {len(ambientes)} leituras de ambiente")

    # Status de operação
    status_ops = [
        StatusdeOperacao.objects.create(em_operacao=True, tempo_de_operacao=4.5),
        StatusdeOperacao.objects.create(em_operacao=True, tempo_de_operacao=6.2),
        StatusdeOperacao.objects.create(em_operacao=True, tempo_de_operacao=3.8),
        StatusdeOperacao.objects.create(em_operacao=False, tempo_de_operacao=0.0),
    ]
    print(f"  ✓ {len(status_ops)} status de operação")

    # Estado de movimento
    movimentos = [
        EstadodeMovimento.objects.create(em_movimento=True, velocidade=8.5),
        EstadodeMovimento.objects.create(em_movimento=True, velocidade=12.3),
        EstadodeMovimento.objects.create(em_movimento=True, velocidade=6.7),
        EstadodeMovimento.objects.create(em_movimento=False, velocidade=0.0),
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
        TemperaturaMaquina.objects.create(temperatura=72.5, maquina=modelos[0]),  # TC5000
        TemperaturaMaquina.objects.create(temperatura=68.3, maquina=modelos[0]),  # TC5000
        TemperaturaMaquina.objects.create(temperatura=75.8, maquina=modelos[2]),  # S780
        TemperaturaMaquina.objects.create(temperatura=71.2, maquina=modelos[2]),  # S780
        TemperaturaMaquina.objects.create(temperatura=69.5, maquina=modelos[4]),  # CR9090
        TemperaturaMaquina.objects.create(temperatura=73.1, maquina=modelos[4]),  # CR9090
    ]

    for t in temps:
        print(f"  ✓ {t.temperatura}°C ({t.maquina.nome})")

    print(f"✅ {len(temps)} temperaturas criadas\n")
    return temps


def criar_colheitadeiras(modelos, operarios, combustiveis, dados_ops, temps):
    """Cria as colheitadeiras completas."""
    print("🚜 Criando colheitadeiras...")

    colheitadeiras = [
        # CASE TC5000 #1 - João Silva
        Colheitadeira.objects.create(
            modelo=modelos[0],              # TC5000
            combustivel=combustiveis[0],    # 85%
            operario=operarios[0],          # João Silva
            pressao_pneus=dados_ops['pneus'][0],
            altura_do_corte=dados_ops['alturas'][0],
            pressao_do_corte=dados_ops['pressoes_corte'][0],
            temp_umi_ambiente=dados_ops['ambientes'][0],
            temperatura_maquina=temps[0],
            status_de_operacao=dados_ops['status_ops'][0],
            estado_de_movimento=dados_ops['movimentos'][0],
        ),

        # CASE TC5000 #2 - Maria Santos
        Colheitadeira.objects.create(
            modelo=modelos[0],              # TC5000
            combustivel=combustiveis[1],    # 92%
            operario=operarios[1],          # Maria Santos
            pressao_pneus=dados_ops['pneus'][1],
            altura_do_corte=dados_ops['alturas'][1],
            pressao_do_corte=dados_ops['pressoes_corte'][1],
            temp_umi_ambiente=dados_ops['ambientes'][1],
            temperatura_maquina=temps[1],
            status_de_operacao=dados_ops['status_ops'][1],
            estado_de_movimento=dados_ops['movimentos'][1],
        ),

        # John Deere S780 #1 - Pedro Costa
        Colheitadeira.objects.create(
            modelo=modelos[2],              # S780
            combustivel=combustiveis[2],    # 78%
            operario=operarios[2],          # Pedro Costa
            pressao_pneus=dados_ops['pneus'][2],
            altura_do_corte=dados_ops['alturas'][2],
            pressao_do_corte=dados_ops['pressoes_corte'][2],
            temp_umi_ambiente=dados_ops['ambientes'][2],
            temperatura_maquina=temps[2],
            status_de_operacao=dados_ops['status_ops'][2],
            estado_de_movimento=dados_ops['movimentos'][2],
        ),

        # John Deere S780 #2 - Ana Oliveira
        Colheitadeira.objects.create(
            modelo=modelos[2],              # S780
            combustivel=combustiveis[3],    # 88%
            operario=operarios[3],          # Ana Oliveira
            pressao_pneus=dados_ops['pneus'][0],
            altura_do_corte=dados_ops['alturas'][0],
            pressao_do_corte=dados_ops['pressoes_corte'][0],
            temp_umi_ambiente=dados_ops['ambientes'][0],
            temperatura_maquina=temps[3],
            status_de_operacao=dados_ops['status_ops'][0],
            estado_de_movimento=dados_ops['movimentos'][0],
        ),

        # New Holland CR9090 #1 - João Silva
        Colheitadeira.objects.create(
            modelo=modelos[4],              # CR9090
            combustivel=combustiveis[0],    # 85%
            operario=operarios[0],          # João Silva
            pressao_pneus=dados_ops['pneus'][1],
            altura_do_corte=dados_ops['alturas'][1],
            pressao_do_corte=dados_ops['pressoes_corte'][1],
            temp_umi_ambiente=dados_ops['ambientes'][1],
            temperatura_maquina=temps[4],
            status_de_operacao=dados_ops['status_ops'][1],
            estado_de_movimento=dados_ops['movimentos'][1],
        ),

        # New Holland CR9090 #2 - Maria Santos
        Colheitadeira.objects.create(
            modelo=modelos[4],              # CR9090
            combustivel=combustiveis[1],    # 92%
            operario=operarios[1],          # Maria Santos
            pressao_pneus=dados_ops['pneus'][2],
            altura_do_corte=dados_ops['alturas'][2],
            pressao_do_corte=dados_ops['pressoes_corte'][2],
            temp_umi_ambiente=dados_ops['ambientes'][2],
            temperatura_maquina=temps[5],
            status_de_operacao=dados_ops['status_ops'][2],
            estado_de_movimento=dados_ops['movimentos'][2],
        ),
    ]

    for i, c in enumerate(colheitadeiras, 1):
        print(f"  ✓ #{i} {c.modelo.nome} ({c.modelo.marca.nome}) - {c.operario.nome}")

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
