# Changelog — FieldNode

Registro histórico e rastreabilidade da evolução técnica do projeto FieldNode.

Este documento consolida marcos históricos, decisões de arquitetura e mudanças relevantes a partir de evidências comprováveis no repositório. O histórico Git foi parcialmente consolidado em diferentes etapas do projeto; portanto, este registro retroativo distingue com rigor o que está formalmente comprovado no histórico de commits, o que foi documentado em relatórios e o que permanece não verificável.

Um commit comprova as alterações que contém, não a conclusão integral de uma tarefa ou semana do roadmap. Os agrupamentos abaixo são retrospectivos e não substituem critérios de aceite, evidências de execução ou aprovação por PR.

---

## 1. Marcos Históricos Retroativos

### Roadmap v1 (auditoria)

#### Contexto
Fase embrionária e de concepção inicial do projeto, originada no contexto de protótipo acadêmico (TCC) de telemetria agrícola. O objetivo consistia em estruturar a ingestão de leituras de telemetria com Django REST Framework, persistência em SQLite/MySQL, interface web inicial em HTML/CSS/JavaScript puro e primeira exploração de regras de anomalia.

#### Principais mudanças
- **Modelagem de dados inicial:** Definição dos modelos de dados fundamentais (`Modelo`, `Colheitadeira`, `LeituraTelemetria`, `TemperaturaMaquina`).
- **Endpoints de ingestão e documentação:** Ingestão de dados com documentação Swagger/Redoc (`drf-yasg`).
- **Comunicação MQTT:** Criação do listener MQTT (`mqtt_listen.py`) e broker Mosquitto para integração de mensagens.
- **Primeiras regras de detecção de anomalias:** Criação de endpoints de anomalia e manutenção baseados em thresholds.
- **Containerização preliminar:** Configuração inicial de `docker-compose.yml` e Dockerfile para o backend Django.

#### Comprovado pelo Git
- Commits de base: `b15a741` (*Primeira versão - Somente models*), `423d05c` (*Api documentada com Sawgger e Redoc*), `2c132da` (*Início do Front com HTML/CSS/JS puro*), `527b9b2` (*Listener MQTT*), `2f928da` (*Mosquitto testado*), `2414191` (*Endpoints de anomalia e limites conhecidos*), `63f46a8` (*Fase 1 concluída: Dashboard funcional + 10 documentos de suporte*).
- Restrições de integridade no ORM: `fb56790` (duplicata retorna 200), `9dfeff2` (migração de `DO_NOTHING` para `PROTECT`), `a7b53b3` (`verbose_name` e proteção relacional).

#### Registrado em documentação
- `docs/CONSOLIDACAO_FINAL.md` não existe neste checkout e, por isso, não é apresentado como evidência disponível. O commit `63f46a8` registra no assunto a conclusão da Fase 1 e menciona dashboard e documentos de suporte; esse assunto, isoladamente, não substitui o conteúdo documental ausente.

#### Limitações de rastreabilidade
- Menções a "ESP32" aparecem apenas como strings identificadoras em payloads e fixtures; nenhum código de firmware (.ino, C/C++, ESP-IDF ou PlatformIO) foi comitado ou preservado no histórico do repositório.

---

### Marcos históricos associados ao Roadmap v2 (S1 a S10, backend)

#### Contexto
Agrupamento retrospectivo de commits e documentos associados a S1–S10, relacionados à robustez operacional e integridade metodológica: outbox offline, motor de eventos, rastreamento de correlação, modelos estatísticos não supervisionados e contratos. A presença desses artefatos não comprova, por si só, o fechamento de cada semana.

#### Principais mudanças
- **S1–S4 (Refatoração de API e Decisões):** Padronização de endpoints com snake_case, máquina de estados para decisões operacionais e refinamento de permissões de acesso.
- **S5 (Honestidade Metodológica e ML):** Auditoria de honestidade metodológica (`docs/HONESTIDADE_METODOLOGICA_ML.md`). Formalização de que o sistema utiliza **Isolation Forest** como sinal complementar não supervisionado (modelo persistido `isolation_forest_v1.pkl`). Delimitação formal de que Random Forest e manutenção preditiva supervisionada dependem de dataset rotulado (planejamento documentado em `docs/PLANO_DATASET_ROTULADO.md`).
- **S6 (Resiliência Offline e Data Mule):** Implementação do cliente de bancada (`simulators/edge_client.py`) com outbox SQLite, filas de prioridade (A/B/C), envio contíguo por cursor e confirmação por ACK. Criação de simulador de transporte de buffer por software (`transbordo_mule_client.py`).
- **S7 (Observabilidade e Tolerância a Falhas):** Implementação de Correlation ID para rastreamento ponta a ponta (`docs/CONTRATO_TELEMETRIA_V1.md`), logs estruturados em JSON e Dead Letter Queue (`docs/DLQ.md`) para segregação de payloads inválidos.
- **S8 (Atenção e Telemetria Canônica):** Criação do motor de priorização de eventos operacionais (`docs/ATTENTION_ENGINE.md`) e desacoplamento de telemetria com modelo Raw→Canonical (`FabricanteMapping`).
- **S9 (IA Agentiva e Validação Comercial):** Prova de conceito de tomada de decisão agentiva com fallback determinístico e formalização de roteiro de entrevistas comerciais (`docs/RESULTADOS_VALIDACAO_COMERCIAL.md`).
- **S10 (Fechamento e Homologação):** Demonstração integrada em closed-loop, correção de idempotência no script de carga `popular_tudo.py` e auditoria cruzada de encerramento da fase.

