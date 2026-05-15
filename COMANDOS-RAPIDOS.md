# ⚡ COMANDOS RÁPIDOS - FieldNode

## 🚀 Inicialização (Copy-Paste)

### Setup Inicial (Uma vez)
```bash
python manage.py migrate
python scripts/popular_banco.py
```

### Rodar Sistema (3 Terminais)
```bash
# Terminal 1 - Django
python manage.py runserver

# Terminal 2 - MQTT Listener
python manage.py mqtt_listen

# Terminal 3 - Simulador (8 máquinas)
python scripts/simular_mqtt.py
```

---

## ✅ Validação

### Validação Automática
```bash
python scripts/validar_sistema.py
```

### Verificar Dados no Banco
```bash
python manage.py shell -c "from api_tcc.models import LeituraTelemetria; print(f'Leituras: {LeituraTelemetria.objects.count()}')"
```

### Testar API
```bash
curl http://127.0.0.1:8000/api/leituras/ultimas/ | python -m json.tool
```

---

## 🌐 URLs

### Dashboard Principal
```
http://127.0.0.1:8000/frontend/dashboard.html
```

### API Swagger
```
http://127.0.0.1:8000/swagger/
```

### Endpoints Úteis
```
http://127.0.0.1:8000/api/leituras/ultimas/
http://127.0.0.1:8000/api/metricas/
http://127.0.0.1:8000/api/status-mqtt/
```

---

## 🧪 Testes Rápidos

### Teste 1: Busca por CASE
1. Abrir dashboard
2. Digitar: `CASE`
3. Esperado: 2 máquinas

### Teste 2: Busca por New Holland
1. Digitar: `NH`
2. Esperado: 3 máquinas

### Teste 3: Busca por Valtra
1. Digitar: `VALTRA`
2. Esperado: 3 máquinas

### Teste 4: Popup
1. Digitar: `NH-CR9000`
2. Clicar na sugestão
3. Esperado: Popup com temperatura crítica

---

## 🐛 Troubleshooting

### Limpar Dados e Recomeçar
```bash
python manage.py flush --no-input
python manage.py migrate
python scripts/popular_banco.py
```

### Ver Logs em Tempo Real
```bash
tail -f logs/fieldnode.log
```

### Matar Processos Travados
```bash
# Windows
taskkill /F /IM python.exe

# Linux/Mac
pkill -f python
```

### Verificar Porta 8000
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

---

## 📊 Verificações Rápidas

### Correção Aplicada?
```bash
grep "CORREÇÃO: Removida validação" api_tcc/services/telemetria.py
```

### Visual Unificado?
```bash
grep "styles.css" frontend/detalhes.html
```

### Novas Máquinas?
```bash
grep "VALTRA-BC8800-01" scripts/simular_mqtt.py
```

---

## 🎬 Demo (60 segundos)

### Preparação (30s antes)
```bash
# Terminal 1
python manage.py runserver

# Terminal 2
python manage.py mqtt_listen

# Terminal 3
python scripts/simular_mqtt.py

# Aguardar 10 segundos
# Abrir: http://127.0.0.1:8000/frontend/dashboard.html
```

### Roteiro
1. **Dashboard** (10s) - 8 máquinas ativas
2. **Busca** (15s) - Digitar "VALTRA" → 3 sugestões
3. **Popup** (15s) - Clicar NH-CR9000-01 → Crítico
4. **Detalhes** (10s) - Ver gráficos históricos
5. **Conclusão** (10s) - Offline-first + IA

---

## 📝 Checklist Pré-Apresentação

```bash
# 1. Validar sistema
python scripts/validar_sistema.py

# 2. Iniciar serviços
python manage.py runserver &
python manage.py mqtt_listen &
python scripts/simular_mqtt.py &

# 3. Aguardar 10 segundos
sleep 10

# 4. Abrir dashboard
# http://127.0.0.1:8000/frontend/dashboard.html

# 5. Testar busca
# Digite "NH" → deve mostrar 3 máquinas

# 6. Testar popup
# Clique em qualquer sugestão → popup abre

# ✅ Pronto para apresentar!
```

---

## 🔥 Comandos de Emergência

### Sistema Não Responde
```bash
# Matar tudo e recomeçar
pkill -f python
python manage.py runserver &
python manage.py mqtt_listen &
python scripts/simular_mqtt.py &
```

### Banco Corrompido
```bash
# Reset total
rm db.sqlite3
python manage.py migrate
python scripts/popular_banco.py
```

### Frontend Não Carrega
```bash
# Limpar cache do navegador
# Ctrl + Shift + Delete (Chrome/Edge)
# Ou abrir em aba anônima
```

---

## 📞 Atalhos Úteis

| Ação | Atalho |
|------|--------|
| Abrir console navegador | F12 |
| Recarregar página | F5 |
| Recarregar sem cache | Ctrl + F5 |
| Parar servidor Django | Ctrl + C |
| Limpar terminal | Ctrl + L |

---

**Última atualização**: 2024
**Equipe**: FieldNode - SENAI-SP
