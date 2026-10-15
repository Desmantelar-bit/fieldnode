# FieldNode

Protótipo técnico de telemetria offline-first e inteligência operacional para máquinas agrícolas. Ingestão Django, dashboard Next.js e sincronização tolerante a falhas de rede rural.

---

## Arquitetura

**Nota:** O diretório oficial do frontend é o `frontend-next/`, construído em
Next.js. Versões legadas e scaffolds não utilizados foram removidos da base.

```mermaid
graph TD
    SOURCE["Fonte de telemetria / simulador"]
    MQTT["Broker MQTT\n(localhost:1883)"]
    SIM["scripts/simular_mqtt.py\n(fallback HTTP se broker cair)"]
    API["API Django 5.2\n:8000"]
    DB[("MySQL 8\nou SQLite")]
    IA["Análise operacional\n(regras + anomalias)"]
    NEXT["Next.js 15\n:3000"]
    SW["Service Worker\n(cache + outbox local)"]
    USER["Navegador"]

    SOURCE -->|"MQTT publish"| MQTT
    MQTT -->|"mqtt_listen.py"| API
    SIM -->|"POST /api/telemetria/"| API
    API -->|"UUID dedup + persist"| DB
    API -->|"agenda modelos"| IA
    IA -->|"lê leituras"| DB
    IA -->|"salva prescrição"| DB
    NEXT -->|"SSR + fetch"| API
    USER -->|"HTTP"| NEXT
    SW -->|"reenvio same-origin; autorização pendente"| API
```

---

## Fluxo de Ingestão

```mermaid
sequenceDiagram
    participant SOURCE as Fonte de telemetria
    participant API as Django API
    participant DB as Banco
    participant IA as Análise operacional

    SOURCE->>API: POST /api/telemetria/ (UUID + X-API-Key)
    API->>API: valida API key
    API->>API: valida payload (range de sensores)
    API->>DB: UUID já existe?
    alt duplicata
        DB-->>API: sim
        API-->>ESP: 200 duplicata ignorada
    else novo
        DB-->>API: não
        API->>DB: INSERT LeituraTelemetria
        API->>IA: agendar anomalias + estado + manutencao
        API-->>ESP: 201 ok + id
    end
```

---

## Pipeline de análise

```mermaid
flowchart LR
    L["Leituras\n(últimas N)"] --> ISO["Isolation Forest\ndetecção de anomalia"]
    L --> RG["Regras ponderadas\n+ score heurístico"]
    L --> TH["Thresholds documentados\ntriagem operacional"]

    ISO --> AGG["Consolidação\nde severidade"]
    RG --> AGG
    TH --> AGG

    AGG -->|"NORMAL"| P1["Manter operação"]
    AGG -->|"ATENCAO"| P2["Inspecionar em 4-8h"]
    AGG -->|"CRITICO"| P3["Inspeção imediata recomendada"]

    P1 --> PRESC[("Prescrição\nsalva no banco")]
    P2 --> PRESC
    P3 --> PRESC
```

---

## Stack

| Camada | Tecnologia |
| --- | --- |
| Backend | Django 5.2 + Django REST Framework |
| Frontend | Next.js 15 + React + Tailwind CSS |
| Banco | MySQL 8 em Docker / SQLite em desenvolvimento |
| Análise | Isolation Forest como sinal não supervisionado + regras/thresholds determinísticos |
| Hardware e transporte | Simuladores MQTT e cliente Python de bancada; ESP32/ESP-NOW permanecem como integração física a validar |
| Offline | Outbox SQLite no cliente Python e fila local IndexedDB no Service Worker |
| Docs API | Swagger em `/swagger/` |
| Testes | Django TestCase + pytest |

---

## Estado do ciclo atual

### O que está implementado e evidenciado neste ciclo

