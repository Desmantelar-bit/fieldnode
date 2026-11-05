# S1-T2 — evidência da escala de vibração

## Decisão D-02

No contrato v1, `vibracao` significa índice adimensional de 0 a 10 e `vibracao_unit` identifica `indice_0_10`. Não existe conversão automática de `g`; payload com `vibracao_unit: "g"` é rejeitado antes da persistência.

## Alterações

- `LeituraTelemetria.vibracao_unit` foi adicionado com default `indice_0_10` para novas leituras e compatibilidade de payload legado sem unidade.
- Migration `0027_leituratelemetria_vibracao_unit.py` depende de `0026_rename_tempumi_ambiente`.
- Validação rejeita unidade desconhecida, `g`, valores fora de 0–10, nulos, tipos inválidos e valores não finitos.
- Backend, simulador, normalização e frontend preservam a unidade do contrato.
- Cards, gráficos, schemas e detalhes não exibem `g` para o índice atual.

## Dados históricos

Nenhum dado foi convertido ou reseeded. O default da migration não é prova da origem de registros antigos; dados sem proveniência continuam sujeitos à ressalva documental.

## Verificação

O teste `api_tcc.tests.test_contract_v1` cobre unidade omitida, unidade válida, `g`, faixa e não finitos. A suíte completa passou com 302 testes. `npm run type-check` e `npm run lint` passaram. O hardware físico não foi declarado migrado: a separação v0/v1 permanece documentada.

## Limitações

Não foi produzida captura visual da aplicação em execução nesta tarefa. A documentação registra a unidade correta, mas isso não substitui uma captura real quando ela for exigida como evidência de aceitação.
