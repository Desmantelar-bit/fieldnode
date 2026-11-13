# S3-T2 — relatório de clientes tipados e polling

**Status: parcial.** Schemas, serviços, leitura validada e polling foram implementados. Ainda faltam teste de ciclo de vida do hook no browser, inspeção de rede e uma estratégia de cache compartilhado adequada à identidade da sessão.

## Contratos encontrados

- `GET /api/events/`: `IsAuthenticatedOrPublicDemo`; filtros `maquina_id`, `tipo`, `severidade`, `status`, `page` e `page_size`; página `{count,page,page_size,pages,next,previous,results}`. `page_size` default 20, limitado a 100. Página inválida retorna 400. Eventos têm severidade `NORMAL|ATENCAO|CRITICO`, status `ABERTO|FECHADO`, qualidade `boa|suspeita|insuficiente`, score de prioridade anulável e contexto JSON.
- `GET /api/decisions/`: mesma permissão e paginação; filtros `maquina_id`, `status`, `severidade`, `page`, `page_size`. Status `PENDENTE|APROVADA|REJEITADA|EXECUTADA|EXPIRADA`. O serializer não entrega transições permitidas nem histórico de auditoria; não foram inventados no schema.
- `GET /api/machines/<id>/health/`: usa a autenticação/permissão default do DRF (`IsAuthenticated`). Retorna `status` (`ok|sem_dados`), `trust_score_medio`, `ultima_atualizacao`, `leituras_analisadas` e `sinais_de_alerta`. Não entrega fatores legíveis, proveniência da última leitura ou intervalo esperado. Esses campos não foram simulados.
- O BFF Next mantém o token em cookie `fieldnode_session` HttpOnly e o encaminha como Token ao Django. Os novos serviços chamam `/api/...` no mesmo origin com `credentials: 'same-origin'`; nenhum token é lido pelo client.

## Implementação

- Schemas Zod explícitos em `eventos.ts`, `decisoes.ts` e `saude.ts`, com tipos inferidos e validação de enums/datas. `events.ts` foi consolidado como reexport do schema de eventos existente para evitar duplicação.
- `eventService`, `decisionService` e `healthService` usam o leitor comum `apiRead.ts`, que classifica autenticação, permissão, 404, 429, 5xx, rede, timeout e payload inválido. Falha de schema usa `safeParse`; diagnósticos de validação só são enviados ao console em desenvolvimento, sem imprimir o payload.
- `usePolling(fetcher, ms, enabled)` faz consulta inicial, agenda novo ciclo após terminar a anterior, cancela via `AbortSignal`, pausa e retoma em `visibilitychange`, e ignora aborts intencionais. O dashboard usa intervalo de 5 segundos.
- A tela atual tem apenas um consumidor deste polling. SWR existe no projeto, mas sua cache não foi ligada a estes clientes: ainda não há mecanismo de escopo/limpeza da cache por usuário/organização que permita compartilhar dados com segurança. Uma segunda instância pode repetir chamadas.
- As telas de eventos, decisões e saúde permanecem fora das tarefas S3-T3 a S3-T5; os serviços tipados ainda não foram ligados a essas telas.

## Testes e verificações

- `npm run test:s3-schemas`: 3 testes aprovados, cobrindo schemas paginados, enums, saúde sem dados, timestamp nulo, classificação de HTTP, schema inválido, rede e cancelamento propagado.
- `npm run test:s3-ui`: 1 teste aprovado para os estados de `DataStateBoundary`.
- `python manage.py test api_tcc.tests.test_data_origin api_tcc.tests.test_telemetria --verbosity 0`: 30 testes aprovados, incluindo serialização da proveniência.
- `npm run type-check`: aprovado.
- `npm run lint`: aprovado sem erros ou warnings.
- `npm run build`: aprovado.
- `python manage.py makemigrations --check --dry-run`: sem alterações pendentes.
- `git diff --check`: aprovado.

## Pendências e limites

- Não há teste de montagem do hook para provar em browser pausa/retomada, desmontagem, troca de parâmetros e ausência de sobreposição.
- Não foi feita inspeção de tráfego real nem medida de duplicação entre consumidores.
- A API de saúde não oferece intervalo esperado; o dashboard não marca um dado como antigo por limiar inventado. Em falha de atualização, mantém os dados com aviso.
- `docs/CLAIMS_VS_CODE.md` não existe neste checkout; nenhuma matriz foi atualizada.
- Nenhuma tela de decisão/atenção/TrustBadge foi antecipada. A tarefa S3-T2 permanece **parcial**, não concluída.
