# 🆘 Solução Rápida de Problemas — FieldNode

**Problema**: `Cannot GET /index.html` ou páginas demoram muito

---

## 🔍 DIAGNÓSTICO RÁPIDO

Execute primeiro:
```bash
python diagnostico.py
```

Este script vai identificar automaticamente o problema.

---

## ❌ PROBLEMA 1: Cannot GET /index.html

### Causa Provável
O servidor HTTP não está servindo da pasta correta.

### Solução Rápida
```bash
# Pare todos os processos Python
taskkill /F /IM python.exe

# Navegue até a pasta do projeto
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC

# Ative o virtualenv
.venv\Scripts\activate

# Inicie MANUALMENTE para ver os erros
cd frontend
python -m http.server 5500

# Abra no navegador
start http://127.0.0.1:5500/index.html
```

### Se ainda não funcionar
```bash
# Verifique se o arquivo existe
dir frontend\index.html

# Se não existir, você está na pasta errada!
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC
dir frontend\index.html
```

---

## 🐌 PROBLEMA 2: Páginas Demoram Muito

### Causa Provável
1. **WiFi lento/instável** — Afeta requisições à API
2. **Muitas requisições simultâneas** — Polling a cada 3s
3. **Firewall/Antivírus** — Bloqueando localhost

### Solução 1: Usar 127.0.0.1 em vez de localhost
```bash
# Em vez de:
http://localhost:5500/index.html

# Use:
http://127.0.0.1:5500/index.html
```

**Por quê?** `localhost` precisa de resolução DNS, `127.0.0.1` é direto.

### Solução 2: Desabilitar IPv6 (temporariamente)
```bash
# Abra o Prompt de Comando como Administrador
netsh interface ipv6 set global randomizeidentifiers=disabled

# Reinicie o navegador
```

### Solução 3: Adicionar exceção no Firewall
```bash
# Windows Defender Firewall
1. Abra "Firewall do Windows Defender"
2. Clique em "Permitir um aplicativo..."
3. Adicione Python (C:\...\python.exe)
4. Marque "Privado" e "Público"
```

### Solução 4: Limpar cache do navegador
```bash
# No navegador, pressione:
Ctrl + Shift + Delete

# Marque:
- Imagens e arquivos em cache
- Cookies e dados de sites

# Clique em "Limpar dados"
```

---

## 🔥 SOLUÇÃO DEFINITIVA: Servidor Alternativo

Se o `http.server` do Python está lento, use um servidor mais rápido:

### Opção A: Servir pelo Django (RECOMENDADO)

Edite `setup/urls.py` e adicione:

```python
from django.views.static import serve
from django.conf import settings
import os

urlpatterns = [
    # ... rotas existentes ...
    
    # Serve o frontend
    path('', lambda request: serve(request, 'index.html', 
         document_root=os.path.join(settings.BASE_DIR, 'frontend'))),
    path('<path:path>', lambda request, path: serve(request, path, 
         document_root=os.path.join(settings.BASE_DIR, 'frontend'))),
]
```

Depois acesse:
```
http://127.0.0.1:8000/index.html
```

### Opção B: Usar Live Server (VS Code)

Se você usa VS Code:

1. Instale a extensão "Live Server"
2. Clique com botão direito em `frontend/index.html`
3. Selecione "Open with Live Server"
4. Abre automaticamente em `http://127.0.0.1:5500`

---

## 🌐 PROBLEMA 3: WiFi Mudou e API Não Conecta

### Causa
O `config.js` pode estar com IP antigo hardcoded.

### Solução
Edite `frontend/config.js`:

```javascript
// ANTES (pode estar assim)
const API = 'http://192.168.1.100:8000';

// DEPOIS (use sempre localhost)
const API = 'http://127.0.0.1:8000';
```

Ou melhor ainda, use detecção automática:

```javascript
const API = (() => {
  // Se está no mesmo host que o Django
  if (window.location.port === '8000') {
    return window.location.origin;
  }
  // Desenvolvimento local
  return 'http://127.0.0.1:8000';
})();
```

