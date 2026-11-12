# PLANO_DATASET_ROTULADO

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
>
> **Regra:** não inventar rótulos, quantidade de amostras ou fontes ainda não confirmadas.

---

## 1. Objetivo

Definir como será construído, organizado, rotulado e validado um dataset
adequado aos experimentos do FieldNode — com rastreabilidade completa da
origem dos dados e critérios explícitos de rotulagem.

TODO(responsável-S5, por quê: sem um plano de dataset, os experimentos de ML não são reproduzíveis nem auditáveis pela banca, quando: início de S5): definir o objetivo técnico específico, as fontes de dados disponíveis e os critérios de rotulagem.

---

## 2. Escopo

### Incluído

TODO(responsável-S5, por quê: delimitar o que será documentado aqui, quando: S5): listar as fontes de dados, os tipos de rótulos e os critérios de inclusão.

### Fora do escopo

TODO(responsável-S5, por quê: evitar que este documento prometa dados que não existem, quando: S5): registrar o que não será tratado (ex: dados de campo reais, dados de fabricantes, integrações externas).

---

## 3. Contexto atual do FieldNode

**Estado verificado em 2026-11-04 (S0-T3):**

- Dados disponíveis são 100% simulados (`scripts/seed_data.py` — 676 linhas; `scripts/simular_mqtt.py`)
- Features atuais do pipeline de IA: `temperatura`, `vibracao`, `rpm`
- Modelo pré-treinado (`isolation_forest_v1.pkl`) treinado com cenário normal simulado
- Sem dataset rotulado de falhas históricas
- Sem dados de sensores físicos reais
- Sem histórico de manutenção real

TODO(responsável-S5, por quê: atualizar com o estado real na semana de execução, quando: início de S5): complementar com fontes de dados disponíveis em S5.

---

## 4. Especificação e conteúdo técnico

### 4.1 Objetivo do dataset

TODO(responsável-S5, por quê: o objetivo do dataset define o que é um bom rótulo, quando: S5): definir para que o dataset será usado (detecção de anomalias? classificação de falhas? previsão de manutenção?).

### 4.2 Fontes de dados

TODO(responsável-S5, por quê: a origem dos dados determina o que pode ser afirmado sobre generalização, quando: S5): documentar cada fonte com: tipo (simulado/real), volume disponível, período, confiabilidade.

**Fontes conhecidas em S0:**
- `scripts/seed_data.py` — geração de dados sintéticos (cenário normal + anomalias simuladas)
- `scripts/simular_mqtt.py` — telemetria simulada em tempo real
- Dados reais de sensores físicos: **não disponíveis em S0**

### 4.3 Dados simulados e reais

TODO(responsável-S5, por quê: a proporção de dados simulados vs. reais afeta a validade dos resultados, quando: S5): documentar a proporção e as implicações para generalização.

**Regra:** não apresentar resultados de dados 100% simulados como evidência de desempenho em campo.

### 4.4 Estrutura das amostras

TODO(responsável-S5, por quê: a estrutura determina o que pode ser usado como feature, quando: S5): documentar os campos de cada amostra, seus tipos e ranges esperados.

**Referência atual:** payload de `LeituraTelemetria`: `temperatura`, `vibracao`, `rpm`, `latitude`, `longitude`, `timestamp`, `maquina_id`.

### 4.5 Features

TODO(responsável-S5, por quê: a seleção de features precisa ser justificada, quando: S5): documentar quais campos serão usados como features, por que e quais serão descartados.

### 4.6 Definição dos rótulos

TODO(responsável-S5, por quê: a definição de rótulo determina o que o modelo aprende, quando: S5): definir os rótulos possíveis e seus critérios. Exemplo: `NORMAL`, `ATENCAO`, `CRITICO`, `FALHA`.

**Não inventar rótulos antes de definir o critério.**

### 4.7 Critérios de rotulagem

TODO(responsável-S5, por quê: critérios reproduzíveis permitem auditoria e expansão do dataset, quando: S5): documentar como cada amostra recebe seu rótulo — regra determinística? especialista humano? registro histórico de manutenção?

### 4.8 Responsáveis pela revisão

TODO(responsável-S5, por quê: rótulos sem revisão independente têm validade questionável, quando: S5): definir quem revisará os rótulos e com que critério.

### 4.9 Tratamento de dados ausentes

TODO(responsável-S5, por quê: dados ausentes sem estratégia documentada causam viés silencioso, quando: S5): definir a estratégia para valores nulos, fora de range e leituras suspeitas.

### 4.10 Prevenção de vazamento de dados

TODO(responsável-S5, por quê: data leakage invalida qualquer métrica de avaliação, quando: S5): documentar como garantir que informação do conjunto de teste não contamina o treinamento.

### 4.11 Divisão treino/validação/teste

TODO(responsável-S5, por quê: a divisão deve ser feita antes do treinamento e documentada, quando: S5): definir proporções, critério de divisão (temporal? aleatória? por máquina?) e justificativa.

### 4.12 Versionamento

TODO(responsável-S5, por quê: sem versionamento, não é possível reproduzir experimentos, quando: S5): definir como o dataset será versionado e referenciado.

### 4.13 Qualidade e limitações

TODO(responsável-S5, por quê: documentar limitações protege a defesa, quando: S5): registrar o que o dataset não representa e quais conclusões não podem ser extraídas.

### 4.14 Governança e reprodutibilidade

TODO(responsável-S5, por quê: a banca pode solicitar reprodução dos experimentos, quando: S5): documentar onde o dataset está armazenado, como acessar e o comando para reproduzir o treinamento.

---

## 5. Evidências e validação

TODO(responsável-S5, por quê: evidências verificáveis são o que separa afirmação de fato, quando: após execução de S5): adicionar:
- caminho ou referência ao dataset
- contagem de amostras por rótulo
- script de geração ou coleta
- hash ou checksum do dataset para reprodutibilidade

**Evidências atuais (S0):**
- `scripts/seed_data.py` — gerador de dados sintéticos (676 linhas)
- Sem dataset rotulado persistido

---

## 6. Limitações e riscos

TODO(responsável-S5, por quê: registro antecipado evita surpresas, quando: S5): complementar.

**Limitações conhecidas em S0:**
- 100% dos dados disponíveis são simulados
- Sem histórico de falhas reais de máquinas agrícolas
- Sem especialista de domínio (agronomia/mecânica) para rotulagem
- Sem dados de temperatura ambiente, umidade ou condições de operação

---

## 7. Critérios de conclusão

TODO(responsável-S5, por quê: critérios claros permitem verificação objetiva, quando: S5): definir critérios verificáveis.

**Critérios propostos (a confirmar em S5):**
- [ ] Dataset com rótulos definidos e documentados
- [ ] Critérios de rotulagem explícitos e reproduzíveis
- [ ] Divisão treino/validação/teste documentada
- [ ] Estratégia de prevenção de data leakage documentada
- [ ] Limitações declaradas explicitamente
- [ ] Revisão por outro membro realizada

---

## 8. Histórico de alterações

| Data | Responsável | Alteração |
|---|---|---|
| 2026-11-04 | S0-T4 (Antigravity) | Criação do esqueleto com estado verificado em S0 |
