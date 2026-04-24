# 🔧 SOLUÇÃO — Erro ao conectar na API

**Seu erro**: "Erro ao conectar na API. Verifique se o Django está rodando."

**Diagnóstico mostrou**: 
- ✅ Django rodando na porta 8000
- ✅ Frontend rodando na porta 5500
- ❌ `requests` não instalado (por isso `simular_dados.py` falhou)

---

## 🎯 SOLUÇÃO EM 4 PASSOS

### 1️⃣ Instalar a dependência faltante
```bash
pip install requests
```

### 2️⃣ Testar se a API está respondendo
```bash
python testar_api.py
```

**Resultado esperado**:
```
✅ Root OK (HTTP 200)
✅ Colheitadeiras OK (HTTP 200)
   → Retornou 0 registro(s)
✅ Telemetria OK (HTTP 200)
✅ Swagger OK (HTTP 200)
```

### 3️⃣ Popular o banco de dados
```bash
python simular_dados.py
```

**Agora deve funcionar** porque o `requests` está instalado.

### 4️⃣ Recarregar o dashboard
```bash
# No navegador, pressione:
Ctrl + F5

# Ou feche e abra novamente:
start http://127.0.0.1:5500/index.html
```

---

## 🔍 SE AINDA DER ERRO

### Teste Manual da API

Abra no navegador:
```
http://127.0.0.1:8000/Colheitadeira/
```

**Deve mostrar**: `[]` (lista vazia) ou JSON com dados

**Se mostrar erro 404**: O Django não está rodando corretamente

**Se não carregar**: Problema de firewall ou porta

---

### Verificar Console do Navegador

1. Abra o dashboard: `http://127.0.0.1:5500/index.html`
2. Pressione `F12` (abre DevTools)
3. Vá na aba "Console"
4. Procure por erros em vermelho

**Erros comuns**:

#### `CORS policy: No 'Access-Control-Allow-Origin'`
→ CORS bloqueando. Mas o `settings.py` já está configurado corretamente.

**Solução**: Reinicie o Django
```bash
# Mate o processo
taskkill /F /IM python.exe

# Inicie novamente
python manage.py runserver
```

#### `Failed to fetch` ou `net::ERR_CONNECTION_REFUSED`
→ Django não está rodando ou está em outra porta

**Solução**: Verifique se o Django está na porta 8000
```bash
netstat -ano | findstr :8000
```

#### `404 Not Found`
→ Endpoint não existe

**Solução**: Verifique a URL no `config.js`
```javascript
const API = 'http://127.0.0.1:8000';  // Deve ser exatamente isso
```

---

## 🚀 COMANDOS COMPLETOS (COPIAR E COLAR)

```bash
# 1. Instalar requests
pip install requests

# 2. Testar API
python testar_api.py

# 3. Popular banco
python simular_dados.py

# 4. Abrir dashboard
start http://127.0.0.1:5500/index.html
```

---

## 📊 VERIFICAÇÃO FINAL

Após executar os comandos acima, você deve ver:

### No terminal do `testar_api.py`:
```
✅ Root OK (HTTP 200)
✅ Colheitadeiras OK (HTTP 200)
✅ Telemetria OK (HTTP 200)
✅ Swagger OK (HTTP 200)
```

### No terminal do `simular_dados.py`:
```
✓ Marca: Case IH
✓ Marca: New Holland
✓ Marca: John Deere
...
✓ Total de leituras enviadas: 60
```

### No dashboard:
- ✅ Bolinha verde "API online"
- ✅ 4 cards de métricas com números
- ✅ Gráfico de temperatura com 4 linhas
- ✅ Tabela com 3 máquinas visíveis

---

## 🆘 AINDA NÃO FUNCIONA?

### Opção 1: Reiniciar tudo do zero
```bash
# 1. Mate todos os processos
taskkill /F /IM python.exe

# 2. Feche todos os terminais

# 3. Abra um terminal NOVO

# 4. Execute:
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC
.venv\Scripts\activate
pip install requests
python iniciar.py
```

### Opção 2: Iniciar manualmente (para ver erros)
```bash
# Terminal 1: Django
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC
.venv\Scripts\activate
python manage.py runserver

# Deixe rodando e observe se aparece algum erro

# Terminal 2: Frontend
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC\frontend
python -m http.server 5500

# Terminal 3: Popular dados
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC
.venv\Scripts\activate
pip install requests
python simular_dados.py

# Abrir navegador
start http://127.0.0.1:5500/index.html
```

---

## 💡 POR QUE O ERRO ACONTECEU?

1. **`requests` não estava instalado**: O `simular_dados.py` usa `requests` para fazer POST na API, mas a biblioteca não estava no `requirements.txt` original.

2. **Banco vazio**: Como o `simular_dados.py` falhou, o banco ficou sem dados. O dashboard tenta buscar dados e não encontra nada, mas isso não deveria dar erro de conexão.

3. **Django pode estar demorando**: Às vezes o Django demora 2-3 segundos para iniciar completamente. O navegador abre antes e tenta conectar, dando erro temporário.

**Solução aplicada**:
- ✅ Adicionado `requests==2.31.0` ao `requirements.txt`
- ✅ Criado `testar_api.py` para verificar conectividade
- ✅ Criado este guia de solução

---

## ✅ CHECKLIST FINAL

- [ ] Instalou `requests` (`pip install requests`)
- [ ] Testou API (`python testar_api.py`)
- [ ] Populou banco (`python simular_dados.py`)
- [ ] Recarregou dashboard (`Ctrl+F5`)
- [ ] Vê bolinha verde "API online"
- [ ] Vê dados nos cards e gráficos

---

**🚀 Execute agora:**

```bash
pip install requests
python testar_api.py
python simular_dados.py
```

**Depois recarregue o dashboard (Ctrl+F5) e deve funcionar!**