---

## 🔧 COMANDOS DE EMERGÊNCIA

### Matar todos os processos Python
```bash
# Windows
taskkill /F /IM python.exe

# Linux/Mac
pkill -f python
```

### Verificar o que está usando uma porta
```bash
# Windows
netstat -ano | findstr :5500
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :5500
lsof -i :8000
```

### Liberar uma porta específica
```bash
# Windows (substitua PID pelo número da coluna final do netstat)
taskkill /F /PID 12345

# Linux/Mac
kill -9 12345
```

### Testar se a API está respondendo
```bash
# Windows (PowerShell)
Invoke-WebRequest http://127.0.0.1:8000/Colheitadeira/

# Windows (curl, se instalado)
curl http://127.0.0.1:8000/Colheitadeira/

# Linux/Mac
curl http://127.0.0.1:8000/Colheitadeira/
```

---

## 📊 TESTE DE VELOCIDADE

Execute este comando para medir a latência:

```bash
# Windows
ping 127.0.0.1 -n 10

# Linux/Mac
ping -c 10 127.0.0.1
```

**Resultado esperado**: < 1ms

Se estiver > 10ms, há problema no loopback do sistema.

---

## 🎯 CHECKLIST DE VERIFICAÇÃO

Execute na ordem:

- [ ] `python diagnostico.py` — Identifica o problema
- [ ] Verifique se está na pasta correta (`dir frontend\index.html`)
- [ ] Mate todos os processos Python (`taskkill /F /IM python.exe`)
- [ ] Ative o virtualenv (`.venv\Scripts\activate`)
- [ ] Inicie manualmente o frontend (`cd frontend && python -m http.server 5500`)
- [ ] Teste no navegador (`http://127.0.0.1:5500/index.html`)
- [ ] Se funcionar, use `python iniciar.py` da próxima vez

---

## 🆘 AINDA NÃO FUNCIONA?

### Teste Mínimo Viável

Crie um arquivo `teste.html` na pasta `frontend`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Teste</title>
</head>
<body>
    <h1>Funcionou!</h1>
    <p>Se você está vendo isso, o servidor está funcionando.</p>
</body>
</html>
```

Depois acesse:
```
http://127.0.0.1:5500/teste.html
```

Se **teste.html funciona** mas **index.html não**:
→ Problema no arquivo `index.html` (pode estar corrompido)

Se **teste.html também não funciona**:
→ Problema no servidor HTTP ou firewall

---

## 📞 ÚLTIMA OPÇÃO: Reiniciar Tudo

```bash
# 1. Feche TODOS os terminais
# 2. Reinicie o computador
# 3. Abra um terminal NOVO
# 4. Execute:

cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC
.venv\Scripts\activate
python diagnostico.py
python iniciar.py
```

---

## 💡 DICAS DE PERFORMANCE

### Para melhorar a velocidade do dashboard:

1. **Use Chrome/Edge** (mais rápido que Firefox para polling)
2. **Feche outras abas** (libera memória)
3. **Desabilite extensões** (podem interferir)
4. **Use modo anônimo** (sem cache/cookies)

### Para reduzir o intervalo de polling:

Edite `frontend/index.html`, procure por:

```javascript
setInterval(atualizarStatusMaquinas, 3000);
```

Mude para 5 segundos (menos requisições):

```javascript
setInterval(atualizarStatusMaquinas, 5000);
```

---

## 📚 DOCUMENTAÇÃO RELACIONADA

- **Diagnóstico completo**: `python diagnostico.py`
- **Guia de instalação**: `COMO-RODAR.md`
- **Início rápido**: `INICIO-RAPIDO.md`
- **Comandos de demo**: `COMANDOS-DEMO.md`

---

**🚀 Problema resolvido? Ótimo! Agora execute:**

```bash
python iniciar.py
```

**Ainda com problemas? Execute:**

```bash
python diagnostico.py
```

E envie a saída completa para análise.
