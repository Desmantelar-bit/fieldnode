# Protocolo de teste de resiliência offline

Este documento descreve a validação de bancada do `simulators/edge_client.py`.
Os resultados devem ser preenchidos com logs reais da execução, não com valores
estimados.

## Execução

```powershell
python simulators/edge_client.py --device-id edge-bench-01 --count 50 --offline
python simulators/edge_client.py --device-id edge-bench-01 --sync-only
```

O cliente usa o contrato existente `POST /api/telemetria/` com `X-API-Key`.
Cada leitura é persistida primeiro, e o ACK precisa devolver o mesmo
`message_id` e `payload_hash`.

## Evidência a registrar

- contagem local por status antes e depois da recuperação;
- distribuição A/B/C e ordem de despacho;
- cursor contíguo local inicial/final;
- contagem de leituras no backend e duplicatas após replay;
- caso de hash divergente, que deve permanecer em `ERRO`;
- tentativas, tempos de retry e resposta para 401/403.

## Lacuna conhecida do contrato S1-T5

O `SyncCursor.last_acked_sequence` do servidor atualmente representa o maior
sequence recebido, não o maior sequence contíguo. O cliente não usa esse valor
para declarar ACK cumulativo: mantém um cursor local contíguo, avançando somente
quando não existem lacunas no outbox. Uma migração futura pode tornar o cursor
do servidor contíguo sem criar outro endpoint de ingestão.

## Resultado real

```text
PASS — cenário executado em 2026-10-08 com Docker Compose, MySQL 8 e o
edge_client local. Device: edge-s8-t1-20261008-01. O banco não tinha leituras
anteriores desse device (baseline = 0).

Distribuição local e no servidor: A=5, B=15, C=30.

Antes da recuperação, com o endpoint HTTP parado:
- SQLite: 50 PENDENTE; 0 SINCRONIZADA; cursor local contíguo = 0.
- message_id distintos = 50; sequence_number distintos = 50.
- Contagem por prioridade no outbox: A=5, B=15, C=30.
- Health endpoint: conexão recusada; db, mosquitto e worker continuaram ativos.

Após a recuperação e sincronização:
- SQLite: 50 SINCRONIZADA; 0 PENDENTE; cursor local contíguo = 50.
- MySQL: 50 leituras para o device; 50 message_id distintos; 50
	sequence_number distintos; duplicatas por message_id = 0; duplicatas por
	sequence_number = 0.
- Os 50 ACKs foram aceitos com message_id e payload_hash correspondentes; não
	houve sequência restante no outbox.
- Ordem comprovada por recebido_em no MySQL: Classe A entre
	2026-10-08T13:13:57.942172Z e 2026-10-08T13:13:58.454760Z; Classe B entre
	2026-10-08T13:13:58.596678Z e 2026-10-08T13:14:00.333408Z; Classe C entre
	2026-10-08T13:14:00.444640Z e 2026-10-08T13:14:03.608189Z. Portanto, a
	última A chegou antes da primeira B, e a última B antes da primeira C.
- Ordem de despacho observada nos ACKs: A sequences 1, 11, 21, 31, 41; B
	sequences 4, 7, 10, 13, 16, 19, 22, 25, 28, 34, 37, 40, 43, 46, 49; em
	seguida as 30 mensagens C.

Comandos executados (PowerShell; a API key foi obtida do ambiente do container,
sem ser impressa ou gravada neste documento):

```powershell
docker compose up -d db mosquitto worker
docker compose build web
docker compose run --rm web python manage.py migrate --noinput
docker compose run --no-deps --service-ports --name api-tcc-s8-t1-web-2 web gunicorn setup.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120 --access-logfile - --error-logfile -
docker stop api-tcc-s8-t1-web-2
python simulators/edge_client.py --device-id edge-s8-t1-20261008-01 --count 50 --offline --buffer-path "$env:TEMP\fieldnode-edge-s8-t1-20261008.sqlite3"
docker start api-tcc-s8-t1-web-2
python simulators/edge_client.py --device-id edge-s8-t1-20261008-01 --sync-only --buffer-path "$env:TEMP\fieldnode-edge-s8-t1-20261008.sqlite3" --api-url http://127.0.0.1:8000/api/telemetria/ --timeout 10 --max-attempts 5 --backoff-base 2 --backoff-max 60
```

Evidências/logs relevantes:

```text
BACKEND_OFFLINE=YES (connection refused/unreachable)
counts={'PENDENTE': 50}
OUTBOX_GROUPS=[('PENDENTE','A',5),('PENDENTE','B',15),('PENDENTE','C',30)]
UNIQUE_MESSAGE_IDS=50
UNIQUE_SEQUENCES=50
HEALTH=ok
ACKs aceitos: 50; cursor_contiguo local final=50
OUTBOX_GROUPS=[('SINCRONIZADA','A',5),('SINCRONIZADA','B',15),('SINCRONIZADA','C',30)]
SERVER_COUNT=50
DUPLICATE_MESSAGE_ROWS=0
DUPLICATE_SEQUENCE_ROWS=0
SERVER_ASSERTIONS=PASS
```

Ocorrências e limites observados durante o ensaio:
- O comando `web` padrão do Compose não iniciou: `collectstatic` falhou por
	ausência de `STATIC_ROOT`, e o shell tentou executar `--bind` como comando.
	Para não alterar configuração fora do escopo, o backend foi iniciado com o
	Gunicorn explícito no container Compose, após reconstruir a imagem `web`.
- A primeira imagem `web` era antiga. Depois de reconstruí-la, as migrations
	0020–0022 apareceram pendentes; foram revisadas (novos campos/tabela e opções)
	e aplicadas. O schema então passou a corresponder ao código atual.
- As tentativas HTTP anteriores à aplicação das migrations responderam 500 e
	permaneceram no outbox; nenhuma leitura desse device foi gravada. O cliente
	também removia a barra final da URL, causando 500 em Django. O cliente agora
	preserva a barra final; o teste standalone verifica essa normalização.
- Não houve alteração no contrato de SyncCursor. O cursor local do edge é
	contíguo e terminou em 50. O SyncCursor do servidor continua representando
	o maior sequence recebido, não o maior contíguo; este ensaio não o trata como
	ACK cumulativo nem como prova de ausência de lacunas.
```

