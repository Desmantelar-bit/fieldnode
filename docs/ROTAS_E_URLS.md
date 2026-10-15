# FieldNode — Matriz Completa de URLs e Rotas

Este documento cataloga todas as rotas do FieldNode (Frontend Next.js e Backend Django REST Framework), seus métodos, autenticação exigida, formato de resposta e comportamento esperado.

---

## 1. Frontend (Next.js 15 — App Router)

| Rota | Tipo | Autenticação | Descrição / Comportamento |
|---|---|---|---|
| `/` | SSR / Redirecionamento | Pública | Redireciona automaticamente para `/dashboard`. |
| `/_not-found` | Estática (404) | Pública | Página 404 com design system FieldNode, botões para Dashboard e Login. |
| `/login` | Estática / Cliente | Pública | Tela de login com validação de credenciais, anti-flash de tema e autenticação por token. |
| `/register` | Estática / Cliente | Pública | Tela de cadastro de novos usuários/operadores da plataforma. |
| `/dashboard` | Dinâmica (SSR/Client) | Sessão / Token | Painel operacional principal: KPIs de frota, taxa de anomalias, mapa resumido, alertas e decisões pendentes. |
| `/maquinas` | Dinâmica (SSR/Client) | Sessão / Token | Listagem, filtros e gestão das máquinas da frota. |
| `/maquinas/[id]/prescricao` | Dinâmica (SSR/Client) | Sessão / Token | Visualização e aprovação de prescrições técnicas geradas para uma máquina específica. |
| `/colheitadeiras` | Dinâmica (SSR/Client) | Sessão / Token | Telemetria detalhada e status de operação das colheitadeiras. |
| `/detalhes` | Dinâmica (SSR/Client) | Sessão / Token | Histórico granular de leituras de sensores (temperatura, vibração, RPM) por máquina. |
| `/operarios` | Dinâmica (SSR/Client) | Sessão / Token | Gestão, cadastro e escala de operadores. |
| `/relatorios` | Dinâmica (SSR/Client) | Sessão / Token | Geração e visualização de relatórios operacionais consolidados. |
| `/mapa` | Dinâmica (SSR/Client) | Sessão / Token | Rastreamento geográfico em tempo real com Leaflet e OpenStreetMap. |

---

## 2. Backend — Sistema e Documentação (Django)

| Rota | Método | Autenticação | Resposta | Descrição |
|---|---|---|---|---|
| `/` | GET | Pública | HTTP 302 | Redireciona para `/swagger/` para exploração interativa da API. |
| `/admin/` | GET, POST | Superuser / Staff | HTML | Django Admin customizado com identidade visual FieldNode. |
| `/swagger/` | GET | Pública | HTML | Documentação interativa Swagger UI (drf-yasg). |
| `/swagger.json/` | GET | Pública | JSON | OpenAPI Schema specification da API. |
| `/redoc/` | GET | Pública | HTML | Interface ReDoc para documentação da API. |
| `/api/health/` | GET | Pública | JSON | Health check da API e do banco de dados (status, db, mqtt_last_seen, version). |

---

## 3. Backend — Autenticação e Gestão de Usuários

| Rota | Método | Autenticação | Resposta | Descrição |
|---|---|---|---|---|
| `/api/auth/login/` | POST | Pública | JSON | Autentica usuário e retorna Token com TTL e expiração configurada. |
| `/api/auth/register/` | POST | Pública | JSON | Registra novo usuário na plataforma. |
| `/api/auth/logout/` | POST | Token | JSON | Invalida e deleta o token de autenticação ativo. |
| `/api/auth/me/` | GET | Token | JSON | Retorna dados e permissões do usuário autenticado. |

---

## 4. Backend — Ingestão e Telemetria

| Rota | Método | Autenticação | Resposta | Descrição |
|---|---|---|---|---|
| `/api/telemetria/` | POST, GET | X-API-Key / Token | JSON | Ingestão individual idempotente de leitura (validação, deduplicação por UUID, isolamento). |
| `/api/telemetria/lote/` | POST | X-API-Key | JSON | Ingestão em lote tolerante a falhas parciais para clientes Edge / Data Mule. |
| `/api/leituras/ultimas/` | GET | Token / Demo | JSON | Retorna a leitura mais recente de cada máquina ativa. |
| `/api/status-mqtt/` | GET | Token / Demo | JSON | Status de conectividade do broker MQTT e atraso da última leitura. |
| `/api/dlq/` | GET | Token | JSON | Dead Letter Queue para inspeção de leituras rejeitadas ou payloads corrompidos. |

