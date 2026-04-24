# ⚡ Início Rápido — FieldNode

**Tempo total**: 5 minutos

---

## 🎯 Opção 1: Automático (RECOMENDADO)

### Windows
```bash
# Duplo clique no arquivo ou execute:
iniciar.bat
```

### Linux/Mac ou Python direto
```bash
python iniciar.py
```

**Pronto!** O script faz tudo automaticamente:
- ✅ Verifica dependências
- ✅ Aplica migrations
- ✅ Popula dados de demonstração
- ✅ Inicia Django e frontend
- ✅ Abre o navegador

---

## 🔧 Opção 2: Manual (se preferir controle total)

### 1. Criar banco MySQL
```sql
CREATE DATABASE fieldnode CHARACTER SET utf8mb4;
```

### 2. Configurar ambiente
```bash
# Ativar virtualenv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac

# Instalar dependências (se necessário)
pip install -r requirements.txt

# Configurar .env (copie .env.example e edite com suas credenciais)
copy .env.example .env          # Windows
cp .env.example .env            # Linux/Mac
```

### 3. Preparar banco
```bash
python manage.py migrate
python simular_dados.py
```

### 4. Iniciar servidores
```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Frontend
cd frontend
python -m http.server 5500

# Abrir navegador
start http://localhost:5500/index.html      # Windows
open http://localhost:5500/index.html       # Mac
xdg-open http://localhost:5500/index.html   # Linux
```

---

## 📊 O que você verá

### Dashboard Principal
- **4 máquinas** cadastradas (Case IH, New Holland, John Deere)
- **60 leituras** de telemetria (15 por máquina)
- **3 cenários** simulados:
  - ✅ CASE-TC5000-01: Operação normal
  - ⚠️ CASE-TC5070-01: Atenção (temp > 75°C)
  - 🔴 NH-CR9000-01: Crítico (temp > 85°C)
  - ✅ JD-S780-01: Normal com variação

### Análise de IA
- **Manutenção preditiva**: Random Forest prevê risco de falha
- **Detecção de anomalias**: Isolation Forest identifica padrões anormais
- **Alertas automáticos**: Temperatura, vibração e RPM

---

## 🐛 Problemas Comuns

### "Access denied for user 'root'"
→ Verifique a senha do MySQL no `.env`

### "No module named 'django'"
→ Ative o virtualenv: `.venv\Scripts\activate`

### "API offline" no dashboard
→ Verifique se o Django está rodando na porta 8000

### Gráficos não aparecem
→ Aguarde 3 segundos ou force refresh (Ctrl+F5)

---

## 📚 Documentação Completa

- **Guia detalhado**: `COMO-RODAR.md`
- **Fixes aplicados**: `FIXES-APLICADOS.md`
- **Checklist da banca**: `CHECKLIST-BANCA.md`
- **README principal**: `README.md`

---

## 🎯 URLs Importantes

| Serviço | URL |
|---------|-----|
| Dashboard | http://localhost:5500/index.html |
| API Django | http://localhost:8000 |
| Swagger | http://localhost:8000/swagger/ |
| Admin | http://localhost:8000/admin/ |

---

## ✅ Verificação Rápida

Após iniciar, verifique:

- [ ] Bolinha verde "API online" no rodapé da sidebar
- [ ] 4 cards de métricas no topo do dashboard
- [ ] Gráfico de temperatura com 4 linhas coloridas
- [ ] Tabela de status atualizando a cada 3s
- [ ] Card "Análise de IA" mostrando previsões
- [ ] Página "Alertas" com avisos de temperatura

---

**🚀 Tudo funcionando? Você está pronto para a apresentação!**

Qualquer dúvida, consulte `COMO-RODAR.md` para instruções detalhadas.
