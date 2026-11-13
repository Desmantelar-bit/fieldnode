# S3-T5 — relatório de implementação

## Diagnóstico e mudanças

- O repositório já possuía `PATCH /api/decisions/<id>/`, validação transacional das transições e `AuditLog`; faltavam `transicoes_permitidas`, evidências e interface.
- `DecisionSerializer` agora expõe transições de acordo com o estado e com a permissão de escrita do usuário, mais o evento e leitura de origem quando vinculados.
- O detalhe GET expõe eventos de auditoria da decisão em ordem cronológica. A trilha preserva ator, ação e horário; o AuditLog guarda hashes de estado, não snapshots dos valores anteriores.
- Foi criada a rota `/decisoes`, com fila, evidência disponível, ações permitidas, campo rotulado “Resultado informado pelo operador” e histórico. As mutações são otimistas e revertem a fila/detalhe quando a API retorna erro.

## Verificação executada

- `python -m pytest api_tcc/tests/test_decisions.py -q` — 9 testes aprovados no ambiente virtual do repositório.
- `python manage.py check` — sem problemas.
- `npm run lint` — concluído sem erros ou avisos.
- `npm run type-check` — concluído sem erros.
- `git diff --check` — sem erros; Git avisou que normalizará LF para CRLF nos arquivos de schema e serviço.

## Pendências de aceite

- Não foi executado E2E nem gravada demonstração; o ambiente não foi iniciado nesta tarefa.
- “Adiar” não está implementado: a máquina atual não possui estado de adiamento ou data de retorno. `EXPIRADA` é uma transição distinta e não foi reinterpretada como adiamento.
- Evidência de janela/limiar/regra e versão só aparece se estiver persistida nos dados de evento; ainda não foi construída uma apresentação completa desses campos.
- Asserções específicas para `transicoes_permitidas`, timeline nova, falha otimista e permissão de leitura não foram adicionadas ao conjunto de testes.

**Status:** integração parcial; critério de aceite E2E ainda não demonstrado.
