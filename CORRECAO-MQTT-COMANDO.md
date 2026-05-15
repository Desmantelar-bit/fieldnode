# ⚠️ CORREÇÃO: Comando MQTT Listener

## ❌ Comando ERRADO
```bash
python scripts/mqtt_listen.py
```

## ✅ Comando CORRETO
```bash
python manage.py mqtt_listen
```

---

## 📍 Por quê?

O `mqtt_listen.py` é um **comando Django** (management command), não um script standalone.

**Localização**: `api_tcc/management/commands/mqtt_listen.py`

---

## 🚀 Comandos Corretos (3 Terminais)

```bash
# Terminal 1 - Django
python manage.py runserver

# Terminal 2 - MQTT Listener (comando Django)
python manage.py mqtt_listen

# Terminal 3 - Simulador
python scripts/simular_mqtt.py
```

---

## ✅ Validação

Se o comando funcionar, você verá:
```
✓ Conectado ao broker MQTT em localhost:1883
Aguardando mensagens em fieldnode/+/leitura...
```

---

**Todos os guias foram atualizados com o comando correto!**
