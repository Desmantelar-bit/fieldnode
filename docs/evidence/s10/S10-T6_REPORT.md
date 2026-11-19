# S10-T6 - evidência

Status inicial: **IMPLEMENTAÇÃO ENTREGUE; VALIDAÇÃO AUTOMATIZADA PENDENTE**.

Implementado: política por `OrganizationPolicy`, comando `purgar_dados_antigos`, dry-run, execução em lotes, isolamento por organização, exportação canônica com hash, `RetentionPurgeRun` e registro em `AuditLog`.

Verificado no Compose: `python manage.py test api_tcc.tests.test_retention --noinput` passou com 2 testes, cobrindo dry-run, isolamento entre duas organizações e bloqueio sem política. `manage.py check` também passou, com três avisos preexistentes do MySQL sobre constraints condicionais.

Pendente: validação de exportação de decisões com desfecho, teste de interrupção/retomada e aprovação dos prazos. Nenhum prazo foi apresentado como obrigação legal ou contratual.
