# ⚡ INÍCIO RÁPIDO — FieldNode

**Cole este arquivo na parede ou mantenha aberto durante a apresentação.**

---

## 🚀 PASSO 1: INICIAR BACKEND

```bash
python manage.py runserver
```

**Aguarde ver:**
```
Starting development server at http://127.0.0.1:8000/
```

✅ **Backend rodando!**

---

## 🎮 PASSO 2: INICIAR SIMULADOR

**Em outro terminal:**

```bash
python scripts/demo_pane.py
```

**Aguarde ver:**
```
[MQTT] Conectado ao broker
[MQTT] Publicado: CASE-TC5000-01 | temp=78.5°C
```

✅ **Simulador enviando dados!**

---

## 🌐 PASSO 3: ABRIR DASHBOARD

**No navegador:**

```
http://127.0.0.1:8000/frontend/dashboard.html
```

**Aguarde 5 segundos → dados aparecem!**

✅ **Dashboard funcionando!**

---

## 📊 URLS PRINCIPAIS

### Dashboard Operacional (USE ESTE)
```
http://127.0.0.1:8000/frontend/dashboard.html
```

### Landing Page
```
http://127.0.0.1:8000/frontend/
```

### Documentação da API
```
http://127.0.0.1:8000/swagger/
```

### Métricas do Sistema
```
http://127.0.0.1:8000/api/metricas/
```

---

## 🔧 TESTE RÁPIDO

**Verifique se tudo está funcionando:**

```bash
curl http://127.0.0.1:8000/api/metricas/
```

**Deve retornar JSON com métricas.**

✅ **Sistema funcionando!**

---

## 🚨 SE ALGO QUEBRAR

### Dashboard vazio?
```bash
python scripts/demo_pane.py
```
Aguarde 10 segundos e recarregue (F5)

### Erro 404?
Verifique a URL:
```
http://127.0.0.1:8000/frontend/dashboard.html
```
(não esqueça `/frontend/`)

### Backend não responde?
```bash
python manage.py runserver
```

---

## 💬 RESPOSTAS RÁPIDAS

**"Como funciona sem internet?"**
> Gateway armazena 30 dias localmente, serve dashboard via Wi-Fi direto.

**"E se enviar duplicado?"**
> UUID único. Backend verifica antes de inserir. Idempotente.

**"Como a IA funciona?"**
> Isolation Forest (anomalias) + Random Forest (manutenção).

**"Por que não JWT?"**
> ESP32 tem memória limitada. API key é equilíbrio correto.

**"Qual a latência?"**
> < 3s do sensor ao dashboard local.

---

## ✅ CHECKLIST RÁPIDO

Antes de apresentar:

- [ ] Backend rodando
- [ ] Simulador rodando
- [ ] Dashboard abre sem erros
- [ ] Dados aparecem após 5s
- [ ] Navegador em tela cheia (F11)
- [ ] Zoom 100% (Ctrl+0)

---

## 🎯 ROTEIRO (15 min)

1. **Problema** (2 min) → Landing page
2. **Solução** (3 min) → Landing page (arquitetura)
3. **Demo** (5 min) → Dashboard + simulador
4. **API** (2 min) → Swagger
5. **Qualidade** (3 min) → Código/docs

---

## 🏆 LEMBRE-SE

- ✅ Fale devagar
- ✅ Olhe para a banca
- ✅ Respire fundo
- ✅ Seja honesto
- ✅ Destaque decisões técnicas

**BOA SORTE! 🚜💚**

---

**IMPRIMA ESTE ARQUIVO EM FONTE GRANDE (18pt+)**
