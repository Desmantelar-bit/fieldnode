# S3-T10 · Grid de calor da frota

## Contrato implementado

`GET /api/events/heatmap/` retorna `start`, `end`, `timezone` e `results`. Cada item contém `machine_id`, `machine_external_code`, `hour`, `worst_severity`, `event_count` e `quality_issue`.

O agrupamento usa `Event.machine` e `Event.leitura_origem__timestamp`, com `TruncHour` no banco. A severidade é ordenada semanticamente por `NORMAL < ATENCAO < CRITICO`; não há ordenação alfabética. Eventos sem `timestamp` não são alocados em uma hora artificial.

## Qualidade e interface

`quality_issue` é derivado de `evidence_quality` suspeita/insuficiente ou `needs_verification=True`. A cor representa severidade; o contorno pontilhado e o ícone representam qualidade a verificar. Células ausentes são narradas como “sem eventos”, não como normalidade.

O componente `HeatGrid` é renderizado no dashboard e possui alternativa textual por célula, legenda e estados de carregamento, erro e ausência de histórico.

## Decisão D-16

Score operacional individual de operador permanece **DEFER**. Nenhum campo, endpoint, ranking ou cálculo foi criado para esse fim.

## Verificação

O teste `api_tcc/tests/test_s3_t10_heatmap.py` passou: `2 passed`. O type-check do frontend também foi executado com saída 0. A captura visual e a comparação automatizada contra a lista de eventos em ambiente ativo permanecem **NÃO VERIFICADAS** nesta execução.
