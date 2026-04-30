# COMANDOS RÁPIDOS — Preparação para Banca

## 🚀 Setup Completo em 3 Comandos

```bash
# 1. Popular o banco de dados
python scripts/popular_banco.py

# 2. Iniciar o simulador (em outro terminal)
python esp_simulator_multi.py

# 3. Abrir o dashboard
# Abrir frontend/index.html no navegador
```

---

## 📋 Pré-requisitos (Verificar Antes)

```bash
# ✅ MySQL rodando
mysql -u root -p -e "SHOW DATABASES LIKE 'fieldnode';"

# ✅ Django funcionando
python manage.py check

# ✅ MQTT listener rodando (você disse que já está)
# Deve estar em outro terminal mostrando:
# "Conectado ao broker MQTT em localhost:1883"

# ✅ Broker MQTT ativo
# Windows: net start mosquitto
# Linux/Mac: mosquitto -v
```

---

## 🎯 O Que Cada Script Faz

### `popular_banco.py`
- Limpa dados antigos
- Cria 6 colheitadeiras completas
- IDs: CASE-TC5000-01, CASE-TC5000-02, DEERE-S780-01, DEERE-S780-02, NH-CR9090-01, NH-CR9090-02
- 4 operários: João Silva, Maria Santos, Pedro Costa, Ana Oliveira
- Todos os dados de referência (pressão, temperatura, combustível, etc)

### `esp_simulator_multi.py`
- Simula telemetria de 6 máquinas via MQTT
- Envia temperatura, vibração, RPM a cada 2s
- Alterna cenários: normal, aquecendo, crítico
- Dados chegam no `mqtt_listen.py` → Django → MySQL

---

## 🎬 Para a Apresentação

### Cenário 1: Operação Normal
```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: MQTT Listener (já rodando)
# python scripts/mqtt_listen.py

# Terminal 3: Simulador
python esp_simulator_multi.py

# Navegador
Abrir frontend/index.html
```

### Cenário 2: Demo de Pane (Momento WOW)
```bash
# Substitua o Terminal 3 por:
python scripts/demo_pane.py

# Escolha: CASE-TC5000-02
# Assista a temperatura subir de 65°C → 92°C
# Dashboard muda de NORMAL → ATENÇÃO → CRÍTICO
```

---

## 🔍 Verificação Rápida

### Dashboard deve mostrar:
- ✅ 6 máquinas na tabela de status
- ✅ Gráficos atualizando a cada 3s
- ✅ Card de combustível mostrando "N/D"
- ✅ Sistema bicolor (máquinas do mesmo modelo)
- ✅ IA ativa após ~1 minuto (30 leituras/máquina)

### Se algo não funcionar:
```bash
# Verifique logs do Django
# Terminal 1 deve mostrar: POST /api/telemetria/ 201

# Verifique logs do MQTT listener
# Terminal 2 deve mostrar: Recebido de CASE-TC5000-01

# Verifique logs do simulador
# Terminal 3 deve mostrar: [OK] CASE-TC5000-01 | Temp: 72.3°C
```

---

## 📊 Dados Criados

| Tabela | Quantidade | Exemplos |
|--------|-----------|----------|
| Marcas | 3 | Case IH, John Deere, New Holland |
| Modelos | 6 | TC5000, S780, CR9090, etc |
| Operários | 4 | João Silva (8 anos), Maria Santos (12 anos) |
| Colheitadeiras | 6 | CASE-TC5000-01, DEERE-S780-01, etc |
| Unidades | 7 | PSI, bar, cm, °C, %, km/h, RPM |

---

## ⚠️ Problemas Comuns

### "Nenhuma leitura recebida do ESP32"
→ MQTT listener não está rodando ou broker offline

### "Erro ao conectar na API"
→ Django não está rodando (`python manage.py runserver`)

### "Dados insuficientes para análise de IA"
→ Aguarde 1 minuto (precisa de 30 leituras por máquina)

### "Card de combustível mostra número"
→ Isso foi corrigido! Deve mostrar "N/D - requer sensor adicional"

---

## ✅ Checklist Final

- [ ] `python scripts/popular_banco.py` executado com sucesso
- [ ] Django rodando em http://localhost:8000
- [ ] MQTT listener conectado e recebendo dados
- [ ] Simulador enviando dados para 6 máquinas
- [ ] Dashboard abrindo e mostrando dados em tempo real
- [ ] IA funcionando após ~1 minuto
- [ ] Demo de pane testado

---

## 🎯 Roteiro para Banca (30 segundos)

1. **Mostre o dashboard** → "6 colheitadeiras operando em tempo real"
2. **Explique o fluxo** → "ESP32 → MQTT → Django → MySQL → Dashboard"
3. **Destaque a IA** → "Isolation Forest + Random Forest com rolling windows"
4. **Rode o demo de pane** → "Temperatura subindo, IA detectando anomalia"
5. **Seja honesto** → "Combustível requer sensor adicional, labels baseados em padrões documentados"

---

**Tudo pronto! Execute os 3 comandos acima e você está pronto para a banca. 🚀**
