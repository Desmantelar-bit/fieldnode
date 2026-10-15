# CONTRATO_FRONT_BACK.md
## FieldNode — Contrato de Integração Frontend × Backend Leviatã V2

> **Gerado em:** 2026-10-15
> **Escopo:** Auditoria técnica completa do frontend `frontend-next` para orientar o merge com o backend Leviatã V2 (Django + DRF + MySQL).
> **Método:** Auditoria frontend complementada por leitura estática, somente leitura, do backend Django presente na raiz deste workspace. Nenhum arquivo de backend foi alterado. Essa cópia local não comprova que produção ou o backend Leviatã V2 de destino esteja na mesma revisão.

---

## 1. Objetivo e Escopo do Documento

Este documento é o mapa técnico do frontend FieldNode, produzido pela leitura do código real de `frontend-next` e complementado por leitura estática, somente leitura, da cópia Django disponível na raiz deste workspace. Ele serve como referência para uma IA ou engenheiro que, em etapa posterior, receberá acesso ao repositório principal do FieldNode (contendo o backend Leviatã V2) e precisará integrar os dois projetos sem repetir a auditoria inicial. A leitura local não comprova que produção ou o backend de destino esteja na mesma revisão; não foram executadas chamadas HTTP contra um servidor.

**O que este documento contém:**
- Stack confirmada com evidências de arquivo
- Inventário completo de rotas, páginas e componentes
- Todos os endpoints HTTP que o frontend consome (método, URL, corpo, resposta esperada)
- Contratos de dados completos (schemas Zod e tipos TypeScript)
- Autenticação e controle de acesso
- Mocks e dados demonstrativos identificados
- Configuração de ambiente e proxy
- Design system e dependências visuais
- Matriz de riscos de integração com prioridade
- Checklist de preservação funcional

---

## 2. Resumo Executivo

O frontend FieldNode é uma aplicação **Next.js 15** com React 18, TypeScript 5 e Tailwind CSS 4, rodando em modo **Server Components + Client Components**. A aplicação é do tipo **offline-first**: possui Service Worker, fila de telemetria e uma guarda de sessão que não faz chamada de rede (apenas verifica presença de token em `localStorage`).

O frontend consome **11 endpoints** distintos do backend Django, mais **1 endpoint de health check** e **1 endpoint de exportação de relatório**. Todos os contratos de API são validados em runtime via schemas **Zod** — qualquer incompatibilidade de formato gera erro explícito no console e lança exceção.

A aplicação tem **10 rotas/páginas** funcionais e **1 rota de redirect**. O design system é baseado em **CSS Custom Properties** (variáveis CSS), com **Glassmorphism** como padrão visual. Nenhuma biblioteca de componentes de terceiros (MUI, Chakra, shadcn) é usada — tudo é construído sobre Tailwind + tokens próprios.

**Estado atual:** O frontend implementa chamadas para a API e tem fallback visual de sparklines; a disponibilidade e compatibilidade em execução não foram verificadas por chamadas HTTP nesta etapa. Não há modo demo global — os mocks encontrados são restritos às sparklines, conforme documentado em `src/data/mockData.ts`.

---

## 3. Stack Tecnológica Confirmada

| Categoria | Tecnologia | Versão | Evidência |
|---|---|---|---|
| Framework | Next.js | `^15.5.23` | `package.json` |
| Runtime | React | `18.3.1` | `package.json` |
| Linguagem | TypeScript | `^5` | `package.json`, `tsconfig.json` |
| Estilização | Tailwind CSS | `^4` | `package.json`, `@tailwindcss/postcss ^4` |
| Build | Next.js (Turbopack implícito) | — | `next.config.ts` |
| Roteador | App Router (Next.js 15) | — | `src/app/` directory structure |
| Componentes UI | Lucide React | `^1.35.0` | `package.json` |
| Gráficos | Recharts | `^3.10.1` | `package.json`, `DashboardMachineData.tsx` |
| Mapas | Leaflet + React-Leaflet | `^1.9.4` / `^4.2.1` | `package.json`, `MapClient.tsx` |
| Cliente HTTP | `fetch` nativo | — | `telemetryService.ts`, `authService.ts` |
| Cache/SWR | SWR | `^2.5.1` | `package.json`, `PrescricaoModal.tsx` |
| Estado global | Redux Toolkit | `^2.12.0` | `package.json` |
| Imutabilidade | Immer | `^11.1.18` | `package.json` |
| Validação | Zod | `^3.23.8` | `package.json`, todos os schemas |
| Classes condicionais | clsx | `^2.1.1` | `package.json` |
| Testes | Playwright | `^1.40.0` | `package.json`, `tests/` |
| Lint | ESLint + eslint-config-next | `^9` / `15.2.2` | `package.json` |
| Fontes | Google Fonts (Space Grotesk, Inter, Snippet, Staatliches) | — | `layout.tsx` |
| Mapa tile source | OpenStreetMap | — | `MapClient.tsx` linha 266 |
| PWA | Service Worker customizado | — | `ServiceWorkerBridge.tsx`, `manifest.json` |

> **NOTA:** Redux Toolkit está listado como dependência (`@reduxjs/toolkit ^2.12.0`, `redux ^5.0.1`, `immer ^11.1.18`) mas **não foi encontrado uso real** de `store`, `createSlice` ou `Provider` nos arquivos lidos. Pode ser uma dependência instalada mas ainda não integrada, ou utilizada em arquivo não lido. Validar antes do merge.

---

## 4. Arquitetura e Estrutura de Diretórios

```
frontend-next/
├── next.config.ts              # Configuração do Next.js: rewrite /api/* → Django, output standalone
├── package.json                # Dependências e scripts
├── .env.local                  # Variáveis de ambiente (ver seção 18)
├── tsconfig.json               # TypeScript config (alias @/ → ./src)
├── public/
│   ├── manifest.json           # PWA manifest
│   ├── sw.js                   # Service Worker (offline-first)
│   ├── icon-192.png
│   └── brand/
│       └── field-backdrop.jpg  # Foto de fundo da tela de login (novo, não rastreado no git)
├── src/
│   ├── app/                    # App Router (Next.js 15)
│   │   ├── layout.tsx          # Root layout: fontes, anti-flash theme, ServiceWorkerBridge
│   │   ├── page.tsx            # / → redirect para /dashboard
│   │   ├── globals.css         # Estilos globais, tokens CSS, glassmorphism
│   │   ├── login/page.tsx      # Tela de login
│   │   ├── register/page.tsx   # Tela de cadastro
│   │   ├── dashboard/page.tsx  # Dashboard principal (Server Component)
│   │   ├── colheitadeiras/page.tsx  # Lista de máquinas agrícolas
│   │   ├── mapa/page.tsx       # Mapa de frota (Client Component, lazy)
│   │   ├── maquinas/
│   │   │   ├── page.tsx        # Lista de máquinas com busca
│   │   │   └── [id]/prescricao/page.tsx  # Prescrição por máquina (Server Component)
│   │   ├── operarios/page.tsx  # Diretório de operários
│   │   ├── detalhes/page.tsx   # Detalhes de telemetria por máquina
│   │   └── relatorios/page.tsx # Relatórios operacionais
│   ├── components/
│   │   ├── AppShell.tsx        # Chrome compartilhado: Sidebar + header + SessionGate
│   │   ├── SessionGate.tsx     # Guarda de sessão (verifica localStorage, sem chamada de rede)
│   │   ├── Sidebar.tsx         # Navegação desktop (rail) + mobile (bottom bar)
│   │   ├── ChatFAB.tsx         # Botão flutuante "Pergunte à IA" (portal no body)
│   │   ├── PrescricaoModal.tsx # Modal de prescrição operacional (SWR)
│   │   ├── DashboardMachineData.tsx  # Bloco de telemetria do dashboard
│   │   ├── FleetGrid.tsx       # Grid de cards de máquinas
│   │   ├── FleetMap.tsx        # Wrapper do MapaFrota
│   │   ├── MapaFrota.tsx       # Wrapper do MapClient (client-only)
│   │   ├── MapClient.tsx       # Implementação Leaflet completa (602 linhas)
│   │   ├── OperatorDirectory.tsx  # Lista + detalhe de operários
│   │   ├── OperatorFormModal.tsx  # Modal de cadastro de operário (novo)
│   │   ├── ApiStatusIndicator.tsx  # Polling de /api/health/ a cada 15s
│   │   ├── MetricCard.tsx      # Card de KPI com tom de cor
│   │   ├── MetricTrendChart.tsx  # Gráfico de linha com séries temporais
│   │   ├── MetricColumnChart.tsx  # Gráfico de colunas por leitura
│   │   ├── HistoryChart.tsx    # Gráfico histórico (detalhes da máquina)
│   │   ├── SparklineCard.tsx   # KPI compacto com sparkline
│   │   ├── ReportButton.tsx    # Botão de geração de relatório
│   │   ├── ReportPreview.tsx   # Preview do relatório com botão de exportação
│   │   ├── StatusBadge.tsx     # Pílula de status (NORMAL/ATENCAO/CRITICO)
│   │   ├── UserProfile.tsx     # Avatar + logout no header
│   │   ├── LogoutButton.tsx    # Botão de logout
│   │   ├── ThemeToggle.tsx     # Alternador dark/light
│   │   ├── AuthLayout.tsx      # Layout das telas de auth
│   │   ├── FieldNodeLogo.tsx   # Logotipo da marca
│   │   ├── ServiceWorkerBridge.tsx  # Registro do SW
│   │   ├── EmptyState.tsx      # Estados vazios e de erro
│   │   ├── BackButton.tsx      # Botão voltar
│   │   ├── SkeletonGrid.tsx    # Skeleton loading
│   │   ├── OperationClock.tsx  # Relógio (novo, não rastreado)
│   │   └── ui/
│   │       └── FeedbackStates.tsx  # LoadingState, EmptyState, ErrorState
│   ├── services/
│   │   ├── telemetryService.ts  # Serviço principal de leitura de dados (PROTEGIDO)
│   │   ├── authService.ts       # Login, registro, logout, token
│   │   └── operatorService.ts   # Criação de operários (novo)
│   ├── schemas/
│   │   ├── index.ts             # Re-exports centralizados
│   │   ├── telemetria.ts        # Schema Zod de leitura de telemetria
│   │   ├── maquinas.ts          # Schema Zod de máquinas e posições
│   │   ├── prescricoes.ts       # Schema Zod de prescrições e análises
│   │   └── relatorios.ts        # Schema Zod de relatório resumo
│   ├── types/
│   │   ├── api.ts               # EstadoRequisicao<T> (loading/sucesso/vazio/erro)
│   │   ├── telemetry.ts         # Re-exports e OperatorSchema (derivados dos schemas)
│   │   ├── telemetryService.ts  # (arquivo de tipos extra, conteúdo não lido)
│   │   ├── FleetGrid.tsx        # Tipos do FleetGrid (arquivo .tsx, conteúdo não lido)
│   │   ├── SkeletonGrid.tsx     # Tipos do SkeletonGrid
│   │   └── page.tsx             # Tipos de página (conteúdo não lido)
│   ├── lib/
│   │   ├── design-tokens.ts     # Tokens Tailwind como strings TypeScript
│   │   ├── theme.ts             # Leitura de CSS vars, chartColors, getStatusColor
│   │   ├── metrics.ts           # Lógica central de métricas: buildPoints, summarize, statusOf
│   │   └── metricThresholds.ts  # Limiares de alerta/risco por métrica
│   └── data/
│       └── mockData.ts          # Dados demonstrativos para sparklines (fallback visual)
├── tests/
│   ├── acceptance_test.js
│   ├── playwright_map_test.js
│   ├── inspect_report_page.js
│   └── ui_refinements_test.js
```

