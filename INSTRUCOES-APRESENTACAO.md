# 🎯 Instruções para Apresentação — FieldNode

## ⚡ INÍCIO RÁPIDO (3 minutos antes da banca)

### 1. Iniciar o Backend
```bash
# No terminal, na pasta do projeto:
python manage.py runserver
```

**Aguarde ver:** `Starting development server at http://127.0.0.1:8000/`

### 2. Abrir o Dashboard Funcional
No navegador, acesse:
```
http://127.0.0.1:8000/frontend/dashboard.html
```

**O que você deve ver:**
- ✅ Tabela de status de máquinas (pode estar vazia se não houver dados)
- ✅ Badge MQTT no topo (mostrando "Conectando..." ou "Offline")
- ✅ Carrossel funcionando (botões Anterior/Próximo)
- ✅ Busca de máquinas funcionando

### 3. Popular com Dados de Demonstração
```bash
# Em outro terminal:
python scripts/demo_pane.py
```

**O que acontece:**
- Simula 3 máquinas enviando telemetria via MQTT
- Dashboard atualiza automaticamente a cada 3 segundos
- Você verá temperatura, vibração, RPM em tempo real

---

## 📂 Estrutura de Páginas

| URL | Propósito | Status |
|-----|-----------|--------|
| `/frontend/` ou `/frontend/index.html` | Landing page do produto (apresentação visual) | ✅ Pronta |
| `/frontend/dashboard.html` | **Dashboard operacional** (demonstração funcional) | ✅ Pronta |
| `/frontend/maquina.html?id=1` | Detalhes de uma máquina específica | ✅ Pronta |
| `/swagger/` | Documentação da API | ✅ Pronta |

---

## 🎬 Roteiro de Apresentação Sugerido

### 1. Contexto do Problema (2 min)
**Mostrar:** Landing page (`/frontend/`)
- Explique o problema: 40% das operações sem sinal
- Mostre a seção "O Problema" com o relato de campo
- Destaque o prejuízo: R$ 12k por parada

### 2. Arquitetura da Solução (3 min)
**Mostrar:** Ainda na landing page, seção "Arquitetura"
- Pipeline: ESP32 → ESP-NOW → Gateway → Django
- Offline-first: funciona sem internet
- Sincronização automática quando conecta

### 3. Demonstração Técnica (5 min)
**Mostrar:** Dashboard (`/frontend/dashboard.html`)

**Passo a passo:**
1. Abra o dashboard (deve estar vazio)
2. Inicie o simulador: `python scripts/demo_pane.py`
3. Aguarde 3-5 segundos
4. **Mostre:**
   - Badge MQTT mudando para "Conectado"
   - Tabela populando com 3 máquinas
   - Valores atualizando em tempo real
   - Clique em uma máquina para abrir o popup
   - Navegue para detalhes completos

### 4. Endpoints da API (2 min)
**Mostrar:** Swagger (`/swagger/`)
- `/api/telemetria/` — ingestão de dados
- `/api/leituras/ultimas/` — última leitura de cada máquina
- `/api/anomalias/` — detecção de anomalias (IA)
- `/api/manutencao/` — previsão de manutenção (IA)

### 5. Resiliência e Qualidade (3 min)
**Mostrar:** Código ou documentação
- Deduplicação por UUID (evita dados duplicados)
- Dead-letter queue (TelemetriaInvalida)
- Testes automatizados
- SQL otimizado (evita N+1 queries)

---

## 🔧 Troubleshooting Rápido

### Dashboard não carrega dados
```bash
# Verifique se o servidor está rodando:
curl http://127.0.0.1:8000/api/leituras/ultimas/

# Deve retornar [] (vazio) ou dados JSON
```

### Badge MQTT sempre offline
**Normal se não houver simulador rodando.**
- Inicie `python scripts/demo_pane.py`
- Aguarde 10 segundos
- Badge deve mudar para "Conectado"

### Erro 404 ao acessar dashboard
**Verifique a URL:**
- ✅ Correto: `http://127.0.0.1:8000/frontend/dashboard.html`
- ❌ Errado: `http://localhost:8000/dashboard.html`

