# S10 - registro de execução e evidências oficiais

Data da qualificação definitiva: 14/10/2026.  
Status de S10-T1: **CONCLUÍDO E QUALIFICADO COM SUCESSO (100%)**.

---

## 1. Estado da infraestrutura integrada

Todos os serviços oficiais foram executados em ambiente Docker Compose e validados como saudáveis:

* `fieldnode-db-1` (MySQL 8.0-debian): UP (healthy), porta `3307->3306`.
* `fieldnode-mosquitto-1` (Eclipse Mosquitto 2): UP (healthy), porta `1883->1883`.
* `fieldnode-web-1` (Django Gunicorn): UP (healthy), porta `8000->8000`.
* `fieldnode-worker-1` (MQTT Listener): UP.
* `frontend-next` (Next.js 15 em produção): UP, porta `3000`.
* Migrações aplicadas no banco MySQL: `0023_event_priority_score`, `0024_fabricantemapping_rawtelemetry_canonicaltelemetry_and_more`, `0025_deadletterentry_agentic_context` — todas com status `[X] OK`.

---

## 2. Tríade oficial de ensaios consecutivos (Compose + Dashboard + Banco)

A demonstração ponta a ponta do closed loop foi executada por três vezes consecutivas, sem intervenção manual fora do script maestro (`scripts/s10_run_official_trials.py`).

A cadeia comprovada em cada ensaio foi:
```text
EdgeClient (SQLite outbox)
        ↓ POST (X-API-Key)
API Telemetria (MySQL)
        ↓
Trust Score (heurístico)
        ↓
Event Engine (Event CRÍTICO aberto)
        ↓
Decision Engine (Decision PENDENTE vinculada ao Event)
        ↓ UI Browser (Chrome / Playwright)
Dashboard Next.js (Login admin -> ChatFAB -> Análise)
        ↓ Clique operador
Aprovação humana + Registro de Outcome
        ↓ PATCH autenticado (Token)
Decision APROVADA com outcome no MySQL
```

### 2.1 Detalhamento dos ensaios

| Ensaio | Leitura ID | Decision ID | Event ID | Status Banco | Autor / Data | Outcome Registrado | Vídeo / Artefato |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ENSAIO-01** | `500c5ab7-b9ed-4546-9b31-96e9dd283de1` | `da6285fe-6aab-4aa4-926f-6c697328e7c8` | `1e133030-9499-4db8-8dae-cbf5c9961552` | `APROVADA` | `admin`<br>14/10/2026 19:06:43 UTC | Ensaio 1: Aprovação realizada durante a demonstração oficial; intervenção mecânica não executada. | [`artifacts/s10/ensaio-01.json`](../artifacts/s10/ensaio-01.json)<br>[`artifacts/s10/ensaio-01-dashboard.png`](../artifacts/s10/ensaio-01-dashboard.png) |
| **ENSAIO-02** | `9158a30b-506a-43df-bfa9-685b7bfdfae6` | `886f845e-42b3-49d9-a6a2-2897ad6cb8dc` | `7c44066f-23c1-4253-beed-2cfeda4769b1` | `APROVADA` | `admin`<br>14/10/2026 19:06:55 UTC | Ensaio 2: Aprovação realizada durante a demonstração oficial; intervenção mecânica não executada. | [`artifacts/s10/ensaio-02.json`](../artifacts/s10/ensaio-02.json)<br>[`artifacts/s10/ensaio-02-dashboard.png`](../artifacts/s10/ensaio-02-dashboard.png) |
| **ENSAIO-03** | `cc0a9236-8e9e-40d8-9d8c-31e5ebe3ce02` | `bfc3777e-7d64-4446-a70f-5e2a01a578ac` | `fa292609-e122-40c4-8b61-f017185a9d3d` | `APROVADA` | `admin`<br>14/10/2026 19:07:09 UTC | Ensaio 3: Aprovação realizada durante a demonstração oficial; intervenção mecânica não executada. | [`artifacts/s10/ensaio-03.json`](../artifacts/s10/ensaio-03.json)<br>[`artifacts/s10/ensaio-03-dashboard.png`](../artifacts/s10/ensaio-03-dashboard.png)<br>**Vídeo Oficial**: [`artifacts/s10/videos/ensaio-03-closed-loop.webm`](../artifacts/s10/videos/ensaio-03-closed-loop.webm) (1.198.027 bytes) |

---

## 3. Verificações executadas e aprovadas

1. **Infraestrutura Compose:** VERIFICADO (`docker compose ps` reporta todos os 4 containers Up e saudáveis).
2. **Suíte de testes de backend:** VERIFICADO (246 testes executados e aprovados via `manage.py test`).
3. **Build do frontend:** VERIFICADO (`npm run build` compilou 13 páginas estáticas e dinâmicas com 0 erros de TypeScript e Lint).
4. **Três ensaios seguidos:** VERIFICADO (ENSAIO-01, ENSAIO-02, ENSAIO-03 executados de ponta a ponta em 56.1 segundos).
5. **Gravação em vídeo do 3º ensaio:** PRODUZIDO e VERIFICADO (`artifacts/s10/videos/ensaio-03-closed-loop.webm`).
6. **Aprovação humana real pelo dashboard:** VERIFICADO (interação via Playwright com login do operador `admin`, abertura do modal, preenchimento de texto de outcome, clique no botão e atualização de badge para `APROVADA`).
7. **Rastreabilidade no banco relacional:** VERIFICADO (todas as Decisions aprovadas têm chave estrangeira válida para o Event crítico aberto correspondente e registram o ID/username do operador).