---

## 5. Inventário de Rotas e Páginas

| Rota | Tipo | Finalidade | Origem dos Dados | Auth? | Estado |
|---|---|---|---|---|---|
| `/` | Server (redirect) | Redireciona para `/dashboard` | — | Não | ✅ Funcional |
| `/login` | Client Component | Autenticação de usuário | `POST /api/auth/login/` | Não | ✅ Funcional |
| `/register` | Client Component | Cadastro de usuário | `POST /api/auth/register/` | Não | ✅ Funcional |
| `/dashboard` | Server Component | Central de operações: KPIs, gráficos, mapa, ChatFAB | `GET /api/colheitadeira/`, `GET /api/leituras/ultimas/` | Sim | ✅ Funcional |
| `/colheitadeiras` | Server Component | Lista de máquinas com métricas | `GET /api/leituras/ultimas/` | Sim | ✅ Funcional |
| `/mapa` | Client Component (lazy) | Mapa Leaflet com posições GPS | `GET /api/maquinas/posicao/` (polling 30s) | Sim | ✅ Funcional |
| `/maquinas` | Client Component | Lista de máquinas com busca/filtro | `GET /api/colheitadeira/` | Sim | ✅ Funcional |
| `/maquinas/[id]/prescricao` | Server Component | Prescrição operacional por máquina | `GET /api/prescricoes/{id}/` | Sim | ✅ Funcional |
| `/operarios` | Server Component | Diretório de operários + cadastro | `GET /api/operario/` + `POST /api/operario/` | Sim | ✅ Funcional |
| `/detalhes?id={maquinaId}` | Client Component | Histórico de telemetria + gráficos + prescrição | `GET /api/telemetria/?maquina_id=` | Sim | ✅ Funcional |
| `/relatorios` | Client Component | Relatório consolidado + exportação XLSX | `GET /api/relatorio/`, `GET /api/relatorio/exportar/` | Sim | ✅ Funcional |

### Notas importantes:
- `/detalhes` usa `searchParams` (query string `?id=`), não rota dinâmica `[id]` — isso pode causar conflito de URL com o padrão REST do backend.
- `/maquinas/[id]/prescricao` é Server Component e faz fetch diretamente, sem passar pelo `telemetryService`.
- A rota `/maquinas` e `/colheitadeiras` são páginas distintas que exibem dados similares de fontes diferentes (`getFleetStatus` vs `getLatestReadings`).

---

## 6. Inventário de Componentes Relevantes

### Componentes de integração críticos (dependem de dados da API):

| Componente | Arquivo | Dados consumidos | Observações |
|---|---|---|---|
| `DashboardMachineData` | `src/components/DashboardMachineData.tsx` | `Machine[]`, `Telemetry[]` | Usa mockData como fallback visual para sparklines |
| `MapClient` | `src/components/MapClient.tsx` | `MachinePosition[]` | Polling 30s; normaliza campos alternativos de latitude/longitude |
| `PrescricaoModal` | `src/components/PrescricaoModal.tsx` | `AnalisePrescricao` | Usa SWR; chamado via ChatFAB e página /detalhes |
| `ChatFAB` | `src/components/ChatFAB.tsx` | `Machine[]` (props) | Portal no `document.body`; z-index 70/80 |
| `OperatorDirectory` | `src/components/OperatorDirectory.tsx` | `Operator[]` (props) | Inclui OperatorFormModal para criação |
| `ApiStatusIndicator` | `src/components/ApiStatusIndicator.tsx` | `GET /api/health/` | Polling 15s; espera `{ status: "ok" }` |
| `FleetMap` | `src/components/FleetMap.tsx` | Delegado ao MapClient | Wrapper simples |

### Componentes visuais sem dependência de API:
`MetricCard`, `MetricTrendChart`, `MetricColumnChart`, `HistoryChart`, `SparklineCard`, `StatusBadge`, `Sidebar`, `AppShell`, `SessionGate`, `ThemeToggle`, `FieldNodeLogo`, `EmptyState`, `BackButton`, `SkeletonGrid`

---

## 7. Arquitetura da Camada de API

### Resolução da URL base

**Arquivo:** `src/services/telemetryService.ts` (linhas 25–53) e `src/services/authService.ts` (linhas 25–43)

```
Prioridade de resolução (client-side):
1. NEXT_PUBLIC_API_URL (se definida e não terminar em /api, adiciona /api)
2. NEXT_PUBLIC_FIELDNODE_SERVER_API_URL
3. Fallback: "/api" (mesma origem → rewrite do Next.js)

Prioridade de resolução (server-side / SSR):
1. FIELDNODE_SERVER_API_URL
2. NEXT_PUBLIC_API_URL
3. Fallback: "http://127.0.0.1:8000/api"
```

**Rewrite do Next.js (`next.config.ts`):**
```
source:      /api/:path*
destination: ${FIELDNODE_SERVER_API_URL}/:path*/
```
O rewrite garante que chamadas client-side para `/api/*` sejam encaminhadas para o Django sem CORS. O `skipTrailingSlashRedirect: true` é necessário porque o Django usa `APPEND_SLASH`.

### Timeout e tratamento de erros

- **Timeout:** 10.000ms (10s) em todas as chamadas via `AbortController`
- **Erros HTTP:** Lançam `Error` com mensagem `HTTP ${status} ${statusText} ${body}`
- **Erros de parse JSON:** Lançam `Error` com mensagem de falha de parse
- **Validação de contrato:** Zod `safeParse` — falha lança `Error("Formato de dados inesperado recebido do servidor.")` e loga no console com detalhes
- **Autenticação:** `telemetryService.ts`, `MapClient.tsx`, `ApiStatusIndicator.tsx` e exportação de relatórios enviam `Authorization: Token {token}` quando há token local. `X-API-Key` também é enviado quando `NEXT_PUBLIC_FIELDNODE_API_KEY` está definida.

