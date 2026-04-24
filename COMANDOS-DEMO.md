# 🎬 Comandos para Demonstração — FieldNode

**Use este arquivo durante a apresentação para copiar e colar comandos rapidamente**

---

## 🚀 INICIAR O SISTEMA

### Opção 1: Automático (RECOMENDADO)
```bash
iniciar.bat
```

### Opção 2: Manual
```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Frontend (em nova janela)
cd frontend
python -m http.server 5500
```

---

## 📊 POPULAR DADOS DE DEMONSTRAÇÃO

```bash
python simular_dados.py
```

---

## 🧪 CENÁRIOS DE TESTE PARA A BANCA

### Cenário 1: Operação Normal ✅
```bash
curl -X POST http://localhost:8000/api/telemetria/ -H "Content-Type: application/json" -d "{\"id\":\"demo-normal-001\",\"maquina_id\":\"CASE-TC5000-01\",\"temperatura\":72.5,\"vibracao\":0.35,\"rpm\":1850,\"timestamp\":\"2024-04-17T14:00:00Z\"}"
```

**Resultado esperado**: Status 201, máquina aparece como NORMAL no dashboard

---

### Cenário 2: Alerta de Atenção ⚠️
```bash
curl -X POST http://localhost:8000/api/telemetria/ -H "Content-Type: application/json" -d "{\"id\":\"demo-atencao-001\",\"maquina_id\":\"CASE-TC5070-01\",\"temperatura\":78.5,\"vibracao\":0.55,\"rpm\":1750,\"timestamp\":\"2024-04-17T14:05:00Z\"}"
```

**Resultado esperado**: Status 201, máquina aparece como ATENÇÃO (amarelo)

---

### Cenário 3: Alerta Crítico 🔴
```bash
curl -X POST http://localhost:8000/api/telemetria/ -H "Content-Type: application/json" -d "{\"id\":\"demo-critico-001\",\"maquina_id\":\"NH-CR9000-01\",\"temperatura\":88.5,\"vibracao\":0.85,\"rpm\":1200,\"timestamp\":\"2024-04-17T14:10:00Z\"}"
```

**Resultado esperado**: Status 201, máquina aparece como CRÍTICO (vermelho), alerta na página Alertas

---

### Cenário 4: Deduplicação (mesmo UUID) 🔄
```bash
curl -X POST http://localhost:8000/api/telemetria/ -H "Content-Type: application/json" -d "{\"id\":\"demo-critico-001\",\"maquina_id\":\"NH-CR9000-01\",\"temperatura\":88.5,\"vibracao\":0.85,\"rpm\":1200,\"timestamp\":\"2024-04-17T14:10:00Z\"}"
```

**Resultado esperado**: Status 200, mensagem "duplicata ignorada"

---

### Cenário 5: Validação de Range (temperatura inválida) ❌
```bash
curl -X POST http://localhost:8000/api/telemetria/ -H "Content-Type: application/json" -d "{\"id\":\"demo-invalido-001\",\"maquina_id\":\"CASE-TC5000-01\",\"temperatura\":-999,\"vibracao\":0.35,\"rpm\":1850,\"timestamp\":\"2024-04-17T14:15:00Z\"}"
```

**Resultado esperado**: Status 400, erro de validação (temperatura fora do range)

---

## 🔍 CONSULTAS NA API

### Listar todas as colheitadeiras
```bash
curl http://localhost:8000/Colheitadeira/
```

### Listar todas as leituras de telemetria
```bash
curl http://localhost:8000/api/telemetria/
```

### Últimas leituras por máquina
```bash
curl http://localhost:8000/api/leituras/ultimas/
```

### Análise de manutenção preditiva
```bash
curl "http://localhost:8000/api/manutencao/?maquina_id=CASE-TC5000-01"
```

### Detecção de anomalias
```bash
curl "http://localhost:8000/api/anomalias/?maquina_id=CASE-TC5000-01"
```

---

## 🧪 TESTES AUTOMATIZADOS

### Rodar todos os testes
```bash
python manage.py test api_tcc.tests
```

### Rodar teste específico
```bash
python manage.py test api_tcc.tests.test_telemetria.TelemetriaServiceTest.test_deduplicacao
```

---

## 📡 MQTT (Opcional — se tiver broker rodando)

### Iniciar broker Mosquitto
```bash
mosquitto -v
```

### Iniciar listener Django
```bash
python manage.py mqtt_listen
```

### Enviar mensagem de teste
```bash
mosquitto_pub -h localhost -p 1883 -t "fieldnode/COLH-01/leitura" -m "{\"id\":\"550e8400-e29b-41d4-a716-446655440000\",\"maquina_id\":\"COLH-01\",\"temperatura\":85.5,\"vibracao\":0.65,\"rpm\":1750,\"timestamp\":\"2024-04-17T10:00:00Z\"}"
```

---

## 🗄️ COMANDOS DO BANCO DE DADOS

### Criar banco (MySQL)
```sql
CREATE DATABASE fieldnode CHARACTER SET utf8mb4;
```

### Verificar tabelas criadas
```sql
USE fieldnode;
SHOW TABLES;
```

### Ver leituras de telemetria
```sql
SELECT * FROM api_tcc_leituratelemetria ORDER BY timestamp DESC LIMIT 10;
```

### Contar leituras por máquina
```sql
SELECT maquina_id, COUNT(*) as total 
FROM api_tcc_leituratelemetria 
GROUP BY maquina_id;
```

