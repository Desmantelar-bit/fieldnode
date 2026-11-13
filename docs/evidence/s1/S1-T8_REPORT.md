# S1-T8 · Relatório de paridade por golden files

## Contrato e fixture

- Fonte canônica: `contracts/severity.v1.json`, schema `severity.v1`.
- O contrato declara os thresholds, ranges, unidades, qualidades de evidência e agora também `severity_order` (`NORMAL < ATENCAO < CRITICO`), evitando ordem hardcoded no simulador.
- Fixture compartilhada: `contracts/fixtures/classificacao.json`; backend, simulador e frontend leem o mesmo arquivo.
- Há **26 casos determinísticos**: 12 sondagens abaixo/no/acima dos quatro thresholds; quatro limites mínimo/máximo; quatro combinações de severidades concordantes ou divergentes; três qualidades de evidência; um dado atrasado; e dois valores fora do range.
- Cada caso válido registra ID, temperatura, vibração, unidade, qualidade, atraso, severidade por métrica, severidade consolidada e classe A/B/C esperada. Os dois inválidos registram `expected_error: range`.
- O passo adjacente é `0.001`, expresso em decimal para thresholds do contrato com uma casa decimal.

## Geração e verificação

`scripts/generate_classification_fixtures.py` calcula os resultados de referência diretamente dos valores e regras declarados em `severity.v1.json`; não chama as funções backend ou frontend testadas. O modo de escrita é local e explícito. `--check` compara o conteúdo versionado sem escrever e falha quando está desatualizado.

Saída local:

```text
Fixture gerada: contracts\fixtures\classificacao.json (26 casos)
Fixture verificada: contracts\fixtures\classificacao.json
```

`test_contract_generator.py` confirma que o modo `--check` detecta arquivo obsoleto sem sobrescrevê-lo e que a geração é determinística. `test_contract_parity.py` injeta uma divergência deliberada no classificador durante um teste isolado e confirma que a expectativa golden a detecta.

## Camadas validadas

- **Backend:** executa as funções reais `classify`, `classify_combined` e `transmission_class`; valida unidade, ranges, severidades individuais/consolidada, classe e erros de range.
- **Borda:** `simulators/test_edge_client.py` executa `classify_priority` contra todos os mesmos casos. O cliente usa `api_tcc.contracts`, sem thresholds paralelos.
- **Frontend:** `frontend-next/tests/contract.test.ts` executa a implementação real `classifyMetric` de `src/lib/metricThresholds.ts` e lê o golden file. A verificação de severidade frontend detecta divergência dos thresholds gerados.
- **Firmware:** não há validação declarada; a fixture é JSON simples para integração futura prevista em S8.

## CI

`.github/workflows/contracts.yml` roda em `push` e `pull_request`, executa o gerador em `--check`, os testes backend/borda e o teste frontend. O workflow não atualiza fixtures. O CI hospedado ainda não foi disparado a partir desta sessão; os mesmos comandos foram executados localmente.

## Resultado local

- `python scripts/generate_classification_fixtures.py --check`: passou.
- Backend + borda e testes de telemetria/gerador: **48 passed** na execução direcionada.
- Frontend: **1 passed** (`npm run test:contracts`).
- Django system check: sem problemas.
- Suíte completa: baseline limpo **331 passed, 7 failed**; estado final **342 passed, os mesmos 7 failed**. As falhas são externas à classificação e estão detalhadas no relatório S1-T7.

As falhas da suíte completa que também aparecem no baseline limpo estão listadas no relatório S1-T7; nenhuma pertence à fixture ou aos três testes de paridade. Nenhuma implementação de firmware foi simulada ou aprovada.

**Classificação local:** IMPLEMENTADO para backend, simulador e frontend; o resultado hospedado do workflow está pendente do próximo `push`/`pull_request`.
