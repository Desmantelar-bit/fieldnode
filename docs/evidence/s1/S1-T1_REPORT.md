# S1-T1 / S1-T2 — execução neste checkout

## Resultado

Implementação realizada para o contrato de severidade e escala de vibração v1. As alterações staged existentes no checkout foram preservadas; os artefatos apagados no estado staged foram recriados no diretório de trabalho. Este relatório documenta somente validações executadas nesta execução.

## Decisões

- D-01: comparação inclusiva `>=`; fronteiras testadas em temperatura e vibração.
- D-02: `vibracao` é índice adimensional 0–10 (`indice_0_10`). Unidade `g` não é convertida e é rejeitada. O campo ausente usa o default do contrato para manter compatibilidade com payload legado; isso não prova a proveniência histórica.
- Classe de transmissão: CRÍTICO tem precedência e sempre é A. Evidência não `boa` ou atraso em casos não críticos conduz a B.
- Firmware físico continua em v0. Não foi criado header ou declarada migração do hardware.

## Arquivos centrais

- `contracts/severity.v1.json`: fonte de limiares heurísticos de bancada.
- `api_tcc/contracts.py`, `api_tcc/services/telemetria.py`, `api_tcc/services/eventos.py`: carregamento, classificação e validação.
- `api_tcc/models.py` e migration `0027_leituratelemetria_vibracao_unit.py`: unidade persistida; valores históricos não foram convertidos.
- `scripts/gen_contracts.py` e `frontend-next/src/lib/metricThresholds.ts`: geração e modo `--check`.
- Simulador, validação/visualização frontend e documentação: alinhados ao índice 0–10.

## Verificações realizadas

- `python manage.py test api_tcc simulators -v 0`: 302 testes passaram.
- `python manage.py check`: sem problemas.
- `python manage.py makemigrations --check --dry-run`: nenhuma migration pendente.
- `python scripts/gen_contracts.py --check`: artefato TS verificado.
- `npm run type-check` e `npm run lint`: passaram após as alterações finais no card.
- `npm run build`: passou após as alterações finais, com 14 páginas estáticas geradas.

## Paridade e limitações

Não foi executada varredura 0–150/0,1 e 0–10/0,05 comparando backend, borda e TypeScript, nem foi produzido CSV/JSON de paridade. A borda importa diretamente o classificador Python; TypeScript não foi executado numa harness independente. Portanto, paridade tripla e critério de zero divergências permanecem NÃO VERIFICADOS. O gerador atual emite TypeScript, não header C++; não há firmware v1 reivindicado.

Busca manual indicou que ainda há literais `g` em comentários e outros arquivos de relatório/histórico a classificar; o texto dos relatórios principais foi atualizado, mas não foi concluída auditoria automatizada abrangente de todos os resíduos. Verificação visual/captura de tela não foi produzida.
