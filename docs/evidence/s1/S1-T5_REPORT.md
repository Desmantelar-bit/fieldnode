# S1-T5 — Relatório de evidência temporal

## Implementação

Migrations incrementais `0033_leituratelemetria_boot_id_and_more` e
`0034_trust_factors_temporal` (após a merge 0032 já existente) adicionam
`boot_id`, `uptime_ms`, `time_source`,
`clock_skew_ms`, `event_time_confidence`, `time_provenance` e `trust_factors`, e torna
`timestamp` anulável para preservar evento sem âncora. 0027 não foi editada.
O serviço de tempo ancora apenas leituras RTC/NTP/gateway explicitamente
declaradas. A reconstrução é reaplicável, determinística e limitada ao mesmo
boot. Leitura sem âncora fica com horário nulo; legado com timestamp é mantido
com confiança 0.5 e origem não verificada.

O Trust Score subtrai `1 - event_time_confidence` e inclui
`hora_do_dispositivo_nao_confiavel` em leituras `unsynced`. Isso é uma regra
heurística v1, não peso validado em campo; calibração operacional segue
pendente. A prioridade S1-T3 não foi alterada.

## Tabela de reconstrução reproduzível

Exemplo determinístico usado pelo teste: âncora gateway em
`2026-11-12T12:00:00Z`, uptime `21600000`; a primeira mensagem foi recebida seis
horas antes, sem relógio e sem hora informada. `ingested_at` abaixo é ilustrativo
do cenário de atraso; o teste confirma a diferença entre evento reconstruído e
ingestão do servidor.

| boot_id | uptime_ms | anchor_uptime_ms | anchor_time | ingested_at | event_time | time_source | event_time_confidence |
|---|---:|---:|---|---|---|---|---:|
| `boot-A` | 0 | 21600000 | 2026-11-12 12:00Z | 2026-11-12 12:00Z | 2026-11-12 06:00Z | unsynced | 0.65 |
| `boot-A` | 5000 | 21600000 | 2026-11-12 12:00Z | 2026-11-12 12:00Z | 2026-11-12 06:00:05Z | unsynced | 0.65 |
| `boot-A` | 21600000 | 21600000 | 2026-11-12 12:00Z | 2026-11-12 12:00Z | 2026-11-12 12:00Z | gateway | 0.80 |
| `boot-A` | 5000 | — | — | 2026-11-12 12:01Z | null (antes da âncora) | unsynced | 0.00 |
| `boot-B` | 5000 | — | — | 2026-11-12 12:01Z | null | unsynced | 0.00 |

Na chegada posterior da âncora de `boot-A` em uptime 6000, somente o item de
`boot-A` resolve para `anchor_time - 1000 ms`; `boot-B` continua sem horário.
Reexecutar a reconstrução produz o mesmo resultado, pois a fórmula sempre usa
uptime e âncora originais.

## Validação

`VERIFICADO`: `python manage.py test api_tcc.tests.test_telemetria
api_tcc.tests.test_identity_contract api_tcc.tests.test_data_health --verbosity 0`
— 63 testes passaram, incluindo lote atrasado de seis horas, ordem por uptime,
boots isolados, leitura sem âncora, âncora posterior, idempotência da
reconstrução, compatibilidade e fator de Trust Score.

`VERIFICADO`: `python manage.py makemigrations --check --dry-run` não detectou
migrations pendentes; `python manage.py check` não reportou problemas.

Validação física do ESP32, relógio RTC e precisão específica do DS3231 não faz
parte desta entrega. Valores de confiança são heurísticas explícitas ainda sem
calibração operacional. `clock_skew_ms` depende de estimativa informada pelo
gateway; o servidor não confunde latência de chegada com skew do relógio.

