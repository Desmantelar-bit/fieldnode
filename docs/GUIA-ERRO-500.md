# 🔧 Guia Rápido - Resolver Erro 500

## 🎯 Passos para Resolver

### 1️⃣ Popular o Banco de Dados

Execute no terminal:

```bash
python scripts/popular_dados_teste.py
```

**Saída esperada**:
```
🌱 Populando banco de dados com dados de teste...
------------------------------------------------------------

👷 Criando operários...
   ✅ João Silva - 5 anos
   ✅ Maria Santos - 3 anos
   ✅ Pedro Oliveira - 8 anos
   ✅ Ana Costa - 2 anos
   ✅ Carlos Souza - 10 anos

🏭 Criando marcas...
   ✅ John Deere
   ✅ Case IH
   ✅ New Holland
   ✅ Massey Ferguson
   ✅ Valtra

🚜 Criando modelos...
   ✅ S790 (John Deere)
   ✅ Axial-Flow 9250 (Case IH)
   ✅ CR10.90 (New Holland)
   ✅ Ideal 9T (Massey Ferguson)
   ✅ BC8800 (Valtra)

📏 Criando unidades de medida...
   ✅ PSI
   ✅ Bar
   ✅ cm
   ✅ m
   ✅ kg
   ✅ L

⛽ Criando combustíveis...
   ✅ Diesel S10 - 100.0%
   ✅ Biodiesel B20 - 80.0%
   ✅ Diesel Comum - 100.0%

============================================================
✅ Dados de teste criados com sucesso!
============================================================

📊 Resumo:
   - Operários: 5
   - Marcas: 5
   - Modelos: 5
   - Unidades de Medida: 6
   - Combustíveis: 3
```

### 2️⃣ Verificar se Funcionou

Teste direto na API:

```bash
# Windows (PowerShell)
Invoke-WebRequest http://127.0.0.1:8000/api/operario/

# Windows (CMD) ou Linux/Mac
curl http://127.0.0.1:8000/api/operario/
```

Ou abra no navegador:
- http://127.0.0.1:8000/api/operario/

**Resposta esperada**:
```json
[
  {
    "id": 1,
    "nome": "João Silva",
    "tempo_de_servico": 5,
    "no_banco": true
  },
  {
    "id": 2,
    "nome": "Maria Santos",
    "tempo_de_servico": 3,
    "no_banco": false
  },
  ...
]
```

### 3️⃣ Testar no Frontend

Acesse:
- http://127.0.0.1:8000/frontend/operarios.html

Deve mostrar a lista de operários!

## 🐛 Se Ainda Houver Erro 500

### Verificar o Log do Servidor

No terminal onde o servidor Django está rodando, procure por:

```
Internal Server Error: /api/operario/
Traceback (most recent call last):
  ...
```

**Copie e cole aqui** toda a mensagem de erro.

### Verificar o Arquivo de Log

```bash
# Windows
type logs\fieldnode_errors.log

# Linux/Mac
cat logs/fieldnode_errors.log
```

### Testar Manualmente no Shell

```bash
python manage.py shell
```

Depois:
```python
from api_tcc.models import Operario
from api_tcc.api.serializers import OperarioSerializer

# Buscar operários
ops = Operario.objects.all()
print(f"Total: {ops.count()}")

# Testar serializer
if ops.count() > 0:
    serializer = OperarioSerializer(ops, many=True)
    print(serializer.data)
```

## 🔍 Possíveis Causas do Erro 500

### 1. Banco de Dados Vazio
**Solução**: Execute `python scripts/popular_dados_teste.py`

### 2. Migrations Não Aplicadas
**Solução**:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Erro no Serializer
**Verificar**: `api_tcc/api/serializers.py`

### 4. Permissões do Banco
**Verificar**: Arquivo `.env` com credenciais corretas

### 5. CORS Bloqueado
**Verificar**: `CORS_ALLOW_ALL_ORIGINS = True` em `settings.py`

## 📋 Checklist de Diagnóstico

- [ ] Servidor Django está rodando?
- [ ] Migrations aplicadas? (`python manage.py migrate`)
- [ ] Dados populados? (`python scripts/popular_dados_teste.py`)
- [ ] API responde? (http://127.0.0.1:8000/api/operario/)
- [ ] CORS configurado? (verificar `settings.py`)
- [ ] Logs verificados? (`logs/fieldnode_errors.log`)

## 🚀 Comando Rápido para Resetar Tudo

Se quiser começar do zero:

```bash
# 1. Deletar banco SQLite (se estiver usando)
del db.sqlite3  # Windows
# rm db.sqlite3  # Linux/Mac

# 2. Recriar migrations
python manage.py makemigrations
python manage.py migrate

# 3. Popular dados
python scripts/popular_dados_teste.py

# 4. Reiniciar servidor
python manage.py runserver
```

## 📞 Próximos Passos

1. Execute `python scripts/popular_dados_teste.py`
2. Copie a saída completa
3. Teste http://127.0.0.1:8000/api/operario/
4. Se ainda houver erro, copie o stack trace do terminal do servidor
5. Cole tudo aqui para análise
