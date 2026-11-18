# S10-T1 · Relatório de CI

Status: IMPLEMENTAÇÃO LOCAL VERIFICADA; EXECUÇÃO REMOTA PENDENTE

## Implementado

- `.github/workflows/ci.yml` com jobs para SQLite, MySQL 8, compilação Python,
  frontend, contratos, firmware, segurança, migrations e documentação.
- Os workflows especializados de firmware e E2E ganharam `workflow_call` para
  serem reutilizados sem duplicar YAML.
- `scripts/check_docs_status.py` verifica documentos obrigatórios e o status
  explícito `Status: ESQUELETO`, sem bloquear texto explicativo ou roadmap.
- `Makefile` ganhou comandos locais para backend, frontend, firmware,
  documentação e execução combinada.

## Limites da evidência

Os jobs do GitHub Actions não foram executados nesta bancada e nenhuma URL de
run ou proteção administrativa da branch `main` foi verificada. A política de
proteção precisa ser configurada no GitHub por um administrador, exigindo os
checks publicados pelo workflow.

Black, Flake8 e Prettier não são dependências nem scripts adotados atualmente;
o CI não finge que são executados. O job Python faz compilação e coleta dos
testes. A adoção dessas ferramentas, se desejada, é trabalho separado.

Firmware compilado em CI continua sendo artefato de compilação, não validação
em bancada ou em máquina real. O E2E permanece sob demanda no CI com a label
`run-e2e`, ou manualmente.

Na primeira execução da suíte completa local, foram coletados 485 testes: 2
falhas nos mocks de correlação MQTT e 1 erro de retorno no caminho de DLQ.
Após a correção desses pontos, a repetição executou os mesmos 485 testes em
166,789 s com resultado `OK`.

## Execução remota ainda necessária

1. Abrir PR de teste e observar os jobs.
2. Exercitar falhas controladas em branch isolada para banco, frontend,
   contrato, firmware, segurança e documentação.
3. Configurar branch protection e registrar a captura/URL dos checks.
