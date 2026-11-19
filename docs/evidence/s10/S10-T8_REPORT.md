# S10-T8 · evidência

## Implementado

- `make gateway-up`, `make preflight` e `make cloud-up`;
- `scripts/preflight.sh` com verificações reais de Compose, backend, migrations,
  MQTT autenticado, frontend e relógio;
- `docs/DEPLOY.md` com separação local/nuvem, segurança, persistência e limites.

## Estado verificado

O Docker Desktop e os cinco serviços estavam disponíveis durante a auditoria
inicial. O preflight foi executado contra o Compose e retornou `preflight=OK`,
com backend, readiness, migrations, MQTT autenticado e frontend verificados.
O tempo de instalação em máquina limpa e o dashboard após clone permanecem
**NÃO VERIFICADOS**.

`cloud-up` está deliberadamente bloqueado até D-26 definir provedor e destino.
Não houve deploy público nem gravação da execução.
