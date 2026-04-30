# 🚀 Guia Rápido — Como Rodar o FieldNode

**Tempo estimado**: 10 minutos  
**Pré-requisitos**: Python 3.12+, MySQL 8, Git

---

## 📋 PASSO A PASSO COMPLETO

### 1️⃣ Preparar o Banco de Dados (1 min)

```bash
# Abra o MySQL (prompt de comando ou MySQL Workbench)
mysql -u root -p

# Dentro do MySQL, execute:
CREATE DATABASE fieldnode CHARACTER SET utf8mb4;
EXIT;
```

---

### 2️⃣ Configurar o Ambiente Python (2 min)

```bash
# Navegue até a pasta do projeto
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC

# Ative o virtualenv (se já existe)
.venv\Scripts\activate

# OU crie um novo virtualenv (se não existe)
python -m venv .venv
.venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

---

### 3️⃣ Configurar Variáveis de Ambiente (1 min)

```bash
# Copie o arquivo de exemplo (se ainda não fez)
copy .env.example .env

# Edite o .env com suas credenciais do MySQL
notepad .env
```

**Conteúdo do `.env`**:
```env
SECRET_KEY=sua-chave-secreta-aqui-pode-ser-qualquer-coisa
DEBUG=True
DB_NAME=fieldnode
DB_USER=root
DB_PASSWORD=SUA_SENHA_DO_MYSQL_AQUI
DB_HOST=localhost
DB_PORT=3306
```

---

### 4️⃣ Aplicar Migrations (1 min)

```bash
# Cria as tabelas no banco de dados
python manage.py migrate
```

**Saída esperada**:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, api_tcc
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying api_tcc.0001_initial... OK
```

---

### 5️⃣ Popular com Dados de Demonstração (1 min)

```bash
# Executa o script de simulação
python simular_dados.py
```

**O que este script faz**:
- ✅ Cria 3 marcas (Case IH, New Holland, John Deere)
- ✅ Cria 4 modelos de colheitadeiras
- ✅ Cadastra 4 operários
- ✅ Cria 4 colheitadeiras completas
- ✅ Envia 60 leituras de telemetria (15 por máquina)
- ✅ Simula 3 cenários: Normal, Atenção e Crítico

**Tempo de execução**: ~30 segundos

---

### 6️⃣ Iniciar o Servidor Django (10 segundos)

```bash
# Inicia o servidor na porta 8000
python manage.py runserver
```

**Saída esperada**:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
April 17, 2024 - 14:30:00
Django version 5.2, using settings 'setup.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

✅ **Servidor rodando!** Deixe este terminal aberto.

---

### 7️⃣ Abrir o Dashboard (10 segundos)

**Opção A: Servir o frontend separadamente (RECOMENDADO)**

Abra um **NOVO terminal** (deixe o Django rodando no primeiro):

```bash
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC

# Serve o frontend na porta 5500
python -m http.server 5500 --directory frontend
```

Depois abra no navegador:
```
http://localhost:5500/index.html
```

---

**Opção B: Acessar direto pelo Django**

Abra no navegador:
```
http://localhost:8000/admin/
```

Depois navegue manualmente até o arquivo `index.html` ou configure uma rota no Django.

---

## ✅ VERIFICAÇÃO RÁPIDA

Após abrir o dashboard, você deve ver:

### No rodapé da sidebar (canto inferior esquerdo):
- 🟢 **"API online"** (bolinha verde pulsando)

### Na página Dashboard:
- 📊 **4 cards de métricas** no topo (Colheitadeiras, Status, Temperatura, Combustível)
- 📈 **Gráfico de temperatura** com 4 linhas coloridas
- 📊 **Gráfico de combustível** (mostrará "N/D" — normal, requer sensor adicional)
- 🔄 **Tabela de status** atualizando a cada 3 segundos
- 🤖 **Card de Análise de IA** mostrando previsões

### Na página Alertas:
- ⚠️ **Alerta CRÍTICO** para NH-CR9000-01 (temperatura > 85°C)
- ⚠️ **Alerta ATENÇÃO** para CASE-TC5070-01 (temperatura > 75°C)

---

## 🐛 TROUBLESHOOTING

### ❌ Erro: "Access denied for user 'root'@'localhost'"
**Solução**: Verifique a senha do MySQL no arquivo `.env`

```bash
# Teste a conexão manualmente
mysql -u root -p
# Digite a senha e veja se conecta
```

---

### ❌ Erro: "No module named 'django'"
**Solução**: Ative o virtualenv e reinstale as dependências

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

---

### ❌ Dashboard não carrega / Console mostra "API offline"
**Solução**: Verifique se o Django está rodando

