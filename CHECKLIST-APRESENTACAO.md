# ✅ CHECKLIST DE APRESENTAÇÃO — FieldNode

**Imprima este arquivo e use durante a preparação e apresentação.**

---

## 📋 PRÉ-APRESENTAÇÃO (30 min antes)

### Setup Técnico
- [ ] Notebook carregado e conectado
- [ ] Projetor testado e funcionando
- [ ] Resolução de tela ajustada (1920x1080 recomendado)
- [ ] Zoom do navegador em 100% (Ctrl+0)
- [ ] Navegador em tela cheia (F11)
- [ ] Fechar abas desnecessárias
- [ ] Desativar notificações (Windows: Win+A → Foco Assistido)

### Arquivos Abertos
- [ ] `CHEAT-SHEET-APRESENTACAO.md` (consulta rápida)
- [ ] `TROUBLESHOOTING.md` (emergências)
- [ ] Terminal 1 pronto (para `python manage.py runserver`)
- [ ] Terminal 2 pronto (para `python scripts/demo_pane.py`)
- [ ] Navegador com abas:
  - [ ] `http://127.0.0.1:8000/frontend/dashboard.html`
  - [ ] `http://127.0.0.1:8000/frontend/`
  - [ ] `http://127.0.0.1:8000/swagger/`

### Teste de Funcionamento
- [ ] Backend iniciado: `python manage.py runserver`
- [ ] API responde: `curl http://127.0.0.1:8000/api/metricas/`
- [ ] Dashboard carrega sem erros
- [ ] Simulador testado: `python scripts/demo_pane.py` (10s)
- [ ] Dados aparecem no dashboard após reload

---

## 🎬 DURANTE A APRESENTAÇÃO (15 min)

### 1. Introdução (1 min)
- [ ] Apresentar equipe
- [ ] Apresentar projeto: "FieldNode — Telemetria Offline-First"
- [ ] Contextualizar: TCC Técnico SENAI 2026

### 2. Problema (2 min)
**Mostrar:** Landing page (`/frontend/`)
- [ ] Explicar: 40% das operações sem sinal
- [ ] Destacar: R$ 12k de prejuízo por parada
- [ ] Mostrar seção "O Problema" com relato de campo

### 3. Solução (3 min)
**Mostrar:** Landing page (seção Arquitetura)
- [ ] Explicar pipeline: ESP32 → ESP-NOW → Gateway → Django
- [ ] Destacar: Offline-first por design
- [ ] Mencionar: Buffer 30 dias + sincronização automática

### 4. Demonstração Técnica (5 min)
**Mostrar:** Dashboard (`/frontend/dashboard.html`)

**Checklist de demo:**
- [ ] Dashboard aberto (pode estar vazio)
- [ ] Iniciar simulador: `python scripts/demo_pane.py`
- [ ] Aguardar 5 segundos
- [ ] Apontar: Badge MQTT mudando para "Conectado"
- [ ] Apontar: Tabela populando com 3 máquinas
- [ ] Apontar: Valores atualizando a cada 3 segundos
- [ ] Clicar em uma máquina → popup abre
- [ ] Mostrar dados no popup
- [ ] Clicar "Ver Detalhes" → maquina.html carrega
- [ ] Mostrar gráficos Chart.js

### 5. API e Documentação (2 min)
**Mostrar:** Swagger (`/swagger/`)
- [ ] Abrir Swagger
- [ ] Mostrar endpoints principais:
  - [ ] `/api/telemetria/` (ingestão)
  - [ ] `/api/leituras/ultimas/` (status)
  - [ ] `/api/anomalias/` (IA)
  - [ ] `/api/manutencao/` (IA)
- [ ] Expandir um endpoint e mostrar schema

### 6. Qualidade e Resiliência (2 min)
**Mostrar:** Código ou documentação
- [ ] Mencionar: Deduplicação UUID
- [ ] Mencionar: Dead-letter queue (TelemetriaInvalida)
- [ ] Mencionar: Testes automatizados
- [ ] Mencionar: SQL otimizado (evita N+1)
- [ ] Opcional: Mostrar métricas (`/api/metricas/`)

---

## 💬 PERGUNTAS DA BANCA

### Preparadas
- [ ] "Como funciona sem internet?"
  - **Resposta:** Gateway armazena 30 dias localmente, serve dashboard via Wi-Fi direto. Sincroniza quando conecta.

