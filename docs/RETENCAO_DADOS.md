# Política de retenção, exportação e exclusão

## Princípios

Os prazos são hipóteses operacionais até aprovação contratual. Política ausente, categoria ausente ou valor inválido bloqueia exclusão automática. `0`, `NULL` e campo ausente não significam apagar.

## Matriz inicial

| Categoria | Fonte e marco temporal | Sensibilidade | Prazo |
|---|---|---|---|
| Telemetria bruta | `LeituraTelemetria.recebido_em` | alta, pode conter GPS | por organização, obrigatório aprovar |
| Telemetria canônica | `CanonicalTelemetry.criado_em` | operacional | por organização, obrigatório aprovar |
| Telemetria agregada | `TelemetryAggregate.recebido_em` | operacional | por organização, obrigatório aprovar |
| Eventos | `Event.criado_em` | operacional e histórico | por organização, obrigatório aprovar |
| Incidentes | `Incident.criado_em` | operacional | por organização, obrigatório aprovar |
| GPS | `LeituraTelemetria.recebido_em`, apenas coordenadas presentes | sensível | por organização, obrigatório aprovar |
| Auditoria | `AuditLog.created_at` | evidência de controle | não é purgada pelo comando |
| Decisões | `Decision.criado_em` | histórico de decisão | não é purgada automaticamente |
| Auxiliares | DLQ, rejeições, hops, cursores | varia | revisão específica antes de apagar |

Os prazos aprovados vivem em `OrganizationPolicy.retention_policy`, como inteiros em dias, com `retention_policy_version` e data de vigência. O modelo existente de organização é reutilizado; não há configuração global fingindo ser contrato de cliente.

## Operação

```bash
python manage.py purgar_dados_antigos --organization UUID --dry-run
python manage.py purgar_dados_antigos --organization UUID --category eventos --dry-run
python manage.py purgar_dados_antigos --organization UUID --category telemetria_canonica --execute --export-dir ./retention-exports
```

O comando exige exatamente `--dry-run` ou `--execute`, trabalha em lotes, filtra no backend pela organização e grava `RetentionPurgeRun` mais `AuditLog`. Registros protegidos por relações históricas são preservados e contabilizados. O `--export-dir` gera JSON canônico com contagem e SHA-256.

Decisões com desfecho (`APROVADA`, `REJEITADA`, `EXECUTADA`, `EXPIRADA`, `decidido_em` ou `outcome_texto`) não são apagadas pela rotina. Antes de qualquer desenho futuro que permita isso, o histórico precisa ser exportado, validado e auditado. `AuditLog` também não é apagado: a purga não pode apagar a prova da própria purga.

## Backup e restore

Backups podem conter dados já purgados do banco ativo. A exclusão do banco não remove cópias históricas. Após restore, reaplicar exclusões autorizadas e registrar nova execução; não prometer eliminação imediata de backups imutáveis.

## Limites atuais

Não há endpoint de exportação/exclusão por organização implementado nesta entrega. O mecanismo entregue é o comando administrativo, sem autorização baseada apenas em um UUID fornecido pelo frontend. Prazos, agendamento, armazenamento externo e retenção legal continuam dependentes de aprovação operacional e contratual.