### Autenticação nos endpoints de telemetria

O frontend envia o token quando disponível, inclusive no `MapClient.tsx` e na fila de telemetria. Isso **não transforma `SessionGate` em controle de acesso**: ela verifica somente a presença local do token.

Na cópia Django lida nesta auditoria, as views de leitura e os ViewSets não definem `IsAuthenticated`, e `REST_FRAMEWORK` não configura `DEFAULT_PERMISSION_CLASSES`; portanto, esses endpoints aceitam chamadas sem token. `IngestaoTelemetriaView.post` valida `X-API-Key` manualmente. Como o frontend lê essa chave de `NEXT_PUBLIC_FIELDNODE_API_KEY`, qualquer valor configurado é exposto no bundle do navegador. A decisão sobre autenticação/autorização efetiva e segredo de ingestão exige uma solução no servidor ou proxy server-side; não pode ser corrigida com segurança somente por um header no cliente.

---

## 8. Inventário Completo de Endpoints Utilizados

### 8.1 Autenticação (`authService.ts`)

#### Login
| Campo | Valor |
|---|---|
| Identificador | `login` |
| Arquivo | `src/services/authService.ts` linha 173 |
| Método | POST |
| URL | `/api/auth/login/` |
| Corpo enviado | `{ username: string, password: string }` |
| Resposta esperada | `{ token: string, user: { id: number, username: string, email: string, first_name: string, last_name: string } }` |
| Autenticação | Nenhuma (endpoint público) |
| Tratamento de erros | Tenta parsear `json.errors`, `json.error`, `json.detail` em ordem |
| Armazenamento | Token: `localStorage["fn-auth-token"]`, User: `localStorage["fn-auth-user"]` |
| Confiança | CONFIRMADO NO CÓDIGO |

#### Registro
| Campo | Valor |
|---|---|
| Identificador | `register` |
| Arquivo | `src/services/authService.ts` linha 202 |
| Método | POST |
| URL | `/api/auth/register/` |
| Corpo enviado | `{ username: string, email: string, password: string, first_name?: string, last_name?: string }` |
| Resposta esperada | `{ token: string, user: AuthUser }` (mesmo formato de login) |
| Confiança | CONFIRMADO NO CÓDIGO |

#### Logout
| Campo | Valor |
|---|---|
| Identificador | `logout` |
| Arquivo | `src/services/authService.ts` linha 228 |
| Método | POST |
| URL | `/api/auth/logout/` |
| Headers | `Authorization: Token {token}` |
| Falha silenciosa | Sim — a sessão local é limpa independente da resposta |
| Confiança | CONFIRMADO NO CÓDIGO |

#### Verify Token
| Campo | Valor |
|---|---|
| Identificador | `verifyToken` |
| Arquivo | `src/services/authService.ts` linha 249 |
| Método | GET |
| URL | `/api/auth/me/` |
| Headers | `Authorization: Token {token}` |
| Resposta esperada | `AuthUser` (mesmo objeto do login) |
| Uso atual | Função exportada mas **não encontrada sendo chamada em nenhuma página** — função implementada mas aparentemente não utilizada |
| Confiança | CONFIRMADO NO CÓDIGO (função), NÃO ENCONTRADO (chamada real) |

---

### 8.2 Telemetria e Frota (`telemetryService.ts`)

#### getFleetStatus — Lista de colheitadeiras
| Campo | Valor |
|---|---|
| Identificador | `getFleetStatus` |
| Arquivo | `src/services/telemetryService.ts` linha 107 |
| Método | GET |
| URL | `/api/colheitadeira/` |
| Headers | `Accept: application/json`, `X-API-Key` (se configurada) |
| Parâmetros | Nenhum |
| Resposta esperada | Array de `ColheitadeiraSchema` (ver seção 10) |
| Consumidores | `dashboard/page.tsx`, `maquinas/page.tsx`, `relatorios/page.tsx` |
| Confiança | CONFIRMADO NO CÓDIGO |

#### getMachinePositions — Posições GPS
| Campo | Valor |
|---|---|
| Identificador | `getMachinePositions` |
| Arquivo | `src/services/telemetryService.ts` linha 121 |
| Método | GET |
| URL | `/api/maquinas/posicao/` ou `/api/maquinas/posicao/?maquina_id={id}` |
| Parâmetros | `maquina_id` (query, opcional) |
| Resposta esperada | Array de `PosicaoMaquinaSchema` (ver seção 10) |
| Consumidores | Via `telemetryService.getMachinePositions` — mas **MapClient.tsx faz o fetch direto** (linha 496) sem usar este método |
| Confiança | CONFIRMADO NO CÓDIGO (método existe), INFERIDO (uso real é via fetch direto no MapClient) |

#### getLatestReadings — Últimas leituras de telemetria
| Campo | Valor |
|---|---|
| Identificador | `getLatestReadings` |
| Arquivo | `src/services/telemetryService.ts` linha 136 |
| Método | GET |
| URL | `/api/leituras/ultimas/` |
| Resposta esperada | Array de `LeituraTelemetriaSchema` (ver seção 10) |
| Consumidores | `dashboard/page.tsx`, `colheitadeiras/page.tsx` |
| Confiança | CONFIRMADO NO CÓDIGO |

#### getMachineReadings — Leituras por máquina
| Campo | Valor |
|---|---|
| Identificador | `getMachineReadings` |
| Arquivo | `src/services/telemetryService.ts` linha 147 |
| Método | GET |
| URL | `/api/telemetria/?maquina_id={machineId}` |
| Parâmetros | `maquina_id` (query, obrigatório) |
| Resposta esperada | Array de `LeituraTelemetriaSchema` |
| Consumidores | `detalhes/page.tsx`, `DashboardMachineData.tsx` |
| Confiança | CONFIRMADO NO CÓDIGO |

#### sendTelemetry — Envio de leitura
| Campo | Valor |
|---|---|
| Identificador | `sendTelemetry` |
| Arquivo | `src/services/telemetryService.ts` linha 172 |
| Método | POST |
| URL | `/api/telemetria/` |
| Corpo enviado | `LeituraTelemetriaInputSchema` (ver seção 10) |
| Headers | `Content-Type: application/json`, `X-API-Key` (se configurada) |
| Consumidores | `queueTelemetry` (usado pelo Service Worker) |
| Confiança | CONFIRMADO NO CÓDIGO |

#### queueTelemetry — Fila de telemetria (offline)
| Campo | Valor |
|---|---|
| Identificador | `queueTelemetry` |
| Arquivo | `src/services/telemetryService.ts` linha 191 |
| Método | Mensagem para Service Worker |
| Comportamento | Posta mensagem `QUEUE_TELEMETRY` ao SW; se SW ausente, chama `sendTelemetry` diretamente |
| Confiança | CONFIRMADO NO CÓDIGO |

#### getOperators — Lista de operários
| Campo | Valor |
|---|---|
| Identificador | `getOperators` |
| Arquivo | `src/services/telemetryService.ts` linha 162 |
| Método | GET |
| URL | `/api/operario/` |
| Headers | `X-API-Key` (se configurada) |
| Resposta esperada | Array de `OperatorSchema` (ver seção 10) |
| Consumidores | `operarios/page.tsx` |
| Confiança | CONFIRMADO NO CÓDIGO |

#### getPrescricoes — Lista de prescrições por máquina
| Campo | Valor |
|---|---|
| Identificador | `getPrescricoes` |
| Arquivo | `src/services/telemetryService.ts` linha 207 |
| Método | GET |
| URL | `/api/prescricoes/lista/?maquina_id={machineId}` |
| Parâmetros | `maquina_id` (query, obrigatório) |
| Resposta esperada | Array de `PrescricaoSchema` |
| Consumidores | `getPrescricao` (método interno) |
| Confiança | CONFIRMADO NO CÓDIGO |

#### getAnalisePrescricao — Análise/Prescrição por máquina
| Campo | Valor |
|---|---|
| Identificador | `getAnalisePrescricao` |
| Arquivo | `src/services/telemetryService.ts` linha 228 |
| Método | GET |
| URL | `/api/prescricoes/{machineId}/` |
| Resposta esperada | `AnalisePrescricaoSchema` (ver seção 10) |
| Consumidores | `PrescricaoModal.tsx` (via SWR), `maquinas/[id]/prescricao/page.tsx` (fetch direto) |
| Confiança | CONFIRMADO NO CÓDIGO |

