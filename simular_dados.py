"""
Script de Simulação de Dados - FieldNode
==========================================

Popula o banco de dados com dados realistas para demonstração.

Uso:
    python simular_dados.py

O que este script faz:
    1. Cria marcas e modelos de colheitadeiras
    2. Cadastra operários
    3. Cria registros de referência (combustível, ambiente, etc)
    4. Cadastra colheitadeiras completas
    5. Envia leituras de telemetria simuladas (cenários normal, atenção e crítico)
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
import random
import time

API_BASE = "http://127.0.0.1:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def post(endpoint, data):
    """Faz POST e retorna o ID do objeto criado"""
    try:
        response = requests.post(f"{API_BASE}{endpoint}", json=data)
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✓ {endpoint}: {data.get('Nome') or data.get('Tipo') or data.get('maquina_id') or 'OK'}")
            return result.get('id') or result
        else:
            print(f"✗ Erro {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Erro de conexão: {e}")
        return None

def get(endpoint):
    """Faz GET e retorna os dados"""
    try:
        response = requests.get(f"{API_BASE}{endpoint}")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

# ============================================================
# PASSO 1: MARCAS E MODELOS
# ============================================================
print_section("PASSO 1: Criando Marcas e Modelos")

marcas = [
    {"Nome": "Case IH"},
    {"Nome": "New Holland"},
    {"Nome": "John Deere"},
]

marca_ids = {}
for marca in marcas:
    marca_id = post("/Marca/", marca)
    if marca_id:
        marca_ids[marca["Nome"]] = marca_id

# Aguarda um pouco para garantir que os dados foram salvos
time.sleep(0.5)

modelos = [
    {"Nome": "TC5000", "Marca_id": marca_ids.get("Case IH")},
    {"Nome": "TC5070", "Marca_id": marca_ids.get("Case IH")},
    {"Nome": "CR9000", "Marca_id": marca_ids.get("New Holland")},
    {"Nome": "S780", "Marca_id": marca_ids.get("John Deere")},
]

modelo_ids = {}
for modelo in modelos:
    if modelo["Marca_id"]:
        modelo_id = post("/Modelo/", modelo)
        if modelo_id:
            modelo_ids[modelo["Nome"]] = modelo_id

time.sleep(0.5)

# ============================================================
# PASSO 2: OPERÁRIOS
# ============================================================
print_section("PASSO 2: Criando Operários")

operarios = [
    {"Nome": "João Silva", "TempodeServico": 8, "Nobanco": True},
    {"Nome": "Maria Santos", "TempodeServico": 5, "Nobanco": True},
    {"Nome": "Pedro Costa", "TempodeServico": 12, "Nobanco": False},
    {"Nome": "Ana Oliveira", "TempodeServico": 3, "Nobanco": True},
]

operario_ids = []
for op in operarios:
    op_id = post("/Operario/", op)
    if op_id:
        operario_ids.append(op_id)

time.sleep(0.5)

# ============================================================
# PASSO 3: UNIDADES DE MEDIDA
# ============================================================
print_section("PASSO 3: Criando Unidades de Medida")

unidades = [
    {"Nome": "PSI"},
    {"Nome": "cm"},
    {"Nome": "bar"},
]

unidade_ids = {}
for un in unidades:
    un_id = post("/Unidadedemedida/", un)
    if un_id:
        unidade_ids[un["Nome"]] = un_id

time.sleep(0.5)

# ============================================================
# PASSO 4: COMBUSTÍVEL
# ============================================================
print_section("PASSO 4: Criando Registros de Combustível")

combustiveis = [
    {"Tipo": "Diesel S10", "Porcentagem": 85.0},
    {"Tipo": "Diesel S10", "Porcentagem": 92.0},
    {"Tipo": "Diesel S10", "Porcentagem": 78.0},
    {"Tipo": "Diesel S10", "Porcentagem": 65.0},
]

combustivel_ids = []
for comb in combustiveis:
    comb_id = post("/Combustivel/", comb)
    if comb_id:
        combustivel_ids.append(comb_id)

time.sleep(0.5)

# ============================================================
# PASSO 5: LEITURAS DE REFERÊNCIA
# ============================================================
print_section("PASSO 5: Criando Leituras de Referência")

# Pressão dos pneus
pressao_pneus_ids = []
for pressao in [32, 34, 30, 33]:
    pp_id = post("/Pressaopneus/", {
        "Pressao": pressao,
        "UnidadedeMedida": unidade_ids.get("PSI")
    })
    if pp_id:
        pressao_pneus_ids.append(pp_id)

time.sleep(0.3)

# Altura de corte
altura_ids = []
for altura in [45, 50, 42, 48]:
    alt_id = post("/Alturadocorte/", {
        "Altura": altura,
        "UnidadedeMedida": unidade_ids.get("cm")
    })
    if alt_id:
        altura_ids.append(alt_id)

time.sleep(0.3)

# Pressão de corte
pressao_corte_ids = []
for pressao in [120, 115, 125, 118]:
    pc_id = post("/Pressaodocorte/", {
        "Pressao": pressao,
        "UnidadedeMedida": unidade_ids.get("bar")
    })
    if pc_id:
        pressao_corte_ids.append(pc_id)

time.sleep(0.3)

# Ambiente
ambiente_ids = []
ambientes = [
    {"Temperatura": 28.5, "Umidade": 65},
    {"Temperatura": 31.2, "Umidade": 58},
    {"Temperatura": 26.8, "Umidade": 72},
    {"Temperatura": 29.4, "Umidade": 61},
]
for amb in ambientes:
    amb_id = post("/Tempumi_ambiente/", amb)
    if amb_id:
        ambiente_ids.append(amb_id)

time.sleep(0.3)

# Temperatura da máquina
temp_maq_ids = []
for temp, modelo_nome in [(72, "TC5000"), (75, "TC5070"), (70, "CR9000"), (73, "S780")]:
    tm_id = post("/Temperaturamaquina/", {
        "Temperatura": temp,
        "Maquina": modelo_ids.get(modelo_nome)
    })
    if tm_id:
        temp_maq_ids.append(tm_id)

time.sleep(0.3)

# Status de operação
status_ids = []
for em_op, tempo in [(True, 4.5), (True, 6.2), (False, 0.0), (True, 3.8)]:
    st_id = post("/Statusdeoperacao/", {
        "Em_Operacao": em_op,
        "Tempo_de_Operacao": tempo
    })
    if st_id:
        status_ids.append(st_id)

time.sleep(0.3)

# Estado de movimento
movimento_ids = []
for em_mov, vel in [(True, 12.5), (True, 10.8), (False, 0.0), (True, 11.2)]:
    mov_id = post("/Estadodemovimento/", {
        "Em_Movimento": em_mov,
        "Velocidade": vel
    })
    if mov_id:
        movimento_ids.append(mov_id)

time.sleep(0.5)

# ============================================================
# PASSO 6: COLHEITADEIRAS
# ============================================================
print_section("PASSO 6: Criando Colheitadeiras")

# Verifica se temos todos os IDs necessários
if not all([modelo_ids, combustivel_ids, operario_ids, pressao_pneus_ids, 
            altura_ids, pressao_corte_ids, ambiente_ids, temp_maq_ids, 
            status_ids, movimento_ids]):
    print("✗ Erro: Faltam dados de referência. Verifique os passos anteriores.")
    exit(1)

colheitadeiras = [
    {
        "Modelo": modelo_ids.get("TC5000"),
        "Combustivel": combustivel_ids[0],
        "Operario": operario_ids[0],
        "PressaoPneus": pressao_pneus_ids[0],
        "AlturadoCorte": altura_ids[0],
        "PressaodoCorte": pressao_corte_ids[0],
        "TempUmi_Ambiente": ambiente_ids[0],
        "TemperaturaMaquina": temp_maq_ids[0],
        "StatusdeOperacao": status_ids[0],
        "EstadodeMovimento": movimento_ids[0],
    },
    {
        "Modelo": modelo_ids.get("TC5070"),
        "Combustivel": combustivel_ids[1],
        "Operario": operario_ids[1],
        "PressaoPneus": pressao_pneus_ids[1],
        "AlturadoCorte": altura_ids[1],
        "PressaodoCorte": pressao_corte_ids[1],
        "TempUmi_Ambiente": ambiente_ids[1],
        "TemperaturaMaquina": temp_maq_ids[1],
        "StatusdeOperacao": status_ids[1],
        "EstadodeMovimento": movimento_ids[1],
    },
    {
        "Modelo": modelo_ids.get("CR9000"),
        "Combustivel": combustivel_ids[2],
        "Operario": operario_ids[2],
        "PressaoPneus": pressao_pneus_ids[2],
        "AlturadoCorte": altura_ids[2],
        "PressaodoCorte": pressao_corte_ids[2],
        "TempUmi_Ambiente": ambiente_ids[2],
        "TemperaturaMaquina": temp_maq_ids[2],
        "StatusdeOperacao": status_ids[2],
        "EstadodeMovimento": movimento_ids[2],
    },
    {
        "Modelo": modelo_ids.get("S780"),
        "Combustivel": combustivel_ids[3],
        "Operario": operario_ids[3],
        "PressaoPneus": pressao_pneus_ids[3],
        "AlturadoCorte": altura_ids[3],
        "PressaodoCorte": pressao_corte_ids[3],
        "TempUmi_Ambiente": ambiente_ids[3],
        "TemperaturaMaquina": temp_maq_ids[3],
        "StatusdeOperacao": status_ids[3],
        "EstadodeMovimento": movimento_ids[3],
    },
]

colheitadeira_ids = []
for colh in colheitadeiras:
    colh_id = post("/Colheitadeira/", colh)
    if colh_id:
        colheitadeira_ids.append(colh_id)

time.sleep(1)

# ============================================================
# PASSO 7: TELEMETRIA SIMULADA
# ============================================================
print_section("PASSO 7: Enviando Leituras de Telemetria")

# Mapeamento de máquinas para IDs de telemetria
maquinas_telemetria = [
    "CASE-TC5000-01",
    "CASE-TC5070-01", 
    "NH-CR9000-01",
    "JD-S780-01",
]

print("Enviando 15 leituras por máquina (60 leituras no total)...")
print("Isso pode levar ~30 segundos...\n")

# Cenários de operação
cenarios = {
    "CASE-TC5000-01": {  # Operação normal
        "temp_base": 72,
        "temp_var": 3,
        "vib_base": 0.35,
        "vib_var": 0.1,
        "rpm_base": 1850,
        "rpm_var": 100,
    },
    "CASE-TC5070-01": {  # Atenção - temperatura elevada
        "temp_base": 78,
        "temp_var": 4,
        "vib_base": 0.55,
        "vib_var": 0.15,
        "rpm_base": 1750,
        "rpm_var": 150,
    },
    "NH-CR9000-01": {  # Crítico - superaquecimento
        "temp_base": 88,
        "temp_var": 3,
        "vib_base": 0.85,
        "vib_var": 0.1,
        "rpm_base": 1200,
        "rpm_var": 100,
    },
    "JD-S780-01": {  # Normal com variação
        "temp_base": 73,
        "temp_var": 5,
        "vib_base": 0.42,
        "vib_var": 0.12,
        "rpm_base": 1820,
        "rpm_var": 120,
    },
}

total_enviadas = 0
total_erros = 0

for maquina_id in maquinas_telemetria:
    cenario = cenarios[maquina_id]
    
    # Envia 15 leituras espaçadas no tempo
    for i in range(15):
        timestamp = datetime.now() - timedelta(minutes=15-i)
        
        # Adiciona variação realista aos valores
        temperatura = cenario["temp_base"] + random.uniform(-cenario["temp_var"], cenario["temp_var"])
        vibracao = max(0.1, cenario["vib_base"] + random.uniform(-cenario["vib_var"], cenario["vib_var"]))
        rpm = max(800, cenario["rpm_base"] + random.uniform(-cenario["rpm_var"], cenario["rpm_var"]))
        
        leitura = {
            "id": str(uuid.uuid4()),
            "maquina_id": maquina_id,
            "temperatura": round(temperatura, 1),
            "vibracao": round(vibracao, 2),
            "rpm": int(rpm),
            "timestamp": timestamp.isoformat() + "Z"
        }
        
        result = post("/api/telemetria/", leitura)
        if result:
            total_enviadas += 1
        else:
            total_erros += 1
        
        # Pequeno delay para não sobrecarregar a API
        time.sleep(0.1)

print(f"\n✓ Total de leituras enviadas: {total_enviadas}")
if total_erros > 0:
    print(f"✗ Total de erros: {total_erros}")

# ============================================================
# RESUMO FINAL
# ============================================================
print_section("RESUMO FINAL")

print("Dados cadastrados com sucesso!\n")
print("📊 Estatísticas:")
print(f"   • Marcas: {len(marca_ids)}")
print(f"   • Modelos: {len(modelo_ids)}")
print(f"   • Operários: {len(operario_ids)}")
print(f"   • Colheitadeiras: {len(colheitadeira_ids)}")
print(f"   • Leituras de telemetria: {total_enviadas}")

print("\n🎯 Próximos passos:")
print("   1. Abra o dashboard: http://localhost:8000")
print("   2. Ou sirva o frontend: python -m http.server 5500 --directory frontend")
print("   3. Aguarde 3 segundos para o polling atualizar a tabela")
print("   4. Verifique os alertas na página 'Alertas'")
print("   5. Veja a análise de IA no card 'Análise de IA'")

print("\n💡 Dica:")
print("   A máquina NH-CR9000-01 está em estado CRÍTICO (temp > 85°C)")
print("   A máquina CASE-TC5070-01 está em ATENÇÃO (temp > 75°C)")
print("   As outras duas estão operando normalmente")

print("\n" + "="*60)
print("  Simulação concluída! Boa apresentação! 🚀")
print("="*60 + "\n")
