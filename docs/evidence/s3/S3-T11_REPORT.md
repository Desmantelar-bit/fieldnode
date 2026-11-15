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

VERIFICADO: três execuções consecutivas no Compose, sequenciais, sem retry:

| Execução | Resultado | Duração aproximada | Retry |
| --- | --- | --- | --- |
| 1 | verde | 49,8 s | não |
| 2 | verde | 38,7 s | não |
| 3 | verde | 40,2 s | não |

VERIFICADO: `docs/evidence/s3/fluxo-central.webm` foi gerado pelo Playwright e
copiado pelo script de pós-execução.

O fluxo também corrigiu a restauração do detalhe após recarga e bloqueou
Service Worker durante E2E para impedir cache privado stale de mascarar o estado
real da API.

CI: configurado em `.github/workflows/fieldnode-e2e.yml`, com ambiente Compose
isolado, migrations, Chromium, execução de `npm run test:e2e` e upload de
relatórios/trace/vídeo. A execução no provedor GitHub não foi disparada neste
checkout, portanto permanece não verificada em ambiente remoto.
