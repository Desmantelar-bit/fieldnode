# S10-T7 · evidência

## Implementado

- executor controlado em `scripts/load/load_test.py` para A-F;
- coletor de cinco `EXPLAIN` em `scripts/load/explain_queries.py`;
- instruções e inventário em `scripts/load/README.md` e `docs/RELATORIO_CARGA.md`;
- índice não alterado porque os compostos pedidos já existem no modelo atual.

## Execução

Os seis perfis e as três repetições por perfil ainda precisam ser executados no
MySQL do Compose. A execução foi bloqueada de forma segura porque o banco não
possui `DeviceCredential` ativa e o ambiente não fornece chave de dispositivo.
Números, gargalo e saturação permanecem **NÃO VERIFICADOS**.

Cinco `EXPLAIN` foram coletados em `artifacts/load/explain.json` contra o MySQL
do Compose. Massa observada no momento: 1.580 leituras, 56 eventos e 52
decisões. O plano de Decision usou `filesort`; não houve migration porque a
massa é pequena e os índices compostos requeridos já existem no modelo.

Validações da estrutura: `py_compile`, `git diff --check`, `docker compose
config --quiet`, `manage.py check` e preflight passaram. A suíte pytest não
foi executável no host/container por dependências ausentes.
