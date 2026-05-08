# 🚀 CHEAT SHEET — Apresentação FieldNode

## ⚡ INÍCIO (2 min)
```bash
# Terminal 1:
python manage.py runserver

# Terminal 2:
python scripts/demo_pane.py

# Navegador:
http://127.0.0.1:8000/frontend/dashboard.html
```

---

## 📂 URLs Principais
| URL | O que é |
|-----|---------|
| `/frontend/dashboard.html` | **Dashboard operacional** ← USAR ESTE |
| `/frontend/` | Landing page (bonita, mas não funcional) |
| `/swagger/` | Documentação da API |

---

## 🎯 Roteiro (15 min)

### 1. Problema (2 min) — Landing page
- 40% das operações sem sinal
- R$ 12k de prejuízo por parada

### 2. Solução (3 min) — Landing page
- ESP32 → ESP-NOW → Gateway → Django
- Offline-first: funciona sem internet
- Buffer 30 dias, sincronização automática

### 3. Demo (5 min) — Dashboard
- Inicie simulador
- Mostre tabela atualizando (3s)
- Badge MQTT "Conectado"
- Clique em máquina → popup
- Navegue para detalhes

### 4. API (2 min) — Swagger
- `/api/telemetria/` — ingestão
- `/api/leituras/ultimas/` — status
- `/api/anomalias/` — IA
- `/api/manutencao/` — IA

### 5. Qualidade (3 min) — Código/Docs
- Deduplicação UUID
- Dead-letter queue
- Testes automatizados
- SQL otimizado

---

## 💬 Respostas Rápidas

**"Como funciona sem internet?"**  
Gateway ESP32 armazena 30 dias localmente, serve dashboard via Wi-Fi direto. Sincroniza quando conecta.

**"E se enviar duplicado?"**  
UUID único por leitura. Backend verifica antes de inserir. Idempotente.

**"Como a IA funciona?"**  
Isolation Forest (anomalias) + Random Forest (manutenção). Labels sintéticos baseados em limites operacionais.

**"Por que não JWT?"**  
ESP32 tem memória limitada. JWT consome 30% da flash. API key é equilíbrio correto para protótipo.

**"Qual a latência?"**  
< 3s do sensor ao dashboard local. ESP-NOW tem latência < 10ms.

---

## 🔧 Troubleshooting

**Dashboard vazio?**  
→ Inicie simulador: `python scripts/demo_pane.py`

**Badge MQTT offline?**  
→ Normal sem simulador. Aguarde 10s após iniciar.

**Erro 404?**  
→ Use URL completa: `http://127.0.0.1:8000/frontend/dashboard.html`

---

## 📊 Métricas para Mostrar
```bash
curl http://127.0.0.1:8000/api/metricas/
```
Retorna: leituras válidas, inválidas, taxa de rejeição, máquinas ativas.

---

## ✅ Checklist Pré-Banca
- [ ] Backend rodando
- [ ] Simulador rodando
- [ ] Dashboard abre sem erros
- [ ] Navegador em tela cheia (F11)
- [ ] Zoom 100% (Ctrl+0)
- [ ] Testar clique em máquina

---

## 🚨 Plano B
Se dashboard quebrar:
1. Mostre landing page (`/frontend/`)
2. Mostre Swagger (`/swagger/`)
3. Faça `curl` no terminal:
```bash
curl -X POST http://127.0.0.1:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: fieldnode-demo-2024" \
  -d '{"id":"test-1","maquina_id":"CASE-01","temperatura":78,"vibracao":0.4,"rpm":1850,"timestamp":"2024-01-01T12:00:00Z"}'

curl http://127.0.0.1:8000/api/leituras/ultimas/
```

---

## 🎯 Mensagem Final
**O projeto está sólido. Apresentem com confiança.**

- ✅ Backend robusto (dedup, validação, IA)
- ✅ Frontend funcional (dashboard + landing)
- ✅ Arquitetura defensável (offline-first)
- ✅ Documentação completa
- ✅ Testes cobrindo fluxos críticos

**Boa sorte! 🚜💚**
