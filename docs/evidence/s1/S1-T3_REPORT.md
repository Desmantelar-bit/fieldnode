# S1-T3 — evidência separada de severidade e prioridade

## Estado inicial e diagnóstico

O checkout iniciou sem alterações locais (`git status --short` vazio). S1-T1 estava implementada em `contracts/severity.v1.json` e a migration 0027 existente registra somente `LeituraTelemetria.vibracao_unit`. A fórmula anterior em `api_tcc/services/eventos.py` era `S × I × U × C`; trust ausente era convertido em zero e zerava a prioridade. Impactos permanecem TEMP_ALTA 1.0, VIBRACAO_ALTA 0.8, ANOMALIA_ESTATISTICA 0.75, ANOMALIA_ML 0.7, TENDENCIA_RISCO 0.6; desconhecido 0.25. A urgência e o cooldown existentes foram preservados. A API ordenava por `-criado_em`.

| Dimensão | Antes | Alteração |
| --- | --- | --- |
| Severidade | `severity.v1`, gravidade crítica/atenção/normal | Mantida sem dependência da evidência |
| Trust Score | Multiplicava o score como C | Só classifica qualidade |
| Impacto | Pesos fixos heurísticos por tipo | Preservado |
| Urgência | Decaimento temporal 24h e agravamento | Preservado |
| API | Mais recente primeiro | `priority_score DESC`, depois criação e ID |
| Interface | Dashboard não consumia eventos | Painel `PriorityEvents` consome o endpoint ordenado e exibe severidade, score e selo em separado |

## Implementação

- Fórmula final: `clamp(severidade × impacto × urgência, 0, 1)`; trust não é lido por `calcular_priority_score`.
- `evidence_quality(trust)`: `>=0.8` boa; `>=0.5` suspeita; demais insuficiente. Valores ausentes, não numéricos, booleanos, NaN, infinitos e fora de `[0,1]` viram insuficiente. Os limites são heurísticos calibráveis, ainda sem calibração operacional.
- `needs_verification` é verdadeiro para qualquer qualidade diferente de boa.
- Eventos antigos recebem defaults seguros `insuficiente` e `True`, sem alterar sua severidade histórica.
- Migration `0028_event_evidence_quality_event_needs_verification.py`, dependente da 0027. O merge remoto simultâneo trouxe também o ramo 0030/0031; foi adicionada a migration de junção sem operações `0032_merge_20261112_1050.py`, dependente de 0028 e 0031. Nenhuma migration aplicada foi editada.
- `EventSerializer` inclui `evidence_quality` e `needs_verification`. O novo painel `PriorityEvents` no dashboard consome `/events/?page_size=5`, mantém os dados anteriores quando a atualização falha e diferencia loading, erro e lista vazia. Evidência suspeita/insuficiente recebe selo sem alterar a cor da severidade.

## Evidências de comportamento

Teste equivalente: Trust `0.95` e `0.2`, mesma severidade crítica, tipo TEMP_ALTA, histórico vazio e urgência 1.0. Ambos resultam em `priority_score = 1.0`; qualidades são `boa` e `insuficiente`; `needs_verification` é falso e verdadeiro, respectivamente.

Sensor em 120 °C com Trust 0.2: a criação mantém `CRITICO`, persiste `priority_score = 1.0`, `evidence_quality = insuficiente` e `needs_verification = True`. Isso indica verificação do sensor, sem confirmar falha mecânica.

Teste de API ordena um evento score 0.9 que requer verificação antes de um score 0.2 com evidência boa, e confirma que o serializer devolve o selo.

## Verificação

- `python manage.py test api_tcc.tests.test_eventos api_tcc.tests.test_contract_fixes -v 2`: 20 testes passaram (inclui comparação 0.95/0.2, 120 °C, ordenação e campos serializados).
- `python manage.py test api_tcc -v 1`: 314 testes passaram contra o grafo unido e com o teste final de 120 °C. A suíte focal `python manage.py test api_tcc.tests.test_eventos api_tcc.tests.test_contract_fixes -v 1` também passou com 20 testes.
- `python manage.py makemigrations --check --dry-run`: nenhuma migration pendente.
- `python manage.py check`: sem problemas.
- `node frontend-next/tests/attention_events_test.cjs`: NÃO VERIFICADO. O runner falhou porque `playwright` não está instalado na árvore local `node_modules`; o pacote permanece declarado em `package.json`. A tentativa de restaurar dependências não concluiu por falta de progresso do npm e foi interrompida.
- Captura de tela S1-T3: NÃO GERADA; depende do runner Playwright.

## Pendências

Os limites de evidência não estão calibrados com dados reais. A UI foi implementada, mas o teste visual automatizado e a captura permanecem pendentes por ausência local do pacote Playwright. Lint/type-check/build foram aprovados antes da adição final do painel; esta versão final do painel não recebeu essas verificações porque os executáveis sumiram junto com as dependências locais.


