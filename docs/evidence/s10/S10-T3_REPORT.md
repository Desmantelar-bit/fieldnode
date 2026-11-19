# S10-T3 - Logs estruturados com identidade de mensagem

Status: implementacao verificada localmente.

Alterados `api_tcc/correlation.py`, `mqtt_listen.py` e `services/telemetria.py`.
O contexto MQTT inclui `correlation_id`, `device_id`, `message_id`, `sequence`
e `boot_id` quando confiaveis. O formatter JSON emite esses campos em cada
registro, com `null` fora de uma mensagem. Tokens sao restaurados em `finally`.

Evidencia: testes confirmaram que duas linhas da mesma mensagem compartilham
os identificadores e que o contexto nao vaza para a mensagem seguinte.

Comando:

```powershell
venv\Scripts\python.exe manage.py test api_tcc.tests.test_json_logging api_tcc.tests.test_correlation api_tcc.tests.test_health
```

Resultado: 96 testes focados passaram na execucao final desta etapa.

Limitacao: `contextvars` nao atravessam processos automaticamente; a fronteira
worker/API usa campos da mensagem e heartbeat compartilhado.