```bash
# Em outro terminal, teste a API
curl http://localhost:8000/Colheitadeira/

# Ou abra no navegador
http://localhost:8000/Colheitadeira/
```

Se retornar JSON com dados, a API está funcionando.

---

### ❌ Gráficos não aparecem
**Solução**: Aguarde 3 segundos para o polling atualizar, ou force refresh (Ctrl+F5)

---

### ❌ Erro: "Table 'fieldnode.api_tcc_colheitadeira' doesn't exist"
**Solução**: Rode as migrations novamente

```bash
python manage.py migrate
```

---

## 🎯 COMANDOS RESUMIDOS (COPIAR E COLAR)

```bash
# 1. Criar banco (no MySQL)
mysql -u root -p -e "CREATE DATABASE fieldnode CHARACTER SET utf8mb4;"

# 2. Ativar virtualenv
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC
.venv\Scripts\activate

# 3. Instalar dependências (se necessário)
pip install -r requirements.txt

# 4. Aplicar migrations
python manage.py migrate

# 5. Popular dados
python simular_dados.py

# 6. Iniciar Django (deixe rodando)
python manage.py runserver

# 7. Em OUTRO terminal, servir frontend
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC
python -m http.server 5500 --directory frontend

# 8. Abrir no navegador
start http://localhost:5500/index.html
```

---

## 📱 COMANDOS OPCIONAIS

### Criar superusuário para acessar /admin/
```bash
python manage.py createsuperuser

# Preencha:
# Username: admin
# Email: admin@fieldnode.com
# Password: admin123
```

Depois acesse: `http://localhost:8000/admin/`

---

### Rodar testes automatizados
```bash
python manage.py test api_tcc.tests
```

---

### Iniciar listener MQTT (se tiver broker rodando)
```bash
# Terminal 1: Inicie o broker
mosquitto -v

# Terminal 2: Inicie o listener
python manage.py mqtt_listen

# Terminal 3: Envie mensagem de teste
mosquitto_pub -h localhost -p 1883 -t "fieldnode/COLH-01/leitura" -m "{\"id\":\"550e8400-e29b-41d4-a716-446655440000\",\"maquina_id\":\"COLH-01\",\"temperatura\":85.5,\"vibracao\":0.65,\"rpm\":1750,\"timestamp\":\"2024-04-17T10:00:00Z\"}"
```

---

## 🎬 DEMONSTRAÇÃO PARA A BANCA

### Cenário 1: Operação Normal
```bash
curl -X POST http://localhost:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -d "{\"id\":\"demo-normal-001\",\"maquina_id\":\"CASE-TC5000-01\",\"temperatura\":72.5,\"vibracao\":0.35,\"rpm\":1850,\"timestamp\":\"2024-04-17T14:00:00Z\"}"
```

### Cenário 2: Alerta de Atenção
```bash
curl -X POST http://localhost:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -d "{\"id\":\"demo-atencao-001\",\"maquina_id\":\"CASE-TC5070-01\",\"temperatura\":78.5,\"vibracao\":0.55,\"rpm\":1750,\"timestamp\":\"2024-04-17T14:05:00Z\"}"
```

### Cenário 3: Alerta Crítico
```bash
curl -X POST http://localhost:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -d "{\"id\":\"demo-critico-001\",\"maquina_id\":\"NH-CR9000-01\",\"temperatura\":88.5,\"vibracao\":0.85,\"rpm\":1200,\"timestamp\":\"2024-04-17T14:10:00Z\"}"
```

---

## 📚 DOCUMENTAÇÃO ADICIONAL

- **API Swagger**: http://localhost:8000/swagger/
- **README completo**: `README.md`
- **Fixes aplicados**: `FIXES-APLICADOS.md`
- **Checklist da banca**: `CHECKLIST-BANCA.md`

---

## ✅ CHECKLIST FINAL

Antes da apresentação, verifique:

- [ ] MySQL rodando
- [ ] Virtualenv ativado
- [ ] Migrations aplicadas
- [ ] Dados simulados carregados
- [ ] Django rodando (porta 8000)
- [ ] Frontend servido (porta 5500)
- [ ] Dashboard abre sem erros
- [ ] API status mostra "online"
- [ ] Tabela atualiza a cada 3s
- [ ] Gráficos renderizam
- [ ] Alertas aparecem na página Alertas
- [ ] IA mostra análise de manutenção

---

**🚀 Sistema pronto para apresentação!**

Qualquer dúvida, consulte os arquivos:
- `FIXES-APLICADOS.md` — Correções técnicas
- `CHECKLIST-BANCA.md` — Preparação para apresentação
