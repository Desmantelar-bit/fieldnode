# S3-T6 — relatório de diagnóstico

## Diagnóstico

- `/maquinas` carrega `/api/colheitadeira/`, que representa a entidade agrícola legada; não há endpoint `/api/machines/` de listagem/classificação.
- O modelo canônico separa `Machine`, `LeituraTelemetria`, `Event` e `MachineDataHealth`. Dashboard, grid e mapa consomem endpoints diferentes (`colheitadeira`, leituras e posições GPS), sem contrato compartilhado de classificação/contagens.
- `event_time` está em `LeituraTelemetria.timestamp`; a saúde agregada usa `MachineDataHealth.ultima_atualizacao`, cujo nome não prova que o instante é o `event_time` confiável.
- O contrato de severidade é `contracts/severity.v1.json`. `MAX_GAP_SECONDS=7200` em `data_health.py` limita penalidade de trust score e não constitui um TTL de atualidade contratado.

## Resultado

Nenhum filtro ou classificação foi implementado nesta etapa. Escolher um limite de atualidade ou inferir estado normal a partir da entidade legada sem contrato compartilhado criaria justamente as divergências que o escopo proíbe. A API também não fornece contagens globais filtradas para comparação entre dashboard, máquinas e mapa.

**Status:** não implementado; consistência cruzada, testes e capturas não verificados.
