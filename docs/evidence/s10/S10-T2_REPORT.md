# S10-T2 · Relatório de métricas

Status: IMPLEMENTAÇÃO LOCAL VERIFICADA; COLETA INTEGRADA PENDENTE

O endpoint `/metrics` e as séries estão implementados em
`api_tcc/metrics.py` e `api_tcc/api/views_prometheus.py`. A instrumentação foi
ligada ao serviço real de ingestão, à criação efetiva de Events e às chamadas
Gemini. A proteção usa token dedicado e responde `403` sem credencial.

Não foram inventadas capturas do Prometheus/Grafana. O perfil de observabilidade
do Compose, scraping externo e validação de dois workers ainda não têm execução
integrada registrada. Portanto, não há evidência de dashboard Grafana nem de
comportamento multiprocess concluído.

Comandos locais previstos para a verificação:

```powershell
$env:USE_SQLITE = "True"
$env:FIELDNODE_METRICS_TOKEN = "token-local"
python manage.py test api_tcc.tests.test_prometheus_metrics
```

Labels permanecem limitados a enums/categorias controladas; `device_id`,
`message_id`, UUID, prompt, resposta e exceção completa não são publicados.
