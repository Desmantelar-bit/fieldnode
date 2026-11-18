# S9-T1 - Relatório de execução

## Auditoria

- `Machine` canônica já existia desde S1-T1, com `Organization` opcional para
  backfill e relações de telemetria, eventos, decisões e ordens.
- `Transbordo` é um modelo legado de catálogo/capacidade e não possui vínculo
  canônico com `Machine` ou organização suficiente para migração automática.
- Não havia `Site`, `Front`, `MachineLink` nem serviço de navegação do grafo.
- A sequência de migrations existente terminava em `0053`; foi criada a
  `0054_machine_tipo_site_front_machine_site_machinelink_and_more.py`.

## Implementação

- `Machine.tipo` foi adicionado como nullable para não converter registros
  históricos desconhecidos silenciosamente.
- `Machine.site` foi adicionado como relação opcional para permitir contexto
  operacional incremental.
- `Site` e `Front` têm organização, identificação, ciclo de vida e validação
  de pertencimento.
- `MachineLink` suporta apenas `ALIMENTA`, `TRANSPORTA_PARA` e `DEPENDE_DE`,
  validade temporal, auditoria básica e constraints de autorreferência/ordem
  de datas.
- `api_tcc/services/operation_graph.py` implementa criação, encerramento e
  BFS limitado com semântica direcional explícita.
- O serviço preserva histórico: encerrar atualiza `valido_ate`; nova relação
  cria outra linha.

## Testes

`api_tcc/tests/test_operation_graph.py` cobre criação, isolamento, Site/Front,
autorreferência, datas, sobreposição, encerramento, profundidade, ciclos,
direção de dependência, validade e máquina sem organização.

Resultado verificado: `venv\Scripts\python.exe manage.py test
api_tcc.tests.test_operation_graph --verbosity 1` passou com **10 testes**;
`python -m pytest api_tcc/tests/test_operation_graph.py
api_tcc/tests/test_machine.py -q` passou com **29 testes**.
Também foi verificado `manage.py check` sem problemas e
`makemigrations --check --dry-run` sem mudanças pendentes.

A suíte ampla do repositório executou 470 testes, mas terminou com duas falhas
preexistentes nos mocks do listener MQTT e um erro de importação porque
`ml.eval.test_public_dataset` depende de `pytest`, ausente no ambiente `venv`.
Esses pontos não são causados pelo Operation Graph e permanecem separados do
aceite desta tarefa.

## Limitações e pendências

- A migração conservadora do legado `Transbordo` foi avaliada e não executada,
  pois faltam dados confiáveis para organização e identidade canônica.
- Não há endpoints, UI, Incident, ConsequenceAssessment ou cálculo financeiro.
- O grafo representa somente relações cadastradas, não a verdade atual do campo.