#### Comprovado pelo Git
- Commits chave: `92bbe80` (*máquina de estados de decisões*), `bb3ff16` (*auditoria de honestidade metodológica S5-T1*), `f92d56b` (*persistência de modelos de anomalia*), `f53ebe3` (*edge client com outbox SQLite e testes*), `910ba13` (*Data Mule e protocolo de resiliência*), `7b16268` (*Correlation ID S7-T2*), `1168900` (*JSON logging S7-T3*), `30b317f` (*DLQ*), `0ea30ce` (*Attention Engine*), `f7b1d00` (*telemetria universal e normalização*), `44f1568` / `5e7f0b4` (*fechamento e homologação S10*).
- Esses commits sustentam as mudanças identificadas por seus diffs e mensagens; não constituem prova automática de conclusão integral de S1–S10.

#### Registrado em documentação
- Documentos presentes em `docs/` que registram aspectos técnicos: `limiares.md`, `ATTENTION_ENGINE.md`, `DLQ.md`, `SEQ_ID.md`, `CONTRATO_TELEMETRIA_V1.md`, `HONESTIDADE_METODOLOGICA_ML.md`, `PLANO_DATASET_ROTULADO.md`, `SEGURANCA.md`, `RESULTADOS_VALIDACAO_COMERCIAL.md`. A existência desses documentos não atesta que todas as tarefas do roadmap foram aceitas.

#### Limitações de rastreabilidade
- **Random Forest:** Embora citado no planejamento original, nenhum código-fonte correspondente foi localizado no repositório ativo; apenas bytecode residual legada (`.pyc`) em `__pycache__` foi encontrada e documentada como dívida técnica em `docs/CLAIMS_VS_CODE.md`.
- **Validação Comercial:** Os registros de entrevistas e projeções financeiras foram identificados como qualitativos/estimados, registrando-se a ausência de fontes primárias auditadas em `docs/RESULTADOS_VALIDACAO_COMERCIAL.md`.

---

### Merge front (Next.js)

#### Contexto
Substituição da interface web legada pela aplicação moderna em Next.js 15 na pasta `frontend-next/`, adotando React 18, Tailwind CSS, SWR, Recharts, Leaflet, mapa de frota, Service Worker para cache/outbox local e rotas de proxy reverso da API.

#### Principais mudanças
- **Estruturação do frontend Next.js:** Migração para o diretório raiz `frontend-next/` e integração no `docker-compose.yml`.
- **Interface e Telas:** Dashboard operacional, tela de frotas, histórico de telemetria, mapa de geolocalização com Leaflet e exportação de relatórios.
- **Service Worker e Resiliência Local:** Implementação de Service Worker (`public/sw.js`) com cache de ativos e fila IndexedDB para requisições de telemetria.
- **Centralização de serviços:** Refatoração de clientes HTTP no frontend via `telemetryService.ts` e rotas de rewrite de API no Next.js.

#### Comprovado pelo Git
- Commits chave: `3692aab` (*consolidação do repositório e remoção de front aninhado*), `fdcef06` (*consolidação do front oficial*), `b2f7a17` (*adição do frontend ao Docker Compose*), `5ef6eb5` (*matriz de rotas em docs/ e atualização do README*), `1938eaf` (*purificação de artefatos de dev*), `3b5f5c0` (*refatoração do telemetryService e consistência visual*), `cd6360f` (*correções de segurança em auth e tratamento de erros na UI*).

#### Registrado em documentação
- `docs/ROTAS_E_URLS.md`, `README.md` (arquitetura e stack), `docs/BASELINE.md`.

