# ⚡ SOLUÇÃO RÁPIDA — Cannot GET /index.html

**Seu problema**: Mudou o WiFi e agora o dashboard não abre

---

## 🎯 SOLUÇÃO EM 3 PASSOS

### 1️⃣ Pare tudo e limpe
```bash
# Mate todos os processos Python
taskkill /F /IM python.exe

# Feche todos os terminais
```

### 2️⃣ Execute o diagnóstico
```bash
# Abra um terminal NOVO
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC
.venv\Scripts\activate
python diagnostico.py
```

**O que vai acontecer**: O script vai identificar automaticamente o problema.

### 3️⃣ Inicie novamente
```bash
python iniciar.py
```

**Pronto!** O navegador vai abrir em `http://127.0.0.1:5500/index.html`

---

## 🔧 SE AINDA NÃO FUNCIONAR

### Teste Manual (para ver o erro exato)

```bash
# 1. Pare tudo
taskkill /F /IM python.exe

# 2. Navegue até a pasta
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC

# 3. Ative o virtualenv
.venv\Scripts\activate

# 4. Inicie o Django
python manage.py runserver

# 5. Em OUTRO terminal, inicie o frontend
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC\frontend
python -m http.server 5500

# 6. Abra no navegador
start http://127.0.0.1:5500/index.html
```

Se aparecer algum erro, copie e cole aqui.

---

## 💡 POR QUE MUDOU PARA 127.0.0.1?

**Antes**: `http://localhost:5500/index.html`  
**Agora**: `http://127.0.0.1:5500/index.html`

**Motivo**: 
- `localhost` precisa de resolução DNS (pode ser lento ou falhar)
- `127.0.0.1` é direto, sem DNS (mais rápido e confiável)

---

## 🚀 MELHORIAS APLICADAS

1. ✅ `iniciar.py` agora usa `127.0.0.1` em vez de `localhost`
2. ✅ `iniciar.bat` também atualizado
3. ✅ Criado `diagnostico.py` para identificar problemas automaticamente
4. ✅ Criado `SOLUCAO-PROBLEMAS.md` com guia completo

---

## 📊 TESTE RÁPIDO

Execute este comando para verificar se o servidor está funcionando:

```bash
# Windows (PowerShell)
Invoke-WebRequest http://127.0.0.1:5500/index.html

# Ou abra direto no navegador
start http://127.0.0.1:5500/index.html
```

---

## 🆘 AINDA COM PROBLEMA?

Execute e me envie a saída:

```bash
python diagnostico.py
```

Isso vai mostrar exatamente onde está o problema.

---

## ✅ CHECKLIST RÁPIDO

- [ ] Matou todos os processos Python (`taskkill /F /IM python.exe`)
- [ ] Está na pasta correta (`cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC`)
- [ ] Virtualenv ativado (`.venv\Scripts\activate`)
- [ ] Executou `python diagnostico.py`
- [ ] Executou `python iniciar.py`
- [ ] Navegador abriu em `http://127.0.0.1:5500/index.html`

---

**🚀 Agora execute:**

```bash
python iniciar.py
```

**Deve funcionar perfeitamente!**
