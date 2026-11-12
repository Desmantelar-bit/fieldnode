# INVESTOR_CTO_PRESSURE_TEST

**Responsável:** A CONFIRMAR  
**Semana:** S12  
**Status:** ESQUELETO  
**Tarefa de preenchimento:** S12-Tx (confirmar identificador exato no roadmap)  
**Última atualização:** 2026-11-04 — criação do esqueleto (S0-T4)

> **Atenção:** o status deste documento só poderá mudar de `ESQUELETO` para outro quando:
> - as seções obrigatórias estiverem preenchidas com dados reais de S12;
> - as evidências estiverem anexadas ou referenciadas;
> - os critérios de conclusão forem atendidos;
> - a revisão da semana S12 for realizada.
>
> **Regra:** não escrever respostas promocionais. Cada resposta deve apontar para uma evidência
> ou assumir explicitamente que a questão ainda não foi validada. Uma resposta honesta de
> "ainda não validamos X" é mais defensável do que uma resposta vaga ou exagerada.

---

## 1. Objetivo

Preparar o projeto para perguntas técnicas e estratégicas difíceis — do tipo
que um CTO, avaliador técnico sênior ou investidor faria ao examinar o
FieldNode com ceticismo construtivo.

TODO(responsável-S12, por quê: perguntas difíceis não respondidas em defesa ou pitch comprometem a credibilidade; respondê-las com antecedência demonstra maturidade técnica, quando: início de S12): identificar as perguntas mais difíceis com base no estado real do sistema em S12.

---

## 2. Escopo

### Incluído

TODO(responsável-S12, por quê: delimitar o que será coberto aqui, quando: S12): listar os temas que serão tratados (arquitetura, escalabilidade, IA, hardware, etc.).

### Fora do escopo

TODO(responsável-S12, por quê: evitar que este documento prometa respostas que ainda não existem, quando: S12): registrar o que não será tratado (ex: valuation, estratégia de go-to-market, parcerias).

---

## 3. Contexto atual do FieldNode

**Estado verificado em 2026-11-04 (S0-T3):**

Ver `docs/CLAIMS_VS_CODE.md` para o mapa completo de afirmações vs. evidências.

Resumo das limitações técnicas críticas conhecidas em S0:
- Dados 100% simulados (sem sensores físicos reais)
- Sem hardware ESP32 implementado
- Sem dataset rotulado de falhas reais
- Sem avaliação supervisionada de ML
- Build do frontend com débito técnico

TODO(responsável-S12, por quê: atualizar com o estado real após as semanas anteriores, quando: início de S12): complementar com o que foi resolvido e o que permanece como limitação.

---

## 4. Especificação e conteúdo técnico

### 4.1 Arquitetura

**Perguntas esperadas:**
- Por que Django e não FastAPI/Node? Qual a latência da ingestão?
- Como o sistema escala para 100 máquinas? 1.000?
- O que acontece se o banco ficar indisponível durante a ingestão?

TODO(responsável-S12, por quê: decisões arquiteturais sem justificativa são vulneráveis em defesa, quando: S12): documentar a justificativa de cada escolha arquitetural e os limites de escala testados.

### 4.2 Escalabilidade

**Perguntas esperadas:**
- Quantas leituras por segundo o sistema suporta?
- Como o Isolation Forest escala com mais máquinas?
- O Service Worker funciona com múltiplos usuários simultâneos?

TODO(responsável-S12, por quê: escalabilidade não testada precisa ser declarada como não validada, quando: S12): documentar o que foi medido e o que não foi.

**Estado em S0:** Sem benchmark de carga realizado. Sem evidência de escalabilidade além de testes unitários.

### 4.3 Segurança

**Perguntas esperadas:**
- O token em `localStorage` é seguro?
- Como a `X-API-Key` é rotacionada se exposta?
- O que acontece com um payload malicioso via MQTT?

TODO(responsável-S12, por quê: vulnerabilidades de segurança não declaradas são piores do que vulnerabilidades declaradas e mitigadas, quando: S12): para cada questão, apontar o estado atual e o plano de mitigação.

**Referência:** `docs/SEGURANCA.md`.

### 4.4 Confiabilidade

**Perguntas esperadas:**
- Qual o SLA do sistema?
- O que acontece se o worker MQTT cair?
- Os dados offline são realmente garantidos?

TODO(responsável-S12, por quê: confiabilidade sem dados de teste é hipótese, não afirmação, quando: S12): documentar o que foi testado e os limites de cada garantia.

### 4.5 Custos

**Perguntas esperadas:**
- Qual o custo de infra para 50 máquinas?
- O Gemini API tem custo por chamada?
- Qual o custo do ESP32 por máquina?

TODO(responsável-S12, por quê: estimativas de custo sem base são perigosas; é melhor declarar "não calculado" do que inventar, quando: S12): documentar o que foi calculado e o que é estimativa sem validação.

**Estado em S0:** Sem estimativa de custo calculada.

### 4.6 Dependências externas

**Perguntas esperadas:**
- O que acontece se a Gemini API mudar ou sair do ar?
- O sistema funciona sem internet?
- Qual a dependência de bibliotecas de terceiros?

TODO(responsável-S12, por quê: dependências não declaradas são riscos invisíveis, quando: S12): documentar cada dependência externa crítica e o fallback existente.