#### getRelatorio — Relatório resumo
| Campo | Valor |
|---|---|
| Identificador | `getRelatorio` |
| Arquivo | `src/services/telemetryService.ts` linha 244 |
| Método | GET |
| URL | `/api/relatorio/?formato={json|csv}&maquina_id={id}&periodo={days}` |
| Parâmetros | `formato` (default: "json"), `maquina_id` (opcional), `periodo` (número de dias, opcional) |
| Resposta esperada | `RelatorioResumoSchema` (ver seção 10) |
| Consumidores | `relatorios/page.tsx` |
| Confiança | CONFIRMADO NO CÓDIGO |

---

### 8.3 Endpoints adicionais (fetch direto, fora do telemetryService)

#### Exportação de relatório
| Campo | Valor |
|---|---|
| Identificador | `exportRelatorio` |
| Arquivo | `src/app/relatorios/page.tsx` linha 78 |
| Método | GET |
| URL | `/api/relatorio/exportar/?maquina_id={id}` |
| Headers | `Accept: */*` |
| Resposta esperada | `Blob` (arquivo XLSX) |
| Transformações | Cria URL de objeto blob e dispara download automático com nome `fieldnode_relatorio_{id}_{date}.xlsx` |
| Confiança | CONFIRMADO NO CÓDIGO |

#### Health check
| Campo | Valor |
|---|---|
| Identificador | `healthCheck` |
| Arquivo | `src/components/ApiStatusIndicator.tsx` linha 16 |
| Método | GET |
| URL | `/api/health/` |
| Timeout | 3.000ms (AbortSignal.timeout) |
| Resposta esperada | `{ status: "ok" }` |
| Confiança | CONFIRMADO NO CÓDIGO |

#### Posições (fetch direto no MapClient)
| Campo | Valor |
|---|---|
| Identificador | `mapPositions` |
| Arquivo | `src/components/MapClient.tsx` linha 496 |
| Método | GET |
| URL | `/api/maquinas/posicao/` |
| Polling | Intervalo de 30.000ms (30s) |
| Normalização | `normalizeApiPositions()` — aceita `lat/lng`, `latitude/longitude`, `latitude_deg/longitude_deg`, `lat_deg/lon`; aceita `telemetria/telemetry/leitura/leitura_atual/last_telemetry` |
| Confiança | CONFIRMADO NO CÓDIGO |

#### createOperator
| Campo | Valor |
|---|---|
| Identificador | `createOperator` |
| Arquivo | `src/services/operatorService.ts` linha 64 |
| Método | POST |
| URL | `/api/operario/` |
| Corpo enviado | `{ nome: string, tempo_de_servico: number, no_banco: boolean }` |
| Resposta esperada | `OperatorSchema` |
| Confiança | CONFIRMADO NO CÓDIGO |

---

## 9. Payloads Enviados e Respostas Esperadas (Resumo)

### Payload de login
```json
{ "username": "string", "password": "string" }
```
### Resposta de login esperada
```json
{
  "token": "string",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string"
  }
}
```

### Payload de registro
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string"
}
```

### Payload de telemetria (envio)
```json
{
  "id": "uuid (opcional)",
  "maquina_id": "string (min 1)",
  "temperatura": "number",
  "vibracao": "number",
  "rpm": "integer",
  "latitude": "number (-90..90, opcional)",
  "longitude": "number (-180..180, opcional)",
  "timestamp": "string ISO 8601 (min 1)"
}
```

### Payload de criação de operário
```json
{ "nome": "string", "tempo_de_servico": 5, "no_banco": true }
```

---

## 10. Contratos de Dados e Tipagem

### 10.1 `LeituraTelemetriaSchema` (telemetria recebida)
**Arquivo:** `src/schemas/telemetria.ts`

```typescript
// Input (envio ao backend)
{
  id?: string (UUID, opcional),
  maquina_id: string,
  temperatura: number,
  vibracao: number,
  rpm: integer,
  latitude?: number,
  longitude?: number,
  timestamp: string
}

// Schema completo (resposta do backend)
{
  id?: string,
  maquina_id: string,
  temperatura: number,
  vibracao: number,
  rpm: integer,
  latitude?: number,
  longitude?: number,
  timestamp: string,
  status_risco?: {
    nivelCor?: string,
    nivelBg?: string,
    rotuloRisco?: string    // Ex: "CRITICO", "ATENCAO"
  },
  nivel_risco?: string,
  total_leituras?: number,
  recebido_em?: string
}
```

**Alias exportado:** `TelemetrySchema` (em `src/schemas/index.ts`)

### 10.2 `ColheitadeiraSchema` (máquina/colheitadeira)
**Arquivo:** `src/schemas/maquinas.ts`

```typescript
{
  id: number,           // z.coerce.number() — aceita string numérica
  ativo?: boolean,
  maquina_id?: string,
  modelo: {
    nome: string,       // default: "Modelo nao informado"
    marca: {
      nome: string      // default: "Marca nao informada"
    }
  },
  operario: {
    nome: string        // default: "Sem operador"
  },
  status_de_operacao: {
    em_operacao: boolean,
    tempo_de_operacao: number
  },
  estado_de_movimento: {
    em_movimento: boolean,
    velocidade: number
  }
}
```

> ⚠️ **COMPATIBILIDADE:** Os campos `modelo`, `operario`, `status_de_operacao`, `estado_de_movimento` usam `z.preprocess` — se vierem como `null` ou `undefined`, o schema retorna objetos com defaults. O backend DEVE retornar esses campos como objetos, não como null/omitir.

### 10.3 `PosicaoMaquinaSchema` (posição GPS)
**Arquivo:** `src/schemas/maquinas.ts`

```typescript
{
  id: number,
  maquina_id?: string,
  modelo: string,        // string plana, não objeto
  lat: number,
  lng: number,
  status: string,        // "operando" | "parada" | outros
  telemetria: {
    temperatura: number,
    rpm: number,
    timestamp: string
  }
}
```

> ⚠️ **IMPORTANTE:** O `MapClient.tsx` implementa `normalizeApiPositions()` que aceita `lat/latitude/latitude_deg/lat_deg` e `lng/longitude/longitude_deg/lon`. O campo `telemetria` aceita alternativas: `telemetria/telemetry/leitura/leitura_atual/last_telemetry`. Isso sugere que o contrato com o backend pode estar em transição ou o backend retorna campos com nomes diferentes.

### 10.4 `OperatorSchema` (operário)
**Arquivo:** `src/types/telemetry.ts`

```typescript
{
  id: number,              // z.coerce.number()
  nome: string,            // default: "Operario sem nome"
  tempo_de_servico: number, // z.coerce.number(), default: 0
  no_banco: boolean        // default: false
}
```

### 10.5 `PrescricaoSchema` (prescrição)
**Arquivo:** `src/schemas/prescricoes.ts`

```typescript
{
  id?: number,
  maquina_id: string,
  titulo: string,
  descricao: string,
  status: "pendente" | "concluida" | "cancelada",
  data_geracao: string
}
```

### 10.6 `AnalisePrescricaoSchema` (análise de IA)
**Arquivo:** `src/schemas/prescricoes.ts`

```typescript
{
  maquina_id: string,
  status: "NORMAL" | "ATENCAO" | "CRITICO",
  motivos: string[],
  metricas: Record<string, unknown>,
  recomendacao: string | null,
  recomendacao_tecnica: string | null,
  explicacao_operador: string | null,
  fonte_explicacao: "ia_generativa" | "fallback_determinístico" | "determinístico",
  gerado_em: string
}
```

### 10.7 `RelatorioResumoSchema` (relatório)
**Arquivo:** `src/schemas/relatorios.ts`

```typescript
{
  status?: string,              // Ex: "ok"
  detalhe?: string,
  periodo: string,
  total_leituras: number,
  maquinas_ativas: number,
  alertas_gerados: number,
  eficiencia_operacional: number,
  dados?: unknown[]
}
```

### 10.8 `AuthUser` (usuário autenticado)
**Arquivo:** `src/services/authService.ts`

```typescript
{
  id: number,
  username: string,
  email: string,
  first_name: string,
  last_name: string
}
```

### 10.9 Limiares operacionais (frontend-only)
**Arquivo:** `src/lib/metricThresholds.ts`

```typescript
temperatura: { alert: 95, critical: 110, unit: "°C", higherIsWorse: true, min: 0, max: 150 }
vibracao:    { alert: 0.5, critical: 0.8, unit: "g", higherIsWorse: true, min: 0, max: 10 }
rpm:         { alert: 1400, critical: 1200, unit: "rpm", higherIsWorse: false, min: 0, max: 3000 }
```

> **DIVERGÊNCIA CONFIRMADA NA CÓPIA LOCAL:** temperatura usa 95/110 °C nos dois lados; vibração usa 0.5/0.8 g no frontend e 5/8 no cálculo do backend; o backend não inclui RPM na classificação de risco, embora o frontend tenha limites 1400/1200. Confirmar unidade e regra operacional antes de alinhar qualquer limite.

---

## 11. Autenticação e Controle de Acesso

### Implementação confirmada

| Aspecto | Implementação | Arquivo |
|---|---|---|
| Tela de login | Formulário com `username` + `password` | `src/app/login/page.tsx` |
| Tela de registro | Formulário com `username, email, password, first_name, last_name` | `src/app/register/page.tsx` |
| Endpoint de login | `POST /api/auth/login/` | `src/services/authService.ts` |
| Endpoint de registro | `POST /api/auth/register/` | `src/services/authService.ts` |
| Endpoint de logout | `POST /api/auth/logout/` | `src/services/authService.ts` |
| Endpoint de verificação | `GET /api/auth/me/` | `src/services/authService.ts` (implementado, uso não verificado) |
| Armazenamento de token | `localStorage["fn-auth-token"]` | `src/services/authService.ts` |
| Armazenamento de usuário | `localStorage["fn-auth-user"]` (JSON) | `src/services/authService.ts` |
| Esquema de token | `Authorization: Token {token}` (DRF Token Auth) | `src/services/authService.ts` |
| Guarda de rota | `SessionGate.tsx` — verifica `localStorage`, sem chamada de rede | `src/components/SessionGate.tsx` |
| Rotas protegidas | Todas dentro do `AppShell` (dashboard, mapa, máquinas, operários, relatórios, detalhes, prescrição) | `src/components/AppShell.tsx` |
| Rotas públicas | `/login`, `/register` (usam `AuthLayout`, fora do `AppShell`/`SessionGate`) | — |
| Tratamento de erros | Parseia `json.errors`, `json.error`, `json.detail` | `src/services/authService.ts` |
| Redirect pós-login | `router.push("/dashboard")` | `login/page.tsx` |
| Redirect sem sessão | `router.replace("/login")` | `SessionGate.tsx` |

### Esquema de token esperado pelo frontend
O frontend aceita `token`, `key` ou `access` como campo do token. `login` aceita usuário ausente e compõe um usuário mínimo; `register` agora rejeita resposta 2xx sem token antes de persistir a sessão. A cópia Django disponível retorna, tanto no login quanto no registro:
```json
{ "token": "string", "user": { "id": 1, "username": "...", ... } }
```
Esse formato vem das views customizadas em `api_tcc/api/views_auth.py`; não é uma resposta presumida do DRF padrão. A compatibilidade com o backend de destino ainda deve ser conferida na revisão que será integrada.

### Endpoints de telemetria sem autenticação
O envio do header pelo navegador está implementado. O risco restante é de segurança no servidor: os endpoints de dados da cópia local estão abertos por padrão e a guarda do frontend é contornável. Além disso, uma chave `NEXT_PUBLIC_*` não pode ser tratada como segredo. Não houve alteração de permissões nem criação de proxy nesta fase.

---

## 12. Máquinas e Dispositivos

### Identificação de máquinas
O frontend usa dois identificadores concorrentes:

| Identificador | Tipo | Uso |
|---|---|---|
| `id` | `number` (coerce) | Chave primária interna do banco (`ColheitadeiraSchema.id`) |
| `maquina_id` | `string` (opcional) | Identificador de negócio, usado em URLs e filtros |

> ⚠️ **RISCO P2 confirmado na cópia local:** o model Django declara `maquina_id` com `null=True, blank=True`; o schema frontend o considera opcional, mas não nullable, e o preprocess atual pode preencher um valor ausente com o `id` numérico interno. Esse fallback pode ser usado indevidamente como identificador de telemetria em filtros/ações. O comportamento para máquinas sem ID de negócio precisa ser decidido antes do merge; não se deve presumir que o ID de banco identifica a máquina na telemetria.

### Relação máquina × operário × leitura
- Uma colheitadeira tem um campo `operario: { nome: string }` (objeto embarcado)
- Uma leitura de telemetria tem `maquina_id` (string) como referência
- Não existe tipo/schema de "dispositivo" separado de "máquina" no frontend

### Status operacional
Derivado de `status_de_operacao.em_operacao: boolean` (na máquina) e de `status: string` (na posição GPS).

---

## 13. Telemetria e Histórico

### Fluxo de dados de telemetria

```
SSR (Server Component, dashboard):
  telemetryService.getLatestReadings() → /api/leituras/ultimas/ → LeituraTelemetriaSchema[]
  → prop initialReadings → DashboardMachineData (hydration imediata)

