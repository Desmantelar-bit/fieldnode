# HONESTIDADE_METODOLOGICA_ML

**Responsável:** A CONFIRMAR  
**Semana:** S5  
**Status:** ESQUELETO  
**Tarefa de preenchimento:** S5-Tx (confirmar identificador exato no roadmap)  
**Última atualização:** 2026-11-04 — criação do esqueleto (S0-T4)

> **Atenção:** o status deste documento só poderá mudar de `ESQUELETO` para outro quando:
> - as seções obrigatórias estiverem preenchidas com dados reais de S5;
> - as evidências estiverem anexadas ou referenciadas;
> - os critérios de conclusão forem atendidos;
> - a revisão da semana S5 for realizada.

---

## 1. Objetivo

Documentar a metodologia de machine learning utilizada pelo FieldNode com
precisão técnica e honestidade sobre limitações, distinguindo o que está
implementado, treinado, avaliado e o que ainda é hipótese ou roadmap.

TODO(responsável-S5, por quê: a banca exigirá fundamentação metodológica; afirmações sem relatório comprometem a defesa, quando: S5): definir o objetivo técnico específico após a execução dos experimentos de S5, referenciando o dataset e o protocolo de avaliação utilizados.

---

## 2. Escopo

### Incluído

TODO(responsável-S5, por quê: delimitar o que será documentado aqui e o que pertence a outros documentos, quando: S5): listar os modelos, algoritmos, pipelines e critérios de avaliação que serão cobertos.

### Fora do escopo

TODO(responsável-S5, por quê: evitar que este documento seja usado para afirmar funcionalidades além do escopo, quando: S5): registrar o que não será tratado aqui (ex: validação comercial, hardware, protocolos de rede).

---

## 3. Contexto atual do FieldNode

**Estado verificado em 2026-11-04 (S0-T3):**

- O pipeline de IA atual está em `api_tcc/ia/pipeline.py` e usa:
  - Regras determinísticas com thresholds documentados em `docs/limiares.md`
  - Isolation Forest como sinal não supervisionado complementar (`api_tcc/ia/deteccao_multivariada.py`)
  - Explicação por LLM (Gemini API) com circuit breaker e fallback (`api_tcc/ia/explicacao_llm.py`)
- Modelo pré-treinado: `api_tcc/ia/modelos/isolation_forest_v1.pkl` — treinado com dados simulados de bancada
- Segundo pipeline em `api_tcc/services/anomaly_detection.py` — `AnomalyDetectorRegistry` com Isolation Forest por máquina e fallback Z-score para cold start
- **Sem dataset rotulado de falhas reais**
- **Sem relatório de avaliação supervisionada**
- **Random Forest mencionado em AGENTS.md, mas não encontrado no código atual**

TODO(responsável-S5, por quê: atualizar com o estado real na semana de execução, quando: início de S5): complementar com decisões arquiteturais, limitações e qualquer mudança ocorrida após S0.

---

## 4. Especificação e conteúdo técnico

### 4.1 Objetivo dos modelos

TODO(responsável-S5, por quê: distinguir formalmente detecção de anomalias de previsão de falhas — essa distinção é cobrada em defesas acadêmicas, quando: S5): documentar o que cada modelo faz, o que não faz e por que a escolha foi feita.

### 4.2 Diferença entre detecção de anomalias e previsão de falhas

> **Regra de ouro:** o FieldNode classifica o estado operacional (NORMAL / ATENCAO / CRITICO).
> Não prevê data, probabilidade calibrada ou taxa de falha mecânica sem dataset rotulado.

TODO(responsável-S5, por quê: a confusão entre "anomalia" e "falha" é o erro mais comum em defesas, quando: S5): escrever uma explicação clara e defensável dessa distinção, com referências ao código.

### 4.3 Isolation Forest — detalhes de implementação

TODO(responsável-S5, por quê: a banca pode questionar cada hiperparâmetro, quando: S5): documentar:
- versão atual: `contamination=0.05`, `random_state=42`, `n_estimators=100`
- features usadas: `temperatura`, `vibracao`, `rpm`
- origem do dataset de treinamento (simulado)
- como o modelo é carregado e usado em produção
- diferença entre o modelo global em `isolation_forest_v1.pkl` e o `AnomalyDetectorRegistry` por máquina

### 4.4 Critérios de seleção e preparação dos dados

