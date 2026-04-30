# ✅ Checklist Pré-Banca — FieldNode

**Data da Apresentação**: _________  
**Horário**: _________

---

## 🔧 Preparação Técnica (1 dia antes)

### Backend Django
- [ ] Banco MySQL rodando e acessível
- [ ] Migrations aplicadas (`python manage.py migrate`)
- [ ] Servidor Django iniciado (`python manage.py runserver`)
- [ ] Endpoint `/swagger/` acessível e documentado
- [ ] Dados de demonstração cadastrados (colheitadeiras, operários)

### Frontend
- [ ] Dashboard abre sem erros no console do navegador
- [ ] Gráficos renderizam corretamente (temperatura, combustível, movimento)
- [ ] Tabela de status em tempo real atualiza a cada 3s
- [ ] Sistema de cores bicolor funciona (máquinas do mesmo modelo)
- [ ] Busca de máquinas com sugestões funciona
- [ ] Popup de detalhes abre ao clicar em uma máquina

### Telemetria (Opcional — se for demonstrar ESP32)
- [ ] Broker MQTT rodando (`mosquitto -v`)
- [ ] Listener MQTT ativo (`python manage.py mqtt_listen`)
- [ ] ESP32 conectado e enviando dados
- [ ] Leituras chegando no banco de dados

### IA e Análise
- [ ] Endpoint `/api/manutencao/` retorna previsões
- [ ] Endpoint `/api/anomalias/` detecta padrões anormais
- [ ] Card de "Análise de IA" no dashboard mostra dados
- [ ] Alertas automáticos funcionando (temperatura, vibração, RPM)

---

## 📊 Dados de Demonstração

### Cenário 1: Operação Normal
```bash
# Máquina operando dentro dos parâmetros
curl -X POST http://localhost:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "uuid-normal-001",
    "maquina_id": "CASE-TC5000-01",
    "temperatura": 72.5,
    "vibracao": 0.35,
    "rpm": 1850,
    "timestamp": "2024-04-17T14:00:00Z"
  }'
```

### Cenário 2: Alerta de Atenção
```bash
# Temperatura elevada (75-85°C)
curl -X POST http://localhost:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "uuid-atencao-001",
    "maquina_id": "CASE-TC5000-02",
    "temperatura": 78.5,
    "vibracao": 0.55,
    "rpm": 1750,
    "timestamp": "2024-04-17T14:05:00Z"
  }'
```

### Cenário 3: Alerta Crítico
```bash
# Temperatura crítica (>85°C) + vibração alta
curl -X POST http://localhost:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "uuid-critico-001",
    "maquina_id": "NH-CR9000-01",
    "temperatura": 88.5,
    "vibracao": 0.85,
    "rpm": 1200,
    "timestamp": "2024-04-17T14:10:00Z"
  }'
```

---

## 🎤 Roteiro de Apresentação (Sugestão)

### 1. Introdução (2 min)
- [ ] Apresentar o problema: colheitadeiras sem sinal no campo
- [ ] Explicar a solução: telemetria offline-first com ESP32
- [ ] Mostrar a arquitetura (slide ou diagrama do README)

### 2. Demonstração do Hardware (3 min) — Opcional
- [ ] Mostrar o ESP32 físico (se disponível)
- [ ] Explicar os sensores (temperatura, vibração, RPM)
- [ ] Demonstrar envio de dados via ESP-NOW → Gateway → API

### 3. Demonstração do Backend (5 min)
- [ ] Abrir `/swagger/` e mostrar endpoints documentados
- [ ] Fazer POST manual em `/api/telemetria/` (Postman ou curl)
- [ ] Mostrar deduplicação (enviar mesmo UUID duas vezes)
- [ ] Mostrar validação de range (temperatura -999°C é rejeitada)

### 4. Demonstração do Dashboard (7 min)
- [ ] Abrir `index.html` e mostrar métricas em tempo real
- [ ] Explicar sistema de cores bicolor (máquinas do mesmo modelo)
- [ ] Mostrar gráficos de temperatura e combustível
- [ ] Demonstrar busca de máquinas com sugestões
- [ ] Abrir popup de detalhes de uma máquina
- [ ] Mostrar análise de IA (manutenção preditiva + anomalias)
- [ ] Demonstrar alertas automáticos (temperatura crítica)

### 5. Código e Arquitetura (3 min)
- [ ] Mostrar estrutura de pastas do projeto
- [ ] Explicar service layer (`services/telemetria.py`)
- [ ] Mostrar testes automatizados (`tests/test_telemetria.py`)
- [ ] Explicar modelo de IA (Random Forest + Isolation Forest)

### 6. Conclusão e Próximos Passos (2 min)
- [ ] Resumir o que foi implementado
- [ ] Mencionar limitações conhecidas (combustível, validação de maquina_id)
- [ ] Apresentar roadmap de produção (autenticação, CAN bus, retreino de IA)

---

## 🐛 Troubleshooting Rápido

### Dashboard não carrega
```bash
# Verificar se a API está rodando
curl http://localhost:8000/Colheitadeira/

# Verificar console do navegador (F12)
# Deve mostrar "API online" no rodapé da sidebar
```

### Gráficos não aparecem
```bash
# Verificar se há dados de telemetria
curl http://localhost:8000/api/telemetria/

# Se vazio, enviar dados de teste (ver Cenário 1 acima)
```

### MQTT não recebe mensagens
```bash
# Verificar se o broker está rodando
ps aux | grep mosquitto

# Testar conexão
mosquitto_sub -h localhost -p 1883 -t "fieldnode/#"

# Enviar mensagem de teste
mosquitto_pub -h localhost -p 1883 -t "fieldnode/teste" -m "hello"
```

### IA não mostra análise
```bash
# Verificar se há leituras suficientes (mínimo 10 por máquina)
curl http://localhost:8000/api/telemetria/ | grep -c "maquina_id"

# Forçar atualização da IA (aguardar 30s ou recarregar página)
```

---

## 📱 Contatos de Emergência

**Vinícius Morales**: viniciusmorales09@gmail.com  
**Paola Machado**: paolasesi351@gmail.com  
**Ana Caroline Furlaneto**: ana.furlaneto19@icloud.com  
**Giovana D'Angelo**: giovanamachadodangelo@gmail.com

---

## 🎯 Pontos-Chave para Destacar

1. **Offline-first**: Sistema funciona sem internet no campo
2. **Deduplicação**: UUID garante que dados não sejam duplicados
3. **Validação**: Sensores com defeito não corrompem o banco
4. **IA em tempo real**: Manutenção preditiva + detecção de anomalias
5. **Escalabilidade**: Arquitetura pronta para integração com frotas existentes

---

## ✅ Checklist Final (30 min antes)

- [ ] Laptop carregado (bateria + carregador)
- [ ] Backup do projeto em pendrive
- [ ] Slides/apresentação prontos
- [ ] Servidor Django rodando
- [ ] Dashboard aberto e funcionando
- [ ] Dados de demonstração carregados
- [ ] Água e calma 😊

---

**BOA SORTE NA APRESENTAÇÃO! 🚀**

Vocês construíram algo real, defensável e com potencial de mercado.  
Confiem no trabalho de vocês.

— Equipe FieldNode
