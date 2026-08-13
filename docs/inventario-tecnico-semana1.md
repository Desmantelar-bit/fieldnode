# Inventario tecnico - Semana 1

Data: 2026-08-13

Escopo: levantamento do estado atual do FieldNode com base em testes executados,
leitura de codigo e evidencias observaveis. Nao inclui implementacao de novas
features.

## Evidencias executadas nesta rodada

| Comando | Resultado |
| --- | --- |
| `venv\Scripts\python.exe manage.py check` | OK, sem issues |
| `venv\Scripts\python.exe manage.py test api_tcc.tests.test_telemetria --verbosity=1` | OK, 3 testes passaram |
| `npm run lint` em `frontend-next` | Falhou antes de analisar codigo: erro de configuracao ESLint/React com estrutura circular |
| `venv\Scripts\python.exe manage.py test api_tcc --verbosity=1` | Falhou na descoberta de testes por conflito entre `api_tcc/tests.py` e pacote `api_tcc/tests/` |
| `venv\Scripts\python.exe scripts\validar_sistema.py` | 11/15 checks passaram |

## Tabela de inventario

| Componente | Estado | Evidencia | Prioridade |
| --- | --- | --- | --- |
| Backend Django | Validado parcialmente | `python manage.py check` passou sem issues; `setup/settings.py` aponta Django 5.2 e app `api_tcc` instalado | P0 |
| Django REST Framework | Presente | `rest_framework` em `INSTALLED_APPS`; views usam `APIView`, `Response` e serializers DRF | P0 |
| Endpoint de ingestao `/api/telemetria/` | Validado | `api_tcc/urls.py` registra `IngestaoTelemetriaView`; testes de ingestao passaram com 201, 400 e duplicata 200 | P0 |
| API key na ingestao | Validado | `views_ingestao.py` valida header `X-API-Key`; teste existente cobre ausencia com 401 em `api_tcc/tests.py` | P0 |
| Deduplicacao por UUID | Validado | `registrar_leitura()` retorna duplicata quando UUID ja existe; teste de telemetria passou | P0 |
| Validacao fisica do payload | Validado parcialmente | `validar_payload()` cobre ranges de temperatura, vibracao, rpm e GPS opcional; testes unitarios existem em `api_tcc/tests.py` | P0 |
| Rate limiting de ingestao | Validado no Bloco 1.3 | `IngestaoThrottle` usa `maquina_id`; flood anterior atingiu 429 na 121a requisicao com `status_counts={201: 1, 200: 119, 429: 1}` | P0 |
| Limite de payload | Observado | `DATA_UPLOAD_MAX_MEMORY_SIZE = 1 * 1024 * 1024` em `setup/settings.py`; nao foi feito teste de payload grande nesta rodada | P1 |
| Escopo do throttle | Observado | `DEFAULT_THROTTLE_CLASSES` permanece vazio; `IngestaoTelemetriaView.get_throttles()` aplica throttle somente em POST | P0 |
| Banco local SQLite | Requer atencao operacional | O flood anterior exigiu `migrate` local porque `db.sqlite3` estava sem coluna `seq_id`; apos migrar, ingestao funcionou | P1 |
| Migrations | Observado | Arquivos de migration existem ate `0008`; nenhum arquivo de migration foi criado nesta rodada | P1 |
| Suite completa Django | Pendente | `python manage.py test api_tcc` falha por conflito de descoberta entre `api_tcc/tests.py` e `api_tcc/tests/` | P1 |
| Testes focados de telemetria | Validado | `api_tcc.tests.test_telemetria` passou 3/3 | P0 |
| Pipeline de IA | Observado | `agendar_processamento_ia()` usa fila em thread daemon; `carregar_dados()` retorna `dados_insuficientes` quando falta amostra minima | P1 |
| Prescricoes | Observado | Rotas `/api/prescricoes/` e `/api/prescricoes/lista/` existem; testes de historico aparecem em `api_tcc/tests.py`, mas nao rodaram na suite ampla por problema de discovery | P1 |
| Metricas operacionais | Observado | `/api/metricas/` existe e `MetricasTest` aparece em `api_tcc/tests.py`; nao validado em rodada automatizada ampla | P2 |
| MQTT listener | Observado | `api_tcc/management/commands/mqtt_listen.py` existe e usa servico de telemetria; nao foi executado nesta rodada | P2 |
| Simulador MQTT/fallback HTTP | Observado | `scripts/simular_mqtt.py` existe; README documenta fallback HTTP; nao foi executado nesta rodada | P2 |
| Frontend Next.js | Parcial | Estrutura `frontend-next` existe com rotas principais; `npm run lint` falhou por configuracao antes de avaliar codigo | P1 |
| Service Worker offline | Observado | `frontend-next/public/sw.js` intercepta POST de telemetria, usa IndexedDB e reenvia em sync; nao foi validado em navegador nesta rodada | P1 |
| Mapa/GPS | Observado | Rota `/api/maquinas/posicao/` existe e frontend tem componentes de mapa; nao foi testado visualmente nesta rodada | P2 |
| Relatorios | Observado | Rotas `/api/relatorio/` e `/api/relatorio/exportar/` existem; nao foi executado teste funcional nesta rodada | P2 |
| Docker | Parcial | `docker-compose.yml` e Dockerfiles existem; validador indicou pendencia em apontamento do frontend para API interna | P1 |
| Swagger/Redoc | Observado | `setup/urls.py` registra `/swagger/`, `/swagger.json/` e `/redoc/`; nao foi aberto nesta rodada | P2 |
| Scripts de validacao | Parcial | `scripts/validar_sistema.py` retornou 11/15; pendencias incluem frontend antigo e checks de rotas/config | P2 |
| Frontend legado | Pendente de decisao | `frontend-old/` ainda existe; validador espera remocao, mas nao faz parte do Bloco 1.4 alterar legado | P3 |
| Higiene do repositorio | Parcial | Antes do inventario, `git status --short` mostrava apenas Bloco 1.3 pendente; este documento e novo artefato do Bloco 1.4 | P0 |

## Pendencias recomendadas

| Prioridade | Pendencia | Motivo |
| --- | --- | --- |
| P1 | Corrigir descoberta da suite Django completa | A suite ampla falha antes de rodar os testes por conflito de layout |
| P1 | Corrigir configuracao do ESLint no `frontend-next` | O lint falha antes de avaliar codigo, reduzindo confianca no frontend |
| P1 | Decidir politica para `frontend-old/` | O validador espera remocao, mas o diretorio ainda existe |
| P1 | Validar payload acima de 1MB em teste dedicado | A configuracao existe, mas ainda falta prova automatizada |
| P2 | Executar validacao visual do frontend e mapa | Componentes existem, mas nao foram verificados em navegador nesta rodada |
| P2 | Testar MQTT/fallback HTTP em ambiente controlado | Fluxo documentado e script existem, mas nao foram exercitados agora |
