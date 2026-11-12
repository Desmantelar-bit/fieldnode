# OBSERVABILIDADE

**Responsável:** A CONFIRMAR  
**Semana:** S10  
**Status:** ESQUELETO  
**Tarefa de preenchimento:** S10-Tx (confirmar identificador exato no roadmap)  
**Última atualização:** 2026-11-04 — criação do esqueleto (S0-T4)

> **Atenção:** o status deste documento só poderá mudar de `ESQUELETO` para outro quando:
> - as seções obrigatórias estiverem preenchidas com dados reais de S10;
> - as evidências estiverem anexadas ou referenciadas;
> - os critérios de conclusão forem atendidos;
> - a revisão da semana S10 for realizada.

---

## 1. Objetivo

Documentar como o comportamento operacional do FieldNode será observado,
diagnosticado e auditado — cobrindo logs, métricas, rastreabilidade de
requisições e monitoramento dos serviços.

TODO(responsável-S10, por quê: observabilidade é critério de manutenibilidade e confiabilidade operacional, quando: início de S10): definir o objetivo técnico específico, as ferramentas que serão usadas e o que será instrumentado.

---

## 2. Escopo

### Incluído

TODO(responsável-S10, por quê: delimitar o que será documentado aqui, quando: S10): listar os componentes que serão instrumentados e as ferramentas de observabilidade que serão usadas.

### Fora do escopo

TODO(responsável-S10, por quê: evitar que este documento prometa mais do que será entregue em S10, quando: S10): registrar o que não será tratado (ex: distributed tracing completo, APM comercial).

---

## 3. Contexto atual do FieldNode

**Estado verificado em 2026-11-04 (S0-T3):**

- JSON logging estruturado presente (`api_tcc/tests/test_json_logging.py` — 385 linhas)
- Correlation ID implementado e testado (`api_tcc/tests/test_correlation.py` — 465 linhas)
- Healthcheck `/api/health/` retorna `{"status":"ok","database":"ok","mqtt_last_seen_seconds":...,"version":"1.0"}`
- Sem ferramenta de APM, tracing distribuído ou dashboard de métricas configurada
- Sem alertas operacionais implementados

TODO(responsável-S10, por quê: atualizar com o estado real após as semanas anteriores, quando: início de S10): complementar com mudanças ocorridas após S0.

---

## 4. Especificação e conteúdo técnico

### 4.1 Logs

TODO(responsável-S10, por quê: logs são a base de qualquer diagnóstico, quando: S10): documentar:
- formato dos logs (JSON estruturado vs. texto)
- campos obrigatórios em cada log entry
- níveis de log por componente
- rotação e retenção
- o que nunca deve ser logado (senhas, tokens, dados sensíveis)

**Estado atual:** JSON logging estruturado confirmado em testes.

### 4.2 Métricas

TODO(responsável-S10, por quê: sem métricas, não é possível detectar degradação progressiva, quando: S10): definir quais métricas serão coletadas, como e onde armazenadas.

**Não implementar ferramenta que não esteja selecionada em S10.**

### 4.3 Rastreabilidade

TODO(responsável-S10, por quê: rastreabilidade permite investigar incidentes, quando: S10): documentar como o Correlation ID flui do cliente ao banco e como consultá-lo nos logs.

**Estado atual:** Correlation ID injetado e testado.

### 4.4 Correlação de eventos

TODO(responsável-S10, por quê: correlacionar eventos de telemetria com anomalias e decisões é o valor central da observabilidade no FieldNode, quando: S10): documentar o fluxo de IDs entre telemetria, anomalia, evento e decisão.

### 4.5 Monitoramento de API

TODO(responsável-S10, por quê: endpoints críticos precisam de monitoramento, quando: S10): definir quais endpoints serão monitorados, com que frequência e qual o critério de alerta.

### 4.6 Saúde dos serviços

TODO(responsável-S10, por quê: healthchecks permitem orquestração automática (Docker Compose), quando: S10): documentar os healthchecks de cada serviço (web, worker, mosquitto, db).

**Estado atual:** `/api/health/` retorna HTTP 200 com status de banco e MQTT.

### 4.7 Monitoramento de ingestão

TODO(responsável-S10, por quê: a ingestão é o ponto crítico de entrada de dados, quando: S10): documentar métricas de taxa de ingestão, taxa de duplicatas, taxa de erros e latência.

### 4.8 Erros e falhas

TODO(responsável-S10, por quê: erros não observáveis não podem ser corrigidos, quando: S10): documentar como erros são capturados, registrados e notificados.

### 4.9 Alertas operacionais

TODO(responsável-S10, por quê: alertas são o mecanismo de resposta proativa, quando: S10): definir quais condições disparam alerta e como o alerta é comunicado.

**Não implementar sistema de alerta externo sem definição prévia de ferramentas.**

### 4.10 Retenção de registros

TODO(responsável-S10, por quê: retenção afeta custo e conformidade, quando: S10): definir por quanto tempo logs e métricas serão retidos e qual a política de limpeza.

### 4.11 Privacidade e proteção de dados

TODO(responsável-S10, por quê: logs não podem conter dados sensíveis, quando: S10): documentar quais campos nunca devem aparecer em logs (senhas, tokens, chaves de API, dados pessoais).

**Referência:** `docs/SEGURANCA.md` — verificar políticas existentes.

### 4.12 Procedimentos de diagnóstico

TODO(responsável-S10, por quê: procedimentos documentados reduzem o tempo de resposta a incidentes, quando: S10): documentar como diagnosticar os problemas mais comuns (banco lento, MQTT desconectado, Isolation Forest não carregado, fila de decisões travada).

---

## 5. Evidências e validação

TODO(responsável-S10, por quê: evidências verificáveis são o que separa afirmação de fato, quando: após execução de S10): adicionar:
- exemplo de log entry estruturado
- comando para buscar por Correlation ID nos logs
- screenshot ou saída do healthcheck
- definição das métricas instrumentadas

**Evidências atuais (S0):**
- `docs/evidence/s0/health.json` — resposta do healthcheck
- `api_tcc/tests/test_json_logging.py` — confirma logging estruturado
- `api_tcc/tests/test_correlation.py` — confirma Correlation ID

---

## 6. Limitações e riscos

TODO(responsável-S10, por quê: registro antecipado evita surpresas, quando: S10): complementar.

**Limitações conhecidas em S0:**
- Sem APM, tracing distribuído ou dashboard de métricas
- Sem alertas operacionais implementados
- Sem política de retenção de logs definida
- MQTT `last_seen_seconds` no healthcheck sugere que o broker não está sempre ativo

---

## 7. Critérios de conclusão

TODO(responsável-S10, por quê: critérios claros permitem verificação objetiva, quando: S10): definir critérios verificáveis.

**Critérios propostos (a confirmar em S10):**
- [ ] Formato de log documentado com campos obrigatórios
- [ ] Correlation ID documentado com exemplo de rastreamento
- [ ] Healthchecks de todos os serviços documentados
- [ ] Procedimentos de diagnóstico dos problemas mais comuns
- [ ] Política de retenção definida
- [ ] Revisão por outro membro realizada

---

## 8. Histórico de alterações

| Data | Responsável | Alteração |
|---|---|---|
| 2026-11-04 | S0-T4 (Antigravity) | Criação do esqueleto com estado verificado em S0 |
