# ⚡ TESTE RÁPIDO - Sistema de Busca (2 minutos)

## 🚀 Iniciar Sistema

```bash
# Terminal 1 - Django
python manage.py runserver

# Terminal 2 - MQTT
python scripts/mqtt_listen.py

# Terminal 3 - Simulador (NOVO - com 8 máquinas)
python scripts/simular_mqtt.py
```

## 🔍 Testar Busca

### 1. Abrir Dashboard
```
http://127.0.0.1:8000/frontend/dashboard.html
```

### 2. Testar Autocompletar

| Digite | Resultado Esperado |
|--------|-------------------|
| `CASE` | 2 máquinas CASE |
| `NH` | 3 máquinas New Holland |
| `VALTRA` | 3 máquinas Valtra |
| `CR9000` | 1 máquina específica |

### 3. Testar Popup
1. Digite `NH`
2. Clique em `NH-CR9000-01`
3. ✅ Popup abre com:
   - Temperatura: ~87°C (CRÍTICO)
   - Análise de IA
   - Barra de risco vermelha

## 🎯 Novas Máquinas

**Total: 8 máquinas (antes eram 3)**

```
CASE (2):          New Holland (3):      Valtra (3):
CASE-TC5000-01     NH-CR9000-01 ⚠️      VALTRA-BC8800-01
CASE-TC5070-01     NH-CR8090-02         VALTRA-BC6800-02
                   NH-CR7090-03         VALTRA-BC5800-03
```

## ✅ Validação Rápida

- [ ] Dashboard mostra 8 máquinas
- [ ] Busca por "NH" mostra 3 resultados
- [ ] Dropdown tem dados de telemetria
- [ ] Popup abre ao clicar
- [ ] IA mostra análise preditiva

## 🐛 Problema?

**Só aparecem 3 máquinas CASE?**
→ Pare o simulador antigo (Ctrl+C) e rode o novo:
```bash
python scripts/simular_mqtt.py
```

**Dropdown não aparece?**
→ Aguarde 5 segundos para polling atualizar

---

**Pronto para apresentar!** 🎉
