# S3-T11 · E2E do fluxo central

## Implementação

A suíte foi organizada em `frontend-next/tests/e2e/central-flow.spec.ts`, com
configuração em `frontend-next/playwright.config.ts` e script
`npm run test:e2e`. O cenário principal não usa `page.route()` nem fixtures de
sucesso. O comando Compose `e2e_prepare_central_flow` cria usuário, organização
e máquina isolados, ingere uma leitura crítica pelo serviço real de telemetria,
confirma o `Event` CRITICO/P1 e cria a `Decision` pelo serviço central.

O teste verifica a API real do evento, percorre a tela de decisões, aprova,
registra o desfecho, recarrega a página e confere o histórico `AuditLog` real.
O vídeo é configurado como obrigatório e é copiado para
`docs/evidence/s3/fluxo-central.webm` pelo script de pós-execução.

## Ambiente

O Compose ativo contém `db`, `web`, `frontend`, `worker` e `mosquitto`. A
preparação usa apenas registros identificados pelo `run_id`; não executa
`down -v`, não remove volumes e não altera a massa de demonstração existente.

## Verificações executadas

VERIFICADO: `docker compose exec -T web python manage.py check`.

VERIFICADO: o comando de preparação gerou leitura, Event CRITICO, banda P1 e
Decision PENDENTE no MySQL do Compose.

VERIFICADO: a API de decisão persistiu as transições e a auditoria nos testes
backend existentes.

NÃO VERIFICADO nesta execução: três execuções Playwright verdes, vídeo final e
integração CI. A instalação de `playwright`/dependências npm no host ficou
bloqueada no registry, e o rebuild do frontend não concluiu a instalação.

Portanto, S3-T11 não deve ser marcado como concluído até essa execução externa
ser possível. O código e a infraestrutura de teste estão preparados para a
rodada final.
