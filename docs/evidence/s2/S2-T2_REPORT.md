# S2-T2 — Throttle global, lockout e registro por flag

**Status: PARCIAL (controles e testes de aplicação implementados; validação de dois workers pendente).**

## Implementação

- DRF usa `AnonRateThrottle` a `60/minute` e `UserRateThrottle` a `300/minute`; ingestão conserva `IngestaoThrottle` junto aos limites globais.
- Login adiciona contadores transacionais no banco para `5/minute` por `REMOTE_ADDR` e identidade normalizada. A identidade e os índices de contador são HMAC com `SECRET_KEY`; `X-Forwarded-For` não é confiado.
- Cinco falhas por identidade armam bloqueio de 15 minutos. A tentativa seguinte recebe `429` genérico. Falha e sucesso retornam mensagens sem indicação de existência da conta.
- Registro tem `REGISTRATION_ENABLED=False` por padrão, sempre retorna `403` quando desabilitado ou em `DEMO_MODE`, e, quando habilitado fora de demo, aplica `3/hour` por IP.
- `SecurityCounter` usa transação e row lock compartilhados por processos; erro nessa infraestrutura responde `503` e não libera autenticação. `DatabaseCache` substitui `LocMemCache` para throttles DRF e usa tabela `fieldnode_throttle_cache`.
- `cleanup_security_counters` remove linhas expiradas; deve ser agendado (sugestão documentada: a cada 15 minutos). Nenhum scheduler foi adicionado.
- `AuditLog` registra tentativas, bloqueios, sucessos e bloqueios de cadastro com identidade HMAC e metadados sem senha/token.

## Evidências de teste

- A execução posterior das suítes de segurança, autenticação, correlação, decisões agentivas e permissões terminou com **77 testes aprovados**. Cobriu flag de registro, 50 tentativas sem usuários criados, limite de login por IP e identidade, falha genérica existente/inexistente, janela de lockout, falha fechada, anti-spoof MQTT e boot do worker.
- Na execução combinada de 85 testes (`test_week2_security`, `test_auth`, `test_correlation`, `test_integration`, `test_agentic`), 83 passaram. Os dois testes que falharam são expectativas antigas no módulo de integração: ele espera `status="ok"` e `status="duplicata ignorada"`, enquanto o código atual do contrato retorna `acked` e `duplicate`; os handlers de ingestão não foram alterados nesta tarefa.
- `python -m py_compile` passou nos módulos Python alterados.
- `python manage.py makemigrations --check --dry-run` informou “No changes detected” depois das migrations 0036/0037.
- A suíte completa anterior executou 349 testes, mas terminou com 6 falhas e 1 erro; essa execução antecedeu correções de testes de IP e tópico MQTT e a migration de auditoria. **Não foi repetida integralmente.**
- `python -m pytest` não coletou testes: `pytest-django` não está instalado neste ambiente. `manage.py test` foi usado no lugar.
- **NÃO VERIFICADO:** 100 logins contra Gunicorn com dois workers, concorrência real de banco, compartilhamento/recuperação no MySQL, 50 cadastros habilitados contra Gunicorn e ausência de regressão dos endpoints de leitura sob carga.

## Limitações

- O teste de concorrência real exige MySQL e dois workers; SQLite de teste não prova a semântica de row lock do MySQL.
- O cache DRF é compartilhado via banco, mas as operações internas de `DatabaseCache` para os throttles genéricos não são tratadas como contadores estritamente atômicos. O limite crítico de login/registro usa `SecurityCounter` transacional.
- A tabela de contadores precisa da rotina `cleanup_security_counters` agendada em produção.
