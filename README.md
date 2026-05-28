# FieldNode

Telemetria offline-first para maquinas agricolas, com ingestao Django, dashboard Next.js e sincronizacao tolerante a falhas.

## Visao Geral

O FieldNode segue um fluxo simples e forte:

```text
Sensor ESP32 -> Gateway Local -> Dashboard Next.js -> API Django -> MySQL
```

A ideia central e nao perder dado quando a rede rural resolve tirar ferias. Os dispositivos coletam telemetria, reenviam quando existe conexao e a API usa UUID para evitar duplicidade.

## Stack

| Camada | Tecnologia |
| --- | --- |
| Backend | Django 5.2 + Django REST Framework |
| Frontend | Next.js + React + Tailwind CSS |
| Banco | MySQL 8 em Docker ou SQLite em desenvolvimento |
| Hardware | ESP32, ESP-NOW e simuladores MQTT |
| Docs API | Swagger em `/swagger/` |

## Rodando Com Docker Compose

Esse e o caminho recomendado para apresentacao, porque sobe backend, banco e frontend juntos. Nada de "na minha maquina foi", esse classico da dramaturgia tecnica.

```bash
docker compose up --build
```

Acesse:

```text
Frontend Next.js: http://127.0.0.1:3000/dashboard
API Django:       http://127.0.0.1:8000/api/health/
Swagger:          http://127.0.0.1:8000/swagger/
```

O `docker-compose.yml` usa:

```text
FIELDNODE_SERVER_API_URL=http://web:8000/api
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
```

Isso existe por um motivo bem pouco poetico: o servidor Next dentro do container fala com Django por `web:8000`, enquanto o navegador do usuario fala com Django por `127.0.0.1:8000`.

## Rodando Localmente Sem Docker

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

### Frontend

Em outro terminal:

```bash
cd frontend-next
npm ci
npm run dev
```

Acesse:

```text
http://127.0.0.1:3000/dashboard
```

## Build De Producao Do Frontend

```bash
cd frontend-next
npm run build
npm run start
```

O Next.js nao e servido pelo Django neste projeto. Ele roda como servico proprio, e o Django fica responsavel pela API. Tentar enfiar SSR dentro de `collectstatic` seria bonito no discurso e torto na pratica.

## Variaveis De Ambiente

Copie `.env.example` para `.env` e ajuste quando necessario.

Variaveis principais:

```text
SECRET_KEY
FIELDNODE_API_KEY
DEBUG
ALLOWED_HOSTS
CORS_ALLOWED_ORIGINS
NEXT_PUBLIC_API_URL
NEXT_PUBLIC_FIELDNODE_API_KEY
FIELDNODE_SERVER_API_URL
USE_SQLITE
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

O arquivo `.env` esta no `.gitignore`. Segredo versionado e o tipo de erro que faz banca tecnica levantar a sobrancelha antes do cafe esfriar.

## Rotas Principais

### Frontend

| Rota | Uso |
| --- | --- |
| `/dashboard` | Visao geral da frota |
| `/colheitadeiras` | Leituras recentes por maquina |
| `/operarios` | Equipe cadastrada |
| `/detalhes?id=COLH-01` | Historico e metricas da maquina |

### API

| Endpoint | Metodo | Uso |
| --- | --- | --- |
| `/api/health/` | GET | Checagem simples de saude |
| `/api/telemetria/` | POST | Ingestao com `X-API-Key` |
| `/api/telemetria/` | GET | Ultimas leituras para debug |
| `/api/leituras/ultimas/` | GET | Ultima leitura por maquina |
| `/api/operario/` | GET | Operarios cadastrados |
| `/api/colheitadeira/` | GET | Frota cadastrada |
| `/api/anomalias/` | GET | Analise de anomalias |
| `/api/manutencao/` | GET | Estimativa de manutencao |
| `/api/prescricoes/` | GET | Prescricao operacional |
| `/api/relatorio/` | GET | Relatorio JSON ou CSV |

Exemplo de ingestao:

```bash
curl -X POST http://127.0.0.1:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: fieldnode-demo-2024" \
  -d "{\"id\":\"550e8400-e29b-41d4-a716-446655440000\",\"maquina_id\":\"COLH-01\",\"temperatura\":78.5,\"vibracao\":0.42,\"rpm\":1850,\"timestamp\":\"2026-05-28T14:32:01Z\"}"
```

## Validacao Rapida

```bash
python scripts/teste_fluxo_completo.py
```

Para validar so a estrutura de arquivos:

```bash
python scripts/validar_sistema.py
```

## Observacoes Para Banca

- A ingestao exige `X-API-Key`.
- O frontend antigo foi removido para evitar rotas quebradas e duplicidade.
- O Next.js roda como servico separado no Compose.
- O dashboard tem timeout de API para nao travar quando o backend demora.
- O `.env` nao deve ser commitado.

## Licenca

MIT