---

## 👤 ADMIN DJANGO

### Criar superusuário
```bash
python manage.py createsuperuser
```

**Credenciais sugeridas**:
- Username: `admin`
- Email: `admin@fieldnode.com`
- Password: `admin123`

### Acessar admin
```
http://localhost:8000/admin/
```

---

## 🌐 URLs IMPORTANTES

| Serviço | URL | Descrição |
|---------|-----|-----------|
| Dashboard | http://localhost:5500/index.html | Interface principal |
| API Root | http://localhost:8000 | Endpoints REST |
| Swagger | http://localhost:8000/swagger/ | Documentação interativa |
| Admin | http://localhost:8000/admin/ | Painel administrativo |
| Colheitadeiras | http://localhost:8000/Colheitadeira/ | Lista de máquinas |
| Telemetria | http://localhost:8000/api/telemetria/ | Endpoint de ingestão |
| Últimas Leituras | http://localhost:8000/api/leituras/ultimas/ | Status em tempo real |
| Manutenção | http://localhost:8000/api/manutencao/ | IA preditiva |
| Anomalias | http://localhost:8000/api/anomalias/ | Detecção de padrões |

---

## 🎯 SEQUÊNCIA RECOMENDADA PARA DEMONSTRAÇÃO

### 1. Mostrar o Dashboard (2 min)
```
1. Abrir http://localhost:5500/index.html
2. Apontar para os 4 cards de métricas
3. Mostrar gráfico de temperatura (4 linhas coloridas)
4. Explicar sistema de cores bicolor
5. Mostrar tabela atualizando em tempo real (aguardar 3s)
```

### 2. Demonstrar API REST (3 min)
```
1. Abrir http://localhost:8000/swagger/
2. Expandir POST /api/telemetria/
3. Clicar em "Try it out"
4. Colar JSON do Cenário 1 (operação normal)
5. Executar e mostrar resposta 201
6. Voltar ao dashboard e mostrar nova leitura
```

### 3. Demonstrar Deduplicação (1 min)
```
1. No Swagger, enviar o MESMO JSON novamente
2. Mostrar resposta 200 "duplicata ignorada"
3. Explicar: UUID garante que dados não sejam duplicados
```

### 4. Demonstrar Validação (1 min)
```
1. No Swagger, enviar JSON com temperatura -999
2. Mostrar erro 400
3. Explicar: sensor com defeito não corrompe o banco
```

### 5. Demonstrar Alertas (2 min)
```
1. Enviar JSON do Cenário 3 (crítico)
2. Ir para página "Alertas" no dashboard
3. Mostrar alerta vermelho para NH-CR9000-01
4. Explicar regras de negócio (temp > 85°C = crítico)
```

### 6. Demonstrar IA (3 min)
```
1. Voltar ao dashboard
2. Rolar até card "Análise de IA"
3. Mostrar previsão de manutenção para cada máquina
4. Explicar Random Forest + Isolation Forest
5. Mostrar probabilidade de falha e fatores principais
```

### 7. Demonstrar Busca (1 min)
```
1. Clicar no campo de busca na tabela
2. Digitar "CASE"
3. Mostrar sugestões em tempo real
4. Selecionar uma máquina
5. Mostrar popup com histórico detalhado
```

---

## 💡 DICAS PARA A APRESENTAÇÃO

### Antes de Começar
- [ ] Feche todas as abas do navegador (exceto dashboard)
- [ ] Aumente o zoom do navegador para 125% (melhor visibilidade)
- [ ] Tenha o Swagger aberto em outra aba
- [ ] Tenha este arquivo aberto para copiar comandos
- [ ] Teste todos os cenários 1 vez antes

### Durante a Apresentação
- [ ] Fale devagar e explique cada passo
- [ ] Aponte com o mouse para os elementos na tela
- [ ] Aguarde 3 segundos após enviar dados (polling)
- [ ] Se algo der errado, use os dados já simulados
- [ ] Destaque o sistema de cores bicolor (diferencial)

### Pontos-Chave para Mencionar
- ✅ Offline-first: funciona sem internet no campo
- ✅ Deduplicação: UUID garante integridade
- ✅ Validação: sensores com defeito não corrompem dados
- ✅ IA em tempo real: manutenção preditiva + anomalias
- ✅ Escalável: pronto para integração com frotas existentes

---

## 🆘 PLANO B (se algo der errado)

### Se a API não responder
```bash
# Reinicie o Django
Ctrl+C no terminal do Django
python manage.py runserver
```

### Se o dashboard não atualizar
```bash
# Force refresh no navegador
Ctrl+F5
```

### Se não houver dados
```bash
# Repopule o banco
python simular_dados.py
```

### Se o MySQL não conectar
```bash
# Verifique se está rodando
mysql -u root -p

# Se não estiver, inicie o serviço
net start MySQL80  # Windows
sudo service mysql start  # Linux
```

---

## 📞 CONTATOS DE EMERGÊNCIA

**Vinícius Morales**: viniciusmorales09@gmail.com  
**Paola Machado**: paolasesi351@gmail.com  
**Ana Caroline Furlaneto**: ana.furlaneto19@icloud.com  
**Giovana D'Angelo**: giovanamachadodangelo@gmail.com

---

**🚀 BOA SORTE NA APRESENTAÇÃO!**

*Vocês construíram algo real e defensável. Confiem no trabalho de vocês.*