### Simulador não envia dados
```bash
# Verifique se o broker MQTT está acessível:
# O demo_pane.py usa broker.emqx.io (público)
# Se houver firewall, pode bloquear porta 1883
```

---

## 📊 Métricas para Mencionar na Banca

Execute durante a apresentação:
```bash
curl http://127.0.0.1:8000/api/metricas/
```

**Retorna:**
```json
{
  "leituras_validas": 247,
  "leituras_invalidas": 3,
  "taxa_rejeicao_pct": 1.2,
  "maquinas_ativas": 3
}
```

**Use para demonstrar:**
- Sistema está processando dados
- Validação está funcionando (rejeita payloads inválidos)
- Múltiplas máquinas sendo monitoradas

---

## 🎯 Perguntas Esperadas da Banca

### "Como funciona sem internet?"
**Resposta:** O Gateway ESP32 armazena até 30 dias de leituras localmente e serve um dashboard via Wi-Fi direto. Quando a máquina volta à sede e encontra internet, sincroniza automaticamente com o backend Django usando deduplicação por UUID.

### "E se o mesmo dado for enviado duas vezes?"
**Resposta:** Cada leitura tem um UUID único. O backend verifica se já existe antes de inserir. Se for duplicata, retorna 200 OK mas não cria registro novo. Isso garante idempotência.

### "Como a IA detecta anomalias?"
**Resposta:** Usamos Isolation Forest (scikit-learn) que identifica leituras fora do padrão sem precisar de dados rotulados. Para manutenção preditiva, usamos Random Forest treinado com labels sintéticos baseados em limites operacionais documentados.

### "Por que não usar JWT?"
**Resposta:** ESP32 tem memória flash limitada. Biblioteca JWT consome ~30% da flash disponível. API key simples via header é o equilíbrio correto entre segurança e limitação de hardware para protótipo. Em produção, migraríamos para AES-128 + rotação de chaves.

### "Qual a latência do alerta?"
**Resposta:** Menos de 3 segundos do sensor ao dashboard local. O ESP32 lê sensores a cada 2 segundos, transmite via ESP-NOW (latência < 10ms) e o Gateway atualiza o dashboard imediatamente.

---

## ✅ Checklist Pré-Apresentação

- [ ] Backend rodando (`python manage.py runserver`)
- [ ] Dashboard abre sem erros (`/frontend/dashboard.html`)
- [ ] Simulador testado (`python scripts/demo_pane.py`)
- [ ] Swagger acessível (`/swagger/`)
- [ ] Navegador em tela cheia (F11)
- [ ] Zoom do navegador em 100% (Ctrl+0)
- [ ] Fechar abas desnecessárias
- [ ] Testar clique em máquina → popup abre
- [ ] Testar navegação para detalhes → maquina.html carrega

---

## 🚨 Plano B (Se algo quebrar)

### Se o dashboard não funcionar:
1. Mostre a landing page (`/frontend/`)
2. Mostre o Swagger (`/swagger/`)
3. Faça requisições via `curl` no terminal:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/telemetria/ \
     -H "Content-Type: application/json" \
     -H "X-API-Key: fieldnode-demo-2024" \
     -d '{"id":"test-123","maquina_id":"CASE-01","temperatura":78,"vibracao":0.4,"rpm":1850,"timestamp":"2024-01-01T12:00:00Z"}'
   
   curl http://127.0.0.1:8000/api/leituras/ultimas/
   ```

### Se o simulador não funcionar:
- Use dados pré-populados: `python scripts/popular_banco.py`
- Mostre os testes: `python manage.py test`

---

## 📝 Notas Finais

- **Foco no dashboard.html**, não na index.html (landing page é bonita mas não demonstra funcionalidade)
- **Deixe o simulador rodando durante toda a apresentação** para mostrar atualização em tempo real
- **Tenha o terminal visível** para mostrar logs do Django (transparência técnica)
- **Não se desculpe por features faltando** — o que está pronto é sólido e defensável

**Boa sorte! 🚜💚**
