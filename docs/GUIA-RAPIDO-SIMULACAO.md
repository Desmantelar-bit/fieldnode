# Guia Rápido — Popular Banco e Iniciar Simulação

## 🎯 Objetivo

Popular o banco de dados com dados realistas de colheitadeiras e iniciar a simulação de telemetria para a apresentação da banca.

---

## 📋 Pré-requisitos

1. **MySQL rodando** com o banco `fieldnode` criado
2. **Django configurado** com `.env` preenchido
3. **MQTT broker rodando** (Mosquitto ou similar)
4. **mqtt_listen.py rodando** (você mencionou que já está)

---

## 🚀 Passo a Passo

### 1. Popular o Banco de Dados

```bash
# No terminal, na raiz do projeto
python scripts/popular_banco.py
```

**O que esse script faz:**
- ✅ Limpa dados existentes (se houver)
- ✅ Cria 3 marcas: Case IH, John Deere, New Holland
- ✅ Cria 6 modelos de colheitadeiras
- ✅ Cria 4 operários com experiências variadas
- ✅ Cria 6 colheitadeiras completas com todos os dados

**Máquinas criadas:**
1. `CASE-TC5000-01` - João Silva (8 anos)
2. `CASE-TC5000-02` - Maria Santos (12 anos)
3. `DEERE-S780-01` - Pedro Costa (5 anos)
4. `DEERE-S780-02` - Ana Oliveira (15 anos)
5. `NH-CR9090-01` - João Silva (8 anos)
6. `NH-CR9090-02` - Maria Santos (12 anos)

---

### 2. Verificar os Dados no Admin

```bash
# Acesse o admin do Django
http://localhost:8000/admin/

# Login com suas credenciais
# Navegue em: api_tcc > Colheitadeiras
```

Você deve ver 6 colheitadeiras cadastradas com todos os dados preenchidos.

---

### 3. Iniciar o Simulador de Telemetria

```bash
# Em um novo terminal
python esp_simulator_multi.py
```

**O que o simulador faz:**
- 📡 Envia dados de telemetria via MQTT para 6 máquinas
- 🌡️ Simula temperatura, vibração e RPM realistas
- 🎭 Alterna entre cenários: normal, aquecendo, crítico
- ⏱️ Envia leituras a cada 2 segundos (com variação)

**Saída esperada:**
```
[OK] Simulador conectado ao broker localhost:1883
[INFO] Iniciando simulação de 6 máquinas
[MAQUINA] CASE-TC5000-01 - Case IH TC5000 - Op: João Silva - Cenário: normal
[MAQUINA] CASE-TC5000-02 - Case IH TC5000 - Op: Maria Santos - Cenário: aquecendo
...
[14:32:15] [OK] CASE-TC5000-01 (normal) | Temp: 72.3°C | Vib: 0.48 | RPM: 1820
[14:32:15] [ATENCAO] CASE-TC5000-02 (aquecendo) | Temp: 86.5°C | Vib: 0.62 | RPM: 1850
```

---

### 4. Verificar no Dashboard

```bash
# Abra o frontend
# Opção 1: Abrir diretamente
frontend/index.html

# Opção 2: Servir com Python
python -m http.server 5500 --directory frontend
# Acesse: http://localhost:5500
```

**O que você deve ver:**
- ✅ 6 máquinas na tabela de status em tempo real
- ✅ Gráficos de temperatura atualizando a cada 3s
- ✅ Cards de métricas com dados reais
- ✅ Sistema bicolor identificando máquinas do mesmo modelo
- ✅ Análise de IA após ~30 leituras por máquina

---

## 🎬 Para a Apresentação da Banca

### Opção 1: Simulação Normal (Recomendado para início)

```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: MQTT Listener (já está rodando)
python scripts/mqtt_listen.py

# Terminal 3: Simulador
python esp_simulator_multi.py

# Navegador: Dashboard
Abrir frontend/index.html
```

### Opção 2: Demo de Pane (Para momento WOW)