Este experimento prova um protocolo de outbox em cliente Python de bancada. Ele
não prova operação em ESP32, persistência em flash, autonomia energética,
perda de energia, rádio, armazenamento por 30 dias ou segurança física da
credencial.

## S8-T2 - protocolo automatizado de resiliencia

O ensaio S8-T2 e orquestrado por `simulators/teste_resiliencia.py`. O script
usa o `edge_client.py` real, cria um `device_id` exclusivo por rodada, para
somente o servico HTTP `web`; o MySQL `db` e o armazenamento local da outbox
permanecem ativos. O script nao controla o broker `mosquitto` nem o `worker`;
os horarios de criacao/inicio desses sidecars devem ser conferidos nos registros
de cada execucao. A identificacao da rodada e externa ao payload: o `device_id`
contem o identificador da execucao, portanto o contrato de ingestao nao foi
alterado para facilitar o teste.

Execucao oficial, com os tempos definidos no S8-T2:

```powershell
python simulators/teste_resiliencia.py
```

O script espera a API responder `GET /api/health/` depois do `docker compose
start web`, observa a outbox SQLite durante a sincronizacao e consulta o banco
do Compose filtrando pelo `device_id` da rodada. Ele grava o JSON bruto em
`artifacts/resilience/resultados.json` e imprime a tabela resumida. Para uma
fumaca curta, util apenas para verificar a mecanica do script:

```powershell
python simulators/teste_resiliencia.py --durations 1,2,3 --count 10
```

### Metricas

| Campo | Definicao |
| --- | --- |
| `generated` | `message_id` distintos registrados na outbox local |
| `received` | `message_id` distintos persistidos no backend para o `device_id` da rodada |
| `lost` | `generated - received` |
| `duplicate_attempts` | tentativas na outbox menos a primeira tentativa de cada leitura |
| `duplicate_persisted` | linhas no banco menos `message_id` distintos; duplicatas por `sequence_number` tambem sao conferidas |
| `out_of_order` | ao ordenar por `recebido_em`, conta cada leitura cujo `sequence_number` e menor que o maior sequence recebido anteriormente |
| `downtime_actual_seconds` | tempo monotonicamente medido depois que `docker compose stop web` termina ate o health endpoint responder saudavel |
| latencia do primeiro ACK (derivada) | `first_successful_sync_at - backend_ready_at`; ambos os timestamps estao no JSON bruto |
| `recovery_time_seconds` | tempo entre `backend_ready_at` e o ultimo ACK; representa a recuperacao completa, com toda a outbox drenada |
| `total_sync_time_seconds` | tempo medido desde o inicio do processo de sincronizacao ate o ultimo ACK |

