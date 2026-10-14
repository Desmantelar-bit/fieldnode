# Auditoria final das dez semanas

Referência: 14/10/2026. Escopo: estado observado no repositório, histórico Git disponível, testes executados nesta auditoria e artefatos S10 já presentes.

> **Última atualização:** 14/10/2026 — rodada de auditoria S10-T3 (encerramento do ciclo).

---

## 1. Resumo executivo

O FieldNode termina este ciclo como protótipo técnico funcional de telemetria offline-first, com API Django, banco relacional, worker MQTT, dashboard Next.js, análise por regras e modelos auxiliares, decisão revisável e demonstração closed loop qualificada em Compose.

O resultado não é um produto de campo pronto. Não há validação física em máquina, escala medida, isolamento multi-tenant completo, execução mecânica automática, validação comercial auditável com compradores ou ensaio oral humano registrado. Essas lacunas permanecem explícitas.

### Estado final dos entregáveis S10

| Item | Status |
|---|---|
| Closed loop técnico demonstrável | VERIFICADO |
| 3 ensaios Compose + aprovação humana | VERIFICADO (JSONs + screenshots + vídeo) |
| Vídeo 3ª execução | VERIFICADO (`artifacts/s10/videos/ensaio-03-closed-loop.webm`, 1.198.027 bytes) |
| Pressure test documentado (S10-T3) | VERIFICADO (`docs/INVESTOR_CTO_PRESSURE_TEST.md`, 15 perguntas respondidas) |
| Ensaio oral do grupo | PENDENTE (`docs/ENSAIO_ORAL_PRESSURE_TEST.md` criado; participação humana não comprovada) |
| Validação comercial 5–6 entrevistas | NÃO ATINGIDA (0 entrevistas auditáveis; 3 registros históricos de fabricantes) |
| Hardware físico / campo | NÃO — escopo de software confirmado |
| CanonicalTelemetry no pipeline de análise | PENDENTE (Trust Score e Event Engine consomem `LeituraTelemetria` legada) |
| Gemini real (execução contra API externa) | PENDENTE (`GEMINI_API_KEY` vazia; código e testes existem) |
| Credenciais literais em working tree | CORRIGIDO nesta rodada |
| Credenciais literais no histórico Git | IDENTIFICADO — rotação necessária (ver seção 5) |

---

## 2. Matriz das semanas

| Semana | Estado final | Evidência principal | Lacuna relevante |
|---|---|---|---|
| S1 — identidade e ingestão | CONCLUÍDO (escopo de software) | `docs/CONTRATO_TELEMETRIA_V1.md`, migrations 0014, testes de identidade, concorrência e telemetria | Não prova entrega física nem ordenação universal em campo |
| S2 — segurança e demo | PARCIAL | `test_auth.py`, `test_permissions.py`, `test_demo_mode.py`, `setup/settings.py` | Segurança de produção, rotação e isolamento multi-tenant ainda não comprovados |
| S3 — Trust Score e Data Health | PARCIAL | `services/data_health.py`, migration 0016, `test_data_health.py` | Pipeline não consome `CanonicalTelemetry` |
| S4 — Event e Decision | CONCLUÍDO (fluxo testado) | migrations 0018–0019, `test_eventos.py`, `test_decisions.py`, `test_concurrency.py` | Aprovação não significa execução física |
| S5 — IA e metodologia | PARCIAL (limites documentados) | `api_tcc/ia/`, `test_anomaly_detection.py`, `docs/HONESTIDADE_METODOLOGICA_ML.md` | Sem calibração, validação de campo ou previsão de falha comprovada; aviso de versão scikit-learn |
| S6 — frontend e integração | CONCLUÍDO (fluxo verificado) | `frontend-next/`, lint/build, testes de UI e rota canônica de prescrição | Cobertura visual depende do ambiente |
| S7 — infraestrutura e observabilidade | PARCIAL | `docker-compose.yml`, health check, DLQ, testes de health e logging | Sem carga representativa, SLO ou alta disponibilidade medida |
| S8 — offline e borda | PARCIAL (simulado) | `simulators/edge_client.py`, Data Mule, protocolos e artefatos de resiliência | Sem ESP32 instalado, rádio, campo ou 30 dias comprovados |
| S9 — correlação, IA agentiva e comercial | PARCIAL | Attention Engine, `gerar_decisao_agentiva`, DLQ, roteiro e consolidação comercial | Gemini real não qualificado; 0 entrevistas comerciais auditáveis |
| S10 — consolidação | PARCIAL (T1 e T2 evidenciados) | `docs/S10_EXECUCOES.md`, vídeo, JSONs, README, proposta v5, revisão cruzada | Ensaio oral humano não comprovado; pressure test concluído documentalmente |