- ingestão HTTP autenticada por `X-API-Key`, validação de payload e deduplicação;
- persistência em SQLite/MySQL, com identidade de máquina, mensagem, sequência, timestamp e hash no cliente de borda;
- cliente Python de bancada com outbox SQLite, prioridades A/B/C, retry, ACK e cursor contíguo;
- Trust Score heurístico e estado agregado de qualidade dos dados;
- geração determinística de eventos e decisões persistentes, com aprovação ou rejeição por usuário autenticado e registro de outcome;
- detecção de anomalias com Isolation Forest, usada como sinal complementar, e regras ponderadas para triagem operacional;
- dashboard Next.js; Service Worker com cache de assets e fila local de telemetria, sem credenciais privilegiadas;
- testes automatizados e artefatos de ensaio de resiliência documentados em `docs/PROTOCOLO_TESTE_RESILIENCIA_OFFLINE.md` e `artifacts/resilience/`.

Essas evidências são de código, testes e bancada de software. A leitura usada nas demonstrações é simulada; isso não comprova sensor físico calibrado, operação em campo, execução mecânica ou resultado econômico.

### Roadmap futuro

- integração física com ESP32 e sensores identificados, incluindo calibração, energia e reinicialização;
- implementação e medição de ESP-NOW ou outro transporte aprovado; a integração física ainda não está comprovada;
- medição específica de retenção e capacidade de armazenamento por 30 dias no hardware-alvo;
- validação progressiva em bancada física e campo, com alcance, estabilidade e condições registradas;
- avaliação de CAN/J1939, ISOBUS e integrações com fabricantes, sem afirmar suporte antes de existir adaptador e ensaio verificável;
- dataset operacional rotulado e avaliação supervisionada de manutenção, se houver volume e protocolo de rotulagem suficientes;
- evolução da autenticação do MVP e repetição dos ensaios oficiais no Compose quando o ambiente estiver disponível.

O roadmap preserva a direção do produto, mas não transforma intenção em resultado. O repositório não sustenta a afirmação de que o FieldNode já prevê falhas mecânicas com modelo supervisionado, armazena 30 dias em ESP32 ou opera por ESP-NOW em ambiente rural.

---

## Execução com Docker (recomendado)

**Pré-requisito:** Docker instalado. Nenhum Python, MySQL ou Mosquitto local necessário.

### 1. Clonar e configurar variáveis

```bash
git clone <repositório>
cd fieldnode
cp .env.example .env
```

Edite o `.env` e preencha no mínimo:

| Variável | O que colocar |
| --- | --- |
| `SECRET_KEY` | Chave secreta Django (veja comentário no .env.example) |
| `FIELDNODE_API_KEY` | UUID para autenticação de ingestão |
| `DB_PASSWORD` | Senha do usuário MySQL |
| `DB_ROOT_PASSWORD` | Senha do root MySQL |

### 2. Subir os serviços

```bash
docker compose up --build
```

Aguarde os healthchecks: `db (healthy)`, `mosquitto (healthy)`, `web (healthy)`.

### 3. Executar migrations

```bash
docker compose exec web python manage.py migrate
```

### 4. (Opcional) Popular com dados de demonstração

```bash
docker compose exec web python manage.py popular_tudo
```

### 5. Acessar