**Dependências críticas conhecidas em S0:**
- Gemini API — circuit breaker + fallback determinístico implementado
- MySQL 8 — SQLite como alternativa de desenvolvimento
- Mosquitto MQTT — simulador com fallback HTTP

### 4.7 Qualidade dos dados

**Perguntas esperadas:**
- Como você sabe que os dados simulados são representativos?
- O Trust Score foi validado com dados reais?
- Como o sistema lida com sensor defeituoso?

TODO(responsável-S12, por quê: dados simulados sem validação de representatividade limitam as conclusões, quando: S12): documentar o que pode e o que não pode ser afirmado sobre a qualidade dos dados.

**Referência:** `docs/DATA_HEALTH.md` e `docs/CLAIMS_VS_CODE.md`.

### 4.8 Metodologia de IA

**Perguntas esperadas:**
- Qual a acurácia do Isolation Forest?
- Por que não usar um modelo supervisionado?
- Como você sabe que a anomalia detectada é real?

TODO(responsável-S12, por quê: perguntas sobre IA sem respostas preparadas comprometem a defesa, quando: S12 — após S5): documentar as respostas com base no relatório de avaliação de S5.

**Estado em S0:** Sem dataset rotulado. Sem relatório de avaliação. Respostas dependem de S5.

**Resposta honesta para "qual a acurácia?":** "Não temos acurácia calculada ainda. O modelo foi treinado com dados simulados e validado apenas com testes de comportamento. A avaliação supervisionada está planejada para S5."

### 4.9 Integração com equipamentos

**Perguntas esperadas:**
- Quais fabricantes são suportados?
- Funciona com CAN/J1939?
- O ESP32 foi testado em campo?

TODO(responsável-S12, por quê: afirmações de compatibilidade sem evidência são vulneráveis, quando: S12): documentar o que foi testado e o que é roadmap.

**Estado em S0:** Dois fabricantes em fixtures (`case_ih_v1`, `john_deere_v1`) — dados simulados. Sem hardware real. CAN/J1939 e ISOBUS são roadmap.

### 4.10 Operação em conectividade limitada

**Perguntas esperadas:**
- Funciona sem internet por 30 dias?
- O que acontece se o buffer ficar cheio?
- Como os dados são priorizados?

TODO(responsável-S12, por quê: afirmações de operação offline sem evidência de teste são vulneráveis, quando: S12 — após S6): documentar os limites testados e os que não foram.

**Estado em S0:** Outbox SQLite implementada em software. Prioridades A/B/C implementadas. Sem teste de 30 dias. Sem teste de overflow de buffer. Protocolo S6 está pendente.

### 4.11 Riscos técnicos

TODO(responsável-S12, por quê: demonstrar consciência dos riscos é sinal de maturidade, quando: S12): listar os 5-10 maiores riscos técnicos com probabilidade e impacto.

### 4.12 Limitações atuais

TODO(responsável-S12, por quê: ser proativo sobre limitações é mais defensável do que ser questionado por elas, quando: S12): listar as limitações que precisam ser declaradas em qualquer apresentação pública.

**Limitações declaráveis em S0:**
- Dados 100% simulados
- Sem hardware físico validado
- Sem avaliação supervisionada de ML
- Build do frontend com débito técnico
- Stack Docker não verificada em execução real

### 4.13 Decisões arquiteturais

TODO(responsável-S12, por quê: decisões sem justificativa parecem arbitrárias para um CTO, quando: S12): documentar as 5-10 decisões arquiteturais mais importantes com justificativa e alternativas consideradas.

### 4.14 Perguntas difíceis

TODO(responsável-S12, por quê: preparar as perguntas com antecedência permite respostas mais sólidas, quando: S12): lista de perguntas difíceis identificadas em sessões de revisão, com a resposta preparada.

| Pergunta | Resposta preparada | Evidência de suporte |
|---|---|---|
| A preencher em S12 | A preencher em S12 | A preencher em S12 |

### 4.15 Respostas sustentadas por evidências

TODO(responsável-S12, por quê: cada resposta deve ter uma âncora verificável, quando: S12): para cada resposta, referenciar o arquivo, teste ou documento que a sustenta.

---

## 5. Evidências e validação

TODO(responsável-S12, por quê: evidências verificáveis são o que separa afirmação de fato, quando: após execução de S12): adicionar referências a cada evidência que sustenta as respostas.

---

## 6. Limitações e riscos

TODO(responsável-S12, por quê: registro antecipado evita surpresas, quando: S12): complementar.

---

## 7. Critérios de conclusão

TODO(responsável-S12, por quê: critérios claros permitem verificação objetiva, quando: S12): definir critérios verificáveis.

**Critérios propostos (a confirmar em S12):**
- [ ] Todas as seções preenchidas com base em evidências reais
- [ ] Perguntas difíceis identificadas e respondidas honestamente
- [ ] Nenhuma resposta promocional sem evidência
- [ ] Referência a `docs/CLAIMS_VS_CODE.md` para cada afirmação técnica
- [ ] Revisão por outro membro realizada (idealmente alguém que faça o papel de CTO)

---

## 8. Histórico de alterações

| Data | Responsável | Alteração |
|---|---|---|
| 2026-11-04 | S0-T4 (Antigravity) | Criação do esqueleto com estado verificado em S0 |
