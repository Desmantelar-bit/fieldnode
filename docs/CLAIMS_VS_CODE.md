# CLAIMS_VS_CODE — Matriz de Afirmações vs. Código

**Tarefa de origem:** S0-T3
**Data de criação:** 2026-11-04
**Revisão independente:** PENDENTE (ver seção "Revisão Cruzada")
**Status do documento:** Versão 1.0 — auditoria inicial concluída

> Este arquivo é a referência oficial para validar o que o FieldNode pode afirmar
> em materiais públicos (README, proposta do TCC, pitch). Qualquer afirmação
> técnica ou funcional deve ser suportada por uma linha desta tabela.
>
> **Regra central:** toda afirmação pública precisa ter evidência verificável.
> Se não houver evidência suficiente, a afirmação deve ser rebaixada para
> `SIMULADO` ou `ROADMAP`, ou removida.

---

## Legenda de Status

| Status | Significado |
|---|---|
| `IMPLEMENTADO` | Implementação funcional com evidência verificável compatível com a afirmação. |
| `SIMULADO` | Demonstração, simulação, protótipo ou validação limitada. Sem comprovação de operação real no ambiente alegado. |
| `ROADMAP` | Funcionalidade planejada, conceitual, incompleta ou não encontrada no código. |

---

## 1. Tabela Principal de Afirmações