| O quê | URL |
| --- | --- |
| Dashboard | [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard) |
| API health | [http://127.0.0.1:8000/api/health/](http://127.0.0.1:8000/api/health/) |
| Swagger | [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/) |

> O frontend Next.js **não é incluído** na composição Docker padrão do backend.
> Para rodar o dashboard Next.js junto, execute `cd frontend-next && npm ci && npm run dev`
> e configure `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api` no `.env`.

### Comandos úteis

```bash
# Logs de todos os serviços
docker compose logs -f

# Logs só do worker MQTT
docker compose logs -f worker

# Status dos serviços e healthchecks
docker compose ps

# Entrar no container web
docker compose exec web bash

# Parar sem apagar volumes
docker compose down

# Parar e apagar volumes (inclusive banco — cuidado)
docker compose down -v
```

### Serviços

| Serviço | Descrição | Porta |
| --- | --- | --- |
| `web` | Django + Gunicorn | 8000 |
| `worker` | mqtt_listen (MQTT → banco) | — |
| `mosquitto` | Broker MQTT | 1883 |
| `db` | MySQL 8 | 3307 (host) |

### Testar fluxo MQTT

```bash
# Publicar uma leitura via broker containerizado
docker compose exec mosquitto mosquitto_pub \
  -h localhost -p 1883 \
  -t "fieldnode/COLH-01/leitura" \
  -m '{"id":"550e8400-e29b-41d4-a716-446655440001","maquina_id":"COLH-01","temperatura":78.5,"vibracao":0.42,"rpm":1850,"timestamp":"2026-10-06T12:00:00Z"}'

# Verificar nos logs do worker
docker compose logs worker --tail=10
```

---

## Setup Local (sem Docker)

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py treinar_isolation_forest
python manage.py runserver
```

O Isolation Forest é treinado offline com o cenário normal de bancada. O arquivo
`api_tcc/ia/modelos/isolation_forest_v1.pkl` acompanha o projeto; para regenerá-lo
de forma determinística, execute `python manage.py treinar_isolation_forest`.
Ele é um sinal não supervisionado complementar aos thresholds determinísticos.

### Frontend

```bash
cd frontend-next
npm ci
npm run dev
```

---

## Variáveis de Ambiente

Copie `.env.example` para `.env` e ajuste.

| Variável | Descrição |
| --- | --- |
| `SECRET_KEY` | Chave secreta Django |
| `FIELDNODE_API_KEY` | API key exigida no header `X-API-Key` |
| `DEMO_MODE` | Quando `True`, leitura pública anônima usa somente `Machine.is_demo=True` |
| `DEBUG` | `True` em dev, `False` em produção |
| `ALLOWED_HOSTS` | Hosts permitidos pelo Django |
| `CORS_ALLOWED_ORIGINS` | Origens permitidas pelo CORS |
| `NEXT_PUBLIC_API_URL` | URL da API usada pelo browser |
| `FIELDNODE_SERVER_API_URL` | URL da API usada pelo servidor Next (container) |
| `USE_SQLITE` | `True` para SQLite em dev |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | Conexão MySQL |

O `.env` está no `.gitignore`. Segredo versionado é o tipo de erro que faz banca técnica levantar a sobrancelha antes do café esfriar.

`FIELDNODE_API_KEY` deve ficar no backend, scripts locais e dispositivos de ingestão. O frontend não recebe segredo via `NEXT_PUBLIC_*`.

---

## Rotas do Frontend

| Rota | Descrição |
| --- | --- |
| `/dashboard` | Visão geral da frota: métricas, grid de máquinas, mapa |
| `/colheitadeiras` | Leituras recentes por máquina com badge de risco |
| `/detalhes?id=COLH-01` | Histórico, gráficos e prescrição da máquina |
| `/mapa` | Mapa de posição em campo (fallback demo se GPS ausente) |
| `/operarios` | Equipe cadastrada |
| `/maquinas` | Frota completa cadastrada |
| `/relatorios` | Geração de relatório JSON e exportação CSV |

---

## API — Endpoints

| Endpoint | Método | Autenticação | Descrição |
| --- | --- | --- | --- |
| `/api/auth/login/` | POST | usuario/senha | Retorna token DRF para operacoes autenticadas |
| `/api/health/` | GET | — | Checagem de saúde |
| `/api/telemetria/` | POST | `X-API-Key` | Ingestão com deduplicação UUID |
| `/api/telemetria/` | GET | — | Últimas 50 leituras (debug) |
| `/api/leituras/ultimas/` | GET | — | Última leitura por máquina com `status_risco` |
| `/api/colheitadeira/` | GET | — | Frota cadastrada |
| `/api/colheitadeira/` | POST/PATCH/DELETE | `Authorization: Token <token>` | Cadastro administrativo de maquinas |
| `/api/operario/` | GET | — | Operários cadastrados |
| `/api/operario/` | POST/PATCH/DELETE | `Authorization: Token <token>` | Cadastro administrativo de operarios |
| `/api/anomalias/` | GET | — | Agenda detecção de anomalias (Isolation Forest) |
| `/api/manutencao/` | GET | — | Agenda análise de manutenção baseada em regras e sinais disponíveis |
| `/api/prescricoes/` | GET | — | Agenda geração de prescrição |
| `/api/prescricoes/lista/` | GET | — | Histórico de prescrições por máquina |
| `/api/relatorio/` | GET | — | Relatório operacional JSON ou CSV |
| `/api/relatorio/exportar/` | GET | — | Exportação CSV com delimitador `;` |
| `/api/maquinas/posicao/` | GET | — | Posição GPS da frota |
| `/api/metricas/` | GET | — | Leituras válidas, inválidas e taxa de rejeição |
| `/api/status-mqtt/` | GET | — | Status de conectividade MQTT |

Com `DEMO_MODE=True`, endpoints públicos de leitura operacional retornam somente dados associados a `Machine.is_demo=True`. Isso não libera escrita, não substitui autorização e não marca máquina real como demonstração.

### Autenticacao administrativa

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "sua-senha"}'
```

Resposta:

```json
{"token": "token-gerado-pelo-drf"}
```

Use o token nas operacoes de escrita dos cadastros:

```bash
Authorization: Token token-gerado-pelo-drf
```

No frontend, o MVP guarda esse token em `localStorage` como
`fn-auth-token`. Isso e aceitavel para o TCC/prototipo, mas e uma
divida tecnica explicita: em producao, o ideal e migrar para cookie `httpOnly`
com uma estrategia de CSRF adequada, porque XSS lendo token em `localStorage`
nao e teoria, e so uma terca-feira ruim.

### Exemplo de ingestão

```bash
curl -X POST http://127.0.0.1:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${FIELDNODE_API_KEY}" \
  -d '{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "maquina_id": "COLH-01",
    "temperatura": 78.5,
    "vibracao": 0.42,
    "rpm": 1850,
    "latitude": -15.793889,
    "longitude": -47.882778,
    "timestamp": "2026-05-28T14:32:01Z"
  }'
```

Resposta `201`:

```json
{"status": "ok", "id": "550e8400-e29b-41d4-a716-446655440000", "ia": {"status": "agendado"}}
```

Reenviar o mesmo `id` retorna `200` sem duplicar o banco:

```json
{"status": "duplicata ignorada", "id": "550e8400-e29b-41d4-a716-446655440000"}
```

---

## Simulador MQTT com Fallback HTTP

```bash
# MQTT normal
python scripts/simular_mqtt.py

# Forçar fallback HTTP (broker inacessível)
MQTT_PORT=1884 DEMO_CYCLES=1 python scripts/simular_mqtt.py
```

O simulador detecta `Connection refused`, entra em modo demo e envia diretamente para `/api/telemetria/` com coordenadas GPS reais. O sistema não para — degrada com graciosidade.

---

## Testes

```bash
# 3 casos de telemetria: ingestão válida, inválida e duplicada
python manage.py test api_tcc.tests.test_telemetria --verbosity=2

# Suite completa do backend
python manage.py test api_tcc

# Validação rápida do fluxo end-to-end
python scripts/teste_fluxo_completo.py
```

Build do frontend com verificação de tipos:

```bash
cd frontend-next && npm run build
```

## Semana 10 - demonstração closed loop

O roteiro reproduzível da banca está em [docs/ROTEIRO_DEMO_BANCA.md](docs/ROTEIRO_DEMO_BANCA.md). Ele usa o `EdgeClient` real em `scripts/s10_closed_loop_demo.py` e demonstra a cadeia:

```text
leitura -> trust_score -> Event -> Decision pendente -> aprovação humana -> outcome
```

O executor automatiza somente a parte de telemetria e consulta da Decision. A aprovação continua no dashboard autenticado; não existe atalho que altere o estado diretamente no banco. O material de perguntas técnicas está em [docs/INVESTOR_CTO_PRESSURE_TEST.md](docs/INVESTOR_CTO_PRESSURE_TEST.md).

Para uma execução preparada no Compose:

```powershell
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py popular_tudo
python scripts/s10_closed_loop_demo.py --device-id COLH-01 --machine-id COLH-01
```

O fluxo completo só é considerado validado depois de três ensaios Compose consecutivos com aprovação humana, outcome e rastreabilidade conferidos. Sem Docker Desktop ou sem a execução observada, o estado correto é **não verificado**, não “demo pronta”.

---

## Resiliência Offline

O Service Worker (`frontend-next/public/sw.js`) faz cache apenas de assets e mantém payloads offline em IndexedDB; respostas de `/api/` ficam na rede para não reutilizar dados autenticados entre sessões. A fila remove headers de credenciais e preserva itens quando a API rejeita a sincronização. O backend atual exige `X-API-Key` em `POST /api/telemetria/`, então o navegador não consegue concluir ingestão sem um contrato server-side seguro; a ingestão operacional é feita pelos clientes de dispositivo/borda. A outbox SQLite do cliente Python mantém retry, ACK e deduplicação. Isso é evidência de software/bancada: não comprova buffer físico de 30 dias, ESP32, ESP-NOW, autonomia ou operação em campo.

---

## Licença

MIT

## Estado da integração do frontend

O frontend oficial consolidado fica em `frontend-next/`, incorporado do clone
`Front Full Node` após comparação de páginas, serviços, assets e contratos. O
backend principal da raiz foi preservado e recebeu os endpoints de autenticação
necessários à integração.

O cadastro público usa `POST /api/auth/register/`, cria um usuário Django
comum com senha hasheada e devolve um token DRF. O login usa
`POST /api/auth/login/`, o logout revoga o token em `POST /api/auth/logout/` e
`GET /api/auth/me/` verifica a sessão. Nenhum desses fluxos concede `staff` ou
`superuser` ao cliente.

Para o proxy same-origin do Next, configure `FIELDNODE_SERVER_API_URL` no
ambiente do servidor Next (por exemplo, `http://127.0.0.1:8000/api`). Nao use
`NEXT_PUBLIC_FIELDNODE_API_KEY`: a chave `FIELDNODE_API_KEY` pertence somente
ao backend/cliente de dispositivo e nunca deve ser incorporada ao bundle web.
`NEXT_PUBLIC_API_URL` e opcional; quando aponta diretamente ao Django, o
navegador precisa de CORS configurado para a origem real.

O Service Worker nao armazena respostas de API. A fila IndexedDB persiste e
tenta reenviar payloads sem armazenar API key/token; quando o backend rejeita a
ingestao web, o item permanece pendente em vez de ser descartado. A sincronizacao
web ainda depende de um contrato server-side autenticado; a ingestao operacional
funcional permanece no cliente de borda, que possui outbox SQLite.

Se `NEXT_PUBLIC_FIELDNODE_API_KEY` foi configurada em uma compilacao anterior,
considere a chave correspondente exposta e rotacione `FIELDNODE_API_KEY` no
backend/dispositivos. O Service Worker novo sanitiza headers em filas IndexedDB
existentes sem remover os payloads pendentes.

O contrato auditado da aplicacao de origem foi preservado em
`docs/CONTRATO_FRONT_BACK_FRONTEND.md`. Ele registra expectativas do frontend
e pendencias que ainda dependem de validacao funcional contra o backend. O
adendo de integração e a matriz de compatibilidade estao no final desse arquivo.