- [ ] "E se enviar duplicado?"
  - **Resposta:** UUID único por leitura. Backend verifica antes de inserir. Idempotente.

- [ ] "Como a IA funciona?"
  - **Resposta:** Isolation Forest (anomalias) + Random Forest (manutenção). Labels sintéticos baseados em limites operacionais.

- [ ] "Por que não JWT?"
  - **Resposta:** ESP32 tem memória limitada. JWT consome 30% da flash. API key é equilíbrio correto para protótipo.

- [ ] "Qual a latência?"
  - **Resposta:** < 3s do sensor ao dashboard local. ESP-NOW tem latência < 10ms.

### Imprevistas
- [ ] Anotar pergunta
- [ ] Respirar fundo
- [ ] Responder honestamente
- [ ] Se não souber: "Boa pergunta, precisaríamos investigar mais a fundo"

---

## 🚨 PLANO B (Se algo quebrar)

### Se dashboard não funcionar:
- [ ] Mostrar landing page (`/frontend/`)
- [ ] Mostrar Swagger (`/swagger/`)
- [ ] Fazer demo via terminal:
  ```bash
  curl -X POST http://127.0.0.1:8000/api/telemetria/ \
    -H "Content-Type: application/json" \
    -H "X-API-Key: fieldnode-demo-2024" \
    -d '{"id":"demo-1","maquina_id":"CASE-01","temperatura":78,"vibracao":0.4,"rpm":1850,"timestamp":"2024-01-01T12:00:00Z"}'
  
  curl http://127.0.0.1:8000/api/leituras/ultimas/
  ```

### Se simulador não funcionar:
- [ ] Usar dados pré-populados: `python scripts/popular_banco.py`
- [ ] Mostrar testes: `python manage.py test`

### Se tudo falhar:
- [ ] Mostrar código-fonte
- [ ] Explicar arquitetura verbalmente
- [ ] Mostrar documentação técnica
- [ ] Destacar decisões técnicas conscientes

---

## 📊 MÉTRICAS PARA MENCIONAR

### Durante a apresentação, mencione:
- [ ] Taxa de amostragem: 1 leitura / 2 segundos
- [ ] Latência do alerta: < 3 segundos
- [ ] Alcance ESP-NOW: 50-500m
- [ ] Capacidade de buffer: 30 dias
- [ ] Acurácia IA (meta): > 85%

### Se perguntarem sobre números:
```bash
curl http://127.0.0.1:8000/api/metricas/
```
Retorna: leituras válidas, inválidas, taxa de rejeição, máquinas ativas.

---

## ✅ PÓS-APRESENTAÇÃO

### Imediatamente após:
- [ ] Agradecer a banca
- [ ] Anotar perguntas que não soube responder
- [ ] Anotar sugestões da banca

### Depois:
- [ ] Revisar feedback
- [ ] Atualizar documentação se necessário
- [ ] Comemorar! 🎉

---

## 🎯 LEMBRETES IMPORTANTES

### Durante a apresentação:
- ✅ Fale devagar e com clareza
- ✅ Olhe para a banca, não só para a tela
- ✅ Respire fundo antes de responder perguntas
- ✅ Seja honesto sobre limitações
- ✅ Destaque decisões técnicas conscientes

### Não faça:
- ❌ Não se desculpe por features faltando
- ❌ Não invente números ou funcionalidades
- ❌ Não entre em pânico se algo quebrar
- ❌ Não fale mal de tecnologias concorrentes

---

## 📞 CONTATOS DE EMERGÊNCIA

**Suporte Técnico:**
- Documentação: `TROUBLESHOOTING.md`
- Cheat sheet: `CHEAT-SHEET-APRESENTACAO.md`

**Comandos de Emergência:**
```bash
# Reset completo:
rm db.sqlite3
python manage.py migrate
python manage.py runserver

# Teste rápido:
curl http://127.0.0.1:8000/api/metricas/
```

---

## 🏆 MENSAGEM FINAL

**Vocês construíram algo sólido.**

- ✅ Backend robusto
- ✅ Frontend funcional
- ✅ Arquitetura defensável
- ✅ IA implementada
- ✅ Documentação completa

**Apresentem com confiança. Boa sorte! 🚜💚**

---

**IMPRIMA ESTE CHECKLIST E MARQUE CADA ITEM DURANTE A PREPARAÇÃO**

---

**Arquivo:** `CHECKLIST-APRESENTACAO.md`  
**Última atualização:** Janeiro 2024  
**Versão:** 1.0
