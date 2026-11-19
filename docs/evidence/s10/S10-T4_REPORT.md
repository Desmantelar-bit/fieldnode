# S10-T4 - Health em camadas e heartbeat

Status: implementacao verificada localmente.

Foram criados `/api/health/live` e `/api/health/ready`, preservando
`/api/health/`. O worker MQTT grava `WorkerHeartbeat` no banco compartilhado,
com intervalo padrao de 20 segundos e timeout padrao de 60 segundos.

O readiness detalha banco, broker, worker, modelo e disco. Dispositivos esperados
sao configurados por `FIELDNODE_EXPECTED_MQTT_DEVICES`; quando vazio, worker e
broker nao bloqueiam readiness. Worker `stale` produz `503` quando ha dispositivos
esperados. O Compose usa liveness no healthcheck da API.

Comando:

```powershell
venv\Scripts\python.exe manage.py test api_tcc.tests.test_json_logging api_tcc.tests.test_health
```

Resultado: 59 testes passaram, incluindo liveness independente do banco,
readiness `503` com worker atrasado e ausencia de falso positivo sem dispositivos.

Limitacoes: broker e verificado por conexao TCP curta com cache de 5 segundos;
isso prova conectividade de rede, nao autenticacao MQTT nem publicacao/consumo.
O modelo e reportado pelo registry, sem treinamento no health check. Compose nao
foi executado nesta etapa.
