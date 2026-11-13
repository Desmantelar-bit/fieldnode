# S2-T7 — Auditoria append-only e normalização de rotas

## Diagnóstico

O repositório já possuía `AuditLog`, mas era limitado a `actor_key`, `action`, `result`, `metadata` e `created_at`, usado pelos controles da S2-T2. O middleware de correlação já validava/gerava um ID e o devolvia em `X-Correlation-ID`. Não havia serviço central, proteção append-only nem registro da transição de estado de `Decision`. Login já era registrado parcialmente; logout, registro e provisionamento não tinham o mesmo contrato.

As únicas rotas duplicadas explícitas identificadas eram aliases sem barra de login, registro e logout. Os consumidores do frontend usam as rotas com barra. O projeto contém middleware `CommonMiddleware`; `APPEND_SLASH=False` agora evita redirecionamento automático de mutações para a rota canônica.

## Implementação

- A migration `0038_s2_t7_t8_audit_device_http` adiciona ao modelo existente objeto, IP, User-Agent, correlation ID, hashes e timestamp `criado_em`, preservando os campos e registros da S2-T2.
- `api_tcc.services.audit.record` centraliza a gravação. Hashes são SHA-256 de JSON canônico; estados de modelos usam whitelist explícita para não incorporar campos secretos futuros.
- A aprovação, rejeição e execução de decisões são registradas na mesma transação que a mudança de estado. Login, falha de login, logout, registro e ações de credenciais também usam o serviço.
- `AuditLog.save`, `delete`, QuerySet `update`, `delete`, `bulk_update` e `_raw_delete` rejeitam mutações existentes. O Admin permite consulta a quem tem permissão de visualização, sem criação, edição ou exclusão.
- O IP vem apenas de `REMOTE_ADDR`; `X-Forwarded-For` não é confiado. User-Agent é limitado a 512 caracteres.
- Rotas sem barra dos endpoints de autenticação foram removidas; a rota com barra é canônica.

## Verificação

VERIFICADO: testes de imutabilidade ORM, permissão do Admin, auditoria da aprovação (ator, objeto, correlation ID, User-Agent, hashes) e ausência de redirecionamento para login sem barra passaram em `api_tcc/tests/test_s2_t7_t8.py` e `api_tcc/tests/test_decisions.py`.

VERIFICADO: `manage.py check` e `makemigrations --check --dry-run` concluíram sem erros e sem mudanças de migration pendentes.

NÃO VERIFICADO: não foi gerada captura de tela do Admin. A restrição foi exercitada por teste das permissões do `ModelAdmin`.

## Limitações

A imutabilidade cobre o ORM e Admin, não acesso direto ao banco, migrations privilegiadas ou infraestrutura. Não há encadeamento de hashes, assinatura nem cópia externa imutável. `Membership` não possui fluxo de alteração de papel implementado no backend inspecionado; nenhuma rota fictícia foi adicionada. Exclusão de usuários com entradas de auditoria precisa ser tratada com cuidado porque alterações FK em cascata são barradas pelo append-only.
