# ROTEIRO_DEMO_BANCA

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
> **Regra:** a demonstração deve distinguir claramente dados reais, dados simulados e
> funcionalidades planejadas. Nunca apresentar como "ao vivo" o que é pre-recorded ou simulado
> sem informar a banca.

---

## 1. Objetivo

Organizar uma demonstração técnica reproduzível e honesta do FieldNode para
a banca avaliadora — com sequência de execução clara, dados identificados
quanto à origem, e plano de contingência para falhas.

TODO(responsável-S12, por quê: uma demo mal planejada pode comprometer a defesa mesmo com um sistema funcional, quando: início de S12): definir o objetivo da apresentação, a narrativa e o ambiente de demonstração.

---

## 2. Escopo

### Incluído

TODO(responsável-S12, por quê: delimitar o que será demonstrado, quando: S12): listar as funcionalidades que serão demonstradas ao vivo.

### Fora do escopo

TODO(responsável-S12, por quê: ser explícito sobre o que não será demonstrado protege a apresentação, quando: S12): registrar o que não será demonstrado (ex: ESP32 físico, campo real, impacto financeiro).

---

## 3. Contexto atual do FieldNode

**Estado verificado em 2026-11-04 (S0-T3):**

Funcionalidades demonstráveis em software (sem hardware físico):
- Ingestão HTTP com deduplicação UUID
- Pipeline de IA (Isolation Forest + regras + LLM)
- Dashboard Next.js com dados simulados
- Outbox SQLite do edge_client com retry
- Data Mule simulator (Python)
- Healthcheck e Swagger

**Não demonstrável sem validação prévia:**
- ESP32 e sensores físicos (Roadmap S8)
- ESP-NOW entre máquinas (Roadmap S8-T5)
- Build de produção do frontend (Issue #2)
- Stack Docker Compose completa (daemon indisponível na auditoria S0)

TODO(responsável-S12, por quê: atualizar com o estado real após as semanas anteriores, quando: início de S12): complementar com funcionalidades concluídas até S11.

---

## 4. Especificação e conteúdo técnico

### 4.1 Objetivo da apresentação

TODO(responsável-S12, por quê: objetivo claro orienta todas as decisões da demo, quando: S12): definir o que a banca deve compreender ao final da apresentação.

### 4.2 Narrativa da demonstração

TODO(responsável-S12, por quê: narrativa conecta as funcionalidades em uma história coerente, quando: S12): escrever a narrativa em 2-3 parágrafos. Exemplo de estrutura:
1. "Uma colhedora opera em campo com conectividade intermitente..."
2. "O sistema captura, prioriza e sincroniza os dados..."
3. "O pipeline de IA classifica o estado e gera uma recomendação..."

### 4.3 Ambiente e pré-requisitos

TODO(responsável-S12, por quê: ambiente incorreto pode inviabilizar a demo, quando: S12): documentar:
- hardware do apresentador (RAM, SO)
- software instalado e versões
- variáveis de ambiente necessárias
- dados de seed carregados

### 4.4 Sequência de execução

TODO(responsável-S12, por quê: a sequência determina se a demo flui sem interrupções, quando: S12): passo a passo numerado com comandos exatos.

### 4.5 Fluxo principal do sistema

TODO(responsável-S12, por quê: o fluxo principal é o coração da demo, quando: S12): documentar o fluxo de ponta a ponta que será demonstrado, com screenshots ou vídeo de referência.

### 4.6 Dados utilizados

TODO(responsável-S12, por quê: a banca pode perguntar sobre a origem dos dados, quando: S12): para cada dado apresentado, declarar:
- **[SIMULADO]** gerado por `seed_data.py` ou `simular_mqtt.py`
- **[REAL]** coletado de sensor físico (somente se S8 for concluída)
- **[FIXTURE]** fixture de teste carregada manualmente

### 4.7 Pontos de evidência

TODO(responsável-S12, por quê: evidências ao longo da demo fortalecem a defesa, quando: S12): listar os momentos em que evidências verificáveis serão apresentadas (logs, banco, testes passando).

### 4.8 Limitações que precisam ser explicadas

TODO(responsável-S12, por quê: ser proativo sobre limitações demonstra maturidade técnica, quando: S12): listar o que precisa ser explicado à banca antes que ela pergunte.

**Limitações conhecidas em S0 que provavelmente persistirão:**
- Dados são simulados, não de sensores físicos reais
- Hardware ESP32 é Roadmap (a menos que S8 seja concluída)
- Sem dataset rotulado de falhas reais
- Build do frontend pode ter débito técnico

### 4.9 Plano de contingência

TODO(responsável-S12, por quê: falhas acontecem; o plano de contingência determina se a demo sobrevive a elas, quando: S12): para cada componente crítico, definir o que fazer se ele falhar.

| Componente | Falha possível | Contingência |
|---|---|---|
| Docker Compose | Daemon indisponível | Execução local com SQLite |
| Broker MQTT | Connection refused | Fallback HTTP do simulador |
| LLM (Gemini) | API key inválida ou timeout | Circuit breaker ativa fallback determinístico |
| Frontend | Build quebrado | API diretamente via Swagger |

### 4.10 Falhas possíveis

TODO(responsável-S12, por quê: antecipar falhas permite preparo, quando: S12): listar as falhas mais prováveis e como detectá-las rapidamente.

### 4.11 Preparação antes da apresentação

TODO(responsável-S12, por quê: preparação insuficiente é a causa mais comum de demo mal-sucedida, quando: S12): checklist de preparação a ser executado no dia anterior e 30 minutos antes.

### 4.12 Checklist final

TODO(responsável-S12, por quê: checklist eliminam erros de última hora, quando: S12):

- [ ] Ambiente iniciado e todos os serviços healthy
- [ ] Dados de seed carregados
- [ ] Variáveis de ambiente configuradas
- [ ] Conexão com internet testada (se LLM for demonstrado)
- [ ] Plano de contingência revisado
- [ ] Tempo de cada seção cronometrado

---

## 5. Evidências e validação

TODO(responsável-S12, por quê: evidências verificáveis são o que separa afirmação de fato, quando: após ensaio de S12): adicionar:
- vídeo de ensaio da demonstração
- tempo medido de cada seção
- resultado do ensaio com falhas identificadas

---

## 6. Limitações e riscos

TODO(responsável-S12, por quê: registro antecipado evita surpresas, quando: S12): complementar.

**Riscos conhecidos em S0:**
- Stack Docker pode não funcionar sem daemon ativo
- Build do frontend com débito técnico pode impedir demonstração visual
- LLM requer API key válida e conectividade

---

## 7. Critérios de conclusão

TODO(responsável-S12, por quê: critérios claros permitem verificação objetiva, quando: S12): definir critérios verificáveis.

**Critérios propostos (a confirmar em S12):**
- [ ] Roteiro executado com sucesso em ensaio completo
- [ ] Plano de contingência testado para cada componente crítico
- [ ] Dados claramente rotulados como simulados/reais
- [ ] Limitações documentadas e preparadas para apresentação oral
- [ ] Revisão por outro membro realizada

---

## 8. Histórico de alterações

| Data | Responsável | Alteração |
|---|---|---|
| 2026-11-04 | S0-T4 (Antigravity) | Criação do esqueleto com estado verificado em S0 |
