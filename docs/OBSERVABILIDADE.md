# Observabilidade

Status: IMPLEMENTAÇÃO PARCIAL VERIFICADA LOCALMENTE

## O que existe

O backend expõe `GET /metrics`, em formato Prometheus, protegido por
`X-Metrics-Token` e pela variável de ambiente `FIELDNODE_METRICS_TOKEN`.
Sem token válido, a resposta é `403`. O endpoint não é incluído no frontend.

As séries são definidas em `api_tcc/metrics.py` e usam somente labels de
conjunto limitado: resultado da ingestão, classe `A/B/C`, tipo/severidade de
Event e categoria controlada de falha LLM. IDs, payloads e exceções completas
não entram em labels.

| Métrica | Tipo | Semântica |
| --- | --- | --- |
| `fieldnode_ingest_total{status}` | Counter | Operações lógicas de ingestão aceitas, rejeitadas, duplicadas, conflitantes ou falhas |
| `fieldnode_ingest_latency_seconds` | Histogram | Tempo no serviço de ingestão |
| `fieldnode_dlq_open` | Gauge | Itens não resolvidos na DLQ no último scrape |
| `fieldnode_outbox_pending{class}` | Gauge | Leituras com `sync_status=pendente` por classe |
| `fieldnode_sync_delay_seconds{class}` | Histogram | Atraso observado entre timestamp do evento e recebimento, apenas quando ambos são válidos |
| `fieldnode_events_created_total{tipo,severidade}` | Counter | Events persistidos pela primeira vez |
| `fieldnode_decisions_pending` | Gauge | Decisions em `PENDENTE` |
| `fieldnode_llm_latency_seconds` | Histogram | Latência de chamada Gemini concluída |
| `fieldnode_llm_failures_total{category}` | Counter | Falhas classificadas sem conteúdo do prompt/resposta |
| `fieldnode_model_version_info{method,version}` | Gauge | Método/versão declarados pelo runtime; não mede acurácia |
| `fieldnode_worker_last_message_age_seconds` | Gauge | Idade da última leitura processada |

Gauges de estado são atualizados no scrape com contagens indexadas. Uma falha
de instrumentação é absorvida para não interromper ingestão, decisões ou
sincronização. A instalação atual usa Gunicorn com dois workers, mas o suporte
Prometheus multiprocess ainda não foi homologado no ambiente integrado; não se
declara essa parte concluída apenas por configurar uma variável.

## Execução local

```powershell
$env:FIELDNODE_METRICS_TOKEN = "token-local"
Invoke-WebRequest http://127.0.0.1:8000/metrics -Headers @{"X-Metrics-Token"="token-local"}
```

Prometheus e Grafana não são dependências do Compose principal nesta etapa.
Coleta integrada, dashboard Grafana e validação multiprocess permanecem como
pendências até haver execução real documentada.
