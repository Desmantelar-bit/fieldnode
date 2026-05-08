# 🔧 Troubleshooting — FieldNode

## 🚨 Diagnóstico Rápido (30 segundos)

### 1. Backend está rodando?
```bash
curl http://127.0.0.1:8000/api/metricas/
```

**✅ Esperado:**
```json
{
  "leituras_validas": 0,
  "leituras_invalidas": 0,
  "taxa_rejeicao_pct": 0.0,
  "maquinas_ativas": 0
}
```

**❌ Se falhar:**
```bash
# Inicie o servidor:
python manage.py runserver
```

---

### 2. Dashboard carrega?
Abra no navegador:
```
http://127.0.0.1:8000/frontend/dashboard.html
```

**✅ Esperado:** Página carrega, mostra tabela (pode estar vazia)

**❌ Se der 404:**
- Verifique a URL (deve ter `/frontend/` no caminho)
- Verifique se o servidor está rodando

**❌ Se carregar mas não mostrar dados:**
- Normal se não houver simulador rodando
- Inicie: `python scripts/demo_pane.py`

---

### 3. Simulador está enviando dados?
```bash
# Terminal separado:
python scripts/demo_pane.py
```

**✅ Esperado:** Mensagens no console:
```
[MQTT] Conectado ao broker
[MQTT] Publicado: CASE-TC5000-01 | temp=78.5°C
[MQTT] Publicado: NH-CR9000-01 | temp=72.3°C
...
```

**❌ Se falhar:**
- Verifique conexão com internet (usa broker público)
- Tente: `pip install paho-mqtt`

---

## 🔍 Diagnósticos Específicos

### Dashboard mostra "Nenhuma leitura recebida"

**Causa:** Banco de dados vazio

**Solução:**
```bash
# Opção 1: Simulador MQTT (recomendado)
python scripts/demo_pane.py

# Opção 2: Popular banco diretamente
python scripts/popular_banco.py

# Opção 3: Enviar leitura manual via API
curl -X POST http://127.0.0.1:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: fieldnode-demo-2024" \
  -d '{
    "id": "test-uuid-001",
    "maquina_id": "CASE-TC5000-01",
    "temperatura": 78.5,
    "vibracao": 0.42,
    "rpm": 1850,
    "timestamp": "2024-01-15T14:30:00Z"
  }'
```

---

### Badge MQTT sempre "Offline"

**Causa:** Nenhuma leitura recebida nos últimos 10 segundos

**Solução:**
```bash
# 1. Verifique se há leituras no banco:
curl http://127.0.0.1:8000/api/leituras/ultimas/

# 2. Se vazio, inicie o simulador:
python scripts/demo_pane.py

# 3. Aguarde 10 segundos e recarregue o dashboard
```

---

### Erro "API key inválida"

**Causa:** Header `X-API-Key` ausente ou incorreto

**Solução:**
```bash
# Verifique a chave no .env:
cat .env | grep FIELDNODE_API_KEY

# Deve ser: FIELDNODE_API_KEY=fieldnode-demo-2024

# Teste com curl:
curl -X POST http://127.0.0.1:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: fieldnode-demo-2024" \
  -d '{"id":"test-1","maquina_id":"TEST-01","temperatura":75,"vibracao":0.3,"rpm":1800,"timestamp":"2024-01-01T12:00:00Z"}'
```

---

### Erro "CORS policy"

**Causa:** Navegador bloqueando requisições cross-origin

**Solução:**
```bash
# Verifique settings.py:
# CORS_ALLOW_ALL_ORIGINS = True (em DEBUG)

# Se ainda falhar, abra o dashboard pela URL correta:
http://127.0.0.1:8000/frontend/dashboard.html
# (não use file:// ou localhost:5500)
```

---

### Popup de máquina não abre

**Causa:** JavaScript não carregou ou erro no console

**Solução:**
1. Abra DevTools (F12)
2. Vá para Console
3. Procure erros em vermelho
4. Verifique se `config.js`, `api.js`, `colors.js`, `status.js` carregaram

**Se houver erro "apiFetch is not defined":**
```bash
# Verifique se config.js está carregando:
curl http://127.0.0.1:8000/frontend/config.js

# Deve retornar:
# const API = 'http://127.0.0.1:8000';
```

---

### Gráficos não aparecem em maquina.html

**Causa:** Chart.js não carregou

**Solução:**
1. Verifique conexão com internet (Chart.js vem de CDN)
2. Abra DevTools → Network
3. Procure por `chart.umd.js` — deve estar 200 OK

**Se offline:**
```bash
# Baixe Chart.js localmente:
# (não implementado no protótipo, mas seria o próximo passo)
```

