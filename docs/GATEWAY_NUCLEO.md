# Gateway edge do FieldNode

## Estado desta fatia

Esta documentação cobre o perfil Compose edge e a autenticação local sobre o banco previamente provisionado. Ela não declara replicação bidirecional, DomainChange, HLC, hotspot físico ou ML runner como concluídos.

## Inicialização

No gateway, copie `.env.example` para `.env`, defina uma `SECRET_KEY` própria, credenciais do banco, `NODE_ROLE=edge` e um `NODE_ID` estável. O `NODE_ID` deve ser provisionado uma vez por instalação e preservado no `.env` ou no mecanismo de secrets do host.

```text
make edge-up
make edge-status
make edge-logs
```

O overlay usa MySQL local persistente em `/srv/fieldnode/mysql` por padrão, expõe apenas a API, o frontend e o MQTT no endereço configurado, e não expõe a porta do MySQL no host. `make edge-down` não remove volumes.

## Autenticação offline

`OFFLINE_AUTH=true` significa que o gateway usa seus dados locais já provisionados. Não é bypass: tokens continuam expirando, lockout e rate limiting continuam persistidos no banco, auditoria continua local e as permissões continuam sendo verificadas por membership e organização no backend. A revogação feita na nuvem só chega ao gateway quando existir sincronização.

O repositório já possui `User`, `Membership`, token DRF expirável e `AuditLog`. A replicação segura de usuários, memberships, papéis, revogações e estado pendente depende do protocolo de replicação futuro e permanece PENDENTE nesta fatia.

## Limites verificados

- IMPLEMENTADO: validação centralizada de `NODE_ROLE` e `NODE_ID`.
- IMPLEMENTADO: overlay edge, persistência MySQL, restart policies e unidade systemd preparada.
- IMPLEMENTADO: login contra o banco local existente, com token expirável e permissões backend.
- PENDENTE: ML runner local, porque não existe contrato/serviço de inferência independente no repositório.
- PENDENTE: teste sem internet, reboot físico, 20 ciclos de energia e decisão D-34, pois exigem gateway e evidência operacional.
- PENDENTE: replicação bidirecional, DomainChange, HLC, conflitos e usuários criados em emergência.

Não usar credenciais de demonstração como instalação permanente. O hotspot exige senha fornecida pelo ambiente do host e não é ativado automaticamente.
