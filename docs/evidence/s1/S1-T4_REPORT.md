# S1-T4 — fila de telemetria do Service Worker

## Estado inicial e diagnóstico

O checkout estava limpo no início. A store IndexedDB `fieldnode-offline/telemetria-pendente` usava `localId` e versão 1; itens guardavam URL, headers, payload e `createdAt`, sem estado ou tentativas. `syncTelemetriaData` interrompia no primeiro não-2xx ou erro de rede. Não havia contagens, desbloqueio de autenticação ou reprocessamento na interface.

## Schema e ciclo de vida

A store atual foi preservada; o banco sobe para versão 2 sem apagar nem renomear itens. Cursor de upgrade inicializa os registros existentes; os defaults também são aplicados ao ler. Cada registro mantém `{localId,url,headers,payload,createdAt}` e adiciona `state`, `attempts`, `last_error`, `next_attempt_at`.

Estados: `pending` envia quando elegível; `retrying` aguarda backoff; `rejected` permanece armazenado até reprocessamento explícito; `auth_blocked` não envia até recuperação de autenticação. Migração não muda a chave nem payload.

- 2xx: apaga apenas após ACK e incrementa `synced`.
- 400/403/404/409/422 e demais 4xx permanentes: persiste `rejected`, mantém item, erro limitado ao status HTTP e não reenvia automaticamente.
- 401: persiste tentativas, bloqueia itens não rejeitados e sinaliza `AUTH_REQUIRED`; após login bem-sucedido ou sessão existente, converte `auth_blocked` em `pending`.
- Rede, 408, 429 e 5xx: `retrying`, incrementa tentativas e agenda novamente. Backoff exponencial `1s × 2^(attempts-1)`, máximo de 1h. `Retry-After` em segundos/data tem precedência, limitado a 1h.
- Sincronizações concorrentes na mesma instância do SW são serializadas com flag; fila é recontada e enviada aos clientes após sync.

`last_error` não armazena corpo da resposta, token ou payload. IndexedDB continua sendo fonte única da fila.

## UI

`ApiStatusIndicator` apresenta contagem de pendentes, retentativas, rejeitadas e bloqueadas por autenticação; mostra motivo HTTP das rejeições, ação para reprocessá-las e link de login. Falha ao consultar a store é distinta de fila vazia. `ServiceWorkerBridge` traduz mensagens do SW para eventos da página.

Captura do indicador: `docs/evidence/s1/S1-T4-queue-indicator.png`. Foi feita no navegador real Chrome via Playwright com um fixture de estado do indicador (2 pendentes, 1 retentativa, 1 rejeitada, 1 bloqueada). Os dados do fixture são simulados para exercitar a representação; não são telemetria persistida de uma sessão de campo.

## Verificação executada

- `node frontend-next/tests/service_worker_queue_test.cjs`: passou `[200,400,200]` (duas remoções após ACK, uma rejeitada, terceira enviada), 401 bloqueia e preserva fila, liberação após autenticação, 503 backoff e elegibilidade, 408/429 (com e sem Retry-After)/500, 400/403/404/409/422 permanentes sem retry automático e reprocessáveis, erro de rede isolado.
- `node frontend-next/tests/service_worker_indicator_test.cjs`: passou as contagens, erro HTTP 422, login necessário; captura salva.
- `npm run lint`: passou.
- `npm run type-check`: passou.
- `npm run build`: passou; 14 páginas estáticas/dinâmicas listadas pelo Next.
- `python manage.py test api_tcc -v 1`: 314 testes passaram após unir o grafo de migrations.
- Testes SW para IndexedDB indisponível, reinicialização do worker e concorrência entre contextos independentes: NÃO EXECUTADOS. O type-check também apontou uso nullable de `useSearchParams` numa tela de detalhes trazida no merge remoto; a guarda mínima foi corrigida e lint/type-check/build passaram depois.

## Limitações e pendências

A serialização evita sobreposição dentro da mesma instância do Service Worker; não foi feito lock transacional entre múltiplos contextos independentes. A harness de fila modela IndexedDB/fetch em Node, não executa o ciclo de upgrade em navegador real. A captura exercita a UI por fixture, não por itens persistidos numa base IndexedDB de sessão real. Falhas de leitura IndexedDB são encaminhadas para estado de erro, mas o teste automatizado dessa falha permanece pendente.