Client-side (após seleção de máquina):
  telemetryService.getMachineReadings(id) → /api/telemetria/?maquina_id={id} → LeituraTelemetriaSchema[]
  → state readings → gráficos (MetricTrendChart, HistoryChart, MetricColumnChart)
```

### Ordenação esperada
O frontend assume que o backend retorna leituras da **mais nova para a mais antiga** (`buildPoints()` faz `.reverse()` para plotar cronologicamente).

### Campos usados diretamente nos gráficos
- `temperatura` (número)
- `vibracao` (número)
- `rpm` (número inteiro)
- `timestamp` (string ISO 8601 — parseada como `new Date(timestamp)`)
- `status_risco.rotuloRisco` (string: "CRITICO", "ATENCAO", ou undefined/normal)
- `maquina_id` (string — para filtrar leituras por máquina)

### Intervalo de atualização
- Dashboard: sem polling automático (Server Component com `force-dynamic`)
- Mapa: polling a cada 30s (setInterval no MapClient)
- Detalhes: carga única ao montar (sem polling)
- PrescricaoModal: SWR com `revalidateOnFocus: false`

---

## 14. Trust Score e Qualidade dos Dados

**NÃO ENCONTRADO** no código atual.

O schema `LeituraTelemetriaSchema` inclui:
- `status_risco?: { nivelCor, nivelBg, rotuloRisco }` — indicador de risco por leitura
- `nivel_risco?: string` — campo alternativo de risco

Não existe campo `trust_score`, `confiabilidade`, `qualidade`, `data_quality` ou similar nos schemas ou componentes. O frontend exibe o `status_risco.rotuloRisco` como "CRITICO" / "ATENCAO" / "NORMAL", mas não há cálculo ou exibição de um Trust Score numérico.

Se o backend Leviatã V2 expuser um Trust Score, o frontend precisará de componente e schema novos para exibi-lo.

---

## 15. Anomalias e Inteligência Artificial

O frontend implementa integração com um sistema de **prescrição operacional** que tem um campo `fonte_explicacao` com os valores:
- `"ia_generativa"` — texto gerado por IA
- `"fallback_determinístico"` — modo offline/seguro
- `"determinístico"` — regra determinística

O frontend **não calcula anomalias**. Ele exibe o resultado da análise do backend no campo `AnalisePrescricaoSchema`. A função de IA (quando presente) produz o texto em `explicacao_operador` ou `recomendacao_tecnica`.

O componente `PrescricaoModal.tsx` exibe o `status` ("NORMAL", "ATENCAO", "CRITICO") e a explicação textual. Não há listagem de anomalias individuais — apenas o resultado consolidado da análise.

---

## 16. Eventos e Decisões

**NÃO ENCONTRADO** no código atual.

Não existe página, componente, tipo, schema ou chamada de API relacionada a "eventos" ou "decisões" de manutenção. O campo `status` da prescrição (`"pendente" | "concluida" | "cancelada"`) é o mais próximo, mas não há interface para aprovar, rejeitar ou executar ações.

O componente `OperatorDetail` tem a seguinte nota explícita (linha 134):
> *"Edição e inativação de operários ainda não têm tela — em desenvolvimento."*

---

## 17. Mocks e Modo Demonstrativo

### Arquivo de mocks
**Arquivo:** `src/data/mockData.ts`

Contém dados estáticos para uso como **fallback visual apenas**:

| Export | Uso |
|---|---|
| `mockRpmSeries` | Sparkline de RPM quando não há leituras reais |
| `mockTemperaturaSeries` | Sparkline de temperatura quando não há leituras reais |
| `mockVibracaoSeries` | Sparkline de vibração quando não há leituras reais |
| `mockFleetSummary` | Definido mas **uso não encontrado** nos arquivos lidos |
| `mockTrendSeries` | Definido mas **uso não encontrado** nos arquivos lidos |

### Uso real dos mocks
**Arquivo:** `src/components/DashboardMachineData.tsx` (linhas 39–43)

```typescript
const DEMO_SERIES: Record<string, ...> = {
  rpm: mockRpmSeries,
  temperatura: mockTemperaturaSeries,
  vibracao: mockVibracaoSeries,
};
```

Os mocks são usados quando `hasReadings === false` (nenhuma leitura da API para a máquina selecionada). O badge "demonstrativo" é exibido nesse caso (linha 431–433).

### Regras documentadas no mockData.ts
```
- Nunca substituir chamadas reais à API por estes dados.
- Usar apenas quando a API não retornar dados ou para sparklines de demonstração.
- Não importar no telemetryService.
```

### Outros comportamentos de fallback
- `SessionGate.tsx`: verifica `localStorage` sem fazer chamada de rede (tolerância offline intencional)
- `MapClient.tsx`: aceita `externalPositions` como prop (não usa — sempre faz fetch próprio)
- Erro de schema Zod: lança exceção (não faz fallback silencioso)

---

## 18. Configuração e Variáveis de Ambiente

### Arquivo `.env.local` (existente no repositório, valores confirmados)

```bash
# Destino do rewrite /api/* (server-side — usado pelo Next.js no SSR e proxy)
FIELDNODE_SERVER_API_URL=http://127.0.0.1:8000/api

