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