Nota: não foi localizado um arquivo único contendo o roadmap integral. A reconstrução foi feita a partir dos documentos do repositório, commits e blocos disponíveis.

---

## 3. Arquitetura observada

```text
EdgeClient / MQTT / HTTP
        → validação e idempotência
        → LeituraTelemetria / RawTelemetry
        → Trust Score e Data Health (modelo legado)
        → Event / prioridade (Attention Engine)
        → Decision pendente
        → aprovação autenticada no dashboard
        → outcome registrado
```

O modelo universal (`CanonicalTelemetry`) existe e está testado, mas Trust Score e Event Engine continuam ligados ao modelo legado. O fluxo demonstrado de S10 usa esse caminho de forma controlada e declarada.

---

## 4. Limpeza e arquitetura

Não foram removidos documentos, scripts ou artefatos de evidência apenas por parecerem antigos. `docs/archive/`, scripts auxiliares e artefatos S10 foram preservados por rastreabilidade.

### Correções desta rodada (14/10/2026)

| Arquivo | Correção |
|---|---|
| `scripts/s10_run_official_trials.py` | Removidos `API_KEY` e `AUTH_TOKEN` literais; substituídos por `os.environ.get()`; adicionada verificação de variáveis vazias com `RuntimeError` explicativo |
| `scripts/demo_pane.py` | Default de `API_KEY` removido; substituído por string vazia |
| `scripts/testar_semana5_ui_decisao.py` | Default de `API_KEY` (`00000000-...`) removido; substituído por `os.environ.get()` |
| `scripts/teste_fluxo_completo.py` | Default de `API_KEY` removido |
| `docs/archive/RESUMO-SEQID.md` | Referência de chave literal substituída por `${FIELDNODE_API_KEY}` |
| `DEMO.md` | Referência de chave literal substituída por `${FIELDNODE_API_KEY}` |
| `README.md` | Referência de chave literal substituída por `${FIELDNODE_API_KEY}` |

### Estrutura preservada

- `.gitignore` cobre ambientes virtuais, `.env`, caches, `node_modules` e bancos locais.
- `docs/archive/` preservado: contém histórico de decisões (SEQ_ID, MQTT, identidade).
- Backup `db.sqlite3.pre-auth-migration-20260924-132308.bak` e bancos SQLite em `artifacts/` identificados como área sensível. **Não removidos** para não destruir evidência; decisão sobre versionamento cabe ao grupo.

---

## 5. Auditoria de segredos

### 5.1. Working tree atual

- Nenhuma credencial real nos arquivos versionados ou rastreados após as correções desta rodada.
- `.env.example` contém apenas placeholders explícitos (`troque-esta-secret-key-antes-de-usar`).
- `frontend-next/.env.local` não contém segredos — verificado.
- `NEXT_PUBLIC_*` não carrega segredos de servidor.

### 5.2. Histórico Git

| Ocorrência | Commit | Arquivo | Tipo | Status |
|---|---|---|---|---|
| Token de autenticação literal (Django `AUTH_TOKEN`) | `44f1568` (origin/main) | `scripts/s10_run_official_trials.py` | Possível segredo real | **ROTACIONAR** |
| API key literal (`fieldnode-demo-2024`) | `44f1568` (origin/main) | `scripts/s10_run_official_trials.py` | Chave de demonstração — verificar se é válida em produção | **ROTACIONAR** |

> **Ação obrigatória:** o commit `44f1568` está publicado em `origin/main`. Os valores são alcançáveis por qualquer pessoa com acesso ao repositório remoto. O grupo deve:
> 1. Invalidar/revogar o token Django (`AUTH_TOKEN`) no painel de administração.
> 2. Substituir a `FIELDNODE_API_KEY` por um novo UUID no ambiente de demonstração.
> 3. Avaliar se a limpeza do histórico é necessária (requer `git rebase` ou `git filter-repo` + `force-push`, com coordenação de todos os colaboradores).

### 5.3. Limites da varredura

- Varredura textual manual com `git log -p`. Ferramenta automatizada (`gitleaks`, `detect-secrets`) não instalada e não executada nesta rodada.
- `git fsck` mostrou objetos inalcançáveis — não expandidos.
- Não equivale a auditoria forense completa de todos os blobs.