# URL pública (client-side) — COMENTADA por padrão
# Quando ausente, o frontend usa /api (mesma origem via rewrite)
# NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api

# Chave de telemetria — COMENTADA por padrão
# NEXT_PUBLIC_FIELDNODE_API_KEY=00000000-0000-4000-8000-000000000000
```

### Configuração do `next.config.ts`

```typescript
const API_BACKEND = process.env.FIELDNODE_SERVER_API_URL ?? "http://127.0.0.1:8000/api";

// Rewrite: /api/:path* → http://127.0.0.1:8000/api/:path*/
// skipTrailingSlashRedirect: true (Django usa APPEND_SLASH)
// output: "standalone"
// reactStrictMode: true
```

### Variáveis de ambiente usadas pelo frontend

| Variável | Onde | Descrição |
|---|---|---|
| `FIELDNODE_SERVER_API_URL` | `next.config.ts`, `telemetryService.ts`, `authService.ts` (server-side) | URL do backend Django para SSR e proxy |
| `NEXT_PUBLIC_API_URL` | `telemetryService.ts`, `authService.ts` (client-side) | URL do backend para o navegador (opcional, default: /api) |
| `NEXT_PUBLIC_FIELDNODE_SERVER_API_URL` | `telemetryService.ts` (client-side) | Alias alternativo de NEXT_PUBLIC_API_URL |
| `NEXT_PUBLIC_FIELDNODE_API_KEY` | `telemetryService.ts` | Chave de API para header X-API-Key (opcional) |

### Comandos de execução

```bash
# Instalação
npm ci

# Desenvolvimento
npm run dev        # next dev (porta padrão 3000)

# Build
npm run build      # next build

# Produção
npm start          # next start

# Lint
npm run lint       # eslint src
```

---

## 19. Design System e Dependências Visuais

### Tokens de tema (CSS Custom Properties)

**Arquivo:** `src/app/globals.css`

O sistema de tema é baseado em classes na `<html>`:
- `.dark` (padrão) — tema escuro
- `.light` — tema claro

A seleção do tema é persistida em `localStorage["fn-theme"]` e aplicada via script inline no `<head>` antes do primeiro paint (anti-flash).

### Tokens confirmados em `src/lib/design-tokens.ts` e `src/lib/theme.ts`

| Token CSS | Uso |
|---|---|
| `--background` | Fundo global |
| `--foreground` | Texto principal |
| `--panel` | Fundo de painéis |
| `--line` | Bordas |
| `--status-normal` | Verde (operando, ok) |
| `--status-atencao` | Âmbar (atenção) |
| `--status-critico` | Vermelho (crítico) |
| `--status-neutro` | Neutro |
| `--chart-normal-stroke/fill` | Série de gráfico normal |
| `--chart-atencao-stroke/fill` | Série de gráfico atenção |
| `--chart-critico-stroke/fill` | Série de gráfico crítico |
| `--chart-blue-stroke/fill` | Série azul (análise) |
| `--chart-violet-stroke/fill` | Série violeta (tendência) |
| `--glow-normal`, `--glow-normal-strong` | Brilho verde |
| `--glow-amber` | Brilho âmbar |
| `--glow-accent` | Brilho de destaque |
| `--text-1`, `--text-2`, `--text-3` | Hierarquia de texto |
| `--ui-accent` | Cor de ação principal |
| `--panel-glass-mid`, `--panel-glass-strong` | Glassmorphism |
| `--border-subtle` | Borda sutil |
| `--border-highlight` | Borda destacada |
| `--shadow-card`, `--shadow-elevated` | Sombras |
| `--metric-rpm`, `--metric-temperature`, `--metric-vibration` | Cores de métricas específicas |

### Classes CSS compostas

| Classe | Uso |
|---|---|
| `.liquid-glass--elevated` | Glassmorphism com elevação (ChatFAB panel, PrescricaoModal) |
| `.liquid-glass--subtle` | Glassmorphism sutil (overlays do mapa) |
| `.glass-panel` | Painel de vidro genérico |
| `.metric-card` | Card de KPI |
| `.btn-brand` | Botão primário da marca |
| `.app-background` | Fundo da aplicação |
| `.app-nav`, `.app-nav--rail`, `.app-nav--bar` | Navegação |
| `.app-nav--active` | Item de nav ativo |
| `.chat-panel-slot`, `.chat-fab-slot` | Posicionamento do ChatFAB |
| `.chat-panel`, `.chat-fab` | Visual do chat |
| `.kpi-group`, `.kpi-group__grid` | Grupo de KPIs |
| `.status-pill` | Pílula de status |
| `.op-list-card`, `.op-list-row` | Tabela de operários |

### Fontes

| Variável CSS | Fonte | Uso |
|---|---|---|
| `--font-display` | Space Grotesk | Títulos e KPIs |
| `--font-body` | Inter | Corpo de texto |
| `--font-brand-field` | Snippet | "FIELD" no logo |
| `--font-brand-node` | Staatliches | "NODE" no logo |

### Dependências visuais que podem quebrar no merge

1. **Aliases TypeScript:** `@/` → `./src/` — deve ser mantido no `tsconfig.json`
2. **Imports de CSS globais:** `globals.css` deve ser importado no `layout.tsx`
3. **Fontes Google:** carregadas no `layout.tsx` via `next/font/google` — não quebrará se mantido
4. **Assets públicos:** `public/manifest.json`, `public/sw.js`, `public/icon-192.png` — devem ser mantidos
5. **Leaflet CSS:** `import "leaflet/dist/leaflet.css"` no `MapClient.tsx` — necessário para o mapa funcionar
6. **OpenStreetMap tiles:** dependência de serviço externo sem autenticação
7. **z-index hierarquia:**
   - `z-0`: conteúdo do mapa
   - `z-10`: overlays do mapa (painéis de busca)
   - `z-50`: Sidebar (desktop rail) e mobile bottom bar
   - `z-[70]`: ChatFAB botão
   - `z-[80]`: ChatFAB painel
   - `z-[110]`: Bottom-sheet de detalhe do operário (mobile)
   - `z-[120]`: PrescricaoModal

---

## 20. Build, Testes e Comandos de Execução

### Scripts disponíveis (`package.json`)
```bash
npm run dev    # next dev
npm run build  # next build
npm start      # next start
npm run lint   # eslint src
```

**Não existe script `tsc --noEmit` nem `test` no package.json** — a verificação de tipos TypeScript deve ser executada manualmente.

### Dependências opcionais (`optionalDependencies`)
```json
"@tailwindcss/oxide-linux-x64-gnu": "^4.3.0",
"lightningcss-linux-x64-gnu": "^1.32.0"
```
Essas dependências são específicas para Linux x64. Em Windows (ambiente atual), elas não serão instaladas. Isso pode causar diferença de comportamento na compilação do CSS entre ambientes.

### Testes Playwright existentes
```
tests/acceptance_test.js
tests/playwright_map_test.js
tests/inspect_report_page.js
tests/ui_refinements_test.js
```
Conteúdo não lido integralmente — verificar se os testes requerem backend rodando.

### Snapshot histórico do git registrado na auditoria anterior (não representa o status desta etapa)

```
Modificados (não commitados):
 D public/brand/auth-backdrop.jpg      (deletado)
 M src/app/detalhes/page.tsx
 M src/app/globals.css
 M src/app/login/page.tsx
 M src/app/register/page.tsx
 M src/components/DashboardMachineData.tsx
 M src/components/MetricCard.tsx
 M src/components/MetricColumnChart.tsx
 M src/components/MetricTrendChart.tsx
 M src/components/OperatorDirectory.tsx
 M src/components/SparklineCard.tsx
 M src/components/UserProfile.tsx
 M src/lib/metrics.ts