### Resultado S8-T2

Resultados executados em 2026-10-09. Todos os horarios sao UTC.

R1 e R2 foram produzidas pelo script de forma autonoma e nao sofreram edicao
posterior. R3 usa o resultado de `edge-s8-t2-r3-0caf9760c3c6`, unico candidato
cujo status VALID foi gerado pelo script sem intervencao manual; os dados sao
copiados fielmente de `artifacts/resilience/resultados-pre-concorrencia-r3.json`.

| Cenario | Device ID | Indisponibilidade real | Geradas | Recebidas | Perdidas | Tentativas duplicadas | Duplicatas MySQL | Fora de ordem | 1o ACK apos health | Recuperacao completa | Estado |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| R1 | `edge-s8-t2-r1-5b64ee82267c` | 35.360 s | 100 | 100 | 0 | 0 | 0 | 87 | 0.570 s | 18.488 s | VALIDADA |
| R2 | `edge-s8-t2-r2-5e2fdf2d7746` | 305.532 s | 100 | 100 | 0 | 0 | 0 | 87 | 0.552 s | 20.281 s | VALIDADA |
| R3 | `edge-s8-t2-r3-0caf9760c3c6` | 1808.062 s | 100 | 100 | 0 | 0 | 0 | 87 | 2.615 s | 13.162 s | DOCUMENTADA COM RESSALVA |

O status da R3 e DOCUMENTADA COM RESSALVA, nao VALIDADA sem restricao. O script
marcou VALID de forma autonoma e os dados de sincronizacao sao coerentes (100/100,
zero perdas, zero duplicatas, SQLite com 100 SINCRONIZADA). Porem, havia um
segundo processo (`edge-s8-t2-r3-e4c6057416e4`) ativo no mesmo Compose durante
parte da janela de 0caf. O script nao detectou interrupcao, mas ausencia de
deteccao nao e prova de ausencia de interferencia. A integridade continua da
janela de indisponibilidade nao pode ser comprovada definitivamente pelos
registros disponiveis.

Tentativas preservadas como evidencia:

- `edge-s8-t2-r3-5aa374f63450` (tentativa 1 — FAILED): interrompida antes de
  completar os 30 minutos; 100 geradas, 100 PENDENTE na outbox, zero recebidas
  no MySQL.
- `edge-s8-t2-r3-e4c6057416e4` (tentativa 2 — INVALIDATED): script marcou
  INVALIDATED porque Docker events mostraram `web` saudavel dentro da janela
  nominal. Reclassificada manualmente para VALID em sessao posterior sem nova
  execucao; essa reclassificacao foi revertida nesta auditoria. SQLite confirma
  100 SINCRONIZADA, mas isso prova sincronizacao, nao a integridade da janela.
- `edge-s8-t2-r3-f5eb9476c97f` (tentativa 3 — INCOMPLETE): SQLite presente com
  100 SINCRONIZADA, mas nenhum resultado foi gravado em qualquer JSON pelo
  script. Sem timestamps de experimento nem consulta ao MySQL registrada. Os
  timestamps e metricas que apareciam no protocolo anterior para esse device
  nao existem em nenhum arquivo de resultado e foram removidos.

### Registros de execucao

| Evento UTC | R1 | R2 | R3 |
| --- | --- | --- | --- |
| Inicio da rodada | 2026-10-09T11:05:45.984764Z | 2026-10-09T11:06:43.712154Z | 2026-10-09T11:16:48.250136Z |
| Backend parado | 2026-10-09T11:05:47.853940Z | 2026-10-09T11:06:45.865717Z | 2026-10-09T11:16:50.190885Z |
| Geracao iniciada | 2026-10-09T11:05:47.854488Z | 2026-10-09T11:06:45.865717Z | 2026-10-09T11:16:50.190885Z |
| Geracao concluida | 2026-10-09T11:05:48.877067Z | 2026-10-09T11:06:46.868252Z | 2026-10-09T11:16:51.226343Z |
| Backend iniciado | 2026-10-09T11:06:17.879790Z | 2026-10-09T11:11:45.858822Z | 2026-10-09T11:46:50.189655Z |
| Health recuperado | 2026-10-09T11:06:23.212650Z | 2026-10-09T11:11:51.392342Z | 2026-10-09T11:46:58.256337Z |
| Primeiro ACK | 2026-10-09T11:06:23.783024Z | 2026-10-09T11:11:51.944359Z | 2026-10-09T11:47:00.871819Z |
| Ultimo ACK / fim | 2026-10-09T11:06:41.700518Z | 2026-10-09T11:12:11.673699Z | 2026-10-09T11:47:11.418458Z |
| Sincronizacao total | 18.484 s | 20.281 s | 13.172 s |