TODO(responsável-S5, por quê: sem documentar seleção de dados, não há reprodutibilidade, quando: S5): documentar fontes, limpeza, normalização e critérios de inclusão/exclusão.

### 4.5 Features utilizadas

TODO(responsável-S5, por quê: a escolha de features precisa ser justificada, quando: S5): listar as features, sua unidade, range esperado e justificativa para inclusão.

### 4.6 Treinamento e versionamento

TODO(responsável-S5, por quê: reprodutibilidade é critério acadêmico, quando: S5): documentar como treinar, como versionar e como garantir que o modelo pré-treinado corresponde ao código atual.

Referência atual: `python manage.py treinar_isolation_forest` — verificar se o comando ainda existe.

### 4.7 Separação entre regras operacionais, modelo estatístico e explicação por LLM

TODO(responsável-S5, por quê: a separação de responsabilidades é exigida pela metodologia e pela defesa, quando: S5): diagrama ou texto explicando que o LLM nunca decide status, apenas reformula.

### 4.8 Critérios de avaliação

TODO(responsável-S5, por quê: sem critério definido, qualquer resultado parece válido, quando: S5): definir como o modelo será avaliado — métrica, baseline e critério de aceitação.

### 4.9 Métricas e resultados

TODO(responsável-S5, por quê: preencher apenas após os experimentos, quando: após execução de S5): não preencher antes. Manter vazio ou com placeholder explícito.

**Resultado:** NÃO MEDIDO — aguardando S5.

### 4.10 Limitações metodológicas

TODO(responsável-S5, por quê: documentar limitações protege a defesa e demonstra maturidade, quando: S5): registrar o que o modelo não pode fazer, o que não foi testado e o que depende de dados reais.

### 4.11 Riscos de interpretação

TODO(responsável-S5, por quê: prevenir que outros membros ou a banca façam inferências indevidas, quando: S5): listar afirmações que parecem razoáveis mas não são sustentadas pelos experimentos.

### 4.12 Reprodutibilidade dos experimentos

TODO(responsável-S5, por quê: reprodutibilidade é critério acadêmico fundamental, quando: S5): documentar o comando exato, o ambiente, o dataset e os parâmetros necessários para reproduzir os resultados.

---

## 5. Evidências e validação

TODO(responsável-S5, por quê: sem evidências, as afirmações são inválidas na defesa, quando: após execução de S5): adicionar:
- relatório de avaliação com métricas
- comando de execução do experimento
- arquivo de dataset ou referência a ele
- log de treinamento com timestamp

**Evidências atuais (S0):**
- `api_tcc/ia/modelos/isolation_forest_v1.pkl` — modelo pré-treinado (origem: dados simulados de bancada)
- `api_tcc/tests/test_anomaly_detection.py` — testes de comportamento (não de acurácia)
- `api_tcc/tests/test_anomaly_persistence.py` — testes de persistência do modelo
- `api_tcc/tests/test_deteccao_multivariada.py` — testes do sinal Isolation Forest

---

## 6. Limitações e riscos

TODO(responsável-S5, por quê: registro antecipado de limitações conhecidas evita surpresas na defesa, quando: S5): complementar com limitações específicas dos experimentos de S5.

**Limitações conhecidas em S0:**
- Dataset de treinamento é 100% simulado — sem leituras de sensores físicos reais
- Não há dataset rotulado de falhas históricas
- O modelo global (`isolation_forest_v1.pkl`) não é por máquina — o `AnomalyDetectorRegistry` em `anomaly_detection.py` treinará por máquina conforme leituras acumulam
- Sem avaliação de drift de modelo ao longo do tempo
- Sem reprodutibilidade garantida se o ambiente de simulação mudar

---

## 7. Critérios de conclusão

TODO(responsável-S5, por quê: critérios claros permitem verificação objetiva, quando: S5): definir critérios verificáveis.

**Critérios propostos (a confirmar em S5):**
- [ ] Dataset documentado e versionado
- [ ] Treinamento reproduzível com um único comando
- [ ] Relatório de avaliação com métricas e baseline
- [ ] Limitações documentadas explicitamente
- [ ] Revisão por outro membro realizada

---

## 8. Histórico de alterações

| Data | Responsável | Alteração |
|---|---|---|
| 2026-11-04 | S0-T4 (Antigravity) | Criação do esqueleto com estado verificado em S0 |
