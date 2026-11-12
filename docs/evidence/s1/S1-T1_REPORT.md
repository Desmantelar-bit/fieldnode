# S1-T1 — evidência do contrato de severidade v1

## Estado inicial

O checkout estava limpo em `main`. `FIELDNODE_LEVIATA_ROADMAP_V5.md` não está presente neste checkout. A baseline histórica registra pendências de Compose, Gitleaks e frontend; elas não foram reclassificadas como resolvidas por esta tarefa.

## Divergências encontradas

| Camada | Antes | Ação |
|---|---|---|
| Eventos backend | temperatura crítica com 85 e comparação `>` | `classify()` lê o contrato e usa `>=` |
| Serviço de telemetria | 95/110 e vibração 5/8 | risco lê o contrato v1 |
| Borda | 95/110 e vibração 5/8 | prioridade lê o contrato v1 |
| Frontend | 95/110 e 0,5/0,8 g | artefato gerado com 75/85 e 5/8 índice |
| RPM | limiares próprios no frontend | dependente de regime, sem classificação fixa |

## Decisões

D-01: fronteiras inclusivas (`>=`). D-02: `vibracao` é índice adimensional `indice_0_10`, faixa 0–10. Classe A tem precedência absoluta para `CRITICO`, inclusive com evidência fraca ou dado atrasado.

## Implementação

- `contracts/severity.v1.json` é a fonte de verdade, com origem `bancada-2026` e `calibravel_por_modelo: true`.
- `api_tcc/contracts.py` valida valores finitos, faixa, métrica e vocabulário de evidência.
- `scripts/gen_contracts.py` valida e gera `frontend-next/src/lib/metricThresholds.ts`; `--check` detecta divergência.
- O firmware v0 não foi alterado. Não há diretório firmware neste checkout, então nenhum header C++ fictício foi criado.

## Verificação

- `python manage.py test api_tcc simulators -v 1`: 302 passaram.
- `python manage.py check`: passou.
- `python manage.py makemigrations --check --dry-run`: nenhuma alteração pendente.
- `python scripts/gen_contracts.py --check`: passou.
- `frontend-next`: `npm run type-check` e `npm run lint`: passaram.

Warnings de sklearn, fallback do Gemini e limitações históricas do Compose/Gitleaks permanecem como pendências ambientais/metodológicas, não como evidência de falha do contrato.