---

## 5. Backend — Inteligência, Eventos e Decisões

| Rota | Método | Autenticação | Resposta | Descrição |
|---|---|---|---|---|
| `/api/anomalias/` | GET | Token / Demo | JSON | Detecção de anomalias multivariadas via Isolation Forest + regras determinísticas. |
| `/api/manutencao/` | GET | Token / Demo | JSON | Análise preditiva de manutenção e cálculo de risco por máquina. |
| `/api/metricas/` | GET | Token / Demo | JSON | Agregação de métricas de telemetria, médias, desvio padrão e tendências. |
| `/api/machines/<id>/health/` | GET | Token / Demo | JSON | Diagnóstico de integridade e Trust Score dos dados da máquina. |
| `/api/events/` | GET | Token / Demo | JSON | Listagem de eventos priorizados pelo Attention Engine. |
| `/api/events/<uuid>/` | GET | Token / Demo | JSON | Detalhes e rastreabilidade de um evento operacional específico. |
| `/api/decisions/` | GET | Token / Demo | JSON | Fila de decisões recomendadas pela IA e histórico de ações. |
| `/api/decisions/<uuid>/` | POST, PATCH | Token | JSON | Aprovação, rejeição ou arquivamento de decisão por operador humano. |
| `/api/prescricoes/` | POST, GET | Token / Demo | JSON | Geração e consulta de prescrições operacionais. |
| `/api/prescricoes/lista/` | GET | Token / Demo | JSON | Histórico de prescrições da frota. |
| `/api/prescricoes/<maquina_id>/`| GET | Token / Demo | JSON | Prescrição técnica ativa para uma colheitadeira específica. |

---

## 6. Backend — Relatórios e Geolocalização

| Rota | Método | Autenticação | Resposta | Descrição |
|---|---|---|---|---|
| `/api/relatorio/` | GET | Token / Demo | JSON/CSV | Relatório executivo consolidado da operação agrícola. |
| `/api/relatorio/exportar/` | GET | Token / Demo | CSV/XLSX | Exportação formatada de telemetria e ocorrências para auditoria. |
| `/api/maquinas/posicao/` | GET | Token / Demo | JSON | Coordenadas geográficas das máquinas para plotagem em mapa. |
| `/api/mapas/demo/` | GET | Token / Demo | JSON | Coordenadas simuladas para testes de interface de mapa. |

---

## 7. Backend — ViewSets Cadastrais (CRUD)

| Rota Base | Model | Métodos Suportados |
|---|---|---|
| `/api/colheitadeira/` | `Colheitadeira` | GET, POST, PUT, PATCH, DELETE |
| `/api/operario/` | `Operario` | GET, POST, PUT, PATCH, DELETE |
| `/api/marca/` | `Marca` | GET, POST, PUT, PATCH, DELETE |
| `/api/modelo/` | `Modelo` | GET, POST, PUT, PATCH, DELETE |
| `/api/combustivel/` | `Combustivel` | GET, POST, PUT, PATCH, DELETE |
| `/api/unidadedemedida/` | `UnidadedeMedida` | GET, POST, PUT, PATCH, DELETE |
| `/api/transbordo/` | `Transbordo` | GET, POST, PUT, PATCH, DELETE |
| `/api/statusdeoperacao/` | `StatusdeOperacao` | GET, POST, PUT, PATCH, DELETE |
| `/api/estadodemovimento/` | `EstadodeMovimento` | GET, POST, PUT, PATCH, DELETE |
| `/api/temperaturamaquina/`| `TemperaturaMaquina` | GET, POST, PUT, PATCH, DELETE |
| `/api/tempumi_ambiente/` | `TempUmi_Ambiente` | GET, POST, PUT, PATCH, DELETE |
| `/api/pressaopneus/` | `PressaoPneus` | GET, POST, PUT, PATCH, DELETE |
| `/api/alturadocorte/` | `AlturadoCorte` | GET, POST, PUT, PATCH, DELETE |
| `/api/pressaodocorte/` | `PressaodoCorte` | GET, POST, PUT, PATCH, DELETE |