#### Limitações de rastreabilidade
- O build de produção (`npm run build`) falhou na auditoria S0 devido à ausência do módulo TypeScript no ambiente de build (`docs/evidence/s0/front_build.txt`, Issue #2).
- O reenvio de telemetria via IndexedDB no Service Worker está codificado, mas sua validação funcional em browser sob queda real de conexão permanece como recurso simulado sem teste E2E comprovado em execução.

---

### Semana 0 (S0) — Baseline e Governança

#### Contexto
Início do ciclo de governança do Roadmap V5: estabelecimento da baseline técnica reproduzível, higienização do repositório, publicação da matriz de claims vs. código e reestruturação do contrato de agentes.

#### Principais mudanças
- **S0-T1 / S0-T2 (Baseline e Higiene):** `docs/BASELINE.md` e `docs/evidence/s0/` registram a auditoria, resultados de testes e limpeza de artefatos. O próprio baseline classifica S0-T1/S0-T2 como parcialmente atendidas e registra bloqueios; esta entrada não declara essas tarefas concluídas.
- **S0-T3 / S0-T4 (Matriz de Claims e Esqueletos de Docs):** Criação de `docs/CLAIMS_VS_CODE.md` como mecanismo de contenção contra afirmações não comprovadas e alinhamento de terminologias de hardware/ML.
- **S0-T5 (Reorganização do Contrato):** O `AGENTS.md` da raiz foi reduzido e as regras detalhadas foram reorganizadas em `docs/agents/CONTRATO.md`; a matriz de rastreabilidade e a revisão de aceitação devem ser consideradas separadamente. Não foi localizada evidência de PR nesta auditoria.
- **S0-T6 (Política de Histórico e Versionamento):** A tag anotada `v0.3.0-baseline` foi criada antes deste changelog. O objeto anotado `9d980ce24db4c93724bd27efa9a295ff1d2f32c8` aponta para o commit `f9bb8fd891d5136ae7f689d4af0d8662e26dc812`; a anotação e o commit descrevem conjuntamente S0-T1/S0-T2, não exclusivamente S0-T1. `docs/BASELINE.md` registra essas tarefas como parciais. Esta tag é mantida como referência histórica e não foi movida ou recriada.

#### Comprovado pelo Git
- Commits chave: `f9bb8fd` (*docs: version S0 baseline and hygiene evidence*), `a651dec` (*docs: add claims matrix and missing doc skeletons*), `2504930` (*docs: tighten claims matrix evidence and reclassify unverified capabilities*).
- `f9bb8fd` contém baseline, evidências e higiene; `a651dec` registra claims/esqueletos; `2504930` refina a matriz. Esses commits não demonstram por si só a aceitação de todas as tarefas S0.

---

## 2. Política de Versionamento e Tags

Para garantir a rastreabilidade nas próximas semanas do projeto, o FieldNode adota a seguinte convenção para marcos de versão e tags Git.

### Padrão de Nomenclatura

```text
vX.Y.Z-semanaN
```

Onde:
- **`X` (Major):** Mudança arquitetural principal, marco de evolução estrutural ou quebra controlada de compatibilidade.
- **`Y` (Minor):** Entrega de nova funcionalidade planejada ou conjunto consistente de tarefas do roadmap.
- **`Z` (Patch):** Correção pontual, ajuste de integridade, documentação ou resolução de defeito.
- **`semanaN`:** Identificação explícita da semana de roadmap à qual a entrega pertence (ex: `baseline` para a Semana 0, `semana1`, `semana2`, ..., `semana12`).

### Exemplos da Convenção
- `v0.3.0-baseline`: referência histórica para o commit `f9bb8fd` (baseline/higiene S0-T1 e S0-T2); o status parcial dessas tarefas está registrado em `docs/BASELINE.md`.
- `v0.4.0-semana1`: Conclusão das entregas e evidências da Semana 1.
- `v0.5.0-semana2`: Conclusão das entregas e evidências da Semana 2.
- `v1.0.0-semana12`: Marco final de fechamento do ciclo de desenvolvimento V5.

### Regras para Criação e Publicação de Tags
1. **Apontamento obrigatório:** A tag deve apontar para um commit existente que represente a conclusão efetiva das tarefas daquele marco.
2. **Evidência mandatória:** Nenhuma tag de versão pode ser criada sem que todos os testes, relatórios e evidências exigidos pelo roadmap estejam devidamente versionados.
3. **Mensagem anotada:** Toda tag deve ser anotada (`git tag -a`), contendo mensagem objetiva descrevendo o marco e o escopo entregue.
4. **Proibição de reescrita:** Tags já criadas ou publicadas no remoto nunca devem ser movidas ou sobrescritas.
5. **Publicação seletiva:** A publicação deve ser feita apontando exclusivamente para a tag desejada (`git push origin <TAG_NAME>`), evitando o uso de `git push --tags`.
6. **Resolução de conflitos:** Caso uma tag já exista local ou remotamente apontando para commit distinto, a operação deve ser interrompida imediatamente para averiguação, sem uso de flags forçadas (`--force`).
