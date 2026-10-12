# Semana 10 — Consolidado de estado do projeto

**Data de referência:** 09/10/2026
**Bloco de origem:** S9 (todas as tarefas)

---

## 1. Estado técnico verificado

| Tarefa | Entrega | Estado | Pendência |
|---|---|---|---|
| S9-T1 — Attention Engine / Priority Score | `Event.priority_score`, testes em `test_eventos.py` | VERIFICADO | — |
| S9-T2 — Universal Telemetry Model | `RawTelemetry`, `CanonicalTelemetry`, `FabricanteMapping`, migration 0024 | VERIFICADO | `TrustScore` e `EventEngine` não consomem `CanonicalTelemetry`; ressalva registrada em `S9-T2_UNIVERSAL_TELEMETRY_MODEL.md` |
| S9-T3 — PoC IA agentiva | `gerar_decisao_agentiva`, `test_agentic.py`, DLQ com contexto `AGENTIC_LLM` | VERIFICADO (código e testes) | Execução real contra Gemini não concluída: `GEMINI_API_KEY` vazia e sem `Event` elegível na base local; registrado em `S9-T3_AGENTIC_AI_POC.md` |
| S9-T4 — Roteiro de validação comercial | `docs/ROTEIRO_VALIDACAO_COMERCIAL.md`, commit `12f2333` | VERIFICADO | Revisão pelo grupo não confirmada no repositório |
| S9-T5 — Consolidação comercial | `docs/RESULTADOS_VALIDACAO_COMERCIAL.md`, commit `0993b3e` | VERIFICADO | Ver seção 2 |

### Ressalva S9-T2

`TrustScore` e `EventEngine` operam sobre `LeituraTelemetria` diretamente, não sobre `CanonicalTelemetry`. O modelo universal existe e está testado, mas o pipeline de análise ainda não o consome. Isso não é regressão — é uma lacuna de integração a fechar em iteração futura.

### Ressalva S9-T3

A PoC está implementada e testada. A demonstração externa com Gemini e a captura de `Decision` agentiva no dashboard dependem de `GEMINI_API_KEY` configurada e de `Event` com `priority_score` elegível na base. Sem essas duas condições, qualquer `Decision` agentiva no banco seria fabricada. A entrega é tecnicamente válida; a demonstração ao vivo permanece pendente.

---

## 2. Lacuna comercial — dívida explícita para S10

Esta seção é obrigatória. A validação comercial do FieldNode **não está concluída** e não deve ser apresentada como concluída à banca.

### Estado real (auditável)

| Critério | Estado |
|---|---|
| Registros históricos investigados | 3 (John Deere, Solinftec, Case IH — todos de 19/09/2026) |
| Entrevistas com evidência primária auditável | 0 |
| Meta de 5–6 conversas | NÃO ATINGIDA |
| Perfis operacionais representados (gestor, manutenção, supervisor, operador, TI usina) | 0 verificáveis |
| Disposição concreta de pagar | NÃO EVIDENCIADA (nível 0 nos três registros) |

### O que isso significa para a banca

- A tese comercial do FieldNode é uma **hipótese exploratória**, não uma validação de mercado.
- Os três registros históricos são sinais compatíveis com as hipóteses, não provas.
- O valor de R$ 5.000–15.000/hora de parada é um relato preservado de documento anterior, sem fonte de medição verificável neste ciclo.
- O teto de R$ 500/máquina (Solinftec) é critério relatado, não orçamento nem compromisso.

### O que não fazer

- Não apresentar os três registros históricos como "três entrevistas realizadas".
- Não usar resultados técnicos (testes, dashboard, IA) como substituto de validação comercial.
- Não declarar que "o mercado validou" a solução.

### Caminho para fechar a dívida

Se houver tempo antes da apresentação final:

1. Realizar pelo menos uma entrevista auditável com perfil operacional (gestor de frota, responsável por manutenção ou supervisor de colheita) usando o roteiro `docs/ROTEIRO_VALIDACAO_COMERCIAL.md`.
2. Preencher a ficha de registro do roteiro (seção 8) e anexar ao repositório.
3. Atualizar `docs/RESULTADOS_VALIDACAO_COMERCIAL.md` com a ficha preenchida.
4. Não inventar entrevista. Uma entrevista real com ficha parcial é mais defensável do que três registros históricos sem fonte primária.

Se não houver tempo:

- Apresentar a lacuna diretamente: "realizamos descoberta qualitativa com especialistas técnicos de fabricantes; validação com usuários operacionais e compradores permanece como próximo passo".
- Isso é metodologicamente honesto e defensável perante banca técnica.

---

## 3. Pendências técnicas abertas

| Item | Origem | Impacto | Ação sugerida |
|---|---|---|---|
| `TrustScore` / `EventEngine` não consomem `CanonicalTelemetry` | S9-T2 | Baixo para TCC; médio para produto | Registrar como dívida técnica; não bloqueia apresentação |
| Execução real do Gemini na PoC agentiva | S9-T3 | Baixo para TCC (código e testes existem) | Configurar `GEMINI_API_KEY` e popular `Event` elegível antes da demo |
| Revisão do roteiro S9-T4 pelo grupo | S9-T4 | Baixo | Confirmar leitura coletiva antes da apresentação |
| Entrevistas comerciais auditáveis | S9-T5 | Alto para tese comercial | Ver seção 2 |

---

## 4. O que está sólido para a banca

- Pipeline de telemetria: ingestão, deduplicação UUID, validação de payload, DLQ.
- Pipeline de IA: Isolation Forest, Random Forest, regras determinísticas, prescrição.
- Attention Engine com `priority_score` testado.
- Universal Telemetry Model com adaptadores simulados para dois fabricantes.
- PoC de decisão agentiva com auditabilidade (prompt versionado, DLQ, metodologia exposta).
- Resiliência offline: EdgeClient com SQLite outbox, Data Mule, Service Worker.
- Autenticação, DEMO_MODE, permissões — todos com testes verdes.
- Dashboard Next.js com rotas documentadas.
- Documentação técnica honesta sobre limites de hardware, ML e escopo.

---

## 5. Posicionamento recomendado para a apresentação

O FieldNode é um **protótipo técnico funcional** de plataforma de telemetria offline-first para máquinas agrícolas. Demonstra:

- arquitetura tolerante a falhas de rede rural;
- pipeline de análise com múltiplas camadas (regras + ML + LLM);
- modelo de interoperabilidade multi-fabricante (simulado);
- decisão agentiva auditável com revisão humana.

A validação comercial está em estágio exploratório. Três especialistas técnicos de fabricantes forneceram sinais compatíveis com as hipóteses do produto. Validação com usuários operacionais e compradores é o próximo passo identificado e documentado.

Essa posição é honesta, defensável e não subestima o trabalho técnico realizado.