Novos (não rastreados):
?? public/brand/field-backdrop.jpg     (novo arquivo de fundo do login)
?? src/components/OperationClock.tsx   (componente novo)
?? src/components/OperatorFormModal.tsx (modal de criação de operário — novo)
?? src/services/operatorService.ts     (serviço de criação de operário — novo)
```

> ⚠️ Esses arquivos modificados e novos são parte do trabalho em andamento. O merge deve preservar todas essas mudanças.

---

## 21. Matriz de Compatibilidade e Riscos

| # | Área | Implementação atual do frontend | Expectativa de integração | Evidência | Risco | Próxima validação |
|---|---|---|---|---|---|---|
| 1 | **Autorização dos endpoints de dados** | O frontend envia token quando existe; `SessionGate` só verifica storage | Na cópia Django, leituras e ViewSets não exigem token; ingestão POST exige `X-API-Key` | `telemetryService.ts`, `MapClient.tsx`, `SessionGate.tsx`, `views_ingestao.py`, `settings.py` | **P1 — BLOQUEADOR DE SEGURANÇA** | Definir política de autorização no backend de destino e remover segredo do bundle público; exige decisão/alteração server-side |
| 2 | **Formato de resposta de auth** | Aceita token como `token`, `key` ou `access`; registro exige token; usuário pode ser sintetizado | Views customizadas locais retornam `{ token, user }` | `authService.ts`; `api/views_auth.py` | **Sem incompatibilidade confirmada na cópia local** | Confirmar a revisão de destino; não assumir o mesmo contrato em produção |
| 3 | **URLs de auth** | Usa `/api/auth/login/`, `/api/auth/register/`, `/api/auth/logout/`, `/api/auth/me/` como caminhos primários | Todas estão registradas em `api_tcc/urls.py` | `authService.ts`; `api_tcc/urls.py` | **Sem incompatibilidade confirmada na cópia local** | Conferir que o backend integrado mantém essas rotas |
| 4 | **Endpoint `/api/colheitadeira/`** | Espera lista e relações aninhadas em `ColheitadeiraSchema` | Router local registra `colheitadeira`; serializer local usa relações aninhadas e inclui `maquina_id` nullable | `telemetryService.ts`; `api_tcc/urls.py`; `api/serializers.py`; `models.py` | **P2 — IMPORTANTE** para registros sem ID de negócio | Decidir a semântica de `maquina_id = null`; não usar ID interno como ID de telemetria |
| 5 | **Endpoint `/api/leituras/ultimas/`** | Espera lista com leituras, métricas e `status_risco` | Rota local existe e retorna lista; cada item é a leitura mais recente de uma máquina | `telemetryService.ts`; `api_tcc/urls.py`; `api/views_ingestao.py` | **Sem incompatibilidade estrutural confirmada na cópia local** | Confirmar a revisão de destino e o limite de 10 máquinas |
| 6 | **Rótulos de `status_risco`** | A UI compara `CRITICO`/`ATENCAO`/`NORMAL` | Backend local retorna objeto, mas usa `Crítico`/`Alerta`/`Normal` | `schemas/telemetria.ts`; `services/telemetria.py`; consumidores em `colheitadeiras/page.tsx` | **Corrigido no frontend**: schema normaliza acentos e rótulos para os valores usados pela UI | Confirmar se backend de destino mantém esses rótulos |
| 7 | **`maquina_id` ausente** | Campo opcional no schema; preprocess pode usar `id` interno como fallback | Model local permite `null`/vazio | `schemas/maquinas.ts`; `api_tcc/models.py` | **P2 — IMPORTANTE**: ID interno pode ser confundido com ID de telemetria | Definir se máquina sem ID deve ser ocultada/desabilitada ou se o backend deve garantir o campo |
| 8 | **Health check `/api/health/`** | Espera `{ status: "ok" }`; qualquer HTTP 200 é considerado online | Rota local existe e retorna `status` e `database` | `ApiStatusIndicator.tsx`; `api_tcc/urls.py`; `api/views_health.py` | **Sem incompatibilidade de rota**; resposta `degradado` ainda pode ser exibida como online devido ao fallback HTTP 200 | Confirmar a semântica desejada para estado degradado |
| 9 | **Endpoint `/api/maquinas/posicao/`** | Espera `id`, `maquina_id`, `modelo`, `lat`, `lng`, `status`, `telemetria` | A view local retorna esses campos e filtra máquinas sem coordenadas | `schemas/maquinas.ts`; `MapClient.tsx`; `api_tcc/views_gps.py` | **Sem incompatibilidade estrutural confirmada**, exceto `maquina_id = null` que não é aceito pelo schema de posição | Garantir identificador não nulo ou definir tratamento frontend para registros sem ID |
| 10 | **Endpoint `/api/prescricoes/{maquina_id}/`** | Espera `AnalisePrescricaoSchema` usando ID de máquina como segmento | Rota local existe; compatibilidade do payload ainda requer comparação do schema com a view | `telemetryService.ts`; `api_tcc/urls.py` | **P2 — IMPORTANTE pendente** quanto ao formato da resposta | Comparar `AnalisePrescricaoSchema` com a resposta real do backend de destino |
| 11 | **Endpoint `/api/relatorio/exportar/`** | Espera Blob XLSX e envia token quando existente | Rota local existe e `RelatorioExportarView` retorna XLSX | `relatorios/page.tsx`; `api_tcc/urls.py`; `api/views_relatorio.py` | **Sem incompatibilidade de rota/formato confirmada na cópia local** | Confirmar que deploy e backend de destino incluem a view |
| 12 | **Limiares de risco do frontend vs backend** | Frontend: temperatura 95/110 °C, vibração 0.5/0.8 g, RPM 1400/1200 | Serviço local: temperatura >95/>110, vibração >5/>8; risco do backend não classifica RPM | `metricThresholds.ts`; `api_tcc/services/telemetria.py` | **P2 — IMPORTANTE confirmado nos números; unidade/regra de negócio pendente** | Confirmar unidade de vibração e fonte de verdade antes de alterar limites ou classificação |
| 13 | **Redux não utilizado** | Dependência instalada, uso não encontrado | Pode ser depedência legada ou planejada | `package.json` | **P3 — MENOR** | Verificar se há uso em arquivo não auditado; remover se legado |
| 14 | **CORS** | Rewrite do Next encaminha `/api/*` pelo servidor Next; URL pública direta pode ignorar o rewrite | A configuração Django local lista origens de desenvolvimento; produção deve usar proxy same-origin ou permitir explicitamente a origem do frontend | `next.config.ts`; `setup/settings.py` | **P2 — deployment condicional**, não bloqueador quando o rewrite same-origin está ativo | Confirmar variáveis de deploy e `CORS_ALLOWED_ORIGINS` do backend de destino |
| 15 | **Ordenação das leituras** | `buildPoints` inverte o array assumindo chegada da mais nova para a mais antiga | Model local ordena `/telemetria/` por `-timestamp`; `/leituras/ultimas/` retorna uma por máquina e ordena por `maquina_id`, não por timestamp global | `metrics.ts`; `api_tcc/models.py`; `api/views_ingestao.py` | **P2 — IMPORTANTE** se a lista de últimas leituras for usada como série temporal entre máquinas | Validar qual endpoint alimenta cada gráfico e não interpretar lista de frota como histórico temporal |
| 16 | **Campos snake_case** | Frontend usa `maquina_id`, `tempo_de_servico`, `no_banco`, `status_de_operacao`, `estado_de_movimento` | Django naturalmente usa snake_case — deve ser compatível | Schemas todos | **P3 — MENOR** | Confirmar naming convention no serializer |
| 17 | **`verifyToken` não chamado** | Função existe mas não foi encontrada sendo chamada | Pode ser bug de implementação ou função planejada | `authService.ts` linha 244 | **P3 — MENOR** | Verificar se há chamada em arquivo não auditado; adicionar se necessário |
| 18 | **`mockFleetSummary` e `mockTrendSeries` não usados** | Exportados em mockData.ts mas não encontrados sendo importados | Código morto ou intencionalmente reservado | `data/mockData.ts` linha 29, 37 | **P3 — MENOR** | Verificar antes de remover |

---

## 22. Itens que Precisam ser Validados no Backend de Destino

As confirmações abaixo foram feitas por leitura estática da cópia Django no workspace, não por chamadas HTTP nem contra produção. Revalidar quando o backend Leviatã V2 de destino estiver disponível:

1. **Segurança/autorização:** decidir e implementar no servidor quais endpoints de leitura exigem usuário autenticado. A presença do token no frontend e o `SessionGate` não protegem endpoints públicos.
2. **Chave da ingestão:** `NEXT_PUBLIC_FIELDNODE_API_KEY` é pública no bundle; validar alternativa server-side para que uma chave secreta não seja distribuída ao navegador.
3. **`maquina_id` nulo:** o model local permite ausência, mas a UI precisa decidir como apresentar/desabilitar ações sem ID de telemetria. Validar também dados existentes.
4. **Rotas e payloads de auth:** estão presentes na cópia local; confirmar que o backend de destino preserva as mesmas URLs e `{ token, user }`.
5. **`status_risco` e limiares:** a estrutura local está confirmada e os rótulos são normalizados no frontend; confirmar limites, especialmente unidade de vibração (0.5/0.8 no frontend versus 5/8 no serviço local) e ausência de risco por RPM no backend.
6. **`maquina_id` nulo em mapa/frota:** a resposta GPS local reflete o campo nullable do model, mas o schema de posição exige string opcional não nullable. Decidir tratamento antes de aceitar registros nulos.
7. **Relatórios, health, posições e prescrições:** health e exportação existem na cópia local; conferir os contratos completos e a disponibilidade no deploy de destino.
8. **CORS/deploy:** confirmar se o frontend usa o rewrite same-origin. Se `NEXT_PUBLIC_API_URL` apontar diretamente para outra origem, liberar a origem real no Django; a lista local contém apenas origens de desenvolvimento.
9. **Ordenação:** `/telemetria/` usa `-timestamp` no model local; `/leituras/ultimas/` seleciona uma leitura por máquina e ordena por `maquina_id`. Confirmar o endpoint apropriado para cada visualização.

---

## 23. Recomendações para o Merge

### Antes do merge:

1. **Mapear cada endpoint do frontend para a view do Django** — usar a tabela de endpoints (seção 8) como checklist.
2. **Definir autorização server-side** para dados operacionais. O frontend já envia token quando há sessão, mas a cópia Django deixa endpoints de leitura públicos; não confiar na guarda client-side.
3. **Retirar segredos do bundle público**: `NEXT_PUBLIC_FIELDNODE_API_KEY` é visível ao usuário; definir proxy server-side ou mecanismo de ingestão adequado antes de usar chave real no navegador.
4. **Resolver `maquina_id` nullable** e testar filtros/ações para máquinas sem identificador de telemetria.
5. **Manter a normalização dos rótulos de risco** e comparar limites do backend com os indicadores locais.
6. **Preservar o rewrite `/api/*`** ou configurar CORS para a origem real quando chamadas forem diretas entre domínios.

### Durante o merge:

7. **Não alterar `telemetryService.ts`** sem autorização explícita — é contrato protegido.
8. **Não alterar os schemas Zod** sem comparar com o que o backend realmente retorna — falha de schema = tela de erro.
9. **Manter o alias `@/`** no `tsconfig.json`.
10. **Manter `skipTrailingSlashRedirect: true`** no `next.config.ts` — necessário para Django.
11. **Manter os arquivos novos não rastreados** (`OperatorFormModal.tsx`, `operatorService.ts`, `OperationClock.tsx`, `field-backdrop.jpg`).

### Após o merge:

12. **Testar cada rota com o backend real** — especialmente `/api/leituras/ultimas/`, `/api/colheitadeira/` e autenticação.
13. **Confirmar rótulos e regras de `status_risco`** — o schema já normaliza os rótulos conhecidos; validar com o backend integrado os limites e as unidades, especialmente vibração e RPM.
14. **Executar `npm run lint && npx tsc --noEmit && npm run build`** antes de declarar o merge completo.
15. **Executar os testes Playwright** (`tests/`) contra o ambiente integrado.

---

## 24. Checklist de Preservação Funcional

### ✅ Funcionalidades prontas (integração real com API)

- [ ] Login com token DRF (`/login`)
- [ ] Registro de usuário (`/register`)
- [ ] Logout com invalidação de token no backend
- [ ] Dashboard com dados de frota e telemetria em tempo de servidor
- [ ] Seletor de máquina com gráfico de saúde operacional e KPIs
- [ ] Lista de máquinas com métricas de alerta (`/colheitadeiras`)
- [ ] Mapa de frota com posições GPS e polling 30s (`/mapa`)
- [ ] Lista de máquinas com busca e filtro (`/maquinas`)
- [ ] Histórico de telemetria por máquina com gráficos (`/detalhes`)
- [ ] Prescrição operacional por máquina (modal e página dedicada)
- [ ] Relatório consolidado com geração e exportação XLSX (`/relatorios`)
- [ ] Diretório de operários com detalhe e cadastro (`/operarios`)
- [ ] ChatFAB "Pergunte à IA" com seleção de máquina e análise de prescrição
- [ ] Indicador de status da API (polling `/api/health/`)
- [ ] Guarda de sessão baseada em `localStorage` (offline-first)
- [ ] Service Worker com fila de telemetria offline
- [ ] Tema dark/light com anti-flash e persistência em `localStorage`
- [ ] Design system glassmorphism com tokens CSS

### ⚠️ Funcionalidades parcialmente prontas

- [ ] `verifyToken` — implementado mas aparentemente não chamado em nenhuma página
- [ ] Filtro por `maquina_id` em `/api/maquinas/posicao/` — método existe no service mas MapClient faz fetch direto

### 📋 Funcionalidades demonstrativas (mocks visuais)

- [ ] Sparklines de KPI quando não há leituras para a máquina selecionada (usa `mockData.ts`)

### ❌ Funcionalidades não implementadas (ausentes no código)

- [ ] Trust Score / confiabilidade dos dados
- [ ] Lista e detalhe de anomalias
- [ ] Eventos e decisões de manutenção
- [ ] Edição/inativação de operários
- [ ] Aprovação/rejeição de prescrições
- [ ] Paginação em qualquer listagem

---

## 25. Evidências Técnicas e Limitações da Auditoria

### O que foi lido integralmente:
- Todos os arquivos de `src/services/`
- Todos os arquivos de `src/schemas/`
- Todos os arquivos de `src/types/api.ts` e `src/types/telemetry.ts`
- Todos os arquivos de `src/lib/`
- Todos os arquivos de `src/data/`
- Todos os arquivos de `src/app/` (pages)
- Componentes: `AppShell`, `SessionGate`, `Sidebar`, `ChatFAB`, `PrescricaoModal`, `DashboardMachineData`, `MapClient`, `MapaFrota`, `OperatorDirectory`, `ApiStatusIndicator`, `layout.tsx`

### O que não foi lido (limitações):
- `src/types/telemetryService.ts` — conteúdo não lido
- `src/types/FleetGrid.tsx` e `src/types/SkeletonGrid.tsx` — conteúdo não lido
- `src/types/page.tsx` — conteúdo não lido
- `src/components/ui/FeedbackStates.tsx` — conteúdo não lido (apenas interface de uso inferida)
- `src/components/FleetGrid.tsx` — conteúdo não lido
- `src/components/FleetMap.tsx` — lido superficialmente (wrapper simples)
- `src/components/HistoryChart.tsx`, `MetricTrendChart.tsx`, `MetricColumnChart.tsx`, `SparklineCard.tsx`, `MetricCard.tsx` — conteúdo não lido
- `src/components/ReportButton.tsx`, `ReportPreview.tsx` — conteúdo não lido
- `src/components/StatusBadge.tsx`, `LogoutButton.tsx`, `ThemeToggle.tsx`, `UserProfile.tsx` — conteúdo não lido
- `src/components/AuthLayout.tsx`, `FieldNodeLogo.tsx`, `BackButton.tsx` — conteúdo não lido
- `src/components/ServiceWorkerBridge.tsx` — conteúdo não lido
- `public/sw.js` — Service Worker não lido
- `src/app/globals.css` — CSS global não lido integralmente
- Todos os testes em `tests/` — não lidos
- `tsconfig.json` — não lido
- `.gitignore`, `README.md` (se existir) — não lidos

### Classificações usadas neste documento:
- **CONFIRMADO NO CÓDIGO** — comportamento diretamente demonstrado pela implementação lida
- **INFERIDO** — interpretação plausível, não comprovada integralmente
- **NÃO ENCONTRADO** — funcionalidade não localizada durante a investigação
- **PRECISA VALIDAR NO BACKEND** — expectativa do frontend cuja compatibilidade depende do backend

---

*Documento produzido via auditoria de código. Nenhum arquivo do backend foi alterado ou acessado. Apenas o arquivo `CONTRATO_FRONT_BACK.md` foi criado nesta fase.*