Todos os timestamps da R3 sao copiados fielmente de
`artifacts/resilience/resultados-pre-concorrencia-r3.json`. Nenhum valor foi
recalculado ou estimado.

Em R1, R2 e R3 a ordem recebida no MySQL foi identica. Despacho/recepcao por
prioridade: A = 1, 11, 21, 31, 41, 51, 61, 71, 81, 91; B = 4, 7, 10, 13, 16,
19, 22, 25, 28, 34, 37, 40, 43, 46, 49, 52, 55, 58, 64, 67, 70, 73, 76, 79,
82, 85, 88, 94, 97, 100; depois as 60 sequencias da classe C. A sequencia
completa esta preservada em `server_received_sequence` no JSON bruto. A contagem
87 mede inversoes de chegada em relacao ao maior `sequence_number` ja recebido,
nao mensagens perdidas. Esse comportamento decorre do despacho intencional por
prioridade A > B > C. O protocolo mede e reporta a desordem; nao define
ordenacao global estrita como criterio de aceite. Integridade exige que o
conjunto final de sequences seja exatamente 1-100 e que todas as leituras sejam
persistidas uma unica vez; isso foi verificado nas tres rodadas.

As latencias de recuperacao sao calculadas como `last_successful_sync_at -
backend_ready_at`. `downtime_actual_seconds` e medido por `time.monotonic()`
desde o `stop web` ate a resposta saudavel do health endpoint.

### Bloqueios e ocorrencias

- Docker Desktop 4.74.0 (engine 29.4.3). O banco Compose estava vazio e sem
  migrations na primeira execucao; migrations aplicadas antes das rodadas oficiais.
- O comando original do servico `web` iniciava Gunicorn sem `--bind`: as quebras
  de linha do YAML dividiam os argumentos em comandos do shell. Corrigido para
  `exec gunicorn` com argumentos na mesma linha; health endpoint passou a
  responder HTTP 200 no host.
- A primeira tentativa R3 (`5aa374f63450`) foi interrompida antes de completar
  os 30 minutos. SQLite: 100 PENDENTE; MySQL: zero recebidas. Registrada como
  FAILED e preservada.
- A tentativa `0caf9760c3c6` foi marcada VALID pelo script de forma autonoma
  (downtime 1808.062 s, 100/100, zero perdas). Porem, havia um segundo processo
  (`e4c6057416e4`) ativo no mesmo Compose durante parte da janela. O script nao
  detectou interrupcao, mas ausencia de deteccao nao e prova de ausencia de
  interferencia. Por isso o status desta rodada e DOCUMENTADA COM RESSALVA, nao
  VALIDADA sem restricao.
- A tentativa `e4c6057416e4` foi marcada INVALIDATED pelo script (Docker events
  mostraram `web` saudavel dentro da janela). Foi reclassificada manualmente
  para VALID em sessao posterior sem nova execucao. Essa reclassificacao foi
  revertida nesta auditoria; o status permanece INVALIDATED.
- A tentativa `f5eb9476c97f` tem SQLite com 100 SINCRONIZADA, mas nenhum
  resultado foi gravado em qualquer JSON pelo script. Timestamps e metricas que
  apareciam no protocolo anterior para esse device nao existem em nenhum arquivo
  de resultado e foram removidos desta documentacao.
- Os 14 testes focados de telemetria (`api_tcc.tests.test_telemetria`) passaram.
  A suite Django completa tem dois erros pre-existentes nao relacionados ao
  protocolo de resiliencia (test_health e test_anomaly_persistence); esses erros
  nao foram introduzidos por esta auditoria e nao bloqueiam as evidencias acima.