---

## 🧪 Testes de Sanidade

### Teste 1: API responde
```bash
curl http://127.0.0.1:8000/api/metricas/
```
**Esperado:** JSON com métricas

---

### Teste 2: Ingestão funciona
```bash
curl -X POST http://127.0.0.1:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: fieldnode-demo-2024" \
  -d '{
    "id": "sanity-test-001",
    "maquina_id": "TEST-SANITY-01",
    "temperatura": 70,
    "vibracao": 0.3,
    "rpm": 1800,
    "timestamp": "2024-01-15T12:00:00Z"
  }'
```
**Esperado:** `{"status":"ok","id":"sanity-test-001"}`

---

### Teste 3: Última leitura retorna dados
```bash
curl http://127.0.0.1:8000/api/leituras/ultimas/
```
**Esperado:** Array com pelo menos 1 máquina

---

### Teste 4: Deduplicação funciona
```bash
# Envie a mesma leitura duas vezes:
curl -X POST http://127.0.0.1:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: fieldnode-demo-2024" \
  -d '{
    "id": "dedup-test-001",
    "maquina_id": "TEST-DEDUP-01",
    "temperatura": 75,
    "vibracao": 0.4,
    "rpm": 1850,
    "timestamp": "2024-01-15T12:00:00Z"
  }'

# Segunda vez:
curl -X POST http://127.0.0.1:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: fieldnode-demo-2024" \
  -d '{
    "id": "dedup-test-001",
    "maquina_id": "TEST-DEDUP-01",
    "temperatura": 75,
    "vibracao": 0.4,
    "rpm": 1850,
    "timestamp": "2024-01-15T12:00:00Z"
  }'
```
**Esperado:** Segunda requisição retorna `{"status":"duplicata ignorada"}`

---

## 🔄 Reset Completo (Se tudo falhar)

```bash
# 1. Pare o servidor (Ctrl+C)

# 2. Limpe o banco de dados:
rm db.sqlite3

# 3. Recrie as tabelas:
python manage.py migrate

# 4. Inicie o servidor:
python manage.py runserver

# 5. Em outro terminal, inicie o simulador:
python scripts/demo_pane.py

# 6. Abra o dashboard:
# http://127.0.0.1:8000/frontend/dashboard.html
```

---

## 📊 Verificação de Estado

### Quantas leituras no banco?
```bash
# Via API:
curl http://127.0.0.1:8000/api/metricas/

# Via SQLite direto:
sqlite3 db.sqlite3 "SELECT COUNT(*) FROM api_tcc_leituratelemetria;"
```

---

### Quais máquinas estão ativas?
```bash
curl http://127.0.0.1:8000/api/leituras/ultimas/ | python -m json.tool
```

---

### Última leitura de uma máquina específica?
```bash
curl "http://127.0.0.1:8000/api/leituras/ultimas/?maquina_id=CASE-TC5000-01" | python -m json.tool
```

---

## 🆘 Suporte de Emergência

### Se nada funcionar durante a apresentação:

1. **Mostre a landing page:**
   ```
   http://127.0.0.1:8000/frontend/
   ```
   (Funciona sempre, não depende de dados)

2. **Mostre o Swagger:**
   ```
   http://127.0.0.1:8000/swagger/
   ```
   (Documentação sempre disponível)

3. **Faça demo via terminal:**
   ```bash
   # Envie leitura:
   curl -X POST http://127.0.0.1:8000/api/telemetria/ \
     -H "Content-Type: application/json" \
     -H "X-API-Key: fieldnode-demo-2024" \
     -d '{"id":"demo-1","maquina_id":"CASE-01","temperatura":78,"vibracao":0.4,"rpm":1850,"timestamp":"2024-01-01T12:00:00Z"}'
   
   # Consulte:
   curl http://127.0.0.1:8000/api/leituras/ultimas/
   ```

4. **Mostre os testes:**
   ```bash
   python manage.py test
   ```
   (Demonstra qualidade do código)

---

## ✅ Checklist de Funcionamento

Antes da apresentação, execute:

```bash
# 1. Backend responde?
curl http://127.0.0.1:8000/api/metricas/

# 2. Dashboard carrega?
# Abra: http://127.0.0.1:8000/frontend/dashboard.html

# 3. Simulador funciona?
python scripts/demo_pane.py
# (Ctrl+C para parar após 10s)

# 4. Dados aparecem no dashboard?
# Recarregue o dashboard (F5)
```

**Se todos os 4 passos funcionarem: ✅ PRONTO PARA APRESENTAR**

---

**Última atualização:** 2024-01-XX  
**Mantenha este arquivo aberto durante a apresentação para consulta rápida.**