```bash
# Substitua o simulador normal pelo demo de pane
python scripts/demo_pane.py

# Escolha uma máquina quando solicitado
# Ex: CASE-TC5000-02
```

**O demo de pane mostra:**
- 🌡️ Temperatura subindo gradualmente de 65°C → 92°C
- 🚨 Dashboard mudando de NORMAL → ATENÇÃO → CRÍTICO
- 🤖 IA detectando anomalias em tempo real
- ⚠️ Alertas automáticos sendo gerados

---

## 🔍 Verificação de Problemas

### Problema: "Nenhuma leitura recebida do ESP32"

**Causa:** MQTT listener não está rodando ou simulador não conectou

**Solução:**
```bash
# Verifique se o broker MQTT está rodando
# Windows (Mosquitto):
net start mosquitto

# Verifique se o listener está rodando
# Deve mostrar: "Conectado ao broker MQTT"
python scripts/mqtt_listen.py

# Verifique se o simulador conectou
# Deve mostrar: "[OK] Simulador conectado ao broker"
python esp_simulator_multi.py
```

---

### Problema: "Erro ao conectar na API"

**Causa:** Django não está rodando

**Solução:**
```bash
python manage.py runserver
```

---

### Problema: "Dados insuficientes para análise de IA"

**Causa:** Menos de 30 leituras por máquina

**Solução:**
- Aguarde ~1 minuto com o simulador rodando
- A IA precisa de 30 leituras para começar a análise
- O dashboard mostra o progresso: "Aguardando mais X leituras"

---

## 📊 Dados Criados pelo Script

### Unidades de Medida
- PSI, bar, cm, °C, %, km/h, RPM

### Marcas e Modelos
- **Case IH**: TC5000, Axial-Flow 9250
- **John Deere**: S780, X9 1100
- **New Holland**: CR9090, CR10.90

### Operários
1. João Silva (8 anos, no banco)
2. Maria Santos (12 anos, no banco)
3. Pedro Costa (5 anos, no banco)
4. Ana Oliveira (15 anos, no banco)

### Combustíveis
- Diesel S10: 85%, 92%, 78%
- Diesel S500: 88%

### Dados Operacionais
- Pressão dos pneus: 30-34 PSI
- Altura de corte: 15-20 cm
- Pressão de corte: 115-125 bar
- Temperatura ambiente: 26-31°C
- Umidade: 58-72%

---

## ✅ Checklist Final

Antes da apresentação, confirme:

- [ ] Banco populado com 6 colheitadeiras
- [ ] Django rodando sem erros
- [ ] MQTT listener conectado e recebendo dados
- [ ] Simulador enviando dados para 6 máquinas
- [ ] Dashboard mostrando dados em tempo real
- [ ] IA funcionando após ~1 minuto de simulação
- [ ] Demo de pane testado e funcionando

---

## 🎯 Dica para a Banca

**Sequência recomendada:**

1. **Início**: Mostre o dashboard com simulação normal
   - "Aqui temos 6 colheitadeiras operando em tempo real"
   - "Os dados chegam via MQTT a cada 2 segundos"
   - "O sistema bicolor identifica máquinas do mesmo modelo"

2. **Meio**: Explique a IA
   - "Após 30 leituras, a IA começa a análise preditiva"
   - "Usamos Isolation Forest para anomalias"
   - "Random Forest para manutenção preditiva"
   - "Rolling windows capturam tendências temporais"

3. **Clímax**: Rode o demo de pane
   - "Agora vou simular uma pane real"
   - "Vejam a temperatura subindo gradualmente"
   - "O dashboard muda de cor automaticamente"
   - "A IA detecta a anomalia antes da falha crítica"

4. **Conclusão**: Mostre o código
   - "Todo o código está documentado"
   - "Deduplicação por UUID no backend"
   - "SQL otimizado sem N+1 queries"
   - "Sistema pronto para produção com ajustes"

---

**Boa sorte na apresentação! 🚀**