---

## 6. Verificações executadas

| Comando | Ambiente | Resultado | Observação |
|---|---|---|---|
| `venv\Scripts\python.exe manage.py test` | SQLite local (testes) | **PASSOU — 282 testes, 0 falhas** | Warnings de versão scikit-learn permanecem; não bloqueiam a suíte |
| `venv\Scripts\python.exe manage.py check` | Local | **PASSOU — 0 issues** | Sistema limpo |
| `venv\Scripts\python.exe manage.py makemigrations --check --dry-run` | Local | **PASSOU — No changes detected** | Modelos coerentes com migrations |
| `git diff --check` | Local | **PASSOU** (avisos de LF/CRLF apenas) | Sem erros de whitespace |
| Verificação de credenciais na working tree | Local | **OK** | Nenhum segredo real encontrado após correções |
| Varredura de histórico Git | `git log -p --all` textual | **IDENTIFICADO** — ver seção 5.2 | 2 ocorrências em commit `44f1568` |
| `npm run lint` em `frontend-next` | Local | PASSOU (estado anterior verificado) | Não repetido nesta rodada |
| `docker compose ps` | Docker Desktop | PASSOU (estado anterior verificado) | Não repetido nesta rodada |

**Nota sobre contagem de testes:** 282 testes na execução desta rodada. A rodada anterior (S10 qualificação) reportou 246 — a diferença reflete testes adicionados nas semanas 8–10. Não há regressão.

---

## 7. Demonstração e ensaio oral

### S10-T1

Três ensaios Compose documentados com aprovação humana pelo dashboard, JSONs, screenshots e vídeo do terceiro ensaio. Evidências em `docs/S10_EXECUCOES.md` e `artifacts/s10/`.

O outcome declara que não houve intervenção mecânica. `APROVADA` ≠ `EXECUTADA`.

### S10-T3

`docs/INVESTOR_CTO_PRESSURE_TEST.md` responde às 15 perguntas da seção 22 do roadmap, com estrutura: resposta oral, evidência, limite e aprofundamento.

O ensaio oral do grupo permanece **PENDENTE**. `docs/ENSAIO_ORAL_PRESSURE_TEST.md` foi criado nesta rodada com protocolo, tabela de cobertura e critério de conclusão. Não há registro de participação humana, ata ou gravação de sessão.

---

## 8. Pendências finais

### Obrigatórias antes da banca

1. **Rotacionar token Django (`AUTH_TOKEN`) e API key** que aparecem no commit `44f1568` do histórico compartilhado. Qualquer pessoa com acesso ao repositório remoto pode extraí-los.
2. **Realizar ensaio oral** com todos os integrantes e preencher `docs/ENSAIO_ORAL_PRESSURE_TEST.md`.

### Recomendadas antes da banca

3. Configurar `GEMINI_API_KEY` no ambiente de demonstração e validar o fluxo agentivo ao vivo.
4. Realizar pelo menos uma entrevista comercial auditável (ver `docs/ROTEIRO_VALIDACAO_COMERCIAL.md`).
5. Avaliar limpeza do histórico Git para remover o commit com credenciais (requer coordenação do grupo e `force-push`).

### Dívida técnica documentada (roadmap futuro, não bloqueia apresentação)

6. Integrar `CanonicalTelemetry` ao Trust Score e ao Event Engine.
7. Fixar e validar a versão de scikit-learn do modelo persistido.
8. Fazer carga representativa e medir ingestão, latência e throughput.
9. Implementar isolamento multi-tenant funcional.
10. Validação física com hardware e campo real.

### Decisão humana necessária

11. Decidir se bancos SQLite (`artifacts/`, backup) devem permanecer versionados.
12. Decidir se a limpeza do histórico Git é necessária e coordenar com todos os colaboradores.

---

## 9. Veredito

**B — IMPLEMENTAÇÃO DO ESCOPO CONCLUÍDA, COM VALIDAÇÕES EXTERNAS PENDENTES.**

Código e documentação dentro do escopo estão finalizados e verificados. A suíte de testes passou (282/282). O fluxo closed loop foi demonstrado três vezes com aprovação humana real. O pressure test cobre todas as 15 perguntas da seção 22.

Permanecem pendentes, por dependerem de ação humana ou acesso externo:
- Rotação de credenciais expostas no histórico Git remoto.
- Ensaio oral real com participação registrada do grupo.
- Execução real da IA agentiva contra Gemini.
- Validação comercial auditável com perfil operacional.