| Afirmação | Onde aparece | Status | Evidência | Formulação permitida |
|---|---|---|---|---|
| **Ingestão HTTP autenticada por `X-API-Key` com deduplicação UUID** | README §"O que está implementado"; CONTRATO_TELEMETRIA_V1.md | `IMPLEMENTADO` | `api_tcc/api/views_ingestao.py` — endpoint `POST /api/telemetria/`; deduplicação por UUID verificada em `api_tcc/tests/test_telemetria.py` e `test_identity_contract.py`; 298/301 testes passando (ver `docs/evidence/s0/tests_django_after_2026-11-04.txt`) | "Ingestão HTTP autenticada por `X-API-Key`, com deduplicação por UUID e rejeição de duplicatas com `200` sem dupla inserção." |
| **Persistência em SQLite/MySQL com identidade de máquina, sequência, timestamp e hash** | README §"O que está implementado" | `IMPLEMENTADO` | `api_tcc/models.py` — models `LeituraTelemetria`, `Machine`; `api_tcc/services/telemetria.py`; `simulators/edge_client.py` — campos `sequence_number`, `payload_hash`; migrations 0001–0026 verificadas; testes `test_identity_contract.py` | "Persistência em SQLite (dev) e MySQL 8 (Docker), com campos de identidade de máquina, número de sequência e hash de payload." |
| **Cliente Python de bancada com outbox SQLite, prioridades A/B/C, retry, ACK e cursor contíguo** | README §"O que está implementado" e §"Resiliência Offline" | `IMPLEMENTADO` | `simulators/edge_client.py` — classes `EdgeBuffer`, lógica de prioridade em `classify_priority()`, cursor contíguo, ACK; testes em `simulators/test_edge_client.py` (6 testes passando via pytest) | "Cliente Python de bancada com outbox SQLite persistente, prioridades A/B/C, retry com ACK e cursor contíguo — validado em simulador de bancada." |
| **Trust Score heurístico e estado agregado de qualidade por máquina** | README §"O que está implementado" | `IMPLEMENTADO` | `api_tcc/services/data_health.py`; `api_tcc/tests/test_data_health.py` (340 linhas de testes); `api_tcc/tests/test_trust_score.py` | "Trust Score heurístico e qualidade de dados agregada por máquina, implementado no backend com testes automatizados." |
| **Detecção de anomalias com Isolation Forest como sinal complementar** | README §"O que está implementado", §"Pipeline de análise" (diagrama); README §Stack | `IMPLEMENTADO` | `api_tcc/ia/deteccao_multivariada.py` — `calcular_score_anomalia()`; `api_tcc/ia/pipeline.py` — `detectar_anomalia()`; `api_tcc/services/anomaly_detection.py` — `AnomalyDetectorRegistry`; modelo pré-treinado em `api_tcc/ia/modelos/isolation_forest_v1.pkl`; testes em `api_tcc/tests/test_anomaly_detection.py`, `test_anomaly_persistence.py`, `test_deteccao_multivariada.py` | "Detecção de anomalias não supervisionada com Isolation Forest como sinal complementar a thresholds determinísticos — treinado com dados simulados de bancada. Sem dataset rotulado de falhas reais e sem avaliação supervisionada." |
| **Regras determinísticas ponderadas e thresholds documentados** | README §"Pipeline de análise"; docs/limiares.md | `IMPLEMENTADO` | `api_tcc/ia/pipeline.py` — `detectar_anomalia()` com thresholds explícitos; `docs/limiares.md` documenta os limiares; `api_tcc/services/anomaly_detection.py` — Z-score e Isolation Forest com fallback | "Regras determinísticas documentadas em `docs/limiares.md` e thresholds explícitos no código, com fallback determinístico quando o modelo não está disponível." |
| **Explicação por LLM (Gemini) com circuit breaker e fallback determinístico** | `api_tcc/ia/explicacao_llm.py` (não citado publicamente no README atual) | `IMPLEMENTADO` | `api_tcc/ia/explicacao_llm.py` — `gerar_explicacao_natural()`; circuit breaker em memória; fallback explícito para texto determinístico quando API falha | "Camada de explicação em linguagem natural via Gemini API, com circuit breaker e fallback determinístico — nunca decide status, apenas reformula a recomendação já calculada." |
| **Nenhuma previsão de falha mecânica com data, probabilidade calibrada ou acurácia declarada** | `api_tcc/ia/pipeline.py` (docstring de `analisar_maquina()`); README §Stack | `IMPLEMENTADO` | `api_tcc/ia/pipeline.py` L120–124: docstring explícita "O QUE NÃO CALCULA"; sem dataset rotulado de falhas históricas; nenhum relatório de avaliação supervisionada no repositório | "O sistema classifica o estado operacional (NORMAL / ATENCAO / CRITICO). Não prevê data, probabilidade calibrada ou taxa de falha mecânica." |
| **Dashboard Next.js com service worker: cache e fila local de telemetria** | README §"O que está implementado" e §"Resiliência Offline" | `IMPLEMENTADO` | `frontend-next/public/sw.js`; README descreve comportamento de fila IndexedDB e limitações (payload inválido/credenciais expiradas); comportamento de fila offline limitado (sem credenciais privilegiadas) | "Service Worker com cache de assets e fila IndexedDB de telemetria pendente — sem credenciais privilegiadas; payload inválido ou credenciais expiradas exigem correção antes do reenvio." |
| **Frontend Next.js com build funcional** | README §"Execução com Docker", §"Testes" | `SIMULADO` | `docs/evidence/s0/front_build.txt` — `npm run build` falhou com `Cannot find module 'typescript'`; débito registrado em [Issue #2](https://github.com/Desmantelar-bit/fieldnode/issues/2); `npm run dev` não foi testado na auditoria | "Frontend Next.js em desenvolvimento (`npm run dev`). Build de produção com débito técnico registrado (Issue #2)." |
| **Autenticação por token DRF (login, logout, registro, verificação de sessão)** | README §"O que está implementado" e §"API — Endpoints principais" | `IMPLEMENTADO` | `api_tcc/api/` — endpoints `/api/auth/login/`, `/api/auth/register/`, `/api/auth/logout/`, `/api/auth/me/`; `api_tcc/tests/test_auth.py`; aviso explícito no README sobre `localStorage` como dívida técnica | "Autenticação por token DRF com registro, login, logout e verificação de sessão. Token armazenado em `localStorage` no MVP — dívida explícita pendente de migração para cookie `httpOnly`." |
| **Geração determinística de eventos e decisões com aprovação/rejeição por usuário** | README §"O que está implementado" | `IMPLEMENTADO` | `api_tcc/services/decisions.py`; `api_tcc/services/agentic.py`; `api_tcc/prompts/agentic_decision_v1.txt`; `api_tcc/tests/test_decisions.py` (309 linhas) | "Geração de eventos e decisões operacionais com aprovação ou rejeição por usuário autenticado e registro de outcome." |
| **Relatórios e exportação CSV/XLSX** | README §"API — Endpoints principais" | `IMPLEMENTADO` | `api_tcc/services/relatorios.py`; `GET /api/relatorio/`, `GET /api/relatorio/exportar/`; dependência `openpyxl` em `requirements.txt` | "Geração de relatório operacional e exportação CSV/XLSX via API autenticada." |
| **Mapa de posição GPS da frota** | README §"Rotas do Frontend" | `SIMULADO` | `GET /api/maquinas/posicao/`; frontend usa Leaflet/React-Leaflet; coordenadas GPS presentes no modelo `LeituraTelemetria`; **dados de localização são simulados** — sem GPS físico validado | "Mapa de posição da frota com coordenadas provenientes de dados simulados. Sem GPS físico validado." |
| **Simulador MQTT com fallback HTTP** | README §"Simulador MQTT" | `IMPLEMENTADO` | `scripts/simular_mqtt.py`; lógica de fallback explícita ao detectar `Connection refused`; testes de integração `api_tcc/tests/test_integration.py` | "Simulador MQTT com fallback automático para HTTP quando o broker está inacessível." |
| **Stack Docker Compose (web + worker MQTT + Mosquitto + MySQL)** | README §"Execução com Docker" | `SIMULADO` | `docker-compose.yml` presente; `docs/evidence/s0/compose_up.txt` — `docker compose up --build -d` não foi executado com sucesso (daemon Docker indisponível no ambiente de auditoria); healthchecks definidos mas não verificados em execução real | "Stack Docker Compose com Django, worker MQTT, Mosquitto e MySQL — definida e documentada, mas não verificada em execução completa nesta auditoria por indisponibilidade do daemon Docker." |
| **Offline — outbox com persistência e sincronização idempotente** | README §"Resiliência Offline" | `SIMULADO` | `simulators/edge_client.py` — outbox SQLite com retry/ACK; `simulators/teste_resiliencia.py` — script para ensaio de resiliência; `simulators/test_edge_client.py`; **sem evidência de testes com interrupção de rede real ou em campo** | "Coleta local com outbox SQLite, prioridades A/B/C e sincronização idempotente — validada em simulador de bancada (software). Protocolo de testes de resiliência em interrupção de rede real está previsto para S6." |
| **Offline — fila IndexedDB no Service Worker do frontend** | README §"Resiliência Offline" | `SIMULADO` | `frontend-next/public/sw.js`; comportamento documentado no README com limitações explícitas; **sem teste automatizado de interrupção de rede no frontend** | "Fila IndexedDB no Service Worker para payloads pendentes — sem credenciais privilegiadas. Sem testes automatizados de resiliência de rede no frontend." |
| **Multi-marca — camada Raw→Canonical com adaptadores para dois fabricantes** | README §Stack ("Hardware e transporte" — implícito em normalizacao.py) | `SIMULADO` | `api_tcc/services/normalizacao.py` — `normalizar()`, `registrar_e_normalizar()`; `api_tcc/models.py` — `RawTelemetry`, `CanonicalTelemetry`, `FabricanteMapping`; `api_tcc/tests/test_normalizacao.py` — testes com `case_ih_v1` e `john_deere_v1`; **dados de ambos fabricantes são fixtures artificiais/simulados, sem ingestão de hardware real** | "Fundação Raw→Canonical com mapeamentos simulados para dois fabricantes (`case_ih_v1` e `john_deere_v1`). Dados são fixtures de teste; sem ingestão de equipamento físico real." |
| **Hardware — ESP32 e sensores** | README §Stack: "ESP32/ESP-NOW permanecem como integração física a validar"; §Roadmap | `ROADMAP` | Não há firmware, código C/C++ para ESP32, biblioteca ESP-IDF ou código PlatformIO no repositório. O termo `ESP32` aparece apenas como `device_id` em fixtures de teste (`test_identity_contract.py`, `test_integration.py`) e no README de Roadmap. `api_tcc/ia/modelos/isolation_forest_v1.pkl` existe como artefato pré-treinado, sem hardware associado | "Protótipo de bancada com Python e simuladores HTTP/MQTT. Integração física com ESP32 e sensores é planejada (Roadmap), não implementada." |
| **Hardware — ESP-NOW entre máquinas** | AGENTS.md §hardware; proposta TCC (não disponível no repositório) | `ROADMAP` | Nenhum código ESP-NOW encontrado. Nenhum firmware presente. Referência no AGENTS.md como integração futura ("ESP-NOW entre máquinas antes da validação de S8-T5") | "ESP-NOW não implementado. Integração física entre máquinas é objetivo de S8." |
| **Data Mule — transporte de buffer offline** | README §Roadmap (implícito); `simulators/transbordo_mule_client.py` | `SIMULADO` | `simulators/transbordo_mule_client.py` — `MuleBuffer`, `MuleClient`, `collect_from_harvester()`; docstring explícita: "O encontro entre os simuladores é uma chamada Python. Isso prova o fluxo de software, não rádio, proximidade física ou comunicação entre ESP32."; testes em `api_tcc/tests/test_data_mule_integration.py`; `simulators/test_transbordo_mule_client.py` (3 testes pytest) | "Simulador de transporte de buffer (Data Mule) por software — coleta da outbox da colhedora para o buffer do mule e posterior sync com o backend. Sem rádio, proximidade física ou hardware real." |
| **Impacto financeiro (custo de parada, economia, retorno)** | Não encontrado no repositório atual. AGENTS.md §roadmap menciona "D-14" como restrição | `ROADMAP` | Nenhum número financeiro encontrado em README, docs/ ou código. AGENTS.md proíbe citar no pitch. CLAIMS_VS_CODE.md é o mecanismo de controle para essa restrição | "Não citar impacto financeiro em materiais públicos. Internamente, qualquer número deve ter fonte primária verificável antes de ser usado. Hipótese não verificada até que fontes primárias sejam documentadas em `docs/RESULTADOS_VALIDACAO_COMERCIAL.md`." |
| **Random Forest para manutenção preditiva** | Mencionado em proposta TCC v4 (não disponível no repositório); AGENTS.md §"IA/análise" lista Random Forest | `ROADMAP` | Nenhuma implementação de Random Forest encontrada nos arquivos `.py` do projeto. Os `__pycache__` de `manutencao.cpython-310.pyc` e `prescricoes.cpython-310.pyc` existem, mas os arquivos-fonte correspondentes não estão no repositório (podem ter sido removidos ou são artefatos legados). Nenhum teste referencia Random Forest. | "Random Forest não está presente no código atual. O pipeline de IA usa Isolation Forest (não supervisionado) + regras determinísticas. Manutenção supervisionada com dataset rotulado é planejada para S5." |
| **Análise preditiva de manutenção** | README §"API — Endpoints principais": `GET /api/manutencao/` | `SIMULADO` | Endpoint `GET /api/manutencao/` declarado no README; `api_tcc/ia/__pycache__/manutencao.cpython-310.pyc` existe mas o `.py` não foi localizado; a prescrição em `api_tcc/services/prescricao.py` trata prescrições operacionais (NORMAL/ATENCAO/CRITICO), não manutenção preditiva com dataset rotulado | "Endpoint `/api/manutencao/` retorna análise operacional baseada em regras e Isolation Forest. Não representa previsão calibrada de manutenção com dataset rotulado de falhas históricas." |
| **Correlação ID e rastreabilidade de requisições** | `docs/CONTRATO_TELEMETRIA_V1.md`; `api_tcc/tests/test_correlation.py` (465 linhas) | `IMPLEMENTADO` | `api_tcc/tests/test_correlation.py` — suíte extensiva (465 linhas); `docs/evidence/s0/health.json` — Correlation ID injetado na resposta de healthcheck; estrutura JSON de logging | "Correlation ID injetado em requisições e respostas, rastreável nos logs estruturados." |
| **DLQ (Dead Letter Queue) para payloads inválidos** | `docs/DLQ.md` | `IMPLEMENTADO` | `api_tcc/services/dlq.py`; `docs/DLQ.md`; testes em `api_tcc/tests/test_dlq.py` | "DLQ implementado para payloads inválidos que não passam pela validação de ingestão." |
| **Atenção Engine e eventos priorizados** | `docs/ATTENTION_ENGINE.md`; `GET /api/events/` | `IMPLEMENTADO` | `api_tcc/services/eventos.py`; `docs/ATTENTION_ENGINE.md`; `api_tcc/tests/test_decisions.py` | "Motor de atenção com priorização de eventos operacionais e fila de decisões." |
| **SEQ_ID — numeração sequencial de leituras por dispositivo** | `docs/SEQ_ID.md` | `IMPLEMENTADO` | `docs/SEQ_ID.md`; `api_tcc/models.py` — campo `seq_id`; `api_tcc/tests/test_seq_id.py` | "Numeração sequencial de leituras por dispositivo, implementada no modelo e documentada." |

---

## 2. As Seis Afirmações Obrigatórias do Roadmap

Conforme exigido pela tarefa S0-T3:

| Afirmação | Formulação permitida hoje | Formulação proibida hoje | Status encontrado |
|---|---|---|---|
| **IA** | "Detecção de anomalias não supervisionada (Isolation Forest por máquina), combinada com regras operacionais e explicação por LLM nos limites da implementação atual: sem dataset rotulado de falhas reais e sem relatório de avaliação S5." | "IA que prevê falhas"; "precisão de X%"; "recall de Y%" sem relatório de avaliação S5 | `IMPLEMENTADO` (dentro dos limites descritos) |
| **Offline** | "Coleta local com outbox SQLite, prioridades A/B/C e sincronização idempotente — validada em simulador de bancada (software). Protocolo de testes com interrupção de rede real está previsto para S6." | "Funciona offline a quilômetros de distância"; "buffer de 30 dias"; "operação de campo validada" | `SIMULADO` |
| **Multi-marca** | "Fundação Raw→Canonical com mapeamentos simulados para dois fabricantes (`case_ih_v1` e `john_deere_v1`) — dados de fixtures artificiais; sem ingestão de hardware físico real." | "Sistema multi-marca"; "agnóstico de OEM"; "suporta qualquer fabricante" | `SIMULADO` |
| **Hardware** | "Simuladores Python de bancada (HTTP e MQTT). Integração física com ESP32 e sensores é objetivo de S8 — não implementada no código atual." | "Protótipo de bancada com ESP32" (pois o ESP32 não está implementado); "ESP-NOW entre máquinas" antes de S8-T5 | `ROADMAP` |
| **Data Mule** | "Simulador de transporte de buffer por software — coleta da outbox de um simulador de colhedora para buffer de mule, com sync subsequente ao backend. Validado apenas em software." | "Rede de Data Mule em campo"; "Data Mule com rádio validado" | `SIMULADO` |
| **Impacto financeiro** | Não citar em materiais públicos ou no pitch. Uso interno: qualquer hipótese de impacto é não verificada e requer fonte primária antes de ser documentada em `RESULTADOS_VALIDACAO_COMERCIAL.md`. | Qualquer número de economia, custo evitado, ROI ou produtividade sem fonte primária verificável | `ROADMAP` |

---

## 3. Divergências Encontradas

### 3.1 Random Forest — afirmação sem evidência no código

- **Afirmação original:** AGENTS.md §"IA/análise" lista "Random Forest" como tecnologia em uso.
- **Documento:** `AGENTS.md` (regra operacional do repositório)
- **Realidade encontrada:** Nenhum arquivo `.py` com `RandomForest` ou `random_forest` foi encontrado no projeto. Os arquivos `__pycache__/manutencao.cpython-310.pyc` e `prescricoes.cpython-310.pyc` existem, mas os `.py`-fonte não estão presentes. Nenhum teste referencia Random Forest.
- **Status atribuído:** `ROADMAP`
- **Alteração realizada:** Nenhuma alteração no AGENTS.md (documento operacional, fora do escopo desta tarefa sem autorização). Registrada como divergência.
- **Evidência:** busca em `api_tcc/**/*.py` e `simulators/**/*.py` via `Select-String` — zero ocorrências de `RandomForest` ou `random_forest`.

### 3.2 ESP32 — hardware citado sem implementação

- **Afirmação original:** AGENTS.md §"hardware / ingestão": "ESP32" listado como componente atual. Proposta TCC v4 (não disponível no repositório) citada no contexto da tarefa como afirmando "ESP-NOW como entregue".
- **Documento:** `AGENTS.md`; proposta TCC v4 (ausente do repositório)
- **Realidade encontrada:** Nenhum firmware, código ESP-IDF, PlatformIO, C/C++ ou biblioteca ESP32 no repositório. `ESP32` aparece apenas como string em `device_id` de fixtures de teste.
- **Status atribuído:** `ROADMAP`
- **Alteração realizada:** README já estava correto: "ESP32/ESP-NOW permanecem como integração física a validar". Nenhuma alteração necessária no README.
- **Evidência:** varredura de arquivos — sem `.c`, `.cpp`, `.ino`, `.h` ou `platformio.ini`; referências a `ESP32` em testes são `device_id` como string, não código de firmware.

### 3.3 Proposta TCC — não disponível no repositório

- **Afirmação original:** O contexto da tarefa menciona "Proposta_TCC_v4 afirma ESP-NOW e Random Forest como entregues".
- **Documento:** Proposta TCC (arquivo não localizado no repositório)
- **Realidade encontrada:** Nenhum arquivo de proposta TCC foi localizado em `docs/`, na raiz ou em subdiretórios do repositório.
- **Status atribuído:** Não aplicável à matriz — a proposta não pode ser auditada sem o arquivo.
- **Alteração realizada:** Nenhuma (arquivo ausente). Registrado como pendência.
- **Evidência:** `Get-ChildItem -Recurse` não encontrou nenhum arquivo com "TCC", "proposta" ou "pitch" (além dos arquivos já conhecidos).

### 3.4 Build do frontend — afirmação implícita de funcionalidade

- **Afirmação original:** README §"Testes": `npm run build` listado como comando de build.
- **Documento:** `README.md`
- **Realidade encontrada:** `npm run build` falhou durante S0-T1 com `Cannot find module 'typescript'`. Débito registrado em Issue #2.
- **Status atribuído:** `SIMULADO` (comando documentado, mas não verificado como bem-sucedido nesta auditoria)
- **Alteração realizada:** Nenhuma — o README já menciona `npm run build` sem afirmar sucesso. Issue #2 já documenta o débito. Mantido como está.

### 3.5 `__pycache__` de módulos removidos (manutencao.py, prescricoes.py)

- **Afirmação original:** `GET /api/manutencao/` listado no README como endpoint ativo.
- **Documento:** `README.md`
- **Realidade encontrada:** `api_tcc/ia/__pycache__/manutencao.cpython-310.pyc` e `prescricoes.cpython-310.pyc` existem, mas os `.py`-fonte não foram localizados. O endpoint pode ser servido por outro módulo (ex: `api_tcc/services/prescricao.py`), mas sem o `.py`-fonte do módulo de manutenção, não é possível confirmar o que `/api/manutencao/` retorna além de classificações operacionais.
- **Status atribuído:** `SIMULADO` — endpoint declarado, origem exata do módulo de manutenção incerta.
- **Alteração realizada:** Nenhuma. Registrado como pendência de investigação.

---

## 4. Pendências de Validação

As seguintes afirmações dependem de evidências futuras e **não podem ser rebaixadas para `IMPLEMENTADO` apenas com evidências atuais**:

| Pendência | Documento de resolução | Semana prevista |
|---|---|---|
| Avaliação supervisionada do Isolation Forest (precisão, recall, F1) com dataset rotulado | `docs/HONESTIDADE_METODOLOGICA_ML.md` + `docs/PLANO_DATASET_ROTULADO.md` | S5 |
| Protocolo de testes de resiliência com interrupção de rede real (não apenas simulador software) | `docs/PROTOCOLO_TESTE_RESILIENCIA.md` | S6 |
| Validação do Data Mule em campo ou bancada física | `docs/REPOSICIONAMENTO_ESCOPO_HARDWARE.md` | S8 |
| Validação do protótipo ESP32 e comunicação de hardware | `docs/REPOSICIONAMENTO_ESCOPO_HARDWARE.md` | S8 |
| Comunicação ESP-NOW entre máquinas | `docs/REPOSICIONAMENTO_ESCOPO_HARDWARE.md` — S8-T5 | S8 |
| Build do frontend (Issue #2) | Resolução técnica do débito TypeScript/ESLint | A definir |
| Stack Docker Compose verificada em execução real | Requer daemon Docker ativo | A definir |
| Fonte primária para qualquer número de impacto financeiro | `docs/RESULTADOS_VALIDACAO_COMERCIAL.md` | S12 |
| Proposta TCC — auditoria de afirmações | Localizar e versionar a proposta no repositório | Imediato |
| Módulo `manutencao.py` — localizar ou confirmar remoção | Investigação do endpoint `/api/manutencao/` | A definir |
| Random Forest — confirmar se é roadmap ou código legado removido | Investigação de histórico Git + decisão de roadmap | A definir |

---

## 5. Revisão Cruzada

**Status:** `PENDENTE`

O roadmap exige revisão cruzada por outro membro antes que esta matriz seja considerada definitiva.

| Campo | Valor |
|---|---|
| Revisor | A CONFIRMAR |
| Data da revisão | Não iniciada |
| Pontos questionados | — |
| Ajustes solicitados | — |
| Resultado | PENDENTE |

> **Nota:** a ausência de revisão independente não invalida a matriz como instrumento de trabalho,
> mas impede a classificação final como `CONCLUÍDO`. Esta entrega é classificada como
> `CONCLUÍDO COM PENDÊNCIAS EXTERNAS`.

---

## 6. Histórico de Alterações

| Data | Responsável | Alteração |
|---|---|---|
| 2026-11-04 | S0-T3 (Antigravity) | Criação da versão 1.0 — auditoria inicial completa do repositório |

## 7. Estado das Pendências Externas

- **Revisão cruzada:** PENDENTE; aguarda revisão e assinatura de outro membro.
- **Proposta TCC:** ausente do repositório nesta data (2026-11-04); auditoria pendente até que o documento seja localizado ou formalmente mantido fora do repositório.
