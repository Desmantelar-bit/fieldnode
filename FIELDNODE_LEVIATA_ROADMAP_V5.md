# FIELDNODE · LEVIATÃ STRATEGIC ROADMAP V5

### Master Plan definitivo V5: foco diesel a fundo, prescrição de alta confiança (PR e prazo-limite) e home de decisão rápida, sobre a V4 (offline, IA, prescrição) e a V3

**Versão:** 5.0 (V4 + pedidos do analista sênior supervisor; **nada da V3 nem da V4 foi removido**) · **Modo:** GODMODE · **Data-base do estado do código:** 2026-10-24 (clone de `Desmantelar-bit/fieldnode`, branch `main`, commit `3b5f5c0`, histórico squashado em 1 commit)
**Fontes:** (1) framework LEVIATÃ sem limite de tempo; (2) `05_Roadmap_Ultimato.md` (16 blocos de revisão, que se contradizem em vários pontos); (3) `contexto_unificado_agente.md`, `FieldNode_Proposta_TCC_v4.docx`, `Pesquisa_Referenciada_FieldNode`, `CLAUDE.md`; (4) roadmap v2 (10 semanas, já executado no backend); (5) **auditoria direta do repositório clonado**, que é a fonte de verdade deste documento.

---

## 0-A. DELTA V4 → V5 (LEIA PRIMEIRO)

> **Origem da V5:** o analista sênior, supervisor do projeto, viu o site e disse que, apresentado como estava, seria "o que qualquer empresa já tem, sem diferencial". Ele pediu **foco em uma parte do motor diesel, analisada a fundo, com muitos sinais e códigos de falha, prescrição com percentual de recomendação e tempo-limite para manutenção, e uma tela inicial de decisão rápida**. A V5 incorpora **todos** os pontos, **sem exceção**, e **não remove nada da V4**: acrescenta 4 fatias (S18 a S21), 3 pilares novos (P4, P5, P6), reordena o calendário e reclassifica prioridades.

### 0-A.1 Os 10 pedidos do analista e onde cada um é entregue

| # | Pedido do analista | Entrega na V5 | Tarefas | Aceite |
|---|---|---|---|---|
| 1 | **Home mais interativa, mapa ao lado da seleção** | Tela inicial dividida: barra de seleção à esquerda + mapa; seleção bidirecional | S20-T1, S20-T9 | `home_100` (E2E) |
| 2 | **Enxugar a home; abrir dados do equipamento só depois de escolher a frota** | Home com no máximo cards e mapa; dados só após seleção hierárquica (site → frente → frota → máquina) | S20-T1, S20-T4, S20-T7 | teste dos 5 s e dos 30 s |
| 3 | **Cards "3 críticos, 6 atenção, 30 normais" que abrem prescrição e tendência** | Cards clicáveis com contagem real; drill-down: lista com prescrição resumida → detalhe com tendências | S20-T2, S20-T3 | `home_100` |
| 4 | **Focar num motor diesel** | Subsistema-âncora: **sistema de combustível diesel de alta pressão (common rail)**; motor e acesso definidos como gate da semana 1 | S18-T1, S18-T10 | `diesel_100` |
| 5 | **Analisar uma parte a fundo (ex.: bomba de alta) com muitos sinais e DTC** | Catálogo de sinais do motor (≥ 8 a 12), indicadores de saúde por componente, decodificação de DTC com correlação | S18-T2, T3, T4, T7, T8 | `diesel_100` |
| 6 | **Padrões irreais desclassificados da métrica** | Perfil de normalidade por sinal e por regime + qualidade por amostra/janela; dado descartado **não entra** em média, tendência nem prognóstico, e o descarte é visível | S18-T5, S18-T6 | teste de desclassificação |
| 7 | **Percentual de recomendação visual** | **PR**: confiança de que a inspeção vai confirmar o defeito, **calibrada com laudos**, com intervalo, tamanho de amostra e selo "provisório" | S19-T4, T5, S20-T6 | `confianca_100` |
| 8 | **Tempo-limite para manutenção + o que fazer** | **PLM (prazo-limite de manutenção)**: horas de motor até a inspeção, **quantil conservador com intervalo**, mais a **escada de confirmação** do que fazer | S19-T6, T7, S16-T2 | backtest e `confianca_100` |
| 9 | **Decisão final do técnico** | Técnico decide e pode divergir com motivo registrado; divergência alimenta o aprendizado; sistema nunca executa | S19-T10 | E2E |
| 10 | **Laudo do técnico (exemplo da bomba com 70% de vida)** | Laudo estruturado (componente, achado, medições, vida útil estimada pelo técnico, decisão, anexos); é a **verdade de campo** que calibra PR e mede precisão | S19-T2, T3, T9, T12 | cenário "bomba 70%" |

### 0-A.2 O que "precisão" significa (e o que a V5 **não** promete)

O analista deu o critério no próprio exemplo: *"enviei a bomba ao técnico e ele disse que ainda tinha 70% de vida útil: perdi tempo, disponibilidade e custo"*. Logo, o que importa é **não recomendar remoção quando o componente está bom** e **avisar a tempo quando está ruim**.

| Termo | Definição **medida** na V5 |
|---|---|
| **Precisão da prescrição** | % das recomendações de um nível cujo **laudo confirmou** o defeito, com **intervalo de confiança** (Wilson) e `n` visível |
| **Cobertura** | % de máquinas/componentes para os quais o sistema emite recomendação (o resto é "monitorar" ou "dados insuficientes") |
| **Abstenção** | quando a evidência é fraca, o sistema **não recomenda** e diz por quê (é o que derruba recomendação inútil) |
| **Percentual de recomendação (PR)** | probabilidade **calibrada** de o laudo confirmar o achado, dada a evidência atual; mostrado como medidor com faixa e `n` |
| **Prazo-limite de manutenção (PLM)** | horas de motor até o ponto em que a inspeção deve ocorrer: **limite inferior conservador** do intervalo de previsão do tempo até o limite, menos margem de segurança; ou **"sem prazo confiável"** |
| **Decisão final** | sempre do técnico |

**Honestidade obrigatória:**
- **"100% de precisão" não existe** e não é promessa da V5. A promessa é **precisão medida, publicada com intervalo, com abstenção** e meta de projeto definida com o analista (D-54).
- **Vida útil residual de componente (ex.: "30% de vida")** só pode ser afirmada **depois** de validada contra laudos/banco de provas. Antes disso o sistema mostra **PLM + PR provisório**, rotulados e com `n`.
- Enquanto `n` for pequeno, a UI exibe **"PR provisório (n = X laudos)"**. Nunca esconder o `n`.

### 0-A.3 Problemas reais do investidor e do gestor: o que o FieldNode entrega

| # | Problema real | O que o FieldNode entrega (V5) | Métrica **medida** | Tarefas |
|---|---|---|---|---|
| 1 | Parada não programada derruba disponibilidade | Detecção precoce + **PLM** por componente | tempo de antecedência (h de motor) entre aviso e falha confirmada | S18, S19-T6 |
| 2 | **Manutenção desnecessária** (peça boa enviada ao técnico) | PR calibrado, **escada de confirmação** e abstenção | precisão por nível, taxa de recomendação sem achado | S19-T5, T7, T9 |
| 3 | Dado não confiável gera decisão ruim | Qualidade por sinal, desclassificação visível, perfil de normalidade | % de dado descartado e motivo | S18-T5, T6 |
| 4 | Operação em área sem conectividade | Offline-first com gateway-núcleo e enlaces | soak de 14 dias | S13, S14 |
| 5 | Dependência de fornecedor e do dado | Data Passport e formatos abertos | export/import com contagem idêntica | S11-T6 |
| 6 | **Falta de prova de valor (ROI)** | **Ledger de valor por decisão** (custo evitado × desperdiçado, com premissas do **cliente**, sem valor padrão) | precisão, ledger, MTTA/MTTR | S21-T1, T2 |
| 7 | Quem decidiu e com base em quê? | Técnico decide; cadeia de auditoria com hash; laudo assinado | auditoria verificável | S16-T8, S19-T10 |
| 8 | Custo e tempo de implantação | Kit com QR, provisionamento em 10 min | tempo de instalação por pessoa de fora | S17-T4, T5 |
| 9 | Integração com o que já existe | OS exportável (`.ics`/webhook), API v1, adaptadores J1939 | OS exportada e aceita pelo sistema do cliente | S4-T4, S11-T7 |
| 10 | Confiança do comprador na ferramenta | Painel de precisão público para o cliente, data room técnico, matriz de diferenciais com fontes | relatório de precisão e pacote de evidências | S19-T9, S21-T3, T7 |

*Observação do professor mantida:* **finanças ficam fora do pitch**. O ledger e o ROI existem no **produto**, com premissas do cliente, e na conversa de piloto.

### 0-A.4 Os novos pilares (além de P1, P2 e P3 da V4)

#### P4 · DIESEL-100 (uma parte a fundo, muitos sinais, dado limpo, DTC)

- [ ] Motor diesel real e acesso definido (S18-T1).
- [ ] Catálogo de sinais **realmente publicados** pelo motor, conjunto mínimo ≥ 8 sinais do subsistema de combustível (S18-T2).
- [ ] Modelo de dados por componente e contrato multicanal (S18-T3, S18-T4).
- [ ] Perfil de normalidade por sinal e regime (S18-T5) e desclassificação de dado irreal (S18-T6).
- [ ] DTC decodificado, correlacionado e ligado a componente e playbook (S18-T7).
- [ ] Indicadores de saúde por componente, incluindo bomba de alta (S18-T8).
- [ ] Dados de oficina/banco de provas (S18-T9) e campanha no motor (S18-T10); falhas reversíveis supervisionadas (S18-T11).
- [ ] `diesel_100.py` verde 3× (S18-T13).

#### P5 · CONFIANÇA-100 (PR, PLM, laudo, precisão, decisão do técnico)

- [ ] Definições formais e política de recomendação (S19-T1, S19-T8).
- [ ] Laudo estruturado e registro de falhas não detectadas (S19-T2, S19-T3).
- [ ] Evidência multi-sinal por componente (S19-T4).
- [ ] **PR calibrado** com intervalo e selo provisório (S19-T5).
- [ ] **PLM** com intervalo, margem e abstenção (S19-T6).
- [ ] **Escada de confirmação** de custo crescente (S19-T7).
- [ ] Painel de precisão e calibração (S19-T9).
- [ ] Decisão final do técnico com divergência registrada (S19-T10).
- [ ] Backtest de PR e PLM (S19-T11) e cenário "bomba com 70% de vida" (S19-T12).
- [ ] `confianca_100.py` verde 3×.

#### P6 · HOME-100 (decisão rápida em uma tela)

- [ ] Layout novo: seleção + mapa, cards clicáveis, dados só após seleção (S20-T1 a T4).
- [ ] Painel do componente com PR, PLM, tendência e DTC (S20-T5) e medidor visual consistente (S20-T6).
- [ ] UI enxuta (S20-T7) e teste de usabilidade com gestores/técnicos (S20-T8).
- [ ] Mapa com seleção bidirecional (S20-T9).
- [ ] `home_100` (E2E) verde 3× e teste dos 30 s: gestor identifica o equipamento crítico e abre a prescrição em **menos de 30 s** sem ajuda.

### 0-A.5 O que muda no jeito de construir (decisões estruturais)

1. **A largura da V4 vira apoio, não objetivo.** O diferencial é **profundidade no subsistema de combustível diesel**. As tarefas de largura (S11, S17 extras, S15-T6, S15-T16, S10-T9) descem para **P3** (regra de corte V5, seção 0-A.7).
2. **O sensor de campo deixa de ser "3 medidas".** O núcleo de dados passa a ser o **barramento do motor** (J1939/OBD, só escuta) com **dezenas de sinais**; os sensores externos (temperatura, vibração) viram **complemento**, não o diagnóstico.
3. **Laudo é a fonte de verdade.** Sem laudo, PR é provisório. Por isso a **coleta de laudos começa na semana 1** (S19-T2, S12-T12, S18-T9).
4. **"O que fazer" tem custo crescente.** O sistema não manda remover a bomba: manda **verificar do mais barato ao mais caro**, na ordem em que a evidência justifica (S19-T7).
5. **Tudo continua offline** (gateway-núcleo) e **auditável** (cadeia de hash).

### 0-A.6 Compras e acessos adicionais (semana 1)

| Item | Para quê | Tarefa |
|---|---|---|
| **Acesso a motor diesel com ECU** (gerador diesel com banco de carga resistivo, trator, caminhão ou veículo diesel de oficina), com **autorização do dono** | núcleo do foco | S18-T1 |
| Cabo/conector de diagnóstico compatível (J1939 9 pinos ou OBD-II) e transceptor CAN | escuta passiva | S8-T12, S18-T2 |
| Parceria com **oficina de bomba/bicos injetores** (banco de provas, laudos) | rótulos reais de estado do componente | S18-T9, S19-T2 |
| Sensores **não invasivos** do subsistema: temperatura do combustível, transdutor **somente de baixa pressão**, ΔP de filtro, acelerômetro no corpo da bomba | complemento do barramento | S18-T12 |
| Mecânico/técnico parceiro para revisar playbooks e laudos | autoridade técnica | S16-T10, S19-T2 |

> **Aviso de segurança (inegociável):** **nunca** interceptar a linha de **alta pressão** do combustível diesel (pressões muito elevadas; risco de lesão grave e incêndio). A alta pressão só é lida **pela ECU via barramento**. Testes com falha só **reversíveis**, com mecânico presente (S18-T11).

### 0-A.7 Regra de corte V5 (substitui a seção 0.6 da V4)

Se o tempo apertar, corta-se **nesta ordem**, **nunca** os pilares P1 a P6:

1. **P3 (executa depois dos pilares):** S0-T4/T5/T6, S10-T7/T9, S11-T4/T5/T7, S17-T5 a T11, S3-T8/T10, S15-T6, S15-T16, S14-T7 (satélite, se o modem não chegar).
2. S11 inteira, S9-T4/T5, S17 restante (exceto S17-T1 e S17-T2).
3. **Nunca cortar:** tudo da V4 listado como "nunca cortar" **e** S18-T1 a T8 e T13, S19-T1 a T12, S20-T1 a T6 e T8, S21-T1 e T2.

### 0-A.8 Autocrítica da V5 (o que pode dar errado)

- **Acesso ao motor** é o gargalo nº 1. Sem motor diesel com ECU, o "aprofundar" vira simulação. **Gate na semana 1 a 2**; se falhar, o plano B é o **banco de provas da oficina** + dados de gerador, e o foco continua sendo o subsistema, **rotulado** pelo que for real.
- **O motor pode não publicar** o sinal que queremos (ex.: pressão do trilho). S18-T2 descobre isso cedo; o conjunto de indicadores se adapta ao que existe.
- **Poucos laudos** nas primeiras semanas: PR nasce **provisório** e a UI diz isso. Quanto mais laudos, mais calibrado.
- **PLM validado** só vale para o que foi observado (sessões, bancada, oficina). Fora disso, "sem prazo confiável".
- **12 semanas é apertado.** A regra de corte protege o foco, e a V4 inteira continua no documento.
- **Meta de precisão** (ex.: "nível 3 só com PR alto") é **proposta de política**, a **fechar com o analista** (D-54), não número cravado.

---

## 0. DELTA V3 → V4 (LEIA PRIMEIRO)

> **Regra de ouro desta versão (pedido da Paola):** *se o projeto não tem a base para uma feature que ela quer, a base vira tarefa e a feature entra.* Nada da V3 foi removido nem resumido. A V4 **acrescenta** 5 fatias novas (S13 a S17), 5 tarefas de hardware (S8-T10 a T14), 2 tarefas de validação (S12-T11, T12), **reordena a execução** (hardware desde o dia 1, em paralelo) e **reclassifica** itens que a V3 tinha adiado.

### 0.1 O que mudou, em uma tabela

| Tema | V3 dizia | V4 faz |
|---|---|---|
| Offline | Sensor + alerta + buffer + dashboard local; Trust/Event/Decision na "sede/nuvem" | **Gateway-Núcleo** (S13): a pilha inteira (ingestão, Trust, Event, Decision, WorkOrder, ML, PWA, login) roda no gateway sem internet; nuvem vira **réplica** com replicação bidirecional |
| "Tempo real" durante 14 dias fora | Mule em rede Docker, LoRa só plano, satélite só simulado | **4 enlaces reais** (S14): LoRa medido em campo, relay LoRa/ESP-NOW no transbordo, celular do operador via BLE, satélite com modem real; **soak test de 14 dias** |
| Hardware | Semana 8, depois de IA e front | **Dia 1, em paralelo com S0 e S1** (trilha B); sensores corretos (DS18B20 inox, termopar K, hall, GPS, MPU6050, RTC); CAN **real** em modo só escuta |
| Dados | Sintéticos + dataset público | **Campanha de dados reais + rig de falha controlada** (motor DC com desbalanceamento, aquecimento supervisionado) |
| IA | IF por regime + LLM só explica | **IA profissional** (S15): 5 detectores comparados com split temporal por sessão, modelo de resíduo, EWMA/CUSUM no nó, autoencoder challenger, incerteza calibrada, SHAP, MLOps com gates e drift, diagnóstico assistido, **copiloto com RAG e ferramentas rodando local** |
| Prescrição | Decision estruturada + OS + desfecho | **Prescrição profissional** (S16): biblioteca de playbooks revisados por mecânico, checklist executável com evidências, estoque, **otimizador de janela de manutenção (OR-Tools)**, what-if, reincidência, cadeia de auditoria à prova de adulteração |
| Itens "adiados" (seção 24 da V3) | DEFER por falta de base | Cada um virou **tarefa que constrói a base** (nova seção 24) |
| Diferenciais extras | nenhum além do núcleo | **S17**: risco térmico de incêndio (ligado à palestra), redundância de sensor, OTA assinada, kit instalável com QR, modo cabine, relatório de turno offline, benchmark entre máquinas, painel executivo, modo replay |

### 0.2 Os três pilares que precisam estar 100% (definição objetiva de "100%")

**"100%" aqui significa: critério de aceite escrito, teste automatizado verde, evidência gravada, funcionando sem internet e depois de reiniciar o equipamento.** Um pilar só é declarado pronto quando **todos** os itens estão marcados.

#### P1 · PRESCRIÇÃO-100 (não é predição, é *o que fazer*)

- [ ] Toda regra e todo achado do motor têm **playbook** revisado por mecânico (S16-T1, S16-T10).
- [ ] A prescrição tem: observação, evidências, **hipótese separada do fato**, ação recomendada, urgência com justificativa, responsável, prazo, estado (S16-T2).
- [ ] Checklist executável por passo, com medições, fotos e assinatura (S16-T3).
- [ ] Peças e estoque considerados antes de agendar (S16-T4).
- [ ] **Otimizador de janela de manutenção** propõe a ordem das intervenções e explica o porquê (S16-T6).
- [ ] "E se eu adiar?" com cenários rotulados como estimativa (S16-T7).
- [ ] Verificação pós-reparo por telemetria e **detecção de reincidência** com escalonamento (S16-T5).
- [ ] Cadeia de auditoria com hash verificável (S16-T8).
- [ ] Ciclo completo **sem internet** e **após reboot do gateway** (S16-T9, S13-T8).
- [ ] Métricas medidas: tempo evento → prescrição → OS → execução; % com playbook; % checklist concluído (S16-T9, S17-T10).

#### P2 · IA-100 (profissional, com número e sem promessa falsa)

- [ ] Campanha de dados reais e rig de falha controlada, versionados (S15-T1, S15-T2).
- [ ] Especificação única de features usada no nó, no gateway e no backend, com vetores de teste (S15-T3).
- [ ] **Cinco detectores comparados** (limiar fixo, EWMA/CUSUM, Isolation Forest por regime, resíduo, autoencoder) em **split temporal por sessão**; se o limiar ganhar, publica que ganhou (S15-T4 a T6).
- [ ] Incerteza calibrada (S15-T7) e explicação por alerta (S15-T8).
- [ ] MLOps: registro, gates champion/challenger, modo sombra, drift, retreino, rollback (S15-T9).
- [ ] Diagnóstico assistido com hipóteses ranqueadas e dados faltantes (S15-T10).
- [ ] Curva de falso alarme caindo com o feedback do mecânico (S15-T11).
- [ ] **Copiloto** com RAG e ferramentas, rodando local, avaliado e testado contra injeção (S15-T12 a T14).
- [ ] **Teste de IA offline**: internet cortada, leituras novas, inferência local; modelo ausente, quebrado e dados insuficientes degradam com selo (S15-T15, S13-T7).
- [ ] Model card e `CLAIMS_VS_CODE.md` coerentes (S5-T6).

*A V4 não promete "prevê a quebra". Promete detecção precoce medida, estimativa de tempo até o limite com incerteza, diagnóstico com hipóteses e prescrição acionável. Previsão supervisionada de falha entra quando a base de rótulos existir (a campanha e o rig são o começo dessa base, S15-T1/T2/T11).*

#### P3 · OFFLINE-100 (o diferencial que separa de dashboard simples)

**Definição OFF-14 (o que a Paola pediu):** a máquina passa **até 14 dias** sem internet e longe da sede. Durante todo esse período:

1. o nó **coleta, tria, alarma localmente** (LED, buzzer, display) e guarda tudo na flash;
2. **alertas de classe A chegam à central em minutos** por um enlace alternativo (LoRa até gateway/relay, celular do operador por BLE, ou satélite), **não só depois do retorno**;
3. telemetria B e C chega em lote por LoRa, relay no transbordo ou mule físico;
4. a **decisão, a prescrição e a OS nascem no gateway local** sem internet, e o operador aprova pelo celular via hotspot;
5. ao final: **0 perda em A e B, 0 duplicata, 0 decisão duplicada**, com números de latência por enlace.

Checklist de pilar:

- [ ] Gateway-Núcleo completo, login offline, PWA offline, ML local (S13-T1 a T7).
- [ ] Replicação bidirecional com ID determinístico e regra de autoridade (S13-T4 a T6).
- [ ] **Teste "apagão total"** com reboot do gateway e do ESP32 (S13-T8).
- [ ] Nó com triagem EWMA/CUSUM e alarme local (S8-T13).
- [ ] LoRa **medido em canavial/campo** (S14-T2, S14-T3), relay no transbordo (S14-T4), mule físico com 3 ESP32 (S14-T5).
- [ ] Celular do operador como mule BLE (S14-T6) e satélite real (S14-T7) para onde nada mais alcança.
- [ ] Connectivity Manager com os enlaces reais e failover (S14-T8).
- [ ] **Soak test de 14 dias** com relatório (S14-T9) e autonomia de energia medida (S14-T10).
- [ ] Painel de cobertura/enlaces e mapa de cobertura (S14-T11).
- [ ] Enlaces autenticados e cifrados (S14-T12).

**Nota de física (uma vez só, sem drama):** "tempo real" exige um enlace de rádio ou satélite entre a máquina e alguém. Não existe sincronização instantânea sem enlace. A V4 resolve isso construindo **camadas de cobertura**: onde o LoRa alcança, é segundos; onde o celular do operador passa, é minutos; onde nada alcança, o satélite alcança. A latência por enlace é **medida** (S14-T1 define o SLA, S14-T9 mede).

### 0.3 Como a V4 trata o que a V3 chamava de "limitação"

| Item que a V3 adiava | Base que faltava | **Tarefa que constrói a base** | Estado V4 |
|---|---|---|---|
| Decisão offline | Pilha só na nuvem | S13-T1 a T8 | **BUILD_NOW** |
| LoRa | Nenhum rádio, nenhuma medição | S14-T2, T3 | **BUILD_NOW** |
| Satélite | Sem modem | S14-T7 (estudo, compra, integração) | **BUILD_NOW com gate de compra** |
| Data Mule | Só Docker | S14-T5, T4, T6 | **BUILD_NOW** |
| CAN/J1939 real | Só emissor de bancada | S8-T12 (escuta em veículo real) | **BUILD_NOW** |
| LSTM/autoencoder | Sem dado | S15-T1, T2 (dados) + S15-T6 | **PROTOTYPE_NOW, adoção por gate** |
| Chatbot | Sem decisões com volume | S15-T12 (RAG sobre playbooks e histórico) | **PROTOTYPE_NOW** |
| LLM local | Sem hardware | S15-T13 (benchmark no gateway) | **VALIDATE_NOW** |
| RUL / tempo até o limite | Sem rótulo | S15-T2 (rig de degradação) + S9-T3 | **PROTOTYPE_NOW com rótulo "validado no rig"** |
| Playbooks | Sem conteúdo | S16-T1, T10 | **BUILD_NOW** |
| Estoque e peças | Sem cadastro | S16-T4 | **BUILD_NOW** |
| Otimização de agenda | Sem solver | S16-T6 | **BUILD_NOW** |
| OTA | Sem firmware | S17-T3 | **BUILD_NOW** |
| Score de operador | Sem política | continua `DEFER` (D-16) | **mantido: risco jurídico, não é falta de base** |
| Microserviços/K8s | n/a | continua `REJECT` | **mantido: não agrega valor medido** |

**O que a V4 mantém (porque protege a defesa, não porque é limitação):** a política de claims. Cada afirmação pública aponta para evidência (`CLAIMS_VS_CODE.md`). O professor já cobrou "não prometa IA sem modelo treinado". A diferença é que agora **há** modelo treinado, dado real e relatório, então a frase fica forte e verdadeira.

### 0.4 Resposta às três avaliações externas

| Ponto levantado | Decisão | Motivo |
|---|---|---|
| Offline precisa ser o núcleo operacional completo no gateway | **Aceito** | Alinha com o pedido original; vira S13 |
| EWMA/CUSUM no nó, alarme local, prescrição curta no display | **Aceito** | Controle estatístico simples não é "Edge AI com LLM"; S8-T13 |
| Replicação bidirecional, ID determinístico, autoridade | **Aceito** | Reaproveita SyncCursor; S13-T4 a T6. HLC só para edição de domínio, **não** para telemetria (continua append-only) |
| Celular do operador como mule BLE | **Aceito** | Barato e real; S14-T6. Web Bluetooth funciona em Chrome no Android; **iPhone não** (decisão: Android-first) |
| Hardware desde o dia 1 | **Aceito** | Reordena a execução; trilha B paralela |
| DHT inútil para máquina; DS18B20 inox, termopar K | **Aceito** | S8-T10 |
| CAN "real" via outro ESP32 ainda é simulação | **Aceito** | S8-T12 escuta veículo real em modo listen-only, nunca transmite |
| GPS ausente | **Aceito** | S8-T11 |
| Campanha de dados reais e rig de falha (motor DC + MPU6050 + desbalanceamento) | **Aceito** | S15-T1, T2 |
| Modelo de resíduo (temperatura esperada por carga) | **Aceito** | S15-T4 |
| Avaliar em dado real, comparar com limiar, publicar se o limiar ganhar | **Aceito** | S15-T5 |
| Playbooks por `regra_id` revisados por mecânico | **Aceito** | S16-T1 |
| Cortar satélite simulado | **Parcial** | Stub some do caminho crítico; **entra satélite real** (S14-T7) |
| Cortar LoRa e ficar só em ESP-NOW | **Recusado** | Paola quer sincronização durante 14 dias fora; ESP-NOW tem alcance curto. LoRa vira tarefa medida |
| Cortar Consequence Engine, deixar só "avise o transbordo" | **Parcial** | Mantém o v0.1 de regras (sem número inventado) e acrescenta a visão simples de aviso ao transbordo (S9-T6) |
| Cortar chatbot | **Recusado** | Paola pediu; vira copiloto com RAG, ferramentas e avaliação, **fora do caminho crítico** |
| Cortar S0-T4/T5/T6, S10-T9, S11-T4/T5 | **Parcial** | Nada é apagado. Passam a **prioridade P3** (executar só depois dos pilares), conforme seção 0.6 |
| LSTM/RUL fora da entrega | **Parcial** | Autoencoder entra como *challenger* com gate de adoção; RUL só como "tempo até o limite" rotulado e validado no rig |
| 5 a 6 entrevistas não provam mercado | **Aceito** | Meta sobe para 8 a 10 e inclui busca de **carta de intenção/piloto** (S12-T11, S12-T12) |
| "Pronto para vender" exige piloto real | **Aceito** | S12-T11 trata o acesso à máquina real como tarefa desde a semana 1 |
| 12 semanas não garantem produto pronto | **Aceito e explícito** | Alvo é **sistema demonstrável com dado real, três pilares 100% e métricas**; não "produto lançado" |

### 0.5 Trilhas e divisão sugerida (proposta, ajuste como quiser)

| Trilha | Foco | Sugestão de responsável | Fatias |
|---|---|---|---|
| **A · Core** | Contrato, segurança, front, decisão, gateway-núcleo, replicação | Paola (+ Ana no front) | S0 a S4, S13, S10 |
| **B · Hardware e enlaces** | Firmware, sensores, CAN, LoRa, mule, satélite, energia, soak | Giovana (+ Vinícius) | S8, S14, S17 (parte física) |
| **C · IA e dados** | Campanha, rig, modelos, MLOps, copiloto | Paola e Vinícius | S5, S15 |
| **D · Prescrição, produto e validação** | Playbooks, otimizador, entrevistas, demo, pitch | Ana e todos | S16, S12, S17 (produto) |

*(Divisão é sugestão baseada em quem já faz o quê; o roadmap funciona com qualquer arranjo.)*

### 0.6 Regra de corte (V4; **SUBSTITUÍDA pela seção 0-A.7 da V5**)

Se o tempo ou o orçamento apertar, corta-se **nesta ordem**, nunca de baixo para cima:

1. **P3 (executa só depois dos pilares):** S0-T4/T5/T6, S10-T9, S10-T7 (carga extra), S11-T4/T5/T7, S17-T10/T11, S3-T8/T10.
2. S11 inteira (UMM real) e S9-T4/T5 (custo e incidentes).
3. S17 (extras), exceto S17-T1 (risco térmico) e S17-T2 (redundância de sensor).
4. S15-T6 (autoencoder), S15-T16 (acústico), S14-T7 (satélite) **se o modem não chegar a tempo** (o pilar OFF-14 continua fechado por LoRa + relay + BLE).
5. **Nunca cortar:** S1, S2-T1/T2/T6, S3-T1/T3/T4/T5, S4-T3 a T5, S5-T2, S6-T5, S8-T1 a T6/T13, S13 inteira, S14-T2/T3/T5/T9, S15-T1 a T5/T9/T15, S16-T1 a T6/T9.

### 0.7 Compras críticas (lead time: pedir na semana 1)

| Item | Para quê | Tarefa |
|---|---|---|
| ESP32 DevKit (≥ 4) | nó, mule, gateway ESP-NOW, emissor de teste | S8-T10 |
| DS18B20 inox (≥ 4) e resistores 4,7 kΩ | temperatura real | S8-T1 |
| Termopar tipo K + MAX31855 (ou MAX6675) | superfície quente/rolamento | S17-T1 |
| MPU6050 (≥ 2) | vibração real | S8-T2 |
| Sensor hall/óptico + ímã | RPM real | S8-T11 |
| Módulo GPS | velocidade e posição | S8-T11 |
| DS3231 (≥ 2) | hora offline | S8-T3 |
| INA219 | medir consumo | S14-T10 |
| OLED + buzzer + LED | alarme local | S8-T13 |
| Transceptor CAN 3,3 V (ex.: SN65HVD230) ou módulo MCP2515 | CAN real | S8-T12 |
| 3 placas ESP32 com LoRa (SX1276/SX1262) + antenas | LoRa e relay | S14-T2 |
| Motor DC pequeno + bateria + massa/fita | rig de desbalanceamento | S15-T2 |
| Microfone I2S (INMP441) | acústico (opcional) | S15-T16 |
| Mini-PC ou Raspberry Pi (≥ 8 GB) + SSD | Gateway-Núcleo | S13-T1 |
| Modem satelital + plano **(confirmar preço, cobertura, mensagem máxima e disponibilidade no Brasil na hora da compra)** | satélite real | S14-T7 |
| Caixa, abraçadeira, bateria, painel solar | kit instalável e soak | S17-T4, S14-T10 |

*Preços e disponibilidade mudam: o roadmap **não** fixa valores. S8-T10 exige cotação real, data e fornecedor registrados em `docs/BOM.md`.*

---

## COMO LER ESTE ARQUIVO (leia antes de executar qualquer bloco)

1. **Este roadmap foi escrito para ser executado por um agente de código** (Claude Code, Cursor, Windsurf, Kilo, etc.) sem reinterpretação. Cada tarefa tem ID, contexto, arquivos prováveis, implementação, testes, critério de aceite e evidência. Se um agente ler só a tarefa `S3-T4`, ele deve conseguir executá-la.
2. **"Semana N" é uma fatia de execução ordenada por dependência.** Na V4 as fatias S0 a S17 rodam em **12 semanas de calendário com quatro pistas em paralelo** (seção 14.2). O marcador **[CORTE-BANCA]** e a **regra de corte** (seção 0.6) dizem o que sacrificar **sem tocar nos três pilares**.
3. **Toda tarefa só é "pronta" quando a evidência existe**, não quando a classe Python existe. Regra herdada do Ultimato e do Leviatã: "pronto" = fluxo completo testado + resultado demonstrável.
4. **Não existe tarefa de "melhorar backend/frontend/IA".** Tudo foi destrinchado em decisão, implementação, teste, métrica ou documento.
5. **Classificações usadas:** `IMPLEMENTADO`, `PARCIALMENTE_IMPLEMENTADO`, `PROTOTIPADO`, `APENAS_DOCUMENTADO`, `HIPÓTESE`, `CONTRADITÓRIO`, `OBSOLETO`, `NÃO_ENCONTRADO` (reconciliação) e `BUILD_NOW`, `PROTOTYPE_NOW`, `VALIDATE_NOW`, `ARCHITECT_NOW`, `DEFER`, `REJECT`, `UNKNOWN` (decisão de implementação).
6. **Camadas por fase:** FOUNDATION, ARCHITECTURE, IMPLEMENTATION, VALIDATION, OBSERVABILITY, SECURITY, TESTING, DOCUMENTATION, BUSINESS VALIDATION.

> **Aviso de honestidade sobre este próprio documento.** Eu (quem escreveu) auditei o código clonado, mas **não rodei** `manage.py test`, `docker compose up`, `npm run build` nem abri a UI. Onde digo "292 testes", é o número que vocês informaram; contei 298 declarações `def test_` por grep, o que **não** é o mesmo que testes executados e passando. A tarefa `S0-T1` existe justamente para transformar esses números em evidência reproduzível.

---

## 1. EXECUTIVE VERDICT

O FieldNode de hoje é **um backend de verdade com uma vitrine que ainda não mostra o backend**.

**O que existe de real e raro (comprovado por código, não por documento):**
- Contrato de identidade de telemetria com idempotência por `(device_id, message_id)`, `sequence_number`, `payload_hash`, `SyncCursor` (migrations 0014, `services/telemetria.py`, `models.SyncCursor`).
- Pipeline `RawTelemetry → CanonicalTelemetry` com `FabricanteMapping` versionado (migration 0024, `services/normalizacao.py`), com 2 fabricantes **simulados**.
- `Trust Score` por leitura e `MachineDataHealth` agregado (`services/data_health.py`, 344 linhas, migrations 0016 e 0017).
- `Event` com `priority_score` e `Decision` com máquina de estados e `outcome_texto` (`models.py`, `services/eventos.py`, `services/decisions.py`, `views_decisions.py`).
- `DeadLetterEntry` (`services/dlq.py`, migration 0021, 0022, 0025).
- Cliente de borda com outbox SQLite, prioridade A/B/C, cursor de ACK e `payload_hash` (`simulators/edge_client.py`, 404 linhas) e um simulador de Data Mule (`transbordo_mule_client.py`).
- Docker Compose com 5 serviços e healthchecks reais, Mosquitto **já com `allow_anonymous false`**, porta publicada só em `127.0.0.1`, gunicorn no lugar de `runserver`.

**O que está errado e é o motivo deste roadmap:**
1. **O diferencial é invisível.** `grep -riE 'decision|trust|priority|prioridade' frontend-next/src` retorna **zero arquivos**. Decision Memory, aprovação humana, Trust Score e priority score existem na API e não aparecem na tela. Para a banca, o FieldNode é "dashboard + mapa", exatamente igual ao outro grupo.
2. **Dado fake na tela.** `DashboardMachineData.tsx` importa `mockRpmSeries`, `mockTemperaturaSeries`, `mockVibracaoSeries` de `data/mockData.ts` (linhas 26 e 40-42). Um único gráfico inventado descoberto na demo derruba a honestidade que vocês construíram.
3. **Dois sistemas de severidade que se contradizem.** Backend: temperatura `> 85 °C` é `CRITICO` (`eventos.py:13`). Borda: prioridade A só acima de `110 °C`, B acima de `95 °C` (`edge_client.py:44-48`). Uma leitura de 90 °C gera evento crítico no servidor e sai como **prioridade C** na fila offline. É o bug mais perigoso para a tese central, porque o crítico espera atrás do rotineiro.
4. **A fórmula do Attention Engine pune dado ruim em vez de sinalizar.** `priority = severidade × impacto × urgência × confiança` (`eventos.py`). Sensor suspeito com leitura de 120 °C vira prioridade baixa. Evento grave com evidência fraca tem que continuar visível e marcado como "inconclusivo, verificar sensor".
5. **Hardware: zero.** Nenhum `.ino`, nenhum `platformio.ini`. Tudo que é "offline" é simulador Python. Sensor de vibração do projeto (SW-420) é um interruptor por limiar, **não mede amplitude**.
6. **Prescrição está em três lugares** (`services/prescricao.py` deprecado usando o modelo legado `Prescricao`, `ia/pipeline.py::analisar_maquina`, `views_prescricao.py` + `services/decisions.py`). O Leviatã manda consolidar antes de adicionar camadas.
7. **IA ainda não é defensável.** O professor já cobrou. Isolation Forest (IF) por máquina após 100 leituras, treinado com simulador, sem harness de avaliação, sem baseline por regime de operação, sem model card. O que dá para afirmar hoje é **detecção de anomalia não supervisionada em dado sintético**, não previsão de falha.
8. **Segurança de borda incompleta.** `RegisterView` é `AllowAny` e `DEFAULT_THROTTLE_CLASSES` é `[]` (só a ingestão tem throttle). Chave do Gemini viaja em query string (`agentic.py:96`, `explicacao_llm.py:72`). Swagger `public=True`. MQTT tem senha única, sem ACL por dispositivo/tópico.
9. **Higiene do repo.** `.next/trace` e `.kiro/settings/*` estão versionados mesmo com `.gitignore`. `api_tcc/api/page.tsx` (React dentro do pacote Python). `frontend-next/src/types/` com `FleetGrid.tsx`, `SkeletonGrid.tsx`, `page.tsx` e `telemetryService.ts` duplicados. Os documentos do v2 que a banca vai pedir (honestidade metodológica, protocolo de resiliência, pressure test, roteiro de demo) **não existem** em `docs/`.
10. **Nada de Motor de Consequência, Operational Graph ou Data Passport no código** (grep só acha uma menção "indisponivel_na_poc" em `agentic.py`).

**A frase estratégica:** o gargalo deixou de ser "construir mais backend". É **fechar o ciclo `leitura → confiança → evento → decisão → ação humana → resultado → aprendizado` e fazê-lo aparecer na tela, com hardware real e números medidos.** Offline, IA, mapa, calendário e chatbot servem a esse ciclo, não competem com ele.

**Veredito:** base promissora e mais séria que a média absoluta de TCC, **mas hoje o repositório diz mais do que a tela mostra, e a tela mostra uma coisa parcialmente falsa**. Corrigível. Este roadmap é a sequência de correção.

---

## 2. PROJECT DISCOVERY

### 2.1 Reconstrução do projeto (Fase 0 do Leviatã)

| Pergunta | Resposta honesta em 2026-10-24 |
|---|---|
| O que é? | Plataforma de telemetria e decisão de manutenção para colheitadeiras, com ingestão resiliente, qualidade de dado explícita e decisões rastreáveis |
| Qual problema? | Máquina agrícola em área sem sinal gera dado que chega tarde, sem contexto e sem ação associada. A parada custa caro (valores de R$ 5 a 15 mil/hora vêm da pesquisa do grupo e **não foram verificados em fonte primária**) |
| Para quem? | Usina de cana e frota agrícola mista. **Comprador, usuário e quem sente a dor são pessoas diferentes** e ainda não foram validados (seção 20) |
| Diferencial tecnológico pretendido | Offline resiliente + confiança de dado visível + decisão rastreável + (futuro) consequência operacional |
| Diferencial real hoje | Contrato de identidade idempotente, Trust Score, Decision Memory. **Todos invisíveis na UI** |
| Fluxo principal | Sensor → (HTTP ou MQTT) → `registrar_leitura` → Raw → Canonical → Trust Score → Event + priority → Decision (PENDENTE) → aprovação humana → outcome |
| Onde os dados nascem? | Hoje: `scripts/simular_mqtt.py`, `simulators/edge_client.py`, `esp_simulator_multi.py`. **Nunca em hardware físico** |
| Como entram? | `POST /api/telemetria/`, `POST /api/telemetria/lote/` (até 500 itens) e `mqtt_listen` (mesmo caminho `registrar_leitura`, o que é correto: validação e dedup únicas) |
| Como são processados? | `services/telemetria.py` (498 linhas): valida limites (`sensor_limits.py`), deduplica, grava, normaliza, calcula Trust Score |
| Onde são armazenados? | MySQL 8 em Compose, SQLite em teste e dev. `LeituraTelemetria` tem FK para `Machine` |
| Como viram informação? | `ia/pipeline.py`, `services/anomaly_detection.py` (IF por máquina), `services/eventos.py` |
| Como viram evento? | `Event` (5 tipos, 3 severidades, `priority_score`) |
| Como viram decisão? | `Decision` com `texto`, `acao_recomendada`, `confianca`, `status`, `decidido_por`, `outcome_texto` |
| Como viram prescrição? | **Texto curto** gerado por regras + opcionalmente explicado pelo Gemini. Não é ordem de serviço. |
| Como chegam ao usuário? | Next.js 15: dashboard, mapa, máquinas, operários, relatórios. **Sem decisões, sem trust, sem prioridade** |
| Onde há automação? | Validação, dedup, normalização, cálculo de score, criação de evento/decisão |
| Onde há intervenção humana? | `PATCH /api/decisions/<id>/` existe. **Nenhuma tela chama** |
| Onde há IA? | IF por máquina (real, mas não avaliado), z-score antes de 100 leituras, Gemini só para explicar |
| O que é comprovado? | Ingestão idempotente, normalização v0.1, DLQ, outbox simulado, decisões persistidas, testes de backend (a executar) |
| O que é hipótese? | Offline em campo, Data Mule físico, multi-marca real, previsão de falha, motor de consequência, "usina prefere painel unificado" |

### 2.2 PROJECT MASTER MAP

```text
SENSOR (simulado)           BORDA (simulada em Python)         NUVEM/SEDE (real, Docker)
-----------------           --------------------------         -------------------------
DS18B20? SW-420? RPM?       edge_client.py                      Mosquitto (senha, 127.0.0.1)
(nenhum físico)             outbox SQLite A/B/C                   |
        |                   cursor last_acked_sequence            v
        +-----------------> payload_hash sha256 ---HTTP/MQTT--> mqtt_listen (worker)
                            transbordo_mule_client.py               |
                            (mule simulado)                         v
                                                              registrar_leitura()
                                                                |  valida limites
                                                                |  dedup (device,message)
                                                                |  Raw -> Canonical
                                                                |  Trust Score
                                                                v
                                                  LeituraTelemetria --FK--> Machine
                                                                |
                                          +---------------------+----------------------+
                                          v                     v                      v
                                      Event+priority      IF por máquina         DLQ (falhas)
                                          |                (anomaly_detection)
                                          v
                                      Decision (PENDENTE) <-- Gemini (só texto)
                                          |
                                          v   PATCH /api/decisions/<id>/   (SEM TELA)
                                  APROVADA/REJEITADA/EXECUTADA + outcome_texto
                                          |
                                          v
                              Next.js (dashboard, mapa...)  <-- NÃO LÊ decisions/trust/priority
                                         + mockData.ts (sparklines falsas)
```

---

## 3. CURRENT STATE · REALITY CHECK

| Domínio | Estado atual | Evidência (arquivo) | Problemas | Maturidade | Próxima evolução necessária |
|---|---|---|---|---|---|
| Ingestão | Funcional, idempotente | `services/telemetria.py`, `views_ingestao.py` (886 linhas), `IngestaoLoteView` | `views_ingestao.py` com 886 linhas acumula responsabilidades; sem backpressure; lote item a item | 7/10 | Dividir view, definir backpressure e limite de payload, métricas |
| Identidade/contrato | Forte | migration 0014, `SyncCursor`, `docs/CONTRATO_TELEMETRIA_V1.md` | Sem `boot_id`/`time_source`: ESP32 sem RTC não tem hora confiável | 7/10 | Estender contrato (S1) |
| Normalização | Fundação v0.1 | `normalizacao.py` (56 linhas), `FabricanteMapping` | 2 fabricantes **inventados**; sem J1939 real; sem proveniência medido/calculado/estimado/simulado | 4/10 | Adaptador J1939 público (S11) |
| Trust Score | Real e testado | `data_health.py`, `MachineDataHealth`, `/api/machines/<id>/health/` | Não aparece no front; explicação legível não padronizada; sem drift de sensor | 6/10 | Expor no front, explicar fatores (S3) |
| Eventos/prioridade | Funcional | `eventos.py` | Severidade conflita com a borda; confiança multiplica prioridade; pesos de impacto fixos | 5/10 | Contrato único + separar severidade/evidência (S1) |
| Decisões | Persistidas | `decisions.py`, `views_decisions.py` | Sem UI; sem `WorkOrder`; `outcome_texto` livre; sem evidência estruturada | 5/10 | Estruturar + UI + OS (S3, S4) |
| Prescrição | **3 implementações** | `services/prescricao.py` (deprecado), `ia/pipeline.py`, `views_prescricao.py` | Duplicação, modelo legado `Prescricao` ainda existe | 3/10 | Consolidar em Decision (S4) |
| IA anomalia | Real, não avaliada | `anomaly_detection.py`, `model_registry.py`, `deteccao_multivariada.py` | Dois detectores concorrentes (`ia/deteccao_multivariada.py` vs `services/anomaly_detection.py`); treino com simulador; sem baseline por regime; sem métricas | 4/10 | Harness + regime + model card (S5) |
| LLM | Auxiliar, correto | `explicacao_llm.py`, `agentic.py`, `prompts/agentic_decision_v1.txt` | Chave em query string; sem guardrail de evidência citada; `operation_graph` indisponível | 5/10 | Header + guardrails (S2, S5) |
| Offline (software) | Outbox + cursor | `edge_client.py`, `teste_resiliencia.py` (413 linhas) | **Resultados nunca publicados**; sem política de disco cheio; sem TTL/compressão | 5/10 | Provar com métrica (S6) |
| Offline (front) | Service Worker | `public/sw.js` | `syncTelemetriaData` lança em qualquer não-2xx: um 400 permanente **trava a fila inteira** (head-of-line blocking) | 4/10 | Estados de erro por item (S1) |
| Data Mule | Simulador | `transbordo_mule_client.py`, `test_data_mule_integration.py` | Transporte não existe; não comprova alcance | 3/10 | Transporte físico (S7, S8) |
| Hardware | **Inexistente** | nenhum `.ino` | Todo o discurso de campo é simulado | 0/10 | Firmware (S8) |
| Autenticação | Token DRF com TTL | `authentication.py`, `views_auth.py`, `TOKEN_TTL_HOURS` | `RegisterView` `AllowAny` sem throttle; sem lockout de login | 4/10 | Throttle + flag (S2) |
| Autorização/tenant | Parcial | `Organization`, `Membership`, `permissions.py` | **Isolamento entre organizações sem teste cruzado dedicado** (existe `test_permissions.py`; conferir cobertura) | 4/10 | Testes de acesso cruzado (S2) |
| MQTT | Autenticado, sem ACL | `mosquitto.conf` | Usuário único; sem ACL por tópico; sem TLS | 5/10 | ACL por dispositivo (S2) |
| Segredos | Melhorou | `.env.example`, `decouple` | Chave Gemini em URL; token no `localStorage` (dívida declarada) | 5/10 | Header + cookie HttpOnly (S2) |
| Frontend | Bonito, desconectado | `frontend-next/src` | Mocks; sem decisões/trust/priority; duplicatas em `src/types` | 4/10 | Integração (S3) |
| Observabilidade | Básica | `middleware.py` (correlation ID), `test_json_logging.py`, `/api/health/` | Sem métricas, sem tracing, sem métrica de backlog offline | 4/10 | Prometheus + painéis (S10) |
| DevOps | Compose bom | `docker-compose.yml`, `Dockerfile` | Sem CI, sem backup/restore testado, sem rollback | 5/10 | CI + backup (S10) |
| Testes | Extenso | `api_tcc/tests/*` (24 arquivos), `simulators/test_*` | Número não verificado; front só tem scripts Playwright soltos; sem E2E integrado em CI | 6/10 | CI (S10) |
| Documentação | Parcial | `docs/*` (9 arquivos), `README.md` | Faltam os 8 documentos que o v2 prometeu; README vende "dashboard + IA" | 4/10 | Recuperar e escrever (S0, S12) |
| Repo | Sujo | `git ls-files` | `.next/trace`, `.kiro/`, `api/page.tsx`, `src/types/*` duplicados, histórico squashado | 3/10 | Higiene (S0) |

---

## 4. DOCUMENT × GITHUB RECONCILIATION

| Afirmação (origem) | Classificação | Evidência / ausência |
|---|---|---|
| "Ingestão idempotente por `(device, message)`" (v2, S1-T5) | **IMPLEMENTADO** | migration 0014, `services/telemetria.py`, `test_identity_contract.py` |
| "Trust Score visível ao usuário" (Ultimato 2.6 item 3, pitch) | **PARCIALMENTE_IMPLEMENTADO** | Backend sim, front não: zero ocorrência de `trust` em `frontend-next/src` |
| "Prioridade nos eventos / fila de atenção" (Ultimato 1.1) | **PARCIALMENTE_IMPLEMENTADO** | `priority_score` no modelo e na API; invisível no front |
| "Decision Memory com aprovação humana" (v2 S4) | **PARCIALMENTE_IMPLEMENTADO** | API completa; **nenhuma tela** |
| "Mosquitto aberto, `allow_anonymous true`" (Ultimato 1.1) | **OBSOLETO** | `mosquitto.conf` hoje: `allow_anonymous false` + `password_file`. Ultimato 2.1 já dizia o contrário: **contradição entre os blocos 1.1 e 2.1, resolvida pelo código a favor de 2.1** |
| "MQTT não checa credencial" (Ultimato 1.1) | **PARCIALMENTE_IMPLEMENTADO** | `mqtt_listen.py:115-118` usa `MQTT_USERNAME/PASSWORD` **se** existirem; se ausentes, conecta sem. Credencial é opcional no worker |
| "API key no front" (Ultimato 1.1) | **OBSOLETO** | Sem `API_KEY` em `frontend-next/src` |
| "Service Worker apaga 400/401 sem recuperação" (Ultimato 2.1) | **OBSOLETO, MAS COM BUG NOVO** | `shouldRetryStatus` só enfileira 408/429/5xx; `syncTelemetriaData` só apaga em 2xx e **lança erro no resto**, interrompendo o laço: poison message trava a fila |
| "Prioridade da borda contradiz o motor" (Ultimato 2.1) | **CONFIRMADO** | `edge_client.py:44-48` (110/95) vs `eventos.py:13` (85) |
| "Confiança multiplica e rebaixa prioridade" (Ultimato 2.1) | **CONFIRMADO** | `calcular_priority_score` |
| "Sparklines mock" (Ultimato 1.1, 2.1) | **CONFIRMADO** | `DashboardMachineData.tsx` |
| "Rate limit no login/registro" (Ultimato 1.1, 2.4) | **CONFIRMADO COMO AUSENTE** | `DEFAULT_THROTTLE_CLASSES: []`, `IngestaoThrottle` usado só em 2 views |
| "Gemini key em query string" (Ultimato 1.1) | **CONFIRMADO** | `agentic.py:96`, `explicacao_llm.py:72` |
| "Lixo versionado `.next/`, `.kiro/`" (Ultimato 1.1) | **CONFIRMADO** | `git ls-files` ainda lista `.next/trace` e `.kiro/settings/*` |
| "`api_tcc/api/page.tsx` e `src/types/*` duplicados" (Ultimato 1.1) | **CONFIRMADO** | arquivos presentes |
| "`AGENTS.md` fala em SaaS B2B high-ticket" (Ultimato 1.1) | **PARCIALMENTE_VERDADEIRO** | O arquivo é um **contrato operacional para agentes** (legítimo e útil para este roadmap). O problema é só o tom de marketing na vista do recrutador |
| "Docs do v2 sumiram" (Ultimato 1.1) | **CONFIRMADO** | `docs/` tem 9 arquivos; **faltam** honestidade metodológica, protocolo de resiliência, roteiro de demo, pressure test, deploy, observabilidade, dataset rotulado |
| "Motor de consequência" (Ultimato 1.1, 2.4) | **NÃO_ENCONTRADO** | Zero código. Era hipótese, continua hipótese |
| "Operational Graph" (v2 S10) | **NÃO_ENCONTRADO** | idem. `agentic.py` declara `indisponivel_na_poc` |
| "Data Passport" (v2 S10) | **NÃO_ENCONTRADO** | idem |
| "Firmware ESP32 / ESP-NOW / LoRa" (Proposta TCC v4) | **NÃO_ENCONTRADO** | Sem `.ino`/PlatformIO. Proposta TCC afirma ESP-NOW como entregue na banca |
| "Buffer de 30 dias" (Proposta TCC v4, CM100 da Case) | **APENAS_DOCUMENTADO** | Sem cálculo de capacidade, sem política de disco cheio |
| "Isolation Forest por máquina" (README, pitch) | **IMPLEMENTADO, NÃO AVALIADO** | `anomaly_detection.py`; sem harness, sem métricas |
| "Random Forest para risco/RUL" (Proposta TCC v4) | **CONTRADITÓRIO** | `requirements.txt` tem scikit-learn mas não há RF supervisionado com rótulo real; a proposta afirma como entregue |
| "292 testes passando" (Ultimato 1.1, informado) | **UNKNOWN** | Grep: 298 declarações `def test_`. Execução não verificada por mim |
| "Chatbot / ChatFAB" (pitch) | **PROTOTIPADO** | `ChatFAB.tsx` existe; conferir se está ligado a function calling real (S5-T8) |
| "Multi-tenancy" | **PARCIALMENTE_IMPLEMENTADO** | `Organization`, `Membership`, `Machine.organization`. Isolamento total sem prova |
| "Deploy público" | **NÃO_ENCONTRADO** | Só Compose local |
| "Dedup silenciosa buggy" (overview memória) | **OBSOLETO** | Corrigido por contrato composto; coberto por `test_identity_contract.py`/`test_concurrency.py` |
| "Cálculo de 30–40% sem sinal (ANATEL 2023), R$ 5–15 mil/h (Embrapa 2022), 40% da frota com +15 anos (ANFAVEA 2023)" | **HIPÓTESE (fonte não verificada)** | Vêm da pesquisa do grupo. Ver decisão D-14 |

### 4.1 Contradições entre blocos do Ultimato (não escondidas)

| Contradição | Blocos | Resolução neste roadmap |
|---|---|---|
| Mosquitto aberto vs exige senha | 1.1 vs 2.1 | Código atual: exige senha. Tarefa remanescente é **ACL por dispositivo** (S2-T1) |
| Calendário: construir interno vs integrar Google/Outlook | 1.7 (interno primeiro) vs 2.4 (integrar, não construir) | **Interno primeiro** (`WorkOrder` + visão agenda) e `.ics` exportável; Google/Outlook como adaptador depois (D-09) |
| Cortar chatbot vs manter tudo | 1.7/2.8 vs prompt do Leviatã ("não reduza ambição") | Mantém tudo no roadmap, **com estado explícito** (BUILD/DEFER). Chatbot é `DEFER` até Decision Memory ter volume, mas o function calling controlado entra como S5-T8 |
| "LoRa mesh" como solução vs "não anunciar LoRa" | 2.4/2.8 vs 1.7 | LoRa fica em `ARCHITECT_NOW` + `VALIDATE_NOW` com hardware (S7-T5); **não anunciar antes de teste físico** |
| Notebook como gateway (hotspot) vs QR para deploy | 1.1 vs plano de demo da memória | **Notebook é o gateway**; cloud é destino do sync (S12-T3) |

---

## 5. CURRENT ARCHITECTURE

```text
                        frontend-next (Next.js 15, :3000)
                           | proxy /api/[...path]/route.ts
                           v
       +---------------- Django 5.2 + DRF (gunicorn :8000) -----------------+
       |  setup/urls -> api_tcc/urls                                         |
       |  auth/*  telemetria/  telemetria/lote/  anomalias/  events/         |
       |  decisions/  prescricoes/*  relatorio/*  machines/<id>/health/      |
       |  dlq/  health/  status-mqtt/  maquinas/posicao/  swagger (public)   |
       |                                                                     |
       |  services/: telemetria, data_health, eventos, decisions,            |
       |             normalizacao, anomaly_detection, agentic, dlq, relatorios|
       |  ia/: pipeline, model_registry, deteccao_multivariada, worker       |
       +------------------------+--------------------------------------------+
                                | ORM
                          MySQL 8 (db)               mqtt_listen (worker)
                                                          ^
                                          Mosquitto (:1883, 127.0.0.1, senha)
                                                          ^
                    simulators/edge_client.py (outbox SQLite) / scripts/simular_mqtt.py
```

**Fronteiras de confiança hoje:**
- Navegador → API: token DRF (TTL 24h), CORS por allowlist, `IsAuthenticatedOrReadOnly` global, `IsAuthenticatedOrPublicDemo` em leituras.
- Dispositivo → API: `HasIngestionCredential` (chave de ingestão) + `IngestaoThrottle` por `maquina_id`.
- Dispositivo → MQTT: **usuário único** compartilhado; sem ACL.
- Worker → banco: confiança total.
- Servidor → Gemini: chave em query string.

**Fronteiras de dados hoje:** `Organization`/`Membership`/`Machine.organization` existem; **nenhuma prova automatizada de que o usuário da organização A não alcança a máquina da organização B em todos os endpoints** (a tarefa S2-T6 cria essa prova).

**O que sobrevive sem internet (hoje):** nada além do próprio notebook com Docker. **Não existe gateway embarcado.** O "gateway" da demo é notebook + hotspot.


---

## 6. TARGET ARCHITECTURE

```text
 CAMPO (sobrevive sem internet)                                   SEDE / NUVEM (conectada)
 ------------------------------                                   ------------------------
 [Sensores reais]  DS18B20 + MPU6050/ADXL345 + RPM (hall) + GPS + RTC DS3231
        |  (ou CAN J1939 via MCP2515, bancada)
        v
 [EDGE NODE  ESP32 #1]  firmware C++ versionado
   - boot_id + contador monotônico + time_source (rtc|gateway|unsynced)
   - triagem local: classe A/B/C com CONTRATO ÚNICO DE SEVERIDADE
   - outbox em flash (LittleFS) com política de disco cheio
        |  ESP-NOW (curto alcance)  /  Wi-Fi  /  LoRa (validar)
        v
 [GATEWAY DE CAMPO]  notebook/mini-PC (demo) -> ESP32 #2 / Raspberry (produto)
   - broker MQTT local (Mosquitto com ACL por dispositivo)
   - Connectivity Manager (ConnectivityProvider: wifi | 4g | mule | lora | sat)
   - Sync Protocol v1 (ACK cumulativo, cursor, checksum, TTL, compressão)
   - dashboard local (Next.js standalone) acessível via hotspot
        |  uplink quando existir / Data Mule (transbordo carrega o buffer)
        v
 [INGESTÃO]  registrar_leitura(): contrato -> dedup -> Raw -> Canonical -> Trust
        |                         falha -> DLQ (com contexto)
        v
 [Machine canônica] --FK-- Telemetry --> [Event Engine] -- severidade (fato) + evidência (qualidade) separadas
        |                                        |
        |                                        v
        |                               [Operation Graph v0.1]  Machine, Transbordo, Caminhão, Frente, Site
        |                                        |
        |                                        v
        |                               [Consequence Engine v0.1]  impacto, horizonte, ativos afetados
        |                                        |
        v                                        v
 [Attention Engine]  P1/P2/P3 + "inconclusivo" quando evidência fraca
        |
        v
 [Decision Engine]  regras determinísticas + IF contextual -> Decision estruturada
        |                  (LLM só redige/explica, nunca decide)
        v
 [Human-in-the-loop] aprovar | rejeitar | adiar -> [WorkOrder] -> responsável -> prazo -> .ics/webhook
        |
        v
 [Outcome] resultado + reavaliação por telemetria posterior
        |
        v
 [Operational Decision Memory] --> rótulo fraco --> avaliação de regras/modelos (futuro supervisionado)
        |
        v
 [API multi-tenant + RBAC] --> [Command Center Next.js]  [Relatórios/XLSX]  [Data Passport export]
```

**Onde cada responsabilidade mora (V3, SUPERADA pela seção 6.1 da V4):**

| Responsabilidade | Mora em | Sobrevive offline? |
|---|---|---|
| Captura, carimbo de tempo, triagem A/B/C, outbox | Edge node (firmware) | **Sim** |
| Alerta local imediato (limiar de segurança) | Edge node/gateway, regra determinística | **Sim** |
| Dashboard local e broker | Gateway de campo | **Sim** |
| Roteamento de canal e protocolo de sync | Gateway (Connectivity Manager) | **Sim** |
| Dedup final, normalização, Trust Score, Event, Decision | Ingestão (sede/nuvem) | Não |
| IF por máquina | Sede (treino) e opcionalmente gateway (inferência com modelo exportado) | Inferência sim, treino não |
| Operation Graph e consequência | Sede | Não (v0.1); regra simplificada no gateway = `ARCHITECT_NOW` |
| LLM | Sede, assíncrono, nunca no caminho crítico | Não |

**Componentes que precisam ser desacoplados:** (a) ingestão vs IA (falha do Gemini/IF jamais bloqueia recebimento: já parcialmente feito com `ia/worker.py`, validar); (b) prioridade de transmissão vs severidade operacional (têm que **ler a mesma tabela**, mas são conceitos distintos); (c) front vs regras de negócio (nenhuma restrição só no front).


### 6.1 ARQUITETURA-ALVO V4: GATEWAY-NÚCLEO (substitui a tabela "Onde cada responsabilidade mora" da V3)

```text
 MÁQUINA (até 14 dias sem internet)                  GATEWAY-NÚCLEO (campo)                     CENTRAL (sede/nuvem)
 -----------------------------------                 ----------------------                     --------------------
 [NÓ ESP32]                                          mini-PC / Raspberry (perfil edge)          réplica + multi-gateway
  sensores reais (DS18B20, K, MPU6050,               ┌──────────────────────────────┐           ┌──────────────────┐
  hall, GPS, RTC, mic opcional)                      │ Mosquitto (ACL por device)   │           │ MySQL (réplica)  │
  triagem EWMA/CUSUM + regras do contrato            │ mqtt_listen / ingestão       │           │ Django (mesmo    │
  ALARME LOCAL (LED, buzzer, OLED)                   │ Raw→Canonical→Trust          │           │ código, role=    │
  prescrição curta por código no display             │ Event + Incident             │           │ cloud)           │
  outbox em flash (LittleFS, CRC, A/B/C)             │ IA local (IF/resíduo/ONNX)   │           │ modelos treinados│
        │                                            │ Decision + Prescrição v2     │           │ + MLOps          │
        │ enlaces (em ordem de preferência):         │ WorkOrder + checklist + OS   │           │ painel executivo │
        ├─ ESP-NOW / Wi-Fi ───────────────────────►  │ PWA operador (hotspot)       │           └────────▲─────────┘
        ├─ LoRa ─────────────────────────────────►   │ Login offline, auditoria     │                    │ replicação
        ├─ Relay no transbordo (LoRa/ESP-NOW) ───►   │ Copiloto (RAG + LLM local)   │                    │ bidirecional
        ├─ Celular do operador (BLE) ────────────►   │ Otimizador de janela (CP-SAT)│ ◄──────────────────┘ (SyncCursor + HLC)
        └─ Satélite (só classe A) ───────────────────────────────────────────────────────────────────►  chega direto à central
                                                     └──────────────────────────────┘
                                                      banco local persistente (volume)
```

| Responsabilidade | Mora em | Sobrevive sem internet? |
|---|---|---|
| Captura, carimbo, triagem A/B/C, **alarme local**, outbox | Nó (firmware) | **Sim** |
| Alerta local imediato (limiar de segurança, EWMA/CUSUM) | Nó | **Sim** |
| Broker, ingestão, normalização, Trust Score | **Gateway-Núcleo** | **Sim** |
| Evento, incidente, consequência | **Gateway-Núcleo** | **Sim** |
| **Inferência de ML** (IF, resíduo, ONNX) | **Gateway-Núcleo** (modelo treinado na central/campanha e distribuído) | **Sim** |
| **Decisão, prescrição, aprovação, OS, checklist, estoque, otimizador** | **Gateway-Núcleo** | **Sim** |
| Login, permissões, auditoria | **Gateway-Núcleo** (usuários replicados) | **Sim** |
| App do operador (PWA, mapa offline) | Gateway via hotspot | **Sim** |
| Copiloto (RAG + LLM local) | Gateway (opcional, fora do caminho crítico) | **Sim**, se o hardware suportar (S15-T13) |
| Treino e retreino de modelos pesados, multi-gateway, executivo | Central | Não (precisa de conexão para sincronizar) |
| LLM em nuvem (Gemini) | Central/gateway com internet | Não; opcional |

**Autoridade de dados:** o que nasce no gateway **pertence** ao gateway (Event, Decision, WorkOrder, Outcome). Edição vinda da central entra como `Proposal` e o gateway decide. Telemetria é append-only (sem conflito). Detalhes em S13-T4 a T6.

**Máquina fora do alcance de qualquer gateway:** o nó continua autônomo (alarme local + flash) e usa os enlaces da lista; o gateway-núcleo pode ser **móvel** (Raspberry no transbordo, S13-T9) para que a decisão nasça perto da máquina.


---

## 7. STRATEGIC THESIS

**Núcleo defensável (em ordem de força):**
1. **Telemetria resiliente com identidade preservada.** Não "funciona offline" (commodity). É: *integridade operacional preservada apesar de conectividade intermitente*, medida por perda, duplicidade, atraso e recuperação.
2. **Confiança operacional explícita.** O sistema sabe e diz quando não deve confiar no sensor. A pesquisa do grupo não encontrou isso exposto ao usuário nas três grandes (**"não achei evidência pública" ≠ "elas não têm"**; é assim que se fala a um investidor).
3. **Decisão rastreável com desfecho.** Evidência → recomendação → aprovação → ordem de serviço → resultado. Esse ativo vira dataset real com o tempo.

**Commodity (não gastar energia de diferenciação):** dashboard com gráfico, mapa, CRUD, alerta por limiar.

**Copiável fácil:** IF genérico, thresholds fixos, Trust Score heurístico isolado, texto de prescrição.

**Moat possível, se validado (hoje NÃO existe):** histórico de decisões com desfecho confirmado, de frota mista, portátil entre OEMs. Só nasce com dados reais e tempo.

**Parte que existe só porque é tecnicamente interessante:** CRDT, vector clock, digital twin, satélite, LLM local no ESP32 (ver seção 24).

**Hipótese que precisa ser validada ANTES de escalar:** uma usina com frota mista sente dor suficiente na fragmentação de portais e na falta de visibilidade em área sem sinal para testar (ou pagar por) um painel independente. **É validação comercial, não técnica** (seção 20).

**Mudança de tese em uma frase** (herdada do Ultimato 2.4, ajustada pela honestidade do 1.7): de "IA que prevê falha" e "offline store-and-forward" para
> **"telemetria resiliente, com dado auditável e decisão rastreável, que mantém a operação visível quando a conectividade falha."**

**O Universal Machine Model cria independência de OEM ou desloca a complexidade para adaptadores?** Resposta honesta: **desloca**. Cada fabricante vira um adaptador que precisa de acesso autorizado, documentação de PGN/SPN e testes. O ganho real não é "fim do vendor lock-in", é **(a)** um contrato canônico único para todo o resto do sistema (Trust, Event, Decision não mudam por fabricante) e **(b)** custo marginal de adicionar uma marca limitado ao adaptador. J1939 padronizado reduz o custo, ISO 15143-3 (AEMP 2.0) cobre integração via API de telemática quando o OEM expõe, e ambos exigem teste por modelo. Não prometer "multi-marca completo".

**O Data Passport é moat ou exportação sofisticada?** Hoje, **exportação sofisticada**. Vira moat só se o histórico normalizado e rastreável for mais valioso que o do OEM, o que depende de volume e de a decisão com desfecho existir. Estado: `PROTOTYPE_NOW` (S11-T6), sem pretensão de moat.

---

## 8. MAJOR RISKS

| Categoria | Maior risco | Sev. | Mitigação (tarefa) |
|---|---|---|---|
| **Técnico** | Contrato de severidade duplicado faz alerta crítico sair com prioridade C | Crítica | S1-T1, S1-T2 |
| **Produto** | Front não mostra o diferencial; banca vê "mais um dashboard" | Crítica | S3 inteira |
| **Comercial** | Zero validação com comprador/usuário real; hipótese "painel unificado" não testada | Alta | S12-T4 a S12-T6 |
| **Dados** | Sensor/relógio incorreto contaminando treino e decisão; ESP32 sem hora | Alta | S1-T5, S5-T3, S8-T3 |
| **ML** | Alegar "previsão de falha" com dado sintético; professor já cobrou | Crítica | S5 inteira, S0-T3 |
| **Conectividade** | Prometer alcance de km sem rádio/mesh físico validado | Alta | S7-T5, S8-T6, D-04 |
| **Hardware** | Nenhum firmware; SW-420 não mede vibração; demo depende de hardware que não existe | Alta | S8 inteira |
| **Escalabilidade** | `views_ingestao.py` com 886 linhas; lote item a item; IF em memória por processo | Média | S1-T7, S10-T7 |
| **Segurança** | Registro aberto sem throttle, MQTT sem ACL, chave em URL, tenant sem prova | Alta | S2 inteira |
| **Processo** | Roadmaps v1 e v2 citavam pendência em tabela sem dono. Documentos sumiram | Média | Regra desta versão: toda pendência vira tarefa com ID ou `DEFER` na seção 24 |
| **Narrativa** | Números de impacto sem fonte primária no pitch (nota 5,5 de outra IA pedia para tirar disclaimers) | Alta | D-14, S12-T7 |

**Premissa que, se estiver errada, invalida parte grande do roadmap:** "Frota mista e conectividade intermitente são a dor". Se as 5 a 6 entrevistas mostrarem que a dor real é só **ordem de serviço manual** (digitação), o roadmap mantém S1 a S6 e rebalanceia S7 a S11 (ver seção 23).

---

## 9. TECHNICAL DEBT (mapa, classificado como **erro real** / **débito** / **evolução futura**)

| Item | Arquivo | Classe | Tarefa |
|---|---|---|---|
| Prioridade da borda ≠ severidade do backend | `edge_client.py`, `eventos.py` | **Erro real** | S1-T1/T2 |
| `syncTelemetriaData` lança e para a fila inteira | `public/sw.js` | **Erro real** | S1-T4 |
| Confiança multiplica prioridade | `eventos.py::calcular_priority_score` | **Erro real** (decisão de produto) | S1-T3 |
| Sparklines mock com fallback silencioso | `DashboardMachineData.tsx`, `mockData.ts` | **Erro real** | S3-T1 |
| Chave Gemini em query string | `agentic.py:96`, `explicacao_llm.py:72` | **Erro real** (baixo) | S2-T4 |
| Registro aberto, sem throttle global | `views_auth.py`, `settings.py` | **Erro real** | S2-T2 |
| `.next/trace`, `.kiro/` versionados | git | **Erro real** | S0-T2 |
| `api_tcc/api/page.tsx` | backend | **Erro real** | S0-T2 |
| Duplicatas em `frontend-next/src/types/` | front | **Erro real** | S0-T2 |
| 3 implementações de prescrição | `services/prescricao.py`, `ia/pipeline.py`, `views_prescricao.py` | **Débito** | S4-T1 |
| Modelo legado `Prescricao` ainda no schema | `models.py:551` | **Débito** | S4-T1 |
| 2 detectores de anomalia concorrentes | `ia/deteccao_multivariada.py` (modelo global `.pkl`) vs `services/anomaly_detection.py` (por máquina) | **Débito** | S5-T1 |
| `views_ingestao.py` com 886 linhas | backend | **Débito** | S1-T7 |
| `views_relatorio.py` (229) + `services/relatorios.py` (326): conferir limite de 300 linhas do `CLAUDE.md` | backend | **Débito** | S1-T7 |
| `api_tcc/api/views.py` e `api_tcc/views.py` coexistem | backend | **Débito** (verificar) | S0-T2 |
| Comandos duplicados `treinar_modelo_anomalia`/`treinar_isolation_forest`, `criar_prescricoes_simples/_teste`, `populate_db/popular_tudo` | `management/commands/` | **Débito** | S0-T2 |
| Token em `localStorage` | front | **Débito declarado** | S2-T5 |
| `Swagger public=True` em qualquer ambiente | `setup/urls.py:23` | **Débito** | S2-T3 |
| Rotas com e sem barra (`auth/login/` e `auth/login`) | `api_tcc/urls.py` | **Débito** (cosmético) | S2-T7 |
| `scripts/` com 6 variações de teste/carga | `scripts/` | **Débito** | S10-T7 |
| Histórico git squashado | repo | **Débito de narrativa** | D-13 |
| Previsão de vida útil (RUL), LSTM, digital twin | n/a | **Evolução futura** | seção 24 |

---

## 10. PRODUCT / COMMERCIAL RISKS

- **Comprador ≠ usuário ≠ quem sente a dor.** Gerente de manutenção sente a dor, gestor de frota compra, operador usa. O roadmap v2 tinha 3 entrevistas genéricas. Esta versão exige **5 a 6, por papel**, com roteiro que não pergunta "você usaria?" (S12-T4).
- **Switching cost não estimado.** A pergunta "por que não usar Solinftec/John Deere/Case IH?" tem resposta honesta hoje: *na telemetria básica eles estão à frente*. A resposta só vira argumento se a validação mostrar (i) frota mista, (ii) trecho sem sinal sem visibilidade, (iii) ordem de serviço manual. Sem isso, é inverdade.
- **Pricing não lastreado.** O kit (R$ 350 a 500) e a assinatura (a partir de R$ 99) são **hipótese de precificação**. O professor mandou **não falar de finanças no pitch**: respeitar. Mantém no documento como hipótese interna.
- **Featuritis.** A lista de hipóteses (satélite, digital twin, mesh) é maior que a capacidade de qualquer equipe de 4 pessoas. O mecanismo contra isso é a seção 24 e o "estado" de cada iniciativa.
- **Concorrência de equipe com ideia quase igual.** O diferencial **não pode** ser "sensor + dashboard". Só é diferencial o que aparece na tela e é medido: confiança do dado, fila de atenção com prioridade, decisão com desfecho, ressincronização provada, hardware real.
- **Sensor insuficiente para prever falha.** Temperatura, vibração binária e RPM não bastam. Sem exemplo de falha rotulado, ninguém prevê falha. O que se promete é **detecção precoce e tempo até o limite**, não "vai quebrar" (seção 7 e S5).

---

## 11. TECHNOLOGY OPPORTUNITY MAP (hipóteses estratégicas, não verdades)

Para cada tecnologia avançada: **problema que resolve · evidência · pré-requisito · valor operacional · complexidade · alternativa mais simples · estado.**

| Iniciativa | Problema | Evidência hoje | Pré-requisito | Alternativa mais simples | **Estado** |
|---|---|---|---|---|---|
| Contrato único de severidade/prioridade | Crítico sai com prioridade C | Bug confirmado | nenhum | n/a | **BUILD_NOW** |
| Front ligado ao motor (decisões, trust, prioridade) | Diferencial invisível | grep zero | S1 | n/a | **BUILD_NOW** |
| Sync Protocol v1 documentado e medido | "offline" sem número | `teste_resiliencia.py` sem resultado | S1 | só `lote/` | **BUILD_NOW** |
| Harness de avaliação do IF | "IA" sem métrica | professor cobrou | S1 | só regras | **BUILD_NOW** |
| `WorkOrder` + `.ics` + webhook | Prescrição é texto curto | caso de MS: digitação manual | S3 | só texto | **BUILD_NOW** |
| Firmware ESP32 + DS18B20 + MQTT | Zero hardware | nenhum `.ino` | S2 (MQTT ACL) | simulador | **BUILD_NOW** |
| Acelerômetro (MPU6050) com RMS/pico/curtose | SW-420 é binário | datasheet | S8-T1 | manter binário e dizer | **PROTOTYPE_NOW** |
| Leitura CAN/J1939 via MCP2515 (bancada) | Sensores externos são pobres | pesquisa do grupo | S8, acesso a banco de teste/simulador J1939 | OBD-II/PIDs | **PROTOTYPE_NOW** |
| Operation Graph v0.1 + Consequence Engine v0.1 | Alerta isolado não diz impacto | nada no código | S1, S4 | regra textual | **PROTOTYPE_NOW** |
| Connectivity Manager (interface + 2 providers) | Escolha de canal ad hoc | `edge_client` só HTTP | S6 | `if/else` | **PROTOTYPE_NOW** |
| Data Mule físico (ESP-NOW/Wi-Fi entre dois ESP32) | Simulador não prova transporte | `transbordo_mule_client.py` | S8 | notebook como mule | **VALIDATE_NOW** |
| LoRa ponto-a-ponto (bancada) | Alcance km sem 4G | pesquisa; zero teste | S8 | ESP-NOW | **VALIDATE_NOW** |
| Normalizador J1939 público (PGN/SPN) | "multi-marca" é simulado | `FabricanteMapping` com 2 fabricantes inventados | S8-T7 | manter simulado e dizer | **PROTOTYPE_NOW** |
| Adaptador ISO 15143-3 (AEMP) | Integração via API de OEM | nenhum | acesso a sandbox | n/a | **ARCHITECT_NOW** |
| Data Passport (export portátil) | Lock-in dos OEMs | nenhum | S11 | CSV | **PROTOTYPE_NOW** |
| IF por máquina com baseline por regime | Comparar parada com trabalho | só features brutas | regime como dado (S5-T3) | regras por regime | **BUILD_NOW** |
| LSTM autoencoder | "IA mais forte" | nenhuma | dataset rotulado | IF | **DEFER** |
| SHAP/LIME | Explicar anomalia | nenhuma | modelo avaliado | contribuição por feature já existe (`contributing_feature`) | **DEFER** |
| Random Forest de risco | "previsão" | sem rótulo real | **200+ decisões com desfecho** (D-03) | regras | **DEFER** |
| Chatbot com function calling controlado | Consulta rápida | `ChatFAB.tsx` | permissões, auditoria (S5-T8) | LLM só explica | **PROTOTYPE_NOW** (escopo mínimo) |
| Chatbot "conversa livre" | n/a | n/a | n/a | n/a | **REJECT** |
| CRDT / vector clock | Conflito de escrita offline | n/a (telemetria é append-only) | edição offline concorrente real | `(device, sequence)` | **REJECT** para telemetria; **DEFER** para configuração editável offline |
| Satélite NTN/TVWS/Swarm | Canal de emergência | zero | estudo de custo/hardware | Data Mule + 4G | **ARCHITECT_NOW** só a interface `ConnectivityProvider`; resto **DEFER** |
| Digital Twin / What-if | Simulação | zero | histórico + consequência maduros | n/a | **DEFER** |
| Edge AI com LLM local no ESP32 | "Impressionar" | inviável em ESP32 | outra placa | regra no edge | **REJECT** |
| Multi-tenancy completo (isolamento por schema) | Venda B2B | `Organization` existe | validação comercial | filtro por organização + testes | **ARCHITECT_NOW**; testes cruzados **BUILD_NOW** |
| Microserviços/Kafka/K8s | "Parecer enterprise" | n/a | volume | monólito modular | **REJECT** |
| App nativo mobile | n/a | n/a | n/a | PWA responsiva | **REJECT** (memória: fora de escopo; existe protótipo Flutter separado) |


### 11.1 RECLASSIFICAÇÃO V4 (itens que a V3 adiava ou simulava)

| Iniciativa | V3 | **V4** | Base que a V4 constrói | Tarefa |
|---|---|---|---|---|
| Decisão/prescrição sem internet | nuvem | **BUILD_NOW** | Gateway-Núcleo, replicação, login offline | S13-T1 a T8 |
| LoRa | plano | **BUILD_NOW** | rádio, firmware, campanha em campo | S14-T2, T3 |
| Relay no transbordo | stub | **BUILD_NOW** | firmware de relay, custódia | S14-T4 |
| Data Mule | Docker | **BUILD_NOW** | 3 ESP32 físicos | S14-T5 |
| Celular como mule (BLE) | inexistente | **BUILD_NOW** | GATT + PWA + HTTPS local | S14-T6, S13-T12 |
| Satélite | simulado | **BUILD_NOW com gate de compra** | estudo, modem, medição | S14-T7 |
| CAN/J1939 | emissor de teste | **BUILD_NOW** | escuta em veículo real, listen-only | S8-T12 |
| Autoencoder | DEFER | **PROTOTYPE_NOW (gate)** | campanha e rig | S15-T1, T2, T6 |
| Copiloto/chatbot | DEFER | **PROTOTYPE_NOW** | RAG, ferramentas, avaliação | S15-T12, T14 |
| LLM local | REJECT (no ESP32) | **VALIDATE_NOW (no gateway)** | benchmark no hardware real | S15-T13 |
| Tempo até o limite / "RUL" | DEFER | **PROTOTYPE_NOW (rotulado "validado no rig")** | rig de degradação | S15-T2, S16-T7 |
| Playbooks | inexistente | **BUILD_NOW** | revisão por mecânico | S16-T1, T10 |
| Otimizador de agenda | inexistente | **BUILD_NOW** | OR-Tools + estoque + grafo | S16-T4, T6 |
| OTA | DEFER | **BUILD_NOW** | firmware versionado, partições | S17-T3 |
| Risco térmico de incêndio | inexistente | **BUILD_NOW** | termopares, rig | S17-T1 |
| Acústica | inexistente | **PROTOTYPE_NOW (gate)** | microfone I2S, rig | S15-T16 |
| CRDT | REJECT | **REJECT telemetria; HLC + autoridade para domínio** | `DomainChange` | S13-T4 a T6 |
| What-if / "digital twin" | DEFER | **what-if estatístico honesto** (não gêmeo digital completo) | S9 + S15-T7 | S16-T7 |
| Score de operador | DEFER | **DEFER (D-16)** | política da usina | n/a |
| Microserviços/Kafka/K8s | REJECT | **REJECT** | n/a | n/a |
| Multi-tenancy por schema | ARCHITECT_NOW | **ARCHITECT_NOW** | filtro + testes cruzados | S2-T6 |


### 11.2 RECLASSIFICAÇÃO V5 (pedidos do analista)

| Iniciativa | V4 | **V5** | Base que a V5 constrói | Tarefa |
|---|---|---|---|---|
| Foco em subsistema do motor diesel | inexistente | **BUILD_NOW** | motor, catálogo de sinais, componentes | S18-T1 a T4 |
| Padrão de normalidade por sinal e regime | baseline por regime genérico | **BUILD_NOW** | perfis robustos por célula de regime | S18-T5 |
| Desclassificação de dado irreal | Trust Score por leitura | **BUILD_NOW** | qualidade por sinal/janela, descarte visível | S18-T6 |
| DTC de motor | inexistente | **BUILD_NOW** | DM1/DM2, mapa para componente | S18-T7 |
| Indicadores de saúde por componente | inexistente | **BUILD_NOW** | HIs sobre dado limpo | S18-T8 |
| Laudo estruturado | `outcome_texto` livre | **BUILD_NOW** | `laudo.v1`, assinatura, auditoria | S19-T2 |
| Percentual de recomendação | `confianca` heurística | **BUILD_NOW** | calibração com laudos | S19-T5 |
| **Prazo-limite de manutenção (PLM)** | horizonte linear de temperatura | **BUILD_NOW** | prognóstico por indicador com intervalo e abstenção | S19-T6 |
| Escada de confirmação | prescrição de um passo | **BUILD_NOW** | degraus com PR mínimo | S19-T7 |
| Política de recomendação | limiar único | **BUILD_NOW** | curva precisão × cobertura | S19-T8 |
| Painel de precisão | inexistente | **BUILD_NOW** | Wilson, calibração, cobertura | S19-T9 |
| Home com mapa + seleção + cards | faixa "Atenção agora" | **BUILD_NOW** | layout novo e estado único | S20-T1 a T4, T9 |
| **Vida útil residual em % afirmada como fato** | n/a | **NÃO FAZER até validar** (mostra-se a estimativa do técnico no laudo) | backtest e laudos | S19-T1, T11 |
| Previsão supervisionada de falha | DEFER | **PROTOTYPE_NOW (só com rótulos)** | laudos, oficina, FailureEvent | S19-T3, T11 |
| Ledger de valor | inexistente | **BUILD_NOW** | laudo + premissas do cliente | S21-T1 |
| Matriz de diferenciais com fonte | inexistente | **BUILD_NOW** | pesquisa pública datada | S21-T7 |

---

## 12. CONSOLIDATED ROADMAP STRUCTURE

Comparação das estruturas existentes (Leviatã exige consolidar, não escolher arbitrariamente uma):

| Critério | Doc A (7 camadas, TCC) | v2 (10 semanas) | Ultimato (7 passos / 10 passos / 6 fases) | **Consolidação V3** |
|---|---|---|---|---|
| Ordem de dependência | Camada de conectividade primeiro | Fundação de dados → segurança → decisão → honestidade ML → front → offline → obs → hardware → validação | Fecha fluxo → valida IA → prova offline → segurança → prescrição → hardware | **Contrato e integridade primeiro**, depois segurança, depois **front ligado ao motor** |
| Risco | Hardware no início (alto risco, sem base) | Backend primeiro (certo) | Front/diferencial primeiro (certo para banca) | Backend já está feito: **o risco restante é integração e prova**, então o front sobe para cedo |
| Valor de validação | Baixo (sem prova) | Médio | Alto | Cada fase termina com **evidência demonstrável** |
| Lacunas | Sem decisão, sem segurança | Sem hardware, sem front integrado | Sem Operational Graph como tarefa | V3 adiciona Graph/Consequence como **PROTOTYPE_NOW** |
| Redundância | Offline repetido 3x | Prescrição em 3 lugares | Segurança em 4 blocos | V3 deduplica: um dono por assunto |

**Regra de ouro herdada de todos os blocos do Ultimato:** *não adicionar camada nova antes de fechar a anterior com evidência*. A ordem consolidada:

```text
FASE 0  baseline e higiene (verdade do repositório)
FASE 1  integridade de dados e contratos únicos
FASE 2  segurança de fronteira e isolamento
FASE 3  front ligado ao motor (Command Center)      <- aqui o diferencial aparece
FASE 4  prescrição operacional (decisão -> OS -> resultado)
FASE 5  IA defensável (avaliar antes de prometer)
FASE 6  resiliência offline provada com métricas
FASE 7  conectividade (Connectivity Manager + Data Mule)
FASE 8  hardware real (firmware, sensores, CAN)
FASE 9  Operational Graph + Consequence Engine v0.1
FASE 10 observabilidade e DevOps de produção
FASE 11 Universal Machine Model real + Data Passport
FASE 12 validação de campo, comercial e narrativa final
```

(Fases 6, 7 e 8 podem andar em paralelo entre integrantes, mas S8 não bloqueia S3 nem S4.)

**Acréscimo V4 à consolidação:** a ordem de dependência não mudou, mas a **execução** agora tem quatro pistas em paralelo (software, hardware/enlaces, IA/dados, produto/validação) e cinco fatias novas (S13 Gateway-Núcleo, S14 Enlaces reais e soak, S15 IA profissional, S16 Prescrição profissional, S17 Diferenciais). A Doc A (conectividade primeiro) estava certa em **começar pelo físico**; a V3 estava certa em **não prometer o que não mede**. A V4 combina as duas: começa pelo físico **e** mede tudo.


---

## 13. DEPENDENCY GRAPH (V5: foco diesel, confiança e home, sobre as pistas da V4)

```text
PISTA A · Core/Front           PISTA B · Motor, hardware e enlaces        PISTA C · Dados, IA e prognóstico        PISTA D · Home, valor, validação
-------------------            -------------------------------------      -------------------------------------    --------------------------------
S0 → S1 contrato               S18-T1 ACESSO AO MOTOR (gate sem.1-2)      S19-T1 definições (PR, PLM, laudo)       S20-T1 layout novo (wireframe)
 │      │                       S8-T10 compras                             S19-T2 laudo (modelo, UI)                S12-T11 acesso/piloto
 │      ├─► S2 segurança        S8-T1 DS18B20→MQTT                          │                                       S12-T4/T5/T12 entrevistas
 │      │                       S18-T2 descoberta de sinais (listen-only)   ▼
 │      ├─► S3 front real ───────────────────────────────┐                S18-T3 modelo componentes                 S20-T2 cards ─► S20-T3 drill-down
 │      │                       S18-T4 contrato v2 multicanal ◄────────────── S18-T4                                  S20-T4 seleção hierárquica
 │      └─► S4 decisão→OS       S18-T5 normalidade por sinal/regime          S18-T6 qualidade/desclassificação            │
 │                              S18-T7 DTC                                     │                                       S20-T5 painel componente ◄─┐
 │                              S18-T8 indicadores de saúde ──────────────────►S19-T4 evidência multi-sinal            S20-T6 medidor PR            │
 │                              S18-T9 banco de provas (oficina)               S19-T5 PR calibrado ───────────────────► S20-T6                       │
 │                              S18-T10 campanha motor ──► S18-T11 falhas     S19-T6 PLM (prognóstico)                 S20-T9 mapa                  │
 │                                    reversíveis                               S19-T7 escada ──► S19-T8 política       S20-T7 enxugar ─► S20-T8 usabilidade
 │                              S14 enlaces ─► S14-T9 soak                      S19-T9 painel de precisão                                            │
 └──► S13 GATEWAY-NÚCLEO ◄──────────────────────────────────────────────────── S19-T10 decisão técnico ─► S19-T12 "bomba 70%"                        │
        │                                                                       S19-T11 backtest                                                      │
        └──► S16 prescrição (playbooks por componente, otimizador) ◄─────────── S15 IA (resíduo, MLOps, copiloto)                                     │
                  │                                                                                                                                  │
                  └──► S21 valor do investidor (ledger, relatório, data room, matriz de diferenciais) ◄───────────────────────────────────────────────┘
 PILARES: P1 PRESCRIÇÃO = S4+S16+S13-T8 · P2 IA = S5+S15 · P3 OFFLINE = S6+S8+S13+S14 · P4 DIESEL = S18 · P5 CONFIANÇA = S19 · P6 HOME = S20
```

**Dependências duras da V5:**
- **S18-T1 (acesso ao motor) é o novo caminho crítico:** sem motor/ECU não há S18-T2 a T8 reais, nem S19-T4 a T6 com dado próprio. Plano B documentado em 0-A.8.
- **S19-T2 (laudo) e S12-T12 (entrevistas) começam na semana 1:** são a fonte dos rótulos de PR.
- **S18-T4 (contrato multicanal) antes de S18-T5 e S18-T6:** perfil de normalidade e qualidade operam sobre o contrato v2.
- **S18-T6 (desclassificação) antes de S18-T8, S19-T4 e S19-T6:** nenhuma métrica ou tendência usa dado descartado.
- **S19-T5 (PR) antes de S20-T6 (medidor) e S19-T7/T8 (escada e política).**
- **S19-T6 (PLM) antes de S20-T3/T5 mostrarem prazo.**
- **S20-T1/T2 podem começar já com os dados atuais** (contagem crítico/atenção/normal da V4), e ganham PR/PLM quando S19 entregar.
- Tudo da V4 continua: contrato (S1) antes de S3, S4, S13, S16; S13-T4 antes de S13-T5; S14-T1 antes de S14-T8; soak precisa de nó+enlace+energia.

**Se S18-T1 atrasar:** seguir com o **banco de provas da oficina** (S18-T9) e com o gerador/veículo disponível; **rotular** tudo o que for simulado (selo SIMULADO) e **não** declarar o pilar P4 fechado.

---

## 14. CONSOLIDATED MASTER ROADMAP · VISÃO GERAL (V5)

### 14.1 Fatias (S0 a S21) e estado

| Fatia | Tema | Pilar | Trilha | Estado dominante | Evidência que fecha |
|---|---|---|---|---|---|
| S0 a S17 | (V4, inalteradas; ver notas V5 nos cabeçalhos) | P1 a P3 | A/B/C/D | ver V4 | ver V4 |
| **S18** | **Foco diesel: sistema de combustível de alta pressão a fundo** | **P4** | **B/C** | **BUILD_NOW** | `diesel_100` |
| **S19** | **Confiança: PR, PLM, laudo, escada, precisão, decisão do técnico** | **P5** | **C/D** | **BUILD_NOW** | `confianca_100` + backtest |
| **S20** | **Home e BI: seleção + mapa, cards, drill-down, componente** | **P6** | **A/D** | **BUILD_NOW** | `home_100` + usabilidade |
| **S21** | **Valor para investidor/gestor: ledger, relatório, data room, matriz** | todos | **D** | **BUILD_NOW** | pacote de evidências |

### 14.2 Calendário de 12 semanas (4 trilhas paralelas) · V5

*Em negrito, o caminho crítico. "Gate" = marco necessário para a semana seguinte. As tarefas da V4 que não aparecem aqui seguem a prioridade V5 (seção 0-A.7) e entram quando houver folga.*

| Sem. | A · Core e front | B · Motor, hardware e enlaces | C · Dados, IA e prognóstico | D · Home, valor e validação | **Gate** |
|---|---|---|---|---|---|
| **1** | S0-T1, T2, T3 · S1-T1, T2, T3 | **S18-T1 (acesso ao motor diesel)** · S8-T10 (compras) · S8-T1 | **S19-T1 (definições)** · S15-T1 (plano) | **S20-T1 (wireframe da home)** · S12-T11 · S12-T4 · contato com oficina (S18-T9) | **Motor e oficina com resposta; primeira leitura física** |
| **2** | S1-T4 a T8 · S2-T1, T2 | **S18-T2 (descoberta de sinais, só escuta)** · S8-T2, T3, T11, T13 | S18-T3 (componentes) · **S19-T2 (laudo: modelo)** | S20-T2 (cards), S20-T4 (seleção) · S12-T5 e T12 (entrevistas, perguntas de laudo) | **Catálogo de sinais do motor publicado** |
| **3** | S2-T3 a T8 · S3-T1, T2 · **S18-T4 (contrato v2)** | S8-T4 · S14-T2 · S18-T12 (sensores não invasivos) | **S18-T5 (normalidade)** · **S18-T6 (qualidade)** | S20-T3 (drill-down) · S19-T2 (laudo: UI mobile) | **Perfil de normalidade e desclassificação rodando** |
| **4** | S3-T3 a T6 · S4-T1 a T3 · S18-T7 (DTC) | **S18-T10 (campanha no motor, sessão 1)** · S14-T5 · **iniciar soak #1** | **S18-T8 (indicadores de saúde)** · S15-T3 | S20-T5 (painel do componente), S20-T6 (medidor) | **Indicadores por componente com dado real** |
| **5** | S13-T1, T2, T4 · S4-T4, T5 | **S18-T9 (banco de provas da oficina)** · S14-T3 | **S19-T4 (evidência multi-sinal)** · S15-T4, T5 | S19-T3 (falhas corretivas) · S20-T9 (mapa) | **Primeiros rótulos de oficina** |
| **6** | S13-T3, T5, T6 | **S18-T11 (falhas reversíveis)** · S8-T12 · S14-T4 | **S19-T5 (PR provisório)** · **S19-T6 (PLM)** | **S19-T7 (escada)** · S19-T8 (política) | **PR e PLM exibidos (provisórios)** |
| **7** | S13-T7, T8 | S14-T6, T7, T12 · soak #1 relatório | **S19-T11 (backtest)** · S15-T7, T9 | **S19-T9 (painel de precisão)** · **S19-T10 (decisão do técnico)** | **Apagão total + backtest inicial** |
| **8** | S6 · S9-T1 a T3 | S14-T8, T11 | S15-T12 (copiloto) · **S19-T12 (cenário "bomba 70%")** | S20-T7 (enxugar) · **S20-T8 (usabilidade #1)** · S16-T1 a T3 | **Cenário da bomba reproduzido** |
| **9** | S16-T4 a T8 | **soak #2** · **S18-T10 (campanha, mais sessões)** · S17-T1, T2 | **S18-T13 (diesel_100)** · S15-T13, T14 | **S21-T1, T2 (ledger, relatório)** · S20-T8 (usabilidade #2) | **diesel_100 verde** |
| **10** | S10 (CI, métricas, backup) | S17-T3, T4 | S15-T15 (IA offline) | **S21-T3 (data room)** · **S21-T7 (matriz de diferenciais)** · S21-T5 | **CI verde, data room** |
| **11** | S11 (T1 a T3, T6) · S13-T8 (reexecutar) | soak #2 termina · S8-T6 | **confianca_100 (reexecutar)** | **home_100** · S16-T9 · S12-T6, T7 | **Pilares P1 a P6 verificados** |
| **12** | S12-T1, T2, T3, T8, T9, T10 | kit e vídeo de fallback | model card, relatório de precisão final | S12-T5 (relatório) · S21-T4 · ensaios | **Freeze, ensaios, pitch** |

### 14.3 O que precisa de gente de fora (começar na semana 1)

- **Dono do motor diesel** (gerador, trator, caminhão ou oficina) com autorização de escuta de barramento (S18-T1).
- **Oficina de bomba/bicos** com banco de provas e disposição de compartilhar **laudos** (S18-T9, S19-T2).
- **Mecânico** para revisar playbooks, escada de confirmação e laudos (S16-T10, S19-T7).
- **Analista sênior supervisor**: validar a **meta de precisão** e a **política de recomendação** (D-54), e participar da revisão da home (S20-T8).
- **3 a 5 gestores/técnicos** para o teste de usabilidade (S20-T8).

---

## 15. DETAILED PHASE-BY-PHASE EXECUTION PLAN

### Convenções de execução (valem para todas as semanas)

- **Branch por tarefa:** `feature/s1-t1-contrato-severidade`. **PR obrigatório para `main`**. **Commits em português**, formato `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`.
- **Definition of Done global (toda tarefa):** (1) testes novos e antigos verdes localmente **e** no CI quando existir; (2) nenhum `TODO` sem `(quem, por quê, quando)`; (3) nenhum arquivo novo acima de 300 linhas sem justificativa (regra do `CLAUDE.md`); (4) sem segredo, sem `console.log` solto, sem `except: pass`; (5) a evidência da tarefa está **commitada** ou anexada ao PR; (6) o `CLAIMS_VS_CODE.md` foi atualizado se a tarefa mudou o que o projeto pode afirmar.
- **Marcação de dado:** toda tela, relatório ou gráfico que dependa de dado simulado deve exibir selo **"SIMULADO"** (tarefa S3-T1 cria o componente; depois é obrigatório).
- **Ordem dentro da semana:** as tarefas estão numeradas por dependência. Execute na ordem, salvo indicação.

---

### SEMANA 0 · BASELINE, HIGIENE E MATRIZ DE VERDADE

> **NOTA V4:** Prioridade **P3** (executa depois dos pilares; **nada removido**): S0-T4, S0-T5 e S0-T6 cabem juntas em meio dia. S0-T1 a T3 continuam obrigatórias na semana 1.


**Camadas:** FOUNDATION · DOCUMENTATION · TESTING

- **Objetivo estratégico:** parar de operar sobre números e afirmações que ninguém verificou. Dar à primeira impressão do repositório (a de um avaliador técnico) uma base honesta.
- **Objetivo técnico:** executar e registrar o estado real (testes, migrations, linhas por arquivo, containers), limpar artefatos versionados e produzir a matriz *claim → evidência* usada por todas as semanas.
- **Por que existe:** o Ultimato inteiro (16 blocos) discorda entre si em pontos verificáveis (Mosquitto aberto vs fechado, 292 testes vs 298 declarações, docs "sumidos"). Roadmap sem baseline é roadmap sobre achismo.
- **Problemas que resolve:** repo sujo (`.next/trace`, `.kiro/`, `api/page.tsx`, `src/types/*` duplicados), documentos prometidos inexistentes, README e Proposta TCC divergentes do código.
- **Dependências recebidas:** nenhuma.
- **Entregáveis:** `docs/BASELINE.md`, repo limpo, `docs/CLAIMS_VS_CODE.md`, esqueletos dos 8 documentos faltantes com dono, `AGENTS.md` ajustado.
- **Arquivos/módulos afetados:** `.gitignore`, `.next/`, `.kiro/`, `api_tcc/api/page.tsx`, `frontend-next/src/types/*`, `api_tcc/management/commands/*`, `README.md`, `docs/*`, `AGENTS.md`.
- **Mudanças arquiteturais:** nenhuma. **Banco:** nenhuma. **Backend:** remoção de comandos duplicados. **Frontend:** remoção de duplicatas de tipos. **Hardware:** nenhuma. **ML/IA:** nenhuma. **Infra:** `git rm --cached`. **Segurança:** varredura de segredos. **Testes:** execução completa e registro. **Documentação:** núcleo da semana.
- **Experimentos:** `docker compose up` do zero em máquina limpa (WSL/VM) cronometrado (meta do `CLAUDE.md`: setup em menos de 10 minutos).
- **Critérios de aceitação:** todos os números do `BASELINE.md` vêm de comandos executados e colados; `git ls-files` sem artefato gerado.
- **Métricas:** testes executados/passando/falhando/pulados; migrations; tempo de setup; linhas por arquivo (>300 listados); cobertura (se medida).
- **Evidências esperadas:** saída bruta dos comandos em `docs/evidence/s0/`.
- **Riscos:** descobrir testes falhando que estavam escondidos. **É vitória, não fracasso.**
- **Decisões que precisam ser tomadas:** D-13 (manter histórico squashado + tag?), D-14 (política para números de impacto sem fonte primária).
- **Perguntas abertas:** o `AGENTS.md` fica na raiz? (resposta nesta semana: **sim**, mas com cabeçalho neutro, ver S0-T5).
- **Definition of Done da semana:** `BASELINE.md` e `CLAIMS_VS_CODE.md` commitados, `git status` limpo após clone novo, `docker compose up` do zero verde.

#### S0-T1 · Baseline reproduzível
- **Objetivo:** substituir "292 testes" por saída de comando.
- **Contexto:** número informado pelo grupo; grep encontra 298 `def test_`; migrations somam 26 arquivos (informado: 25).
- **Problema atual:** nenhum número do projeto tem evidência anexada.
- **Estado desejado:** `docs/BASELINE.md` com data, commit, ambiente e saída real.
- **Dependências · Pré-requisitos:** nenhuma · Python 3.12, Docker, Node 20.
- **Arquivos prováveis:** `docs/BASELINE.md`, `docs/evidence/s0/*.txt`.
- **Implementação esperada:**
```bash
git rev-parse HEAD | tee docs/evidence/s0/commit.txt
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python manage.py test api_tcc simulators -v 2 2>&1 | tee docs/evidence/s0/tests_django.txt
pytest -q 2>&1 | tee docs/evidence/s0/tests_pytest.txt            # pytest.ini existe
python manage.py makemigrations --check --dry-run | tee docs/evidence/s0/migrations_check.txt
find . -name '*.py' -not -path './.venv/*' -not -path './*/migrations/*' | xargs wc -l | sort -n | tail -20 > docs/evidence/s0/linhas_py.txt
(cd frontend-next && npm ci && npm run lint && npx tsc --noEmit && npm run build) 2>&1 | tee ../docs/evidence/s0/front_build.txt
( time docker compose up --build -d ) 2>&1 | tee docs/evidence/s0/compose_up.txt
docker compose exec -T web python manage.py migrate
curl -s localhost:8000/api/health/ | tee docs/evidence/s0/health.json
```
- **Testes necessários:** a própria execução. Se algum teste falhar, **abrir issue** (não corrigir silenciosamente nesta tarefa).
- **Critério de aceite:** `BASELINE.md` lista: testes (passaram/falharam/pulados), migrations, tempo de setup, arquivos >300 linhas, estado do build do front.
- **Evidência de conclusão:** arquivos em `docs/evidence/s0/` commitados.
- **Risco:** SQLite local vs MySQL em Compose divergem (tabela travada em teste de concorrência é esperada, conforme Ultimato 1.1). Registrar nos dois ambientes.
- **Relação com a estratégia:** pré-requisito do princípio "pronto = evidência".

#### S0-T2 · Higiene do repositório
- **Objetivo:** primeira impressão limpa e sem ambiguidade de qual arquivo vale.
- **Contexto:** `.gitignore` já lista `.next/` e `.kiro/`, mas arquivos rastreados antes continuam rastreados.
- **Problema atual:** `.next/trace`, `.kiro/settings/cli.json` e `.kirocrew-cli-settings.lock` em `git ls-files`; `api_tcc/api/page.tsx`; `frontend-next/src/types/{FleetGrid,SkeletonGrid,page,telemetryService}.tsx|ts` duplicando `components/`, `app/`, `services/`; comandos de gerenciamento duplicados.
- **Estado desejado:** um arquivo por conceito; `src/types/` só com `.ts` de tipos.
- **Dependências · Pré-requisitos:** S0-T1 (testes verdes antes e depois) · nenhum.
- **Arquivos prováveis:** os listados acima + `api_tcc/management/commands/{criar_prescricoes_simples,criar_prescricoes_teste,populate_db,popular_tudo,treinar_isolation_forest,treinar_modelo_anomalia}.py`.
- **Implementação esperada:**
```bash
git rm -r --cached .next .kiro
git rm api_tcc/api/page.tsx
# para cada par duplicado: diff, manter a versão importada por código vivo, apagar a outra
for f in FleetGrid SkeletonGrid; do diff frontend-next/src/types/$f.tsx frontend-next/src/components/$f.tsx; done
grep -rn "from '@/types/\(FleetGrid\|SkeletonGrid\|page\|telemetryService\)" frontend-next/src || echo "ninguém importa"
# comandos de gerenciamento: manter 1 por função, os demais viram alias deprecado por 1 ciclo ou saem
grep -rn "treinar_isolation_forest\|treinar_modelo_anomalia" --include=*.py --include=*.md --include=*.yml . | grep -v migrations
# conferir se há dado sensível versionado
git ls-files | grep -Ei '\.(sqlite3?|bak|env)$|backup|secret' || echo "nenhum"
pip install gitleaks 2>/dev/null; gitleaks detect --no-git --source . --redact || true
```
- **Testes necessários:** suíte completa antes e depois; `npm run build`; `docker compose up`.
- **Critério de aceite:** `git ls-files | grep -E '^(\.next|\.kiro)/'` vazio; `api_tcc/api/page.tsx` ausente; `grep -c` de duplicatas em `src/types` = 0; `gitleaks` sem achado crítico.
- **Evidência de conclusão:** diff do PR com remoção líquida de arquivos; saída do gitleaks.
- **Risco:** apagar a versão "viva" de um componente. Mitigação: `grep` de imports **antes** de apagar.
- **Relação com a estratégia:** o recrutador/banca abre a árvore antes do README.

#### S0-T3 · Matriz de claims (CLAIMS_VS_CODE.md)
- **Objetivo:** cada afirmação pública do projeto aponta para uma evidência ou vira "roadmap".
- **Contexto:** `Proposta_TCC_v4` afirma ESP-NOW e Random Forest como entregues; README e pitch afirmam "IA", "offline", "multi-marca".
- **Problema atual:** documentos descrevem sistemas diferentes do repositório (contradição já apontada no Documento 01 do v2).
- **Estado desejado:** tabela `Afirmação | Onde aparece | Status (IMPLEMENTADO/SIMULADO/ROADMAP) | Evidência (arquivo/teste/vídeo) | Formulação permitida`.
- **Dependências · Pré-requisitos:** S0-T1 · nenhuma.
- **Arquivos prováveis:** `docs/CLAIMS_VS_CODE.md`, `README.md`, versão revisada da proposta.
- **Implementação esperada:** seed de linhas obrigatórias:

| Afirmação | Formulação **permitida** hoje | Formulação **proibida** hoje |
|---|---|---|
| IA | "Detecção de anomalias não supervisionada (Isolation Forest por máquina) + regras operacionais + explicação por LLM" | "IA que prevê falhas", "precisão de X%" sem relatório S5 |
| Offline | "Coleta local com outbox, prioridade A/B/C, sincronização idempotente, validada em simulador (ver protocolo S6)" | "Funciona offline a km de distância", "buffer de 30 dias" |
| Multi-marca | "Fundação Raw→Canonical com adaptadores simulados para dois fabricantes" | "Multi-marca", "agnóstico de OEM" |
| Hardware | "Protótipo de bancada com ESP32 (após S8)" | "ESP-NOW entre máquinas" antes de S8-T5 |
| Data Mule | "Simulador de transporte de buffer" (até S7/S8) | "Rede de data mule em campo" |
| Impacto financeiro | (não citar no pitch, orientação do professor); internamente "hipótese não verificada" | Qualquer número sem fonte primária (D-14) |

- **Testes necessários:** revisão cruzada por outro membro.
- **Critério de aceite:** nenhuma frase de `README.md` e da proposta contradiz uma linha da matriz.
- **Evidência de conclusão:** PR com diff de textos ajustados.
- **Risco:** desconforto de "admitir". Mitigação: é exatamente o que o professor cobrou ("não se pode prometer decisão por IA sem modelo treinado").
- **Relação com a estratégia:** protege a defesa sob questionamento adversarial.

#### S0-T4 · Esqueletos dos documentos faltantes, com dono
- **Objetivo:** cada documento prometido passa a existir como arquivo com responsável e semana de preenchimento.
- **Contexto:** `docs/` tem `ATTENTION_ENGINE`, `CONTRATO_TELEMETRIA_V1`, `DATA_HEALTH`, `DLQ`, `ROTAS_E_URLS`, `SEGURANCA`, `SEQ_ID`, `alertas`, `limiares`.
- **Problema atual:** faltam documentos que a banca pede.
- **Estado desejado:** arquivos criados com cabeçalho `Responsável: · Semana: · Status: ESQUELETO`.
- **Dependências · Pré-requisitos:** nenhuma · nenhum.
- **Arquivos prováveis (criar):** `HONESTIDADE_METODOLOGICA_ML.md` (S5), `PROTOCOLO_TESTE_RESILIENCIA.md` (S6), `REPOSICIONAMENTO_ESCOPO_HARDWARE.md` (S8), `OBSERVABILIDADE.md` e `DEPLOY.md` (S10), `PLANO_DATASET_ROTULADO.md` (S5), `ROTEIRO_DEMO_BANCA.md` e `INVESTOR_CTO_PRESSURE_TEST.md` (S12), `RESULTADOS_VALIDACAO_COMERCIAL.md` (S12).
- **Implementação esperada:** template único; `TODO(quem, por quê, quando)` em cada seção.
- **Testes necessários:** nenhum (markdown). Opcional: `markdownlint` (já há `.markdownlint.json` em versões anteriores).
- **Critério de aceite:** os 8 arquivos existem e referenciam a tarefa que os preenche.
- **Evidência de conclusão:** árvore de `docs/`.
- **Risco:** esqueleto virar esquecimento. Mitigação: o CI (S10) falha se `Status: ESQUELETO` sobrar após a semana alvo.
- **Relação com a estratégia:** fim do padrão "pendência citada em tabela sem dono".

#### S0-T5 · `AGENTS.md`: manter como contrato, trocar o cabeçalho
- **Objetivo:** manter o contrato para agentes (útil: é o que torna este roadmap executável) sem que a primeira leitura do recrutador seja marketing.
- **Contexto:** 37 KB na raiz com frases de "SaaS B2B high-ticket".
- **Problema atual:** primeira impressão de arquivo grandiloquente.
- **Estado desejado:** `AGENTS.md` enxuto no topo (regras operacionais) e detalhe movido para `docs/agents/`.
- **Dependências · Pré-requisitos:** nenhuma · nenhum.
- **Arquivos prováveis:** `AGENTS.md`, `docs/agents/CONTRATO.md`.
- **Implementação esperada:** adicionar no topo: "Estado das tarefas: ver `FIELDNODE_LEVIATA_ROADMAP_V5.md`. Regra: nada é marcado pronto sem a evidência da tarefa. Nunca afirmar em README/UI algo ausente de `docs/CLAIMS_VS_CODE.md`."
- **Testes necessários:** nenhum.
- **Critério de aceite:** `AGENTS.md` com menos de 120 linhas; nenhum termo "high-ticket" ou "não trate como projeto escolar" na raiz.
- **Evidência de conclusão:** PR.
- **Risco:** perder regras úteis. Mitigação: mover, não apagar.
- **Relação com a estratégia:** o roadmap é executado por agentes; o contrato precisa apontar para ele.

#### S0-T6 · Política de histórico e versionamento
- **Objetivo:** não perder a história do roadmap sem reescrever Git.
- **Contexto:** histórico squashado em 1 commit (`3b5f5c0`).
- **Problema atual:** impossível mostrar evolução (ativo narrativo).
- **Estado desejado:** `CHANGELOG.md` retroativo + tags semânticas daqui em diante.
- **Dependências · Pré-requisitos:** nenhuma · nenhum.
- **Arquivos prováveis:** `CHANGELOG.md`.
- **Implementação esperada:** `CHANGELOG.md` com blocos: "Roadmap v1 (auditoria)", "Roadmap v2 (S1 a S10, backend)", "Merge front (Next.js)". Tag `v0.3.0-baseline` no commit da S0-T1. Convenção de tag `vX.Y.Z-semanaN`.
- **Testes necessários:** nenhum.
- **Critério de aceite:** `git tag` lista a baseline.
- **Evidência de conclusão:** tag no remoto.
- **Risco:** nenhum.
- **Relação com a estratégia:** rastreabilidade do próprio projeto (coerente com o discurso de "decisão rastreável").

---

### SEMANA 1 · CONTRATOS ÚNICOS E INTEGRIDADE DE DADOS

> **NOTA V4:** O hardware **não espera** a S1: usa o contrato v0 (limiares atuais) e migra para o v1 por versão. Os valores do contrato v1 são reajustáveis com dados reais (S15-T1) por versão de contrato. Incluir o firmware (S8-T13) na matriz de paridade (S1-T8).


**Camadas:** FOUNDATION · ARCHITECTURE · TESTING

- **Objetivo estratégico:** garantir que o mesmo dado receba a mesma classificação em qualquer ponto do sistema, e que nenhuma mensagem seja perdida ou atrasada por uma regra desalinhada.
- **Objetivo técnico:** um contrato versionado de severidade/prioridade/escala consumido por backend, borda e front; separar *severidade (fato)* de *qualidade da evidência* e de *prioridade de atenção*; contrato de tempo para dispositivo sem relógio; semântica de ACK explícita; fila do Service Worker sem bloqueio.
- **Por que existe:** achados de maior risco do repositório hoje: (1) quatro conjuntos de limiares e **três escalas de vibração** (backend `> 85 °C`; borda `95/110 °C`, vibração `5/8`; front `95/110 °C`, vibração `0,5/0,8 g`; `sensor_limits` vibração 0 a 10; proposta TCC vibração 0,0 a 1,0); (2) crítico sai como prioridade C; (3) fila do SW trava com mensagem inválida.
- **Problemas que resolve:** classificação divergente, prioridade invertida, evidência fraca rebaixando alerta grave, hora inconsistente no ESP32, fila presa.
- **Dependências recebidas:** S0 (baseline verde, repo limpo).
- **Entregáveis:** `contracts/severity.v1.json`, módulo Python, geração de header C++ e de TS, `Event.evidence_quality`, migration 0027 (campos de tempo), semântica de ACK documentada e testada, `sw.js` por item, views de ingestão divididas, teste de contrato cruzado.
- **Arquivos/módulos afetados:** `api_tcc/services/eventos.py`, `api_tcc/services/sensor_limits.py`, `api_tcc/services/telemetria.py`, `api_tcc/models.py`, `api_tcc/api/views_ingestao.py`, `simulators/edge_client.py`, `frontend-next/src/lib/metricThresholds.ts`, `frontend-next/public/sw.js`, `docs/limiares.md`, `docs/CONTRATO_TELEMETRIA_V1.md`.
- **Arquitetura:** nasce o diretório `contracts/` como fonte única. **Banco:** `Event.evidence_quality`, `Event.needs_verification`, `LeituraTelemetria.boot_id`, `time_source`, `clock_skew_ms`. **Backend:** priority score sem multiplicar confiança. **Frontend:** `metricThresholds.ts` gerado do contrato. **Hardware:** header C++ gerado. **ML/IA:** nenhuma. **Infra:** script de geração no CI. **Segurança:** limite de payload e 429 com `Retry-After`. **Testes:** golden files. **Documentação:** `limiares.md` e `CONTRATO_TELEMETRIA_V1.md` reescritos.
- **Experimentos:** varrer 0 a 150 °C e 0 a 10 de vibração e comparar a classe da borda, do backend e do front ponto a ponto (esperado: divergência zero ao final).
- **Critérios de aceitação:** teste de contrato cruzado verde; nenhum literal `85`, `95`, `110` em código fora do contrato.
- **Métricas:** pontos de divergência (hoje > 0, meta 0); latência de ingestão p95 antes/depois da divisão das views.
- **Evidências esperadas:** saída do teste de contrato; tabela de divergências antes/depois.
- **Riscos:** mudar limiar muda eventos e decisões já gerados em dados de demo (re-seed). Quebra de cliente antigo (mitigação: campos novos opcionais, `schema_version`).
- **Decisões:** D-01 (valores do contrato v1), D-02 (escala de vibração), D-15 (confiança não rebaixa severidade).
- **Perguntas abertas:** qual a unidade real do `vibracao` quando entrar o acelerômetro (S8-T2)? Resposta provisória: **índice adimensional 0 a 10 no contrato v1**, com campo `vibracao_unit` e conversão explícita quando houver RMS em g.
- **Definition of Done da semana:** teste cruzado verde; `git grep -nE '\b(85|95|110)\b' -- '*.py' '*.ts' '*.tsx'` fora de `contracts/` e testes retorna vazio.

#### S1-T1 · Contrato único de severidade e prioridade de transmissão
- **Objetivo:** uma fonte de verdade para limiares, severidade e classe A/B/C.
- **Contexto:** `eventos.py:13` (`TEMP_ALTA_CRITICA_C = 85.0`), `edge_client.py:44-48` (110/95 e 8/5), `metricThresholds.ts` (95/110, 0,5/0,8 g), `docs/limiares.md` (85, tendência 0,5, vibração média 5).
- **Problema atual:** leitura de 90 °C: backend `CRITICO`, borda classe C, front "normal". Pior caso possível para o alerta crítico em fila offline.
- **Estado desejado:** `contracts/severity.v1.json` lido por todos. Prioridade de transmissão = função de (severidade, qualidade da evidência, atraso), **não** limiar próprio.
- **Dependências · Pré-requisitos:** S0 · decisão D-01.
- **Arquivos prováveis:** `contracts/severity.v1.json`, `api_tcc/contracts.py`, `scripts/gen_contracts.py`, `simulators/edge_client.py`, `frontend-next/src/lib/metricThresholds.ts`, `firmware/include/severity_contract.h` (S8).
- **Implementação esperada:** valores v1 **heurísticos de bancada** (mesma advertência de `limiares.md`), com `source: "bancada-2026"` e `calibravel_por_modelo: true`.
```json
{
  "schema": "severity.v1",
  "metrics": {
    "temperatura": { "unit": "C",  "atencao": 75.0, "critico": 85.0,  "range": [0, 150] },
    "vibracao":    { "unit": "indice_0_10", "atencao": 5.0, "critico": 8.0, "range": [0, 10] },
    "rpm":         { "unit": "rpm", "severity": "dependente_de_regime", "range": [0, 5000] }
  },
  "transmission_class": {
    "A": "severidade == CRITICO",
    "B": "severidade == ATENCAO OR evidence_quality != boa OR dado_atrasado",
    "C": "caso contrario"
  },
  "note": "Valores de bancada. Limites por modelo vem de Machine/Modelo quando existirem (S5-T3, S11)."
}
```
```python
# api_tcc/contracts.py
import json
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=1)
def severity_contract() -> dict:
    return json.loads((Path(__file__).resolve().parent.parent / "contracts" / "severity.v1.json").read_text())

def classify(metric: str, value: float) -> str:
    m = severity_contract()["metrics"][metric]
    if "critico" not in m:
        return "NORMAL"          # rpm: severidade por regime, tratada em S5-T3
    if value >= m["critico"]:
        return "CRITICO"
    if value >= m["atencao"]:
        return "ATENCAO"
    return "NORMAL"

def transmission_class(severidade: str, evidence_quality: str, atrasado: bool) -> str:
    if severidade == "CRITICO":
        return "A"
    if severidade == "ATENCAO" or evidence_quality != "boa" or atrasado:
        return "B"
    return "C"
```
Nota: o backend hoje usa `>` e não `>=`; **decidir e documentar** (D-01) e testar fronteira exata (85.0, 85.0001, 84.9999).
- **Testes necessários:** fronteiras exatas; paridade backend × borda × TS (S1-T8); `docs/limiares.md` gerado ou conferido pelo teste.
- **Critério de aceite:** nenhuma leitura é `CRITICO` no backend e classe diferente de A na borda (varredura 0 a 150 °C passo 0,1 e vibração 0 a 10 passo 0,05).
- **Evidência de conclusão:** saída da varredura (0 divergências).
- **Risco:** o valor 85 °C como crítico é de bancada; para motor real é baixo. **Não afirmar como limite operacional** (já dito em `limiares.md`).
- **Relação com a estratégia:** fecha o bug que contradiz a tese "crítico sai primeiro".

#### S1-T2 · Escala e unidade de vibração (resolver as três escalas)
- **Objetivo:** uma definição de `vibracao` documentada, validada e exibida com a unidade correta.
- **Contexto:** `sensor_limits.py` (0 a 10), front `metricThresholds.ts` (`unit: 'g'`, 0,5/0,8), Proposta TCC (0,0 a 1,0), `edge_client` (5/8).
- **Problema atual:** o mesmo número é "índice", "g" ou "fração" conforme o arquivo; qualquer análise que cruze camadas é inválida.
- **Estado desejado:** campo `vibracao` = índice adimensional 0 a 10 (contrato v1); `vibracao_unit` e (futuro) `vibracao_rms_g`, `vibracao_pico_g`, `vibracao_curtose` como campos novos opcionais.
- **Dependências · Pré-requisitos:** S1-T1 · D-02.
- **Arquivos prováveis:** `api_tcc/services/sensor_limits.py`, `api_tcc/services/telemetria.py`, migration 0027, `frontend-next/src/lib/metricThresholds.ts`, `docs/CONTRATO_TELEMETRIA_V1.md`.
- **Implementação esperada:** adicionar `vibracao_unit` (default `indice_0_10`) ao `LeituraTelemetria` e ao `validar_payload`; rejeitar payload cuja unidade não conste na lista aceita; o front lê `unit` do contrato em vez de `'g'`.
- **Testes necessários:** payload com `vibracao_unit: "g"` e valor 0.6 é rejeitado ou convertido conforme D-02 (teste documenta qual); gráfico mostra a unidade certa (teste de componente).
- **Critério de aceite:** `grep -rn "'g'" frontend-next/src/lib` vazio; contrato documenta a escala.
- **Evidência de conclusão:** PR + captura de tela do gráfico com unidade.
- **Risco:** dados de demo com escala antiga: re-seed.
- **Relação com a estratégia:** sem escala única, Trust Score, IF e Decision comparam coisas diferentes.

#### S1-T3 · Separar severidade, qualidade da evidência e prioridade de atenção
- **Objetivo:** dado suspeito **não** rebaixa um evento grave; ele o marca como "inconclusivo, verificar".
- **Contexto:** `calcular_priority_score` multiplica `trust_score_herdado` (Ultimato 2.1, problema 6).
- **Problema atual:** sensor travado em 120 °C vira prioridade baixa (confiança baixa × severidade alta).
- **Estado desejado:** `priority_score = severidade × impacto × urgência` (sem confiança); `evidence_quality ∈ {boa, suspeita, insuficiente}` derivada do Trust Score; `needs_verification = evidence_quality != 'boa'`.
- **Dependências · Pré-requisitos:** S1-T1 · nenhum.
- **Arquivos prováveis:** `api_tcc/models.py` (`Event`), migration 0027, `api_tcc/services/eventos.py`, `api_tcc/api/views_events.py`, `docs/ATTENTION_ENGINE.md`.
- **Implementação esperada:**
```python
# eventos.py
EVIDENCE_BOA, EVIDENCE_SUSPEITA = 0.8, 0.5   # heurística calibrável; documentar

def evidence_quality(trust: float | None) -> str:
    if trust is None:
        return "insuficiente"
    if trust >= EVIDENCE_BOA:
        return "boa"
    if trust >= EVIDENCE_SUSPEITA:
        return "suspeita"
    return "insuficiente"

def calcular_priority_score(event, historico) -> float:
    s = SEVERITY_NORMALIZED.get(event.severidade, 0.0)
    i = OPERATIONAL_IMPACT_WEIGHTS.get(event.tipo, UNKNOWN_OPERATIONAL_IMPACT)
    u = _calcular_urgencia(event, historico)
    return _clamp_score(s * i * u)          # confiança saiu da multiplicação
# ao criar Event: event.evidence_quality = evidence_quality(trust); event.needs_verification = event.evidence_quality != "boa"
```
Ordenação na API: `ORDER BY severidade DESC, needs_verification ASC?` **Não.** Ordenar por `priority_score DESC`; `needs_verification` é **selo**, não fator de ordem.
- **Testes necessários:** dois eventos de mesma severidade com trust 0.95 e 0.2 têm **o mesmo** `priority_score` e `needs_verification` diferente; sensor travado a 120 °C aparece no topo marcado "verificar sensor".
- **Critério de aceite:** teste acima verde; `docs/ATTENTION_ENGINE.md` atualizado com a fórmula nova e a justificativa.
- **Evidência de conclusão:** teste + trecho do doc.
- **Risco:** ruído (sensor ruim gerando muitos P1). Mitigação: cooldown já existente + agrupamento por máquina na UI (S3-T5).
- **Relação com a estratégia:** pilar "confiança operacional" passa a *informar* em vez de *esconder*.

#### S1-T4 · Fila do Service Worker por item (sem head-of-line blocking)
- **Objetivo:** uma mensagem inválida não pode travar as demais, e nenhuma pode sumir.
- **Contexto:** `public/sw.js`: `shouldRetryStatus` enfileira só 408/429/5xx; `syncTelemetriaData` percorre a fila e **lança** em qualquer não-2xx.
- **Problema atual:** um 400 permanente (payload inválido) ou 401 (token expirado) interrompe o laço; itens atrás ficam presos para sempre.
- **Estado desejado:** cada item tem estado `pending | retrying | rejected | auth_blocked`, `attempts`, `last_error`, `next_attempt_at`; 2xx apaga; 4xx permanente vira `rejected` (visível, reprocessável); 401 pausa **toda** a fila e pede login; 5xx/408/429 com backoff exponencial.
- **Dependências · Pré-requisitos:** nenhuma · nenhuma.
- **Arquivos prováveis:** `frontend-next/public/sw.js`, `frontend-next/src/components/ServiceWorkerBridge.tsx`, `frontend-next/src/components/ApiStatusIndicator.tsx`.
- **Implementação esperada:**
```js
async function syncTelemetriaData() {
  const db = await openDb();
  const items = (await readAll(db)).filter(i => i.state !== 'rejected' && (i.next_attempt_at ?? 0) <= Date.now());
  let synced = 0;
  for (const item of items) {
    let response;
    try {
      response = await fetch(item.url, { method: 'POST', headers: buildHeaders(item.headers), body: JSON.stringify(item.payload) });
    } catch { await bump(db, item, 'retrying', 'rede'); continue; }          // continua os demais

    if (response.ok) { await deleteItem(db, item.localId); synced++; continue; }
    if (response.status === 401) { await markAll(db, 'auth_blocked'); await notifyClients({ type: 'AUTH_REQUIRED' }); break; }
    if (shouldRetryStatus(response.status)) { await bump(db, item, 'retrying', `HTTP ${response.status}`); continue; }
    await setState(db, item, 'rejected', `HTTP ${response.status}: ${await safeText(response)}`);   // 400/403/404/409/422
  }
  await notifyClients({ type: 'TELEMETRY_SYNC_RESULT', synced, pending: await countBy(db) });
}
```
- **Testes necessários:** teste de unidade do SW com `fetch` mockado: fila `[ok, 400, ok]` resulta em 2 enviados e 1 `rejected`; fila com 401 pausa tudo; 503 reagenda com backoff. (Playwright já existe em `frontend-next/tests/`.)
- **Critério de aceite:** os três cenários verdes; UI mostra contagem de `pending`, `rejected`, `auth_blocked`.
- **Evidência de conclusão:** saída dos testes + captura do indicador.
- **Risco:** `rejected` acumular sem ninguém ver. Mitigação: contador no `ApiStatusIndicator` e botão "reprocessar".
- **Relação com a estratégia:** sem isso, a promessa "nenhuma mensagem some" é falsa no lado do navegador.

#### S1-T5 · Contrato de tempo para dispositivo sem relógio
- **Objetivo:** hora confiável (ou explicitamente não confiável) em toda leitura.
- **Contexto:** ESP32 sem NTP offline não tem horário; o contrato exige `timestamp`. Proposta de solução do Ultimato 1.1/2.6: RTC DS3231, ou o gateway carimba, ou `boot_id` + contador.
- **Problema atual:** nenhum campo diz *de onde veio* a hora; `grep -ri 'boot_id\|time_source' api_tcc simulators` retorna vazio.
- **Estado desejado:** `boot_id` (UUID por boot), `uptime_ms` (contador monotônico), `time_source ∈ {rtc, gateway, ntp, unsynced}`, `clock_skew_ms` calculado no gateway quando possível. Ordenação sempre por `event_time`; reconstrução temporal reaplicada ao ressincronizar.
- **Dependências · Pré-requisitos:** S1-T2 (mesma migration 0027) · nenhum.
- **Arquivos prováveis:** `api_tcc/models.py`, migration 0027, `services/telemetria.py`, `services/data_health.py`, `simulators/edge_client.py`, `docs/CONTRATO_TELEMETRIA_V1.md`.
- **Implementação esperada:** `time_source='unsynced'` ⇒ `event_time_confidence` baixa ⇒ **penalidade explícita no Trust Score** (fator "hora do dispositivo não confiável") e leitura carimbada com `ingested_at - uptime_delta` quando houver `boot_id` conhecido. Algoritmo de reconstrução: para leituras do mesmo `boot_id`, `event_time = anchor_time + (uptime_ms - anchor_uptime_ms)`, onde `anchor` é a primeira leitura do boot que chegou com `time_source != unsynced` ou a hora do gateway no primeiro contato.
- **Testes necessários:** lote fora de ordem de um mesmo `boot_id` é reordenado corretamente; `unsynced` reduz trust e aparece nos fatores; dois boots não se misturam.
- **Critério de aceite:** teste de lote atrasado de 6 horas não aparece como "agora" (`event_time` ≠ `ingested_at`).
- **Evidência de conclusão:** teste + tabela de reconstrução.
- **Risco:** deriva de relógio do RTC; documentar a precisão (DS3231 ±2 ppm típico, conferir datasheet na S8).
- **Relação com a estratégia:** o diferencial "reconstrução temporal" só existe se a hora for tratada como dado com proveniência.

#### S1-T6 · Semântica de ACK e remoção da outbox
- **Objetivo:** nenhuma mensagem é removida antes de confirmação **de persistência**, e o comportamento em cada falha é conhecido.
- **Contexto:** `edge_client.py` tem `outbox`, `edge_cursor.last_acked_sequence`, `payload_hash`; o servidor devolve status por item no lote.
- **Problema atual:** o contrato de ACK não está escrito; não há teste de queda **entre** o envio e a confirmação (a janela clássica de duplicata/perda).
- **Estado desejado:** semântica **at-least-once + idempotência** documentada; ACK só conta se o servidor devolver `status ∈ {criado, duplicata}` com o `payload_hash` que o cliente enviou; divergência de hash vira `conflito` (DLQ), nunca "ok".
- **Dependências · Pré-requisitos:** S1-T5 · nenhum.
- **Arquivos prováveis:** `simulators/edge_client.py`, `api_tcc/api/views_ingestao.py`, `services/telemetria.py`, `docs/SYNC_PROTOCOL_V1.md` (esqueleto; fechado em S6-T1).
- **Implementação esperada:** resposta do servidor por item:
```json
{ "message_id": "uuid", "sequence_number": 18422, "status": "acked|duplicate|rejected|conflict",
  "payload_hash": "sha256...", "last_acked_sequence": 18422 }
```
Regra do cliente: `DELETE` da outbox só quando `status ∈ {acked, duplicate}` **e** `payload_hash` bate. `conflict` (mesmo `(device, message)` com hash diferente) vai para a DLQ do servidor com `contexto=SYNC` e fica `blocked` no cliente.
- **Testes necessários:** (a) kill do cliente após `POST` e antes de ler a resposta: ao reiniciar reenvia, servidor responde `duplicate`, outbox esvazia, banco com 1 linha; (b) mesmo `message_id` com payload diferente: `conflict`; (c) servidor retorna 500 no meio do lote: itens anteriores confirmados não reenviam.
- **Critério de aceite:** três testes verdes; documento descreve a garantia exata ("entrega pelo menos uma vez, efeito exatamente uma vez nos cenários documentados").
- **Evidência de conclusão:** testes + `docs/SYNC_PROTOCOL_V1.md` (versão inicial).
- **Risco:** prometer "zero perda" sem condição. **Formulação permitida:** "sincronização resiliente com deduplicação e recuperação de falhas, validada nos cenários documentados" (Ultimato 1.7).
- **Relação com a estratégia:** base técnica do pilar 1.

#### S1-T7 · Dividir `views_ingestao.py` e impor limites
- **Objetivo:** módulos coesos e ingestão com defesa de volume.
- **Contexto:** `views_ingestao.py` tem 886 linhas (regra do `CLAUDE.md`: sugerir refatoração acima de 300). `IngestaoLoteView` aceita até 500 itens, processa um a um.
- **Problema atual:** responsabilidades misturadas (ingestão, lote, últimas leituras, métricas, anomalias, manutenção, status MQTT) e nenhum backpressure.
- **Estado desejado:** `views_ingestao.py` (POST single), `views_lote.py`, `views_leituras.py`, `views_metricas.py`, `views_status.py`; `DATA_UPLOAD_MAX_MEMORY_SIZE` definido; `429` + `Retry-After` quando o lote excede a taxa; resposta inclui `accepted/rejected/duplicates`.
- **Dependências · Pré-requisitos:** S1-T6 · suíte verde.
- **Arquivos prováveis:** `api_tcc/api/views_ingestao.py` → quebrar, `api_tcc/urls.py`, `setup/settings.py`.
- **Implementação esperada:** extração mecânica, **sem mudança de comportamento** (URLs idênticas), cada arquivo < 300 linhas; throttle por `device_id` (hoje por `maquina_id`).
- **Testes necessários:** suíte inteira idêntica antes/depois; teste novo: lote com 501 itens = 400; lote acima da taxa = 429 com header.
- **Critério de aceite:** nenhum arquivo de view > 300 linhas; mesmos status e payloads (testes de contrato existentes verdes).
- **Evidência de conclusão:** `wc -l` antes/depois no PR.
- **Risco:** quebra de import circular. Mitigação: mover primeiro, ajustar `urls.py` depois, um commit por view.
- **Relação com a estratégia:** manutenibilidade e prova de que a refatoração não muda semântica.

#### S1-T8 · Teste de contrato cruzado (golden files)
- **Objetivo:** impedir que o bug de S1-T1 volte.
- **Contexto:** hoje cada camada testa sua regra isoladamente.
- **Problema atual:** testes unitários passam enquanto as camadas divergem.
- **Estado desejado:** `contracts/fixtures/classificacao.json` (entrada → classe esperada) lido por **backend, `edge_client`, e (depois) firmware e front**.
- **Dependências · Pré-requisitos:** S1-T1, S1-T2 · nenhum.
- **Arquivos prováveis:** `contracts/fixtures/*.json`, `api_tcc/tests/test_contract_parity.py`, `simulators/test_edge_client.py`, `frontend-next/tests/contract.test.ts`.
- **Implementação esperada:**
```python
import json
from pathlib import Path
from api_tcc.contracts import classify, transmission_class
from simulators.edge_client import classify_priority

FIX = json.loads((Path("contracts/fixtures/classificacao.json")).read_text())

def test_paridade_backend_borda():
    for case in FIX:
        sev = max((classify("temperatura", case["temperatura"]), classify("vibracao", case["vibracao"])), key=["NORMAL","ATENCAO","CRITICO"].index)
        assert case["severidade"] == sev
        assert case["classe"] == classify_priority(case) == transmission_class(sev, case.get("evidence_quality","boa"), False)
```
Gerar o arquivo de fixtures com a **varredura de fronteiras** (valores logo abaixo, no limite e logo acima de cada limiar).
- **Testes necessários:** o próprio teste; no CI roda sempre.
- **Critério de aceite:** teste verde nas 3 camadas (backend, borda, front).
- **Evidência de conclusão:** saída do CI.
- **Risco:** fixtures desatualizadas. Mitigação: gerar a partir de `severity.v1.json`.
- **Relação com a estratégia:** a "verdade única" é verificada, não prometida.


---

### SEMANA 2 · SEGURANÇA DE FRONTEIRA E ISOLAMENTO

> **NOTA V4:** Para a primeira prova de bancada (S8-T1) usar o perfil `demo` local. Credencial por dispositivo (S2-T1/T8) é exigida antes de qualquer ambiente compartilhado ou piloto.


**Camadas:** SECURITY · TESTING · OBSERVABILITY

- **Objetivo estratégico:** nada do que a banca ou o QR code expõem pode ser vetor de abuso; e o sistema precisa **provar** que uma organização não alcança dados de outra.
- **Objetivo técnico:** MQTT com identidade e ACL por dispositivo; throttle global e lockout; registro público atrás de flag; Swagger fechado fora de dev; segredo do Gemini em header; sessão do navegador sem token em `localStorage`; matriz de testes de acesso cruzado; trilha de auditoria; ingestão com credencial por dispositivo.
- **Por que existe:** Ultimato 1.1, 1.7 e 2.4 convergem: "segurança mínima antes de qualquer piloto/QR". Estado real verificado: `allow_anonymous false` e bind em `127.0.0.1` **já existem**; o que falta é ACL por tópico, credencial por dispositivo, throttle global, flag de registro, header para o Gemini, isolamento provado.
- **Problemas que resolve:** `RegisterView` `AllowAny` sem throttle; `DEFAULT_THROTTLE_CLASSES: []`; um único usuário MQTT para todos; `Swagger public=True`; chave Gemini em URL; `HasIngestionCredential` com chave global; ausência de prova de isolamento.
- **Dependências recebidas:** S1 (`device_id` no contrato; classe de transmissão).
- **Entregáveis:** `mosquitto/acl.conf`, `scripts/provision_device.py`, flags `REGISTRATION_ENABLED` e `SWAGGER_ENABLED`, throttles globais, `AuditLog`, matriz de isolamento, sessão via cookie HttpOnly, threat model.
- **Arquivos/módulos afetados:** `mosquitto/mosquitto.conf`, `docker-compose.yml`, `api_tcc/management/commands/mqtt_listen.py`, `api_tcc/permissions.py`, `api_tcc/authentication.py`, `api_tcc/api/views_auth.py`, `setup/settings.py`, `setup/urls.py`, `api_tcc/services/agentic.py`, `api_tcc/ia/explicacao_llm.py`, `frontend-next/src/app/api/[...path]/route.ts`, `frontend-next/src/services/authService.ts`, `docs/SEGURANCA.md`.
- **Arquitetura:** identidade por dispositivo como cidadã de primeira classe (`DeviceCredential`). **Banco:** `DeviceCredential`, `AuditLog`. **Backend:** throttles, flags, auditoria. **Frontend:** BFF com cookie HttpOnly. **Hardware:** convenção de credencial por dispositivo (S8 consome). **ML/IA:** header do Gemini. **Infra:** ACL do Mosquitto, TLS planejado. **Testes:** matriz cruzada, anti-spoof de tópico. **Docs:** modelo de ameaças.
- **Experimentos:** tentar, com `mosquitto_pub`, publicar no tópico de outro dispositivo; 100 logins errados em 1 minuto; registrar 50 usuários em loop.
- **Critérios de aceitação:** todos os testes de abuso falham como esperado; `grep -rn "?key=" api_tcc` vazio; `localStorage` sem token.
- **Métricas:** requisições bloqueadas por throttle; tentativas de acesso cruzado negadas (= 100% da matriz); tópicos MQTT negados.
- **Evidências esperadas:** saída dos testes, log do Mosquitto com negação por ACL, captura do DevTools sem token no storage.
- **Riscos:** quebrar o fluxo da demo (credenciais novas). Mitigação: `provision_device.py` com perfil `demo`.
- **Decisões:** D-05 (cookie HttpOnly via BFF vs token DRF puro), D-06 (credencial por dispositivo: hash em banco vs `password_file`), D-12 (TLS no gateway local).
- **Perguntas abertas:** o QR aponta para hotspot local (sem TLS) ou para cloud (com TLS)? Resposta provisória: **hotspot local**, porque a demo prova offline (S12-T3).
- **Definition of Done da semana:** suíte de segurança verde em CI local, `docs/SEGURANCA.md` com modelo de ameaças, nenhum segredo em URL.

#### S2-T1 · MQTT com ACL por dispositivo e anti-spoof de tópico
- **Objetivo:** dispositivo A só publica em `fieldnode/A/#`; payload com `device_id` diferente do tópico é rejeitado.
- **Contexto:** hoje 1 usuário (`MQTT_USERNAME`) compartilhado; `mqtt_listen.py:115-118` só autentica **se** as variáveis existirem; tópico assinado `fieldnode/#`.
- **Problema atual:** quem tiver a senha injeta telemetria como qualquer máquina; worker sobe sem credencial se esquecerem a env.
- **Estado desejado:** um usuário por dispositivo, ACL por padrão `%u`, worker com usuário próprio de leitura, falha de boot se credencial ausente fora de DEBUG.
- **Dependências · Pré-requisitos:** S1-T5 · acesso ao `mosquitto_passwd`.
- **Arquivos prováveis:** `mosquitto/mosquitto.conf`, `mosquitto/acl.conf`, `docker-compose.yml`, `api_tcc/management/commands/mqtt_listen.py`, `scripts/provision_device.py`.
- **Implementação esperada:**
```conf
# mosquitto/acl.conf
user fieldnode-worker
topic read fieldnode/#
topic write fieldnode/_ack/#

# dispositivos: %u = usuário MQTT = device_id
pattern write fieldnode/%u/telemetria
pattern write fieldnode/%u/status
pattern read  fieldnode/_ack/%u
```
```conf
# mosquitto.conf (acrescentar)
acl_file /mosquitto/config/acl.conf
```
```python
# mqtt_listen.py: anti-spoof
def _on_message(self, client, userdata, msg):
    parts = msg.topic.split("/")                 # fieldnode/<device_id>/telemetria
    topic_device = parts[1] if len(parts) > 2 else None
    data = json.loads(msg.payload)
    if str(data.get("device_id") or data.get("maquina_id")) != topic_device:
        registrar_dlq(contexto="MQTT_SPOOF", motivo=f"topic={topic_device} payload={data.get('device_id')}")
        return
    ...
```
`provision_device.py <device_id>` gera senha aleatória, grava com `mosquitto_passwd`, imprime **uma vez** o par para gravar no firmware, registra `DeviceCredential` (hash) no Django.
- **Testes necessários:** `mosquitto_pub -u dev-A -t fieldnode/dev-B/telemetria` negado; payload com `device_id` ≠ tópico vai para DLQ; worker sem credencial falha ao iniciar quando `DEBUG=False`.
- **Critério de aceite:** três testes acima verdes; log do Mosquitto registra `Denied PUBLISH`.
- **Evidência de conclusão:** trecho de log + teste automatizado (pode usar `paho` no teste de integração).
- **Risco:** esquecer de provisionar o dispositivo da demo. Mitigação: perfil `demo` e checklist de S12-T3.
- **Relação com a estratégia:** pré-requisito do firmware (S8) e do argumento "proteção de dados".

#### S2-T2 · Throttle global, lockout e registro por flag
- **Objetivo:** login e registro deixam de ser vetor de abuso.
- **Contexto:** `DEFAULT_THROTTLE_CLASSES: []`; `RegisterView` `AllowAny`; só ingestão tem throttle.
- **Problema atual:** brute force de login e spam de contas (Ultimato 1.1, 2.4).
- **Estado desejado:** `AnonRateThrottle` e `ScopedRateThrottle` globais; `login` 5/min por IP e por usuário; `register` 3/hora por IP; `REGISTRATION_ENABLED=False` por padrão; `DEMO_MODE=True` bloqueia criação de usuário.
- **Dependências · Pré-requisitos:** nenhuma · cache configurado (usar `LocMemCache` em dev, Redis opcional em prod; **com 2 workers gunicorn, LocMem não é compartilhado**: usar cache de banco `DatabaseCache` ou Redis).
- **Arquivos prováveis:** `setup/settings.py`, `api_tcc/api/views_auth.py`, `api_tcc/api/throttles.py`.
- **Implementação esperada:**
```python
REST_FRAMEWORK |= {
  "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle", "rest_framework.throttling.UserRateThrottle"],
  "DEFAULT_THROTTLE_RATES": {"anon": "60/min", "user": "300/min", "ingestao": "120/minute", "login": "5/min", "register": "3/hour"},
}
CACHES = {"default": {"BACKEND": "django.core.cache.backends.db.DatabaseCache", "LOCATION": "fn_cache"}}  # createcachetable
# views_auth.py
class RegisterView(APIView):
    permission_classes = [AllowAny]; throttle_scope = "register"
    def post(self, request):
        if not settings.REGISTRATION_ENABLED or settings.DEMO_MODE:
            return Response({"detail": "Registro desabilitado."}, status=403)
```
Lockout adicional: após 5 falhas por usuário em 15 min, resposta 429 sem revelar se o usuário existe (mensagem idêntica para usuário inexistente).
- **Testes necessários:** 6º login errado em 1 min = 429; registro com flag falsa = 403; resposta idêntica para usuário existente/inexistente.
- **Critério de aceite:** testes verdes sob 2 workers (rodar o teste contra gunicorn do Compose).
- **Evidência de conclusão:** saída do teste + trecho de log.
- **Risco:** throttle por IP no hotspot da banca (muita gente atrás do mesmo NAT). Mitigação: limites generosos para `anon` de leitura e restritos só em `login`/`register`.
- **Relação com a estratégia:** o QR code na tela não pode virar porta aberta.

#### S2-T3 · Swagger e documentação fora de dev
- **Objetivo:** documentação interativa não pública em produção/demo.
- **Contexto:** `setup/urls.py:23` `public=True`; rota `/` redireciona para `/swagger/`.
- **Problema atual:** qualquer pessoa vê (e tenta usar) todos os endpoints.
- **Estado desejado:** `SWAGGER_ENABLED` (padrão `DEBUG`); fora disso exige `is_staff`.
- **Dependências · Pré-requisitos:** nenhuma · nenhum.
- **Arquivos prováveis:** `setup/urls.py`, `setup/settings.py`.
- **Implementação esperada:** `permission_classes=(permissions.IsAdminUser,)` no `get_schema_view` quando `SWAGGER_ENABLED=False`; `/` redireciona para o front.
- **Testes necessários:** anônimo = 401/403 em `/swagger/` com flag desligada.
- **Critério de aceite:** teste verde.
- **Evidência de conclusão:** teste.
- **Risco:** baixo.
- **Relação com a estratégia:** reduz superfície visível.

#### S2-T4 · Chave do Gemini em header, sem vazar em log
- **Objetivo:** segredo fora de URL e de log.
- **Contexto:** `agentic.py:96` e `explicacao_llm.py:72` usam `?key=`.
- **Problema atual:** chave em log de proxy e em stack trace de `requests`.
- **Estado desejado:** header `x-goog-api-key`; filtro de log que mascara `key=` e `x-goog-api-key`; timeout de 2 s com **circuit breaker** (já exigido no plano do projeto: falha do provedor não congela a UI).
- **Dependências · Pré-requisitos:** nenhuma · nenhum.
- **Arquivos prováveis:** `api_tcc/services/agentic.py`, `api_tcc/ia/explicacao_llm.py`, `api_tcc/middleware.py`.
- **Implementação esperada:**
```python
resp = requests.post(GEMINI_URL, headers={"x-goog-api-key": api_key, "Content-Type": "application/json"}, json=body, timeout=2.0)
```
Filtro `RedactSecretsFilter` em `LOGGING`. Cache do resultado por `decision_id` (não chamar LLM a cada GET).
- **Testes necessários:** `test_resiliencia_llm.py` (existe) estendido: URL chamada não contém `key=`; log capturado não contém a chave; timeout vira fallback determinístico.
- **Critério de aceite:** `grep -rn "key=" api_tcc --include=*.py` só em testes/negativo.
- **Evidência de conclusão:** teste verde.
- **Risco:** baixo.
- **Relação com a estratégia:** pergunta recorrente: "Gemini é seguro para dados de empresa?" Resposta técnica: só recebe evidência que o backend monta e **autoriza** (S5-T7), nunca acesso direto ao banco.

#### S2-T5 · Sessão do navegador sem token em `localStorage`
- **Objetivo:** XSS não rouba sessão.
- **Contexto:** dívida declarada em `docs/SEGURANCA.md`; já existe BFF `app/api/[...path]/route.ts`.
- **Problema atual:** token DRF legível por qualquer script.
- **Estado desejado:** login via BFF; token guardado em cookie `HttpOnly; Secure (quando HTTPS); SameSite=Lax`; BFF injeta `Authorization` ao chamar o Django; logout apaga cookie e invalida token; proteção CSRF por header customizado exigido nas mutações.
- **Dependências · Pré-requisitos:** S2-T2 · D-05.
- **Arquivos prováveis:** `frontend-next/src/app/api/[...path]/route.ts`, `frontend-next/src/app/login/page.tsx`, `frontend-next/src/services/authService.ts`, `frontend-next/src/components/SessionGate.tsx`, `frontend-next/public/sw.js` (o SW precisa de credencial: usar `credentials: 'include'`, não header manual).
- **Implementação esperada:** `POST /api/auth/login` (Next) chama Django, recebe token, `Set-Cookie`; `route.ts` lê o cookie e repassa `Authorization: Token ...`; mutações exigem `X-FieldNode-CSRF: 1`.
- **Testes necessários:** E2E Playwright: após login, `localStorage`/`sessionStorage` sem chave de token; mutação sem header CSRF = 403; logout invalida.
- **Critério de aceite:** DevTools > Application sem token legível por JS.
- **Evidência de conclusão:** captura + teste.
- **Risco:** SW e cookie HttpOnly interagem mal. Mitigação: SW sempre `fetch` ao mesmo origin (BFF) com `credentials: 'include'`.
- **Relação com a estratégia:** fecha a dívida que todo avaliador de segurança aponta.

#### S2-T6 · Matriz de isolamento entre organizações (acesso cruzado)
- **Objetivo:** responder com teste "existe algum caminho pelo qual um usuário da organização A acessa dados da B?".
- **Contexto:** `Organization`, `Membership`, `Machine.organization`; `test_permissions.py` existe.
- **Problema atual:** sem matriz exaustiva; endpoint novo pode nascer sem filtro.
- **Estado desejado:** teste parametrizado que percorre **todas** as rotas de `api_tcc/urls.py` e falha se uma rota não estiver declarada na matriz.
- **Dependências · Pré-requisitos:** S2-T2 · nenhum.
- **Arquivos prováveis:** `api_tcc/tests/test_tenant_isolation.py`, `api_tcc/permissions.py`, views (filtros de queryset).
- **Implementação esperada:**
```python
ROTAS = {  # nome da rota -> (método, como montar o recurso da org A, status esperado para user da org B)
 "decision-action": ("PATCH", lambda a: {"decision_id": a.decision.id}, 404),
 "machine-data-health": ("GET", lambda a: {"machine_id": a.machine.external_code}, 404),
 "events-list": ("GET", None, "lista sem itens da org A"),
 "prescricao-maquina": ("GET", lambda a: {"maquina_id": a.machine.external_code}, 404),
 "maquinas-posicao": ("GET", None, "sem máquinas da org A"),
 "relatorio-exportar": ("GET", None, "sem linhas da org A"),
 "dlq-list": ("GET", None, "sem entradas da org A"),
 ...
}
def test_toda_rota_esta_na_matriz():
    nomes = {p.name for p in get_resolver().url_patterns[...] if p.name}
    assert nomes - set(ROTAS) - ROTAS_PUBLICAS == set(), "Rota nova sem teste de isolamento"
```
Retornar **404** (não 403) para recurso de outra organização, para não vazar existência.
- **Testes necessários:** a própria matriz; incluir `DEMO_MODE` (só `is_demo=True` é público).
- **Critério de aceite:** 100% das rotas na matriz e verdes.
- **Evidência de conclusão:** saída do teste.
- **Risco:** descobrir vazamento real. **É o ponto da tarefa.** Corrigir antes de qualquer exposição.
- **Relação com a estratégia:** pergunta 5 do pressure test ("como protege dados?") com prova.

#### S2-T7 · Trilha de auditoria e normalização de rotas
- **Objetivo:** toda ação sensível deixa rastro imutável.
- **Contexto:** Decision já guarda `decidido_por`/`decidido_em`, mas login, registro, mudança de papel e criação de credencial não.
- **Problema atual:** sem log de auditoria; rotas duplicadas com e sem barra confundem logs.
- **Estado desejado:** `AuditLog(actor, action, object_type, object_id, ip, user_agent, correlation_id, before_hash, after_hash, criado_em)` append-only; admin somente leitura; rotas sem barra final removidas ou redirecionadas.
- **Dependências · Pré-requisitos:** S2-T2 · nenhum.
- **Arquivos prováveis:** `api_tcc/models.py`, migration, `api_tcc/services/audit.py`, `api_tcc/urls.py`.
- **Implementação esperada:** `audit.record("decision.approve", decision, request)`; correlation ID reaproveitado de `middleware.py`.
- **Testes necessários:** aprovação de decisão cria 1 `AuditLog` com `correlation_id`; tentativa de `update`/`delete` em `AuditLog` via ORM falha (override de `save`/`delete`).
- **Critério de aceite:** testes verdes.
- **Evidência de conclusão:** tela do admin read-only.
- **Risco:** volume. Mitigação: só ações sensíveis; retenção definida em S10-T6.
- **Relação com a estratégia:** requisito da escada de autonomia (Leviatã fase 14: "nenhum salto sem trilha de auditoria").

#### S2-T8 · Credencial de ingestão por dispositivo e modelo de ameaças
- **Objetivo:** substituir a chave global `FIELDNODE_API_KEY` por credencial por dispositivo e documentar o que se defende.
- **Contexto:** `HasIngestionCredential` (global). Risco registrado no v2: chave extraível de flash de ESP32 permite forjar telemetria.
- **Problema atual:** vazou uma chave = vazaram todos.
- **Estado desejado:** `DeviceCredential(device_id, key_hash, created_at, revoked_at, last_seen_at)`; `X-Device-Id` + `X-Device-Key`; revogação por dispositivo; `docs/SEGURANCA.md` com STRIDE resumido.
- **Dependências · Pré-requisitos:** S2-T1 · nenhum.
- **Arquivos prováveis:** `api_tcc/models.py`, `api_tcc/permissions.py`, `scripts/provision_device.py`, `docs/SEGURANCA.md`.
- **Implementação esperada:** comparação em tempo constante (`hmac.compare_digest`) do hash; chave de 32 bytes aleatórios; rotação sem quebrar dispositivo (aceitar chave antiga por janela de 24 h se `rotating=True`). **Flash encryption** do ESP32 listada como mitigação de S8 (`ARCHITECT_NOW`).
- **Testes necessários:** chave revogada = 401; chave de A não autoriza payload com `device_id` B (403).
- **Critério de aceite:** testes verdes; `FIELDNODE_API_KEY` legada só aceita em `DEBUG`.
- **Evidência de conclusão:** testes + `SEGURANCA.md`.
- **Risco:** complexidade de provisionamento para a demo. Mitigação: perfil `demo` com uma credencial documentada **somente** em ambiente local.
- **Relação com a estratégia:** resposta honesta ao "e se alguém clonar o sensor?".

---

### SEMANA 3 · COMMAND CENTER (O DIFERENCIAL APARECE NA TELA)

> **NOTA V5:** A home nova, os cards por equipamento e o drill-down estão na **S20**. A faixa 'Atenção agora' (S3-T3) continua e alimenta os cards (S20-T2). S3-T8 e S3-T10 passam a **P3**.


> **NOTA V4:** S3 é pré-requisito do pilar P1. PWA offline e mapa offline estão em S13-T3; HTTPS local em S13-T12.


**Camadas:** IMPLEMENTATION · VALIDATION · TESTING

- **Objetivo estratégico:** a banca, a usina e o outro grupo precisam **ver** o que só o FieldNode tem: confiança do dado, fila de atenção por prioridade, decisão com aprovação e desfecho. Front deixa de ser vitrine e vira cockpit.
- **Objetivo técnico:** ligar o `frontend-next` a `events`, `decisions`, `machines/<id>/health`; remover todo mock; padronizar estados (carregando, sem histórico, desatualizado, offline, erro, inválido); filtros consistentes entre dashboard, máquinas e mapa; bottom sheet no mapa mobile.
- **Por que existe:** grep em `frontend-next/src` por `decision|trust|priority|prioridade` retorna zero arquivos. O diferencial está só na API.
- **Problemas que resolve:** mocks (`DashboardMachineData.tsx`), mistura de severidade com observabilidade, popup grande no mobile, ausência de botão de ação.
- **Dependências recebidas:** S1 (contrato único, `evidence_quality`, escala de vibração), S2 (sessão por cookie, permissões).
- **Entregáveis:** `DataStateBoundary`, `SimulatedBadge`, clientes tipados (zod), faixa "Atenção agora", `TrustBadge` com fatores, `/decisoes`, filtros rápidos, bottom sheet, painel de contato, E2E Playwright.
- **Arquivos/módulos afetados:** `frontend-next/src/components/*`, `src/app/{dashboard,maquinas,mapa,decisoes}`, `src/schemas/*`, `src/services/*`, `src/data/mockData.ts` (remover), `api_tcc/api/views_events.py`, `views_decisions.py`, `serializers.py`.
- **Arquitetura:** o front consome **apenas** API; nenhuma regra de negócio duplicada (limiares vêm do contrato gerado). **Banco:** `LeituraTelemetria.data_origin`. **Backend:** query params de filtro, serializer de saúde com fatores legíveis. **Frontend:** núcleo. **Hardware:** nenhuma. **ML/IA:** exibir `contributing_feature` e explicação. **Infra:** nenhuma. **Segurança:** UI nunca é a única barreira (permissões no backend). **Testes:** Playwright E2E. **Docs:** capturas para README.
- **Experimentos:** teste de 5 segundos com alguém de fora do grupo: "o que precisa de atenção agora?" (meta: responder em menos de 5 s olhando só o topo do dashboard).
- **Critérios de aceitação:** `grep -rn "mockData" frontend-next/src` vazio; fluxo "evento crítico → decisão → aprovar" executável só pela UI.
- **Métricas:** tempo para achar a decisão crítica; chamadas HTTP por carga de dashboard (sem N+1); Lighthouse acessibilidade ≥ 90.
- **Evidências esperadas:** gravação de tela, E2E verde, `grep` limpo.
- **Riscos:** regressão visual; dado real escasso no dashboard (parece vazio). Mitigação: modo demo com selo SIMULADO, nunca mock silencioso.
- **Decisões:** D-07 (faixas P1/P2/P3 e seus cortes), D-16 (score de operador: não fazer sem fundamento).
- **Perguntas abertas:** polling vs SSE/WebSocket? Resposta provisória: **polling de 3 a 5 s** (já é o padrão); SSE `DEFER`.
- **Definition of Done da semana:** E2E verde; gravação do fluxo completo; `CLAIMS_VS_CODE.md` atualizado (trust, prioridade e decisão passam a `IMPLEMENTADO` de ponta a ponta).

#### S3-T1 · Remover mocks, criar `DataStateBoundary` e selo SIMULADO
- **Objetivo:** nunca mostrar série inventada como telemetria real.
- **Contexto:** `DashboardMachineData.tsx:26,40-42` importa `mockRpmSeries`, `mockTemperaturaSeries`, `mockVibracaoSeries`; `mockData.ts` também tem `mockFleetSummary` e `mockTrendSeries`.
- **Problema atual:** fallback silencioso.
- **Estado desejado:** estados explícitos e `data_origin ∈ {medido, simulado, calculado, estimado}` vindo da API.
- **Dependências · Pré-requisitos:** S1-T5 · migration `data_origin` (default `simulado` para tudo gerado por scripts).
- **Arquivos prováveis:** `src/components/ui/FeedbackStates.tsx`, novo `DataStateBoundary.tsx`, `SimulatedBadge.tsx`, `DashboardMachineData.tsx`, `src/data/mockData.ts` (apagar), `api_tcc/models.py`, `serializers.py`.
- **Implementação esperada:**
```tsx
type DataState = 'loading' | 'ok' | 'sem_historico' | 'desatualizado' | 'offline' | 'erro' | 'invalido';
export function DataStateBoundary({ state, simulated, children, onRetry }: Props) {
  switch (state) {
    case 'loading': return <SkeletonGrid />;
    case 'sem_historico': return <EmptyState title="Sem histórico suficiente" hint="Aguardando pelo menos N leituras" />;
    case 'desatualizado': return <>{children}<StaleBanner /></>;  // mostra o dado COM aviso, nunca esconde
    case 'offline': return <OfflineBanner onRetry={onRetry} />;
    case 'erro': return <ErrorState onRetry={onRetry} />;
    default: return <>{simulated && <SimulatedBadge />}{children}</>;
  }
}
```
Regra de "desatualizado": `agora - event_time_ultima_leitura > 3 × intervalo_esperado` (intervalo vem do contrato/máquina).
- **Testes necessários:** componente com cada estado; teste que garante que **nenhum** import de `mockData` existe fora de testes/storybook.
- **Critério de aceite:** `grep -rn "mockData" frontend-next/src` vazio; API fora do ar mostra erro, não gráfico.
- **Evidência de conclusão:** capturas dos 7 estados.
- **Risco:** dashboard vazio na demo. Mitigação: seed demo **com selo**.
- **Relação com a estratégia:** protege a honestidade (princípio do Ultimato 2.1: "um único dado fake derruba a credibilidade de tudo").

#### S3-T2 · Clientes tipados e hook de dados
- **Objetivo:** contrato de API validado em tempo de execução.
- **Contexto:** `src/schemas/` já tem `maquinas`, `prescricoes`, `relatorios`, `telemetria` (zod).
- **Problema atual:** nenhum schema para `events`, `decisions`, `health`.
- **Estado desejado:** `schemas/{eventos,decisoes,saude}.ts` + `services/{eventService,decisionService,healthService}.ts` + hook `usePolling(fetcher, ms)` com `AbortController`.
- **Dependências · Pré-requisitos:** S1 · endpoints existentes (`/api/events/`, `/api/decisions/`, `/api/machines/<id>/health/`).
- **Arquivos prováveis:** `src/schemas/*`, `src/services/*`, `src/lib/usePolling.ts`.
- **Implementação esperada:** `safeParse`; payload inválido vira estado `invalido` (nunca quebra a tela); polling pausa com aba oculta (`visibilitychange`).
- **Testes necessários:** schema rejeita payload malformado; hook cancela requisição ao desmontar.
- **Critério de aceite:** zero `any`; testes verdes.
- **Evidência de conclusão:** `tsc --noEmit` limpo.
- **Risco:** polling duplicado entre componentes. Mitigação: cache compartilhado por chave.
- **Relação com a estratégia:** base de todas as telas.

#### S3-T3 · Faixa "Atenção agora" e fila P1/P2/P3
- **Objetivo:** o topo do dashboard responde "o que exige atenção agora?".
- **Contexto:** `priority_score` existe na API e é invisível.
- **Problema atual:** gráficos antes de decisões.
- **Estado desejado:** faixa no topo: "3 decisões pendentes · 1 risco crítico · 2 eventos críticos · 1 máquina com dados instáveis" + botão "Resolver agora" que abre a fila.
- **Dependências · Pré-requisitos:** S3-T2 · D-07.
- **Arquivos prováveis:** `src/app/dashboard/page.tsx`, novo `AttentionStrip.tsx`, `contracts/attention.v1.json`.
- **Implementação esperada:** bandas em `attention.v1.json` (heurística calibrável): `P1 >= 0.60`, `P2 >= 0.30`, `P3 < 0.30`; **qualquer** `CRITICO` é P1 independente do score (regra de segurança). Item com `needs_verification` recebe selo "verificar sensor".
- **Testes necessários:** E2E: evento crítico novo aparece em P1 em até 1 ciclo de polling; evento de sensor suspeito aparece com selo.
- **Critério de aceite:** teste dos 5 segundos (experimento da semana).
- **Evidência de conclusão:** gravação + teste.
- **Risco:** bandas arbitrárias. Documentar como heurística (honestidade).
- **Relação com a estratégia:** é a "fila de atenção automática" que as grandes não expõem (Ultimato 2.6).

#### S3-T4 · Trust Score com explicação legível
- **Objetivo:** "78/100" nunca aparece sozinho.
- **Contexto:** `MachineDataHealth.sinais_de_alerta` (JSON) e `/api/machines/<id>/health/`.
- **Problema atual:** sem badge no front; fatores em formato técnico.
- **Estado desejado:** `TrustBadge` com cor e tooltip: "Dados 78% confiáveis · 2 lacunas de leitura · sensor repetindo valor · hora do dispositivo não confiável".
- **Dependências · Pré-requisitos:** S3-T2, S1-T5 · nenhum.
- **Arquivos prováveis:** `src/components/TrustBadge.tsx`, `StatusBadge.tsx`, `MapClient.tsx`, `TelemetryMachineCard.tsx`, `api_tcc/services/data_health.py` (códigos estáveis dos fatores).
- **Implementação esperada:** backend devolve `[{codigo:"GAP_LEITURA", peso:-0.12, detalhe:"42 min"}]`; front mapeia `codigo → texto pt-BR` em um único dicionário.
- **Testes necessários:** cada código tem texto; fator desconhecido cai em "Outro fator (código)", nunca some.
- **Critério de aceite:** badge visível em máquinas, mapa e detalhes.
- **Evidência de conclusão:** capturas.
- **Risco:** só mostrar fatores **realmente calculados** (Ultimato 1.7).
- **Relação com a estratégia:** pilar 2.

#### S3-T5 · Central de decisões (lista, detalhe, ação, histórico)
- **Objetivo:** a recomendação vira ferramenta de trabalho.
- **Contexto:** `PATCH /api/decisions/<id>/` com máquina de estados; `outcome_texto`.
- **Problema atual:** nenhuma tela chama o endpoint.
- **Estado desejado:** `/decisoes` (fila) e painel na máquina: o que foi detectado, evidência (leituras, limiar, janela), qualidade do dado, regra/versão, ação recomendada, botões **Aprovar · Rejeitar · Adiar · Marcar executada**, campo de desfecho, linha do tempo (quem, quando).
- **Dependências · Pré-requisitos:** S3-T2, S3-T4, S2-T5 · nenhum.
- **Arquivos prováveis:** `src/app/decisoes/page.tsx`, `src/components/DecisionCard.tsx`, `DecisionTimeline.tsx`, `PrescricaoModal.tsx` (consolidar), `api_tcc/api/views_decisions.py`.
- **Implementação esperada:** botões só habilitados para transições válidas (receber `transicoes_permitidas` do backend para não duplicar a máquina de estados); erro 400 mostra a razão; atualização otimista com reversão.
- **Testes necessários:** E2E: PENDENTE → APROVADA → EXECUTADA com desfecho; transição inválida mostrada como erro; usuário sem papel não vê botões.
- **Critério de aceite:** fluxo completo pela UI.
- **Evidência de conclusão:** gravação.
- **Risco:** "resultado informado pelo operador" ≠ "eficácia comprovada": a UI rotula **"resultado informado"**.
- **Relação com a estratégia:** pilar 3 visível.

#### S3-T6 · Máquinas: filtros rápidos e separação severidade × observabilidade
- **Objetivo:** responder "o que exige atenção agora?" na tela de máquinas.
- **Contexto:** Ultimato 1.7 (prioridade 2).
- **Problema atual:** máquina sem telemetria há horas aparece como "normal".
- **Estado desejado:** filtros: **Críticas · Precisam de atenção · Normais · Sem dados recentes**; parâmetros de URL compartilhados com dashboard e mapa; backend filtra (mesma definição de "crítica" em todo lugar).
- **Dependências · Pré-requisitos:** S3-T2 · nenhum.
- **Arquivos prováveis:** `src/app/maquinas/page.tsx`, `src/components/FleetGrid.tsx`, `api_tcc/api/viewsets.py` (filtros), `api_tcc/api/views_events.py`.
- **Implementação esperada:** `GET /api/machines/?estado=critica|atencao|normal|sem_dados&fabricante=&modelo=`; **"sem_dados" é problema de observabilidade, não "tudo normal"**.
- **Testes necessários:** máquina com leitura de 3 h atrás cai em `sem_dados`; máquina crítica offline continua `critica`.
- **Critério de aceite:** mesma contagem no dashboard, máquinas e mapa para o mesmo filtro.
- **Evidência de conclusão:** teste de consistência + captura.
- **Risco:** definição de "atenção" divergir de S1-T1. Fonte única: contrato.
- **Relação com a estratégia:** elimina um falso "tudo normal".

#### S3-T7 · Mapa mobile: bottom sheet e filtros em gaveta
- **Objetivo:** o popup não esconde o mapa.
- **Contexto:** problema conhecido do mapa no mobile.
- **Problema atual:** painel grande sem fechar.
- **Estado desejado:** bottom sheet compacta (`CH-03 · Crítico · dados 78% · Temp 96 °C · Vibração · [Ver decisão]`), botão X acessível, altura máxima 45%, gaveta de filtros fechável, estado preservado.
- **Dependências · Pré-requisitos:** S3-T4, S3-T6 · nenhum.
- **Arquivos prováveis:** `MapClient.tsx`, `FleetMap.tsx`, `MapaFrota.tsx` (três componentes de mapa: **consolidar em um**), `app/mapa/page.tsx`.
- **Implementação esperada:** foco preso na sheet, `Esc` fecha, `aria-modal`, swipe para baixo fecha.
- **Testes necessários:** Playwright com viewport 390×844: abrir, fechar, filtros persistem; existe `tests/playwright_map_test.js` para estender.
- **Critério de aceite:** mapa sempre visível ≥ 55% da altura com a sheet aberta.
- **Evidência de conclusão:** captura mobile.
- **Risco:** três componentes de mapa duplicados; escolher um (D-17).
- **Relação com a estratégia:** pedido explícito do grupo.

#### S3-T8 · Painel "Quem está por trás do FieldNode"
- **Objetivo:** humanizar sem virar currículo.
- **Contexto:** pedido do grupo (botão de contato criativo).
- **Problema atual:** inexistente.
- **Estado desejado:** botão discreto no canto abre painel com nome, papel no projeto, GitHub, LinkedIn, e-mail e uma frase curta de cada integrante; **links reais, sem perfis fictícios**.
- **Dependências · Pré-requisitos:** nenhuma · dados reais dos 4 integrantes (Paola, Ana, Giovana, Vinícius).
- **Arquivos prováveis:** `src/components/TeamPanel.tsx`, `src/data/team.ts`.
- **Implementação esperada:** animação discreta (respeitar `prefers-reduced-motion`).
- **Testes necessários:** links com `rel="noopener noreferrer"`; foco/teclado.
- **Critério de aceite:** acessível por teclado, sem layout shift.
- **Evidência de conclusão:** captura.
- **Risco:** pessoal. Só publicar o que cada integrante autorizar (LGPD básica).
- **Relação com a estratégia:** acabamento de produto, **depois** do que é funcional.

#### S3-T9 · Busca global, tooltips, contraste e redundância de botões
- **Objetivo:** os refinamentos do Leviatã (fase 16) que já eram pedido do grupo.
- **Contexto:** lista `known_improvements`: busca global, tooltips informativos, correções de contraste, redundância de botões, fila vs resumo.
- **Problema atual:** botões repetidos entre páginas; contraste não auditado.
- **Estado desejado:** `Ctrl+K` busca máquinas, operadores, decisões; tooltips explicam cada métrica e o limiar usado; contraste ≥ 4.5:1 (texto) e 3:1 (ícones) em tema claro e escuro; um botão por ação; "fila" (itens a tratar) separada do "resumo geral".
- **Dependências · Pré-requisitos:** S3-T3 · nenhum.
- **Arquivos prováveis:** `Sidebar.tsx`, `AppShell.tsx`, `ThemeToggle.tsx`, `src/lib/design-tokens.ts`, `globals.css`.
- **Implementação esperada:** auditoria com `@axe-core/playwright` e correção dos tokens.
- **Testes necessários:** axe sem violações sérias nas 6 páginas principais.
- **Critério de aceite:** 0 violações `serious/critical`.
- **Evidência de conclusão:** relatório axe.
- **Risco:** escopo infinito. Limitar às 6 páginas principais.
- **Relação com a estratégia:** qualidade percebida e acessibilidade (parte do Leviatã).

#### S3-T10 · Grid de calor da frota (e por que **não** score de operador)
- **Objetivo:** mostrar padrão no tempo; recusar uma métrica sem fundamento.
- **Contexto:** pedido de grid de calor; ideia de "score operacional de operador".
- **Problema atual:** sem visão temporal agregada da frota.
- **Estado desejado:** heatmap máquina × hora (cor = pior severidade da hora; textura/ícone = qualidade do dado ruim). **Score de operador: `DEFER` (D-16)**, porque atribuir "nota" a pessoa a partir de telemetria sem validação é injusto e juridicamente sensível.
- **Dependências · Pré-requisitos:** S3-T6 · endpoint de agregação por hora.
- **Arquivos prováveis:** `src/components/HeatGrid.tsx`, `api_tcc/api/views_events.py` (agregação), `docs/DECISOES.md`.
- **Implementação esperada:** agregação no banco (`GROUP BY machine, hour`), nunca no cliente.
- **Testes necessários:** agregação conta corretamente leituras fora de ordem (usa `event_time`).
- **Critério de aceite:** heatmap coerente com a lista de eventos.
- **Evidência de conclusão:** captura.
- **Risco:** performance. Índice `(machine, event_time)`.
- **Relação com a estratégia:** anti-hype: recusar o score de operador **é** uma decisão registrada.

#### S3-T11 · E2E do fluxo central e evidência em vídeo
- **Objetivo:** prova automatizada do ciclo.
- **Contexto:** `frontend-next/tests/*.js` (Playwright) e `evidence.mjs` já existem, soltos.
- **Problema atual:** testes de UI fora de uma suíte única e do CI.
- **Estado desejado:** `npm run test:e2e` executa: semear leitura crítica → aparece em P1 → abrir decisão → aprovar → registrar desfecho → conferir auditoria; grava vídeo.
- **Dependências · Pré-requisitos:** S3-T5 · ambiente Compose.
- **Arquivos prováveis:** `frontend-next/tests/e2e/*.spec.ts`, `playwright.config.ts`, `package.json`.
- **Implementação esperada:** `page.route` apenas para simular falha de API; **nenhum mock de resposta** no teste principal (usa backend real).
- **Testes necessários:** o próprio E2E, três execuções seguidas sem flake.
- **Critério de aceite:** 3 execuções verdes.
- **Evidência de conclusão:** vídeo `docs/evidence/s3/fluxo-central.webm`.
- **Risco:** flakiness por polling. Esperar por condição, não por tempo fixo.
- **Relação com a estratégia:** vídeo reaproveitado no pitch e no README.


---

### SEMANA 4 · PRESCRIÇÃO OPERACIONAL (DECISÃO → ORDEM DE SERVIÇO → RESULTADO)

> **NOTA V5:** A prescrição ganha **PR, PLM, laudo estruturado e escada de confirmação** na **S19**. A OS e o desfecho da S4 continuam como estão.


> **NOTA V4:** S4 entrega a **estrutura** (Decision, WorkOrder, desfecho). O **conteúdo** (playbooks, checklist, estoque, otimizador, what-if, auditoria) está na **S16**. O pilar P1 só fecha com S16-T9.


**Camadas:** ARCHITECTURE · IMPLEMENTATION · TESTING

- **Objetivo estratégico:** a recomendação deixa de ser "agende inspeção preventiva" e vira trabalho acompanhável: quem faz, até quando, com que evidência, e o que aconteceu depois.
- **Objetivo técnico:** consolidar as 3 implementações de prescrição em `Decision`; estruturar a decisão (evidências, regra/versão, janela, confiança); criar `WorkOrder` ligada à `Decision`; exportar (`.ics`, JSON, webhook, mensagem pronta para WhatsApp); registrar execução e reavaliação por telemetria posterior; feedback de falso alarme que ajusta o limiar **da máquina** com trilha.
- **Por que existe:** Ultimato 2.1, 2.4, 2.6: a prescrição atual é "texto curto genérico"; o loop fechado (alerta → decisão → OS exportável → resultado) é o item que o caso de MS mostrou ser digitação manual.
- **Problemas que resolve:** 3 caminhos de prescrição (`services/prescricao.py` deprecado, `ia/pipeline.py`, `views_prescricao.py`+`services/decisions.py`); modelo legado `Prescricao`; `outcome_texto` livre; ausência de responsável/prazo; ausência de reavaliação.
- **Dependências recebidas:** S1 (severidade/evidência), S2 (auditoria, papéis), S3 (UI de decisões).
- **Entregáveis:** `Decision` v2 (campos estruturados), `WorkOrder`, `MaintenanceContact`, exportadores, reavaliação automática, feedback de limiar, remoção do legado.
- **Arquivos/módulos afetados:** `api_tcc/models.py`, `services/decisions.py`, `services/prescricao.py` (remover), `ia/pipeline.py`, `api/views_prescricao.py`, `api/views_decisions.py`, novo `services/workorders.py`, `services/exporters.py`, `frontend-next/src/app/decisoes`.
- **Arquitetura:** `Event → Decision → WorkOrder → Outcome → Reavaliação`. **Banco:** migrations 0029 a 0032 (`Decision` campos, `WorkOrder`, `MaintenanceContact`, `ThresholdOverride`). **Backend:** serviços de OS e exportação. **Frontend:** formulário de OS e agenda interna. **Hardware:** nenhuma. **ML/IA:** feedback vira rótulo fraco (consumido em S5-T9). **Infra:** nenhuma. **Segurança:** só papéis autorizados criam OS; contato profissional, nunca telefone pessoal. **Testes:** máquina de estados e exportação. **Docs:** `docs/OPERATIONAL_DECISION_MEMORY.md`.
- **Experimentos:** simular 20 decisões com aprovação/rejeição/execução e medir tempo médio de ciclo e taxa de falso alarme.
- **Critérios de aceitação:** decisão crítica aprovada gera OS com responsável e prazo, exportável; reavaliação marca "sintoma persistiu / cessou".
- **Métricas:** tempo evento → decisão → aprovação → execução; % de decisões com desfecho; % rejeitadas como falso alarme.
- **Evidências esperadas:** gravação, `.ics` abrindo no Google Agenda/Outlook, teste de reavaliação.
- **Riscos:** inventar telefone, escala, peça ou integração que não existe. **Proibido** (Ultimato 1.7 e 2.1). Contato vem de cadastro real.
- **Decisões:** D-09 (agenda interna primeiro, Google/Outlook como adaptador depois), D-10 (WhatsApp: gerar mensagem/link `wa.me`, sem API paga nesta fase).
- **Perguntas abertas:** peças sugeridas dependem de catálogo real; fica `DEFER` até haver cadastro de manutenção (S5-T10).
- **Definition of Done da semana:** fluxo completo demonstrado e gravado, legado removido, testes verdes.

#### S4-T1 · Consolidar prescrição em `Decision` e remover o legado
- **Objetivo:** um único caminho para gerar recomendação.
- **Contexto:** `services/prescricao.py` ("Deprecated legacy prescription service") usa `Prescricao`; `ia/pipeline.py::analisar_maquina` e `views_prescricao.py` geram o mesmo conceito.
- **Problema atual:** textos e limiares divergentes; modelo legado no schema.
- **Estado desejado:** `Decision` é a única saída; `views_prescricao.py` vira camada fina de compatibilidade (`/api/prescricoes/` retorna decisões); `Prescricao` removida por migration segura.
- **Dependências · Pré-requisitos:** S3-T5 · backup do banco de demo.
- **Arquivos prováveis:** os listados + migration `0029_remove_prescricao`.
- **Implementação esperada:** mapear cada campo de `Prescricao` para `Decision.detalhes` (migração de dados antes do drop); manter rotas por 1 ciclo com cabeçalho `Deprecation: true`.
- **Testes necessários:** `test_decisions.py` + novo teste: as rotas antigas devolvem decisões equivalentes.
- **Critério de aceite:** `grep -rn "Prescricao\b" api_tcc --include=*.py` só em migrations antigas.
- **Evidência de conclusão:** diff + testes.
- **Risco:** perder histórico de demo. Mitigação: dump antes.
- **Relação com a estratégia:** um motor, uma verdade (Leviatã: eliminar duplicação antes de crescer).

#### S4-T2 · `Decision` estruturada (evidência, regra, janela, confiança, horizonte)
- **Objetivo:** cada decisão explica a si mesma sem depender do LLM.
- **Contexto:** `Decision` tem `texto`, `acao_recomendada`, `confianca`, `detalhes` (JSON livre).
- **Problema atual:** sem esquema do que vai em `detalhes`.
- **Estado desejado:** `detalhes` validado por schema `decision.v1`: `observado`, `evidencias[]` (leitura_id, valor, limiar, instante), `janela_analisada`, `qualidade_dado`, `regra_id`, `regra_versao`, `modelo_versao`, `dados_faltantes[]`, `horizonte_minutos` (**apenas** se houver política validada; senão `null`), `alternativas[]`.
- **Dependências · Pré-requisitos:** S4-T1 · S1-T3.
- **Arquivos prováveis:** `services/decisions.py`, `api_tcc/schemas/decision_v1.json`, `serializers.py`.
- **Implementação esperada:**
```json
{
  "schema": "decision.v1",
  "observado": "Temperatura acima do limite crítico por 3 leituras consecutivas",
  "evidencias": [{"leitura_id": "uuid", "campo": "temperatura", "valor": 91.2, "limiar": 85.0, "event_time": "2026-10-26T14:02:11Z"}],
  "janela_analisada": {"inicio": "...", "fim": "...", "n_leituras": 24},
  "qualidade_dado": {"evidence_quality": "boa", "fatores": []},
  "regra": {"id": "TEMP_ALTA_CRITICA", "versao": "1.0"},
  "modelo": {"id": "anomalia-v1", "score": 0.82, "contribuinte": "temperatura"},
  "dados_faltantes": ["pressao_oleo", "temperatura_liquido_arrefecimento"],
  "horizonte_minutos": null,
  "alternativas": ["monitorar por 15 min", "reduzir carga"]
}
```
`horizonte_minutos` só é preenchido por regra validada (ex.: extrapolação linear com R² mínimo documentado); caso contrário `null` e a UI mostra "sem estimativa confiável".
- **Testes necessários:** validação JSON Schema; decisão sem evidência é rejeitada na criação.
- **Critério de aceite:** nenhuma `Decision` criada sem `evidencias`.
- **Evidência de conclusão:** testes.
- **Risco:** inventar horizonte. **Proibido** sem validação.
- **Relação com a estratégia:** rastreabilidade (pilar 3).

#### S4-T3 · `WorkOrder`, responsável real e prazo
- **Objetivo:** aprovar uma decisão cria a ação acompanhável.
- **Contexto:** inexistente; o caso de MS descrevia digitação manual de OS.
- **Problema atual:** decisão termina em "aprovada".
- **Estado desejado:** `WorkOrder(id, decision, machine, titulo, descricao, prioridade, responsavel(FK User|MaintenanceContact), prazo, status, checklist JSON, pecas_sugeridas JSON?, criado_por, historico)`, status `ABERTA → AGENDADA → EM_EXECUCAO → CONCLUIDA | CANCELADA`.
- **Dependências · Pré-requisitos:** S4-T2 · `MaintenanceContact(nome, funcao, email, telefone_profissional, organization)` cadastrado pela organização.
- **Arquivos prováveis:** `models.py`, `services/workorders.py`, `api/views_workorders.py`, `src/app/decisoes/[id]/os`.
- **Implementação esperada:** `approve(decision, user, responsavel, prazo)` em transação: muda status da decisão, cria OS, grava `AuditLog`; prazo **sugerido** só se existir política por severidade configurada pela organização (`OrganizationPolicy`), senão campo obrigatório manual.
- **Testes necessários:** aprovação atômica (falha ao criar OS desfaz status); usuário de outra organização não cria OS; contato fora da organização é rejeitado.
- **Critério de aceite:** testes verdes.
- **Evidência de conclusão:** gravação.
- **Risco:** peças e checklist exigem catálogo real. Ficam como campos livres até S5-T10.
- **Relação com a estratégia:** "prescrição acionável" (Ultimato 2.6 item 9).

#### S4-T4 · Exportação: `.ics`, JSON/webhook e mensagem pronta
- **Objetivo:** a OS chega à ferramenta que o responsável já usa.
- **Contexto:** sem integração externa; agenda do Google/Outlook é D-09.
- **Problema atual:** nenhuma saída da decisão para o mundo.
- **Estado desejado:** `GET /api/workorders/<id>/export.ics`; `POST` de webhook configurável por organização (HMAC no cabeçalho); botão "copiar mensagem" e link `https://wa.me/<numero>?text=...` **gerado, não enviado**.
- **Dependências · Pré-requisitos:** S4-T3 · nenhum.
- **Arquivos prováveis:** `services/exporters.py`, `api/views_workorders.py`.
- **Implementação esperada:**
```python
def to_ics(os):
    return "\r\n".join([
      "BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//FieldNode//OS//PT-BR","BEGIN:VEVENT",
      f"UID:{os.id}@fieldnode", f"DTSTAMP:{now:%Y%m%dT%H%M%SZ}",
      f"DTSTART:{os.prazo:%Y%m%dT%H%M%SZ}", f"SUMMARY:OS {os.titulo} ({os.machine.external_code})",
      f"DESCRIPTION:{_esc(os.descricao)}\\nDecisão: {os.decision_id}", "END:VEVENT","END:VCALENDAR"])
```
Webhook: `X-FieldNode-Signature: sha256=<hmac(body, secret_da_org)>`, 3 tentativas, falha vai para DLQ (`contexto=WEBHOOK`).
- **Testes necessários:** `.ics` valida em parser (`icalendar`); assinatura HMAC confere; webhook fora do ar não bloqueia aprovação.
- **Critério de aceite:** arquivo abre no Google Agenda e Outlook (teste manual com captura).
- **Evidência de conclusão:** capturas.
- **Risco:** vazar dado no webhook. Payload mínimo e documentado.
- **Relação com a estratégia:** prova de "ação, não dashboard".

#### S4-T5 · Execução, reavaliação e resultado verificável
- **Objetivo:** distinguir "operador disse que resolveu" de "a telemetria depois confirma".
- **Contexto:** `outcome_texto` é livre.
- **Problema atual:** nenhum fechamento verificável.
- **Estado desejado:** ao concluir OS, abre-se `Reevaluation` (janela configurável): compara a condição antes/depois (ex.: % de leituras acima do limiar nas N leituras seguintes). Resultado: `SINTOMA_CESSOU | SINTOMA_PERSISTE | DADOS_INSUFICIENTES`. UI rotula "resultado informado" e "verificado por telemetria" separadamente.
- **Dependências · Pré-requisitos:** S4-T3 · nenhum.
- **Arquivos prováveis:** `models.py`, `services/reevaluation.py`, comando `reavaliar_decisoes` (agendável).
- **Implementação esperada:** função pura `avaliar(antes, depois, regra) -> resultado`, testada com séries sintéticas.
- **Testes necessários:** três cenários (cessou, persiste, insuficiente) e dado fora de ordem.
- **Critério de aceite:** testes verdes; UI mostra os dois rótulos.
- **Evidência de conclusão:** captura.
- **Risco:** afirmar eficácia. A UI **nunca** diz "problema resolvido", só o que cada fonte informou.
- **Relação com a estratégia:** fecha o ciclo e gera rótulo fraco.

#### S4-T6 · Feedback do mecânico ajusta o limiar da máquina (com trilha)
- **Objetivo:** reduzir alert fatigue com aprendizado auditável.
- **Contexto:** hoje só há cooldown.
- **Problema atual:** falso alarme reaparece idêntico.
- **Estado desejado:** rejeitar com motivo `FALSO_ALARME` oferece "ajustar limiar desta máquina" (`ThresholdOverride(machine, metric, atencao, critico, motivo, criado_por, expira_em)`); ajuste só dentro de faixa segura do contrato; expira; entra em `AuditLog`; **nunca** ultrapassa o limite crítico de segurança do contrato.
- **Dependências · Pré-requisitos:** S4-T3, S2-T7 · nenhum.
- **Arquivos prováveis:** `models.py`, `services/eventos.py`, UI de decisão.
- **Implementação esperada:** `limiar_efetivo = min(max(override, piso), teto)` com `teto` do contrato.
- **Testes necessários:** override não ultrapassa teto; expira; auditado.
- **Critério de aceite:** testes verdes.
- **Evidência de conclusão:** testes.
- **Risco:** operador "silenciar" risco real. Mitigação: teto de segurança + papel exigido + expiração.
- **Relação com a estratégia:** diferencial "supressão com feedback" (Ultimato 2.6 item 6).

#### S4-T7 · Agenda interna de manutenção
- **Objetivo:** visualizar OS por dia/máquina/responsável.
- **Contexto:** pedido de calendário integrado às prescrições.
- **Problema atual:** inexistente.
- **Estado desejado:** visão semanal/mensal read/reagendar de `WorkOrder`; sem integrar RH; contato profissional apenas.
- **Dependências · Pré-requisitos:** S4-T3 · nenhum.
- **Arquivos prováveis:** `src/app/agenda/page.tsx`, `src/components/AgendaGrid.tsx`.
- **Implementação esperada:** consumo de `GET /api/workorders/?de=&ate=`; reagendar = `PATCH` com histórico.
- **Testes necessários:** reagendamento gera auditoria; conflito de responsável mostra aviso, não bloqueia.
- **Critério de aceite:** E2E reagendar OS.
- **Evidência de conclusão:** gravação.
- **Risco:** virar CMMS completo. Escopo travado: criar, ver, reagendar, concluir.
- **Relação com a estratégia:** fecha o pedido sem sobreconstruir.

---

### SEMANA 5 · IA DEFENSÁVEL (AVALIAR ANTES DE PROMETER)

> **NOTA V5:** A avaliação passa a incluir **PR e PLM** (S19-T11) e **perfis por sinal e regime** (S18-T5). IA-100 = S5 + S15; a confiança por componente fica no pilar P5 (S19).


> **NOTA V4:** S5 permanece como base do pilar P2, mas a avaliação **deixa de depender só de dado sintético**: S15-T1/T2 fornecem dados reais e o rig, e S5-T2 deve consumi-los. IA-100 = S5 + S15.


**Camadas:** VALIDATION · TESTING · DOCUMENTATION

- **Objetivo estratégico:** a resposta ao professor ("não se pode prometer decisão por IA sem modelo treinado") vira um relatório com números, não um argumento.
- **Objetivo técnico:** unificar os dois detectores de anomalia; medir precisão, recall, falso positivo e tempo até a detecção em cenários reproduzíveis separados do treino; condicionar a detecção ao regime de operação; model card; validar o método em dataset público; LLM com guardrails de evidência; rótulo fraco a partir das decisões.
- **Por que existe:** Ultimato 1.7 seção 5 e 2.4: "IF por máquina", "baseline por contexto", "avaliação real", "Gemini só explica". Estado verificado: dois detectores (`ia/deteccao_multivariada.py` global com `.pkl` treinado no simulador e `services/anomaly_detection.py` por máquina após 100 leituras), sem harness.
- **Problemas que resolve:** 100 leituras podem ser 10 minutos de máquina parada; IF treinado com dado contaminado aprende o defeito como normal; "precisão" sem métrica; LLM sem restrição de evidência.
- **Dependências recebidas:** S1 (escala/limiares), S3 (UI), S4 (rótulos fracos).
- **Entregáveis:** `ml/eval/` com cenários e métricas, relatório, regime de operação como dado, baseline por regime, model card, validação em dataset público, guardrails do LLM, plano de rótulo.
- **Arquivos/módulos afetados:** `api_tcc/services/anomaly_detection.py`, `api_tcc/ia/*`, novo `ml/eval/`, `docs/HONESTIDADE_METODOLOGICA_ML.md`, `docs/AVALIACAO_ANOMALIA.md`, `docs/PLANO_DATASET_ROTULADO.md`.
- **Arquitetura:** camadas A (evidências), B (decisão determinística), C (explicação LLM), D (revisão humana e desfecho). **Banco:** `LeituraTelemetria.regime`, `ModelCard`/arquivos em `models/`. **Backend:** unificação. **Frontend:** exibir `contributing_feature`. **Hardware:** nenhuma. **ML/IA:** núcleo. **Infra:** `make eval`. **Segurança:** o LLM só recebe evidência montada e autorizada. **Testes:** cenários golden. **Docs:** três documentos.
- **Experimentos:** 8 cenários do Ultimato (normal, subida gradual, pico isolado, sensor travado, lacuna, máquina desligada, fora de ordem, mudança de carga) × 20 sementes.
- **Critérios de aceitação:** relatório reproduzível com `make eval`; nenhuma frase "prevê falha" em material.
- **Métricas:** precisão, recall, F1, taxa de falso positivo por hora, tempo até detecção (s), taxa de "inconclusivo" correto.
- **Evidências esperadas:** `docs/AVALIACAO_ANOMALIA.md` com tabela por cenário e **versão do modelo/dados**.
- **Riscos:** números ruins. **É resultado válido**; publicar com limitações.
- **Decisões:** D-03 (Random Forest só com 200+ decisões com desfecho), D-08 (IF por máquina só após critérios de dado), D-18 (dataset público escolhido).
- **Perguntas abertas:** vale um modelo global de grupo (por modelo de máquina) como baseline inicial? Hipótese a testar na S5-T4.
- **Definition of Done da semana:** `make eval` roda do zero e reproduz o relatório; claims de IA em README/pitch conferidos com a matriz.

#### S5-T1 · Unificar detectores e registrar versões
- **Objetivo:** um caminho de anomalia, versionado.
- **Contexto:** `ia/deteccao_multivariada.py` (`isolation_forest_v1.pkl`, `contamination=0.05`, treino com `df_normal`) e `services/anomaly_detection.py` (`MODEL_VERSION="anomalia-v1"`, mínimo 100 leituras, z-score antes).
- **Problema atual:** resultados diferentes por rota; `.pkl` versionado no Git.
- **Estado desejado:** `services/anomaly_detection.py` único; `model_registry.py` guarda artefato + metadados (`treinado_em`, `n_amostras`, `hash_dataset`, `features`, `contamination`, `versao`); `.pkl` fora do Git (ou via LFS), gerado por `treinar_modelo_anomalia`.
- **Dependências · Pré-requisitos:** S0-T2 · nenhum.
- **Arquivos prováveis:** os dois módulos, `ia/model_registry.py`, `management/commands/treinar_*`, `.gitignore`.
- **Implementação esperada:** manter só `treinar_modelo_anomalia`; remover o `.pkl` do Git (`git rm --cached`); carregamento falha de forma **explícita** (sem modelo ⇒ z-score com selo "baseline estatístico", não IF).
- **Testes necessários:** reprodutibilidade (mesma entrada, mesmo score em duas chamadas); fallback sinalizado.
- **Critério de aceite:** um único módulo de detecção; resposta de API inclui `detection_method` e `model_version`.
- **Evidência de conclusão:** testes.
- **Risco:** `anomaly_detection` guarda estado em memória por processo (2 workers gunicorn = 2 estados). Documentar e, se necessário, mover histórico para consulta ao banco por janela.
- **Relação com a estratégia:** auditável e reproduzível.

#### S5-T2 · Harness de avaliação com cenários reproduzíveis
- **Objetivo:** substituir "precisão" por medição.
- **Contexto:** Ultimato 1.7 e 2.4 listam os cenários.
- **Problema atual:** testes unitários existem (`test_anomaly_detection.py`), mas não há avaliação **contra rótulo conhecido**, **separada do treino**.
- **Estado desejado:** `ml/eval/scenarios.py` gera séries com rótulo (início/fim da anomalia); `ml/eval/run.py` treina em `normal`, avalia em conjunto **independente**; saída em `docs/AVALIACAO_ANOMALIA.md`.
- **Dependências · Pré-requisitos:** S5-T1 · S1-T1.
- **Arquivos prováveis:** `ml/eval/{scenarios,metrics,run}.py`, `Makefile`.
- **Implementação esperada:**
```python
@dataclass
class Cenario:
    nome: str; serie: pd.DataFrame; rotulo: np.ndarray; esperado: str   # "alerta"|"sem_alerta"|"inconclusivo"
def subida_gradual(seed, passo=0.05): ...        # +0.05 °C/leitura a partir da leitura 200
def sensor_travado(seed): ...                    # valor repetido 30x, trust deve cair
def lacuna_comunicacao(seed): ...                # 40 min sem dados: sistema NÃO interpreta silêncio como normal
def maquina_desligada(seed): ...                 # rpm 0: não gera anomalia térmica
def mudanca_de_carga(seed): ...                  # degrau esperado: não deve alertar
def tempo_ate_deteccao(res, rotulo) -> float: ...# s entre início da anomalia e 1º alerta
```
Para cada cenário e semente: TP, FP, FN, TN, tempo até detecção, `score`, `versao_modelo`; agregar com média ± desvio. Rotular explicitamente: **"métrica de teste sintético, não de campo"**.
- **Testes necessários:** o harness é determinístico (mesma semente = mesmo resultado); cenário `lacuna` exige alerta de **observabilidade**.
- **Critério de aceite:** `make eval` produz o relatório sem intervenção.
- **Evidência de conclusão:** relatório commitado.
- **Risco:** ajustar o modelo até o relatório "ficar bonito" (overfitting ao próprio benchmark). Mitigação: cenários fixados em arquivo antes de ajustar.
- **Relação com a estratégia:** responde ao professor.

#### S5-T3 · Regime de operação e baseline contextual
- **Objetivo:** anomalia é desvio em relação ao esperado **naquela condição**.
- **Contexto:** hoje IF vê `(temperatura, vibracao, rpm)` sem contexto.
- **Problema atual:** máquina parada compara-se com máquina trabalhando; subida de carga vira falso positivo.
- **Estado desejado:** `regime ∈ {desligada, marcha_lenta, trabalhando, deslocamento, desconhecido}` derivado de `rpm`, `velocidade` e GPS; IF treinado **por regime**; estado desconhecido não alerta como anomalia, alerta como observabilidade.
- **Dependências · Pré-requisitos:** S5-T1 · velocidade (GPS) quando existir; até lá regras por `rpm`.
- **Arquivos prováveis:** `services/regime.py`, `anomaly_detection.py`, migration `regime`.
- **Implementação esperada:**
```python
def inferir_regime(rpm, velocidade_kmh=None) -> str:
    if rpm is None: return "desconhecido"
    if rpm < 300: return "desligada"
    if rpm < 1000 and (velocidade_kmh or 0) < 1: return "marcha_lenta"
    if (velocidade_kmh or 0) > 8 and rpm < 1800: return "deslocamento"
    return "trabalhando"
```
Cortes são **heurística de bancada**, a calibrar por modelo de máquina (campo de metadados da S5-T10).
- **Testes necessários:** cenários `maquina_desligada` e `mudanca_de_carga` sem falso positivo.
- **Critério de aceite:** FP desses cenários ≤ meta definida no relatório (registrar a meta **antes** de medir).
- **Evidência de conclusão:** relatório.
- **Risco:** regime errado contamina treino. Mitigação: treino só com `regime == trabalhando` e `evidence_quality == boa`.
- **Relação com a estratégia:** o ponto que impede "IA que alarma tudo".

#### S5-T4 · Critérios de treino por máquina e baseline de grupo
- **Objetivo:** não treinar modelo individual com dado insuficiente ou contaminado.
- **Contexto:** `MINIMUM_TRAINING_READINGS = 100`, `CONTAMINATION = 0.05`.
- **Problema atual:** 100 leituras podem representar 10 minutos de um único estado.
- **Estado desejado:** treino por máquina só se: ≥ N leituras **e** ≥ H horas de cobertura **e** ≥ 2 regimes representados **e** `trust` médio ≥ 0.8 **e** sem evento crítico aberto na janela. Caso contrário usa baseline de **grupo (modelo de máquina)** ou regras. Rejeição de modelo novo se piorar em validação interna (champion/challenger simples).
- **Dependências · Pré-requisitos:** S5-T3 · nenhum.
- **Arquivos prováveis:** `anomaly_detection.py`, `model_registry.py`.
- **Implementação esperada:** `pode_treinar(machine) -> (bool, motivos[])` exposto na API de saúde do modelo.
- **Testes necessários:** janela com anomalia persistente não treina; modelo ruim não substitui o anterior.
- **Critério de aceite:** testes verdes; motivo de não treinar visível.
- **Evidência de conclusão:** testes.
- **Risco:** N, H arbitrários. Documentar como parâmetros calibráveis.
- **Relação com a estratégia:** resposta técnica ao "e se treinar com dado ruim?".

#### S5-T5 · Validação do método em dataset público
- **Objetivo:** provar que a metodologia detecta falha **real**, mesmo que não de colheitadeira.
- **Contexto:** Ultimato 2.6 sugere CWRU (rolamento) e AI4I (manutenção preditiva).
- **Problema atual:** só dado sintético próprio.
- **Estado desejado:** notebook/script que aplica o pipeline (features + IF) em dataset público, reporta métricas e **diz** que valida o método, não o produto. Escolha do dataset: D-18 (verificar licença e disponibilidade na hora; **não assumir** formatos).
- **Dependências · Pré-requisitos:** S5-T2 · acesso ao dataset (verificar licença).
- **Arquivos prováveis:** `ml/eval/public_dataset.py`, `docs/AVALIACAO_ANOMALIA.md`.
- **Implementação esperada:** extrair RMS, pico, curtose por janela; comparar IF vs limiar simples (**se o IF não ganhar do limiar simples, dizer**).
- **Testes necessários:** reprodutibilidade por semente.
- **Critério de aceite:** tabela IF vs baseline com métricas.
- **Evidência de conclusão:** relatório.
- **Risco:** transferência para colheitadeira não comprovada. Frase obrigatória no relatório.
- **Relação com a estratégia:** ancora a metodologia fora do próprio simulador.

#### S5-T6 · Model card e `HONESTIDADE_METODOLOGICA_ML.md`
- **Objetivo:** documento único do que cada modelo é, com que dado, e o que **não** é.
- **Contexto:** esqueleto criado em S0-T4.
- **Problema atual:** nenhum documento separa detecção, previsão e prescrição.
- **Estado desejado:** tabela: componente → tipo → dado de treino → rótulo → é preditivo? → confiança científica; model card do IF (uso pretendido, fora de escopo, limitações, métricas); vocabulário permitido ("score de anomalia", **não** "probabilidade de quebra").
- **Dependências · Pré-requisitos:** S5-T2 a T5 · nenhum.
- **Arquivos prováveis:** `docs/HONESTIDADE_METODOLOGICA_ML.md`, `docs/MODEL_CARD_ANOMALIA.md`.
- **Implementação esperada:** inclui a regra: IF produz score, não data de falha nem RUL.
- **Testes necessários:** revisão por pares.
- **Critério de aceite:** aceito pelo grupo.
- **Evidência de conclusão:** commit.
- **Risco:** nenhum.
- **Relação com a estratégia:** protege a defesa.

#### S5-T7 · LLM com guardrails de evidência
- **Objetivo:** o LLM explica, não inventa.
- **Contexto:** `explicacao_llm.py`, `agentic.py`, `prompts/agentic_decision_v1.txt`, `test_agentic.py`.
- **Problema atual:** sem verificação de que cada afirmação do texto aponta para evidência.
- **Estado desejado:** o prompt recebe **apenas** o JSON `decision.v1`; a saída deve ser JSON com `texto` e `evidencias_citadas[]` (ids que existem em `evidencias`); validador rejeita saída que cite id inexistente, invente número, prazo ou peça; falha ⇒ DLQ `contexto=AGENTIC_LLM` e texto determinístico; circuit breaker 2 s.
- **Dependências · Pré-requisitos:** S4-T2, S2-T4 · nenhum.
- **Arquivos prováveis:** `services/agentic.py`, `ia/explicacao_llm.py`, `prompts/*`.
- **Implementação esperada:** validador compara todos os números do texto com `{evidencias, limiares}`; números fora do conjunto reprovam.
- **Testes necessários:** resposta mockada com número inventado é rejeitada; com id inexistente é rejeitada; timeout usa fallback.
- **Critério de aceite:** testes verdes.
- **Evidência de conclusão:** testes.
- **Risco:** LLM "criativo". Mitigação: temperatura baixa e validador.
- **Relação com a estratégia:** responde "Gemini é seguro?" (recebe só o que o backend autoriza).

#### S5-T8 · Assistente com function calling controlado (escopo mínimo)
- **Objetivo:** consultar o sistema em linguagem natural **sem** acesso livre.
- **Contexto:** `ChatFAB.tsx` existe; chatbot geral foi corretamente adiado.
- **Problema atual:** UI sem contrato claro do que o assistente pode fazer.
- **Estado desejado:** 4 ferramentas somente leitura, com permissão do usuário: `listar_maquinas_criticas`, `explicar_decisao(id)`, `saude_da_maquina(id)`, `eventos_recentes(id)`. Toda resposta cita ids. Ações (aprovar/rejeitar) **não** passam pelo assistente.
- **Dependências · Pré-requisitos:** S5-T7, S2-T6 · nenhum.
- **Arquivos prováveis:** `api/views_assistant.py`, `services/assistant_tools.py`, `ChatFAB.tsx`.
- **Implementação esperada:** executor valida argumentos contra schema; filtro de organização aplicado **dentro** da ferramenta.
- **Testes necessários:** pergunta sobre máquina de outra organização retorna "não encontrada"; tentativa de prompt injection via campo `texto` de decisão não executa ferramenta fora da lista.
- **Critério de aceite:** testes de isolamento e de injeção verdes.
- **Evidência de conclusão:** testes.
- **Risco:** superfície nova. Se não houver tempo, `DEFER` e esconder o FAB (nunca deixar botão que não faz o prometido).
- **Relação com a estratégia:** entrega a ideia sem a parte perigosa.

#### S5-T9 · Plano de dataset rotulado a partir de decisões
- **Objetivo:** o ativo de longo prazo começa a ser coletado corretamente.
- **Contexto:** `Decision.status`, `outcome_texto`, `Reevaluation` (S4-T5).
- **Problema atual:** sem critério de entrada para supervisionado.
- **Estado desejado:** `docs/PLANO_DATASET_ROTULADO.md`: rótulo fraco (executada + sintoma cessou = ação previniu; rejeitada como falso alarme = negativo; evento crítico posterior sem ação = positivo), tabela `LabeledWindow`, critério: **≥ 200 decisões com desfecho** (D-03) antes de treinar RF.
- **Dependências · Pré-requisitos:** S4-T5 · nenhum.
- **Arquivos prováveis:** `docs/PLANO_DATASET_ROTULADO.md`, `models.py` (`LabeledWindow`), comando `exportar_dataset_rotulado`.
- **Implementação esperada:** exportação com `machine`, janela de features, rótulo, fonte do rótulo (humano/telemetria/ambos), versão da regra.
- **Testes necessários:** exportação reproduzível.
- **Critério de aceite:** comando gera CSV com cabeçalho documentado.
- **Evidência de conclusão:** arquivo de exemplo.
- **Risco:** correlação ≠ causalidade (Ultimato 2.5). Documentar.
- **Relação com a estratégia:** transforma "vamos ter um RF melhor" em critério mensurável.

#### S5-T10 · Metadados e manutenção por máquina
- **Objetivo:** dar contexto ao modelo e à decisão.
- **Contexto:** Ultimato 2.6 seção 4: sem tabela de manutenção, o modelo não tem contexto.
- **Problema atual:** `Machine` sem horas acumuladas, ano, limites por modelo, histórico de manutenção.
- **Estado desejado:** `MachineSpec(machine/modelo, ano, horas_motor, limites_json)` e `MaintenanceRecord(machine, data, tipo, pecas, horas_motor, observacao)`; importação CSV.
- **Dependências · Pré-requisitos:** S4-T3 · nenhum.
- **Arquivos prováveis:** `models.py`, `management/commands/importar_manutencao.py`, UI mínima.
- **Implementação esperada:** limites por modelo substituem o contrato **somente** dentro da faixa de segurança.
- **Testes necessários:** importação rejeita linha inválida com relatório.
- **Critério de aceite:** decisão mostra "horas desde a última manutenção" quando houver dado.
- **Evidência de conclusão:** captura.
- **Risco:** dado real é dado sensível do cliente. Política de retenção (S10-T6).
- **Relação com a estratégia:** pré-requisito de qualquer modelo de manutenção de verdade.

---

### SEMANA 6 · RESILIÊNCIA OFFLINE PROVADA

> **NOTA V4:** O protocolo da S6 vale para o simulador **e** para o hardware: repetir S6-T5 com o nó físico (S8) e com o soak de 14 dias (S14-T9).


**Camadas:** VALIDATION · OBSERVABILITY · TESTING

- **Objetivo estratégico:** transformar "funciona offline" em número publicado, com a fronteira exata do que o simulador prova e do que não prova.
- **Objetivo técnico:** especificar o Sync Protocol v1; calcular capacidade de armazenamento; definir política de disco cheio; implementar TTL, compressão e checksum fim a fim; reconstrução temporal no ingestor; executar o protocolo de resiliência com critérios definidos **antes** da execução; publicar métricas.
- **Por que existe:** Ultimato 1.7 seção 4 e 2.4: não prometer "zero perda" nem "duas semanas" sem teste e cálculo; offline-first, store-and-forward, Data Mule e rádios são conceitos diferentes.
- **Problemas que resolve:** `teste_resiliencia.py` (413 linhas) sem resultado publicado; requisito de duas semanas offline sem cálculo; mensagens críticas poderem sumir quando o disco enche.
- **Dependências recebidas:** S1 (ACK, tempo, contrato), S2 (credencial por dispositivo).
- **Entregáveis:** `docs/SYNC_PROTOCOL_V1.md`, calculadora de capacidade, política de armazenamento, protocolo automatizado e resultados.
- **Arquivos/módulos afetados:** `simulators/edge_client.py`, `simulators/teste_resiliencia.py`, `api_tcc/services/telemetria.py`, `api_tcc/services/reconstrucao.py`, `docs/*`.
- **Arquitetura:** edge client / transportador / ingestor como **três responsabilidades** em módulos. **Banco:** `SyncReport`. **Backend:** reconstrução temporal. **Frontend:** indicador de backlog. **Hardware:** parâmetros de flash para S8. **ML/IA:** nenhuma. **Infra:** `docker compose stop/start web` orquestrado. **Segurança:** hash fim a fim. **Testes:** protocolo de falhas. **Docs:** protocolo + capacidade.
- **Experimentos:** quedas de 30 s, 5 min, 30 min, 6 h; reinício do cliente no meio do envio; servidor indisponível; mensagens fora de ordem; replay em massa; disco cheio simulado (limite de tamanho no SQLite).
- **Critérios de aceitação:** tabela de resultados por cenário com perda, duplicata, latência de recuperação, ordem; critérios de sucesso escritos **antes**.
- **Métricas:** mensagens geradas/recebidas/duplicadas/perdidas; tempo de recuperação; p95 de latência por classe; bytes em disco por hora.
- **Evidências esperadas:** `docs/PROTOCOLO_TESTE_RESILIENCIA.md` com saída bruta.
- **Riscos:** descobrir perda/duplicata real. **Publicar e corrigir.**
- **Decisões:** D-04 (simulador de bancada rotulado como tal), D-11 (política de descarte de classe C quando disco cheio).
- **Perguntas abertas:** TTL por classe (A nunca expira; B 72 h; C 14 dias?) é decisão de produto, não de engenharia: registrar como hipótese.
- **Definition of Done da semana:** protocolo executado 3 vezes com resultados idênticos em estrutura; documento publicado.

#### S6-T1 · Sync Protocol v1 (especificação)
- **Objetivo:** contrato único de sincronização, independente do transporte.
- **Contexto:** `docs/SYNC_PROTOCOL_V1.md` (esqueleto de S1-T6).
- **Problema atual:** comportamento está só no código.
- **Estado desejado:** especificação de: envelope do pacote, ACK cumulativo, cursor, reenvio, TTL, compressão, prioridades, conflito, códigos de erro, versionamento.
- **Dependências · Pré-requisitos:** S1-T6 · nenhum.
- **Arquivos prováveis:** `docs/SYNC_PROTOCOL_V1.md`, `contracts/sync.v1.json`.
- **Implementação esperada:**
```json
{
  "device_id": "COLH-03", "message_id": "uuid", "sequence": 18422,
  "event_time": "2026-10-26T18:00:00Z", "boot_id": "uuid", "time_source": "rtc",
  "priority": "A", "schema_version": "1.2", "ttl_s": 1209600,
  "payload_hash": "sha256...", "encoding": "json|gzip+base64",
  "payload": {"temperatura": 97.4, "vibracao": 6.8, "rpm": 0, "lat": -21.123, "lon": -50.321}
}
```
Resposta: `{"status":"acked","last_acked_sequence":18422}` (lote: lista por item).
- **Testes necessários:** validação do envelope em JSON Schema, usada por cliente e servidor.
- **Critério de aceite:** schema único compartilhado.
- **Evidência de conclusão:** documento + teste de schema.
- **Risco:** divergência com firmware. Mitigação: geração de código do schema (S8).
- **Relação com a estratégia:** vira também a especificação do firmware.

#### S6-T2 · Capacidade de armazenamento e política de disco cheio
- **Objetivo:** responder "cabe 14 dias?" com conta.
- **Contexto:** meta de duas semanas offline; CM100 da Case guarda 30 dias (citação do grupo).
- **Problema atual:** sem cálculo; sem política quando enche.
- **Estado desejado:** `armazenamento = msgs/s × bytes/msg × segundos_offline × (1 + overhead)` com overhead de índice/metadados/WAL/margem; política: ao atingir 90 %, comprimir C; 95 %, agregar C (média/máx/mín por minuto); 98 %, descartar C mais antigo **registrando perda**; **A e B nunca são descartados sem alerta e registro**.
- **Dependências · Pré-requisitos:** S6-T1 · nenhum.
- **Arquivos prováveis:** `simulators/edge_client.py`, `scripts/capacity_calc.py`, `docs/CAPACIDADE.md`.
- **Implementação esperada:**
```python
def capacidade(msgs_por_s=0.5, bytes_msg=220, dias=14, overhead=0.6, compressao_C=0.35, frac_C=0.9):
    seg = dias*86400
    bruto = msgs_por_s*bytes_msg*seg
    efetivo = bruto*(frac_C*compressao_C + (1-frac_C))*(1+overhead)
    return bruto/1e6, efetivo/1e6   # MB
```
Com 1 amostra a cada 2 s (0,5 msg/s) e ~220 B, 14 dias dão ~133 MB brutos; **calcular com os valores medidos do protocolo, não estes de exemplo**. Comparar com flash disponível do ESP32 (S8).
- **Testes necessários:** teste do edge client com limite de tamanho: descarta classe C, mantém A/B, registra perda.
- **Critério de aceite:** nenhuma mensagem A/B some silenciosamente nos testes.
- **Evidência de conclusão:** `docs/CAPACIDADE.md`.
- **Risco:** premissa de bytes por mensagem errada. Medir.
- **Relação com a estratégia:** requisito de capacidade, não promessa.

#### S6-T3 · Compressão, checksum e TTL
- **Objetivo:** reduzir volume e detectar corrupção/obsolescência.
- **Contexto:** `payload_hash` existe; sem TTL nem compressão.
- **Problema atual:** C ocupa o mesmo que A.
- **Estado desejado:** agregação de classe C (janela de 60 s com média/mín/máx/n), `gzip` em lote, TTL por classe, descarte por TTL registrado.
- **Dependências · Pré-requisitos:** S6-T1, S6-T2 · nenhum.
- **Arquivos prováveis:** `edge_client.py`, `services/telemetria.py`.
- **Implementação esperada:** o servidor expande agregados em `LeituraTelemetria` marcadas `agregada=True` (ou tabela própria); o `payload_hash` cobre o corpo **descomprimido**.
- **Testes necessários:** hash confere após gzip; agregado preserva máx (nunca perder pico).
- **Critério de aceite:** testes verdes; redução de bytes medida e reportada.
- **Evidência de conclusão:** número no relatório.
- **Risco:** agregação perder pico crítico. Regra: **máximo sempre preservado**; qualquer leitura A nunca é agregada.
- **Relação com a estratégia:** viabiliza o requisito de capacidade.

#### S6-T4 · Reconstrução temporal no ingestor
- **Objetivo:** dado atrasado entra na linha do tempo certa.
- **Contexto:** Ultimato 2.7; S1-T5.
- **Problema atual:** gráficos e Trust Score devem ordenar por `event_time`.
- **Estado desejado:** serviço `reconstrucao.py` reordena e recalcula gaps/Trust quando lote antigo chega; eventos gerados por leitura atrasada **mantêm `event_time` original** e ganham selo `atrasado`; decisão não duplica evento já fechado.
- **Dependências · Pré-requisitos:** S1-T5 · nenhum.
- **Arquivos prováveis:** `services/reconstrucao.py`, `services/data_health.py`, `services/eventos.py`.
- **Implementação esperada:** recálculo incremental na vizinhança da janela afetada (não reprocessa tudo).
- **Testes necessários:** lote de 6 h atrasado reordenado; trust do período recalculado; sem decisão duplicada.
- **Critério de aceite:** testes verdes.
- **Evidência de conclusão:** testes.
- **Risco:** recálculo caro. Limitar à janela afetada.
- **Relação com a estratégia:** o diferencial real do "sync bem feito".

#### S6-T5 · Execução do protocolo e publicação dos números
- **Objetivo:** produzir o documento que a banca pedirá.
- **Contexto:** `simulators/teste_resiliencia.py` (413 linhas) existe e nunca teve resultado publicado.
- **Problema atual:** sem evidência.
- **Estado desejado:** matriz de cenários com **critérios de sucesso escritos antes**: perda = 0 em A e B; duplicata no banco = 0; recuperação < X s por GB; ordem por `event_time` correta.
- **Dependências · Pré-requisitos:** S6-T1 a T4 · Compose.
- **Arquivos prováveis:** `simulators/teste_resiliencia.py`, `docs/PROTOCOLO_TESTE_RESILIENCIA.md`.
- **Implementação esperada:** o script derruba/sobe `web` via `docker compose`, gera N leituras por classe, registra timestamps, imprime tabela. Rodar 3 vezes.
- **Testes necessários:** o próprio protocolo.
- **Critério de aceite:** documento com a tabela real e a frase de limite: *"validado em simulador de software; não comprova alcance de rádio nem comportamento em hardware"*.
- **Evidência de conclusão:** saída bruta em `docs/evidence/s6/`.
- **Risco:** número ruim. Publicar e explicar.
- **Relação com a estratégia:** formulação defensável: "sincronização resiliente com deduplicação e recuperação de falhas, validada nos cenários documentados".

#### S6-T6 · Backlog e saúde de sincronização visíveis
- **Objetivo:** operador vê quanto está pendente e o que foi perdido.
- **Contexto:** `ApiStatusIndicator.tsx`, `/api/status-mqtt/`, `SyncCursor`.
- **Problema atual:** invisível.
- **Estado desejado:** painel "Sincronização": por dispositivo, último ACK, pendentes por classe, atraso máximo, perdas registradas; alerta quando backlog cresce.
- **Dependências · Pré-requisitos:** S6-T1 · nenhum.
- **Arquivos prováveis:** `api/views_sync.py`, `src/components/SyncPanel.tsx`.
- **Implementação esperada:** `SyncReport` atualizado pelo ingestor a cada lote.
- **Testes necessários:** backlog sintético aparece; perda registrada aparece em vermelho.
- **Critério de aceite:** E2E.
- **Evidência de conclusão:** captura.
- **Risco:** baixo.
- **Relação com a estratégia:** o offline passa a ser observável.


---

### SEMANA 7 · CONNECTIVITY MANAGER E DATA MULE COMO MOTOR DE SINCRONIZAÇÃO

> **NOTA V4:** S7-T3 (Mule em rede Docker) passa a ser **pré-teste de protocolo**; o transporte real está em S14-T5/T6. S7-T5 (LoRa) é **executado** em S14-T2/T3. S7-T6 (satélite simulado) fica só como *test double* de testes; o canal real é S14-T7. S7-T1 continua sendo a base do manager real (S14-T8).


**Camadas:** ARCHITECTURE · IMPLEMENTATION · VALIDATION

- **Objetivo estratégico:** sair de "store-and-forward" (que qualquer telemetria decente faz) para **"o sistema decide por qual caminho cada mensagem sai e mantém a operação visível"**, sem prometer rádio que ainda não foi medido.
- **Objetivo técnico:** interface `ConnectivityProvider` com providers `http`, `mqtt`, `mule`, `lora` (stub), `sat` (simulado só para classe A); `ConnectivityManager` com política por classe/TTL/custo; protocolo de **custódia** para o Data Mule (origem só apaga após ACK do backend); transporte do Mule sobre rede real (LAN/hotspot) em vez de chamada de função; relatório de entrega por salto; especificação de quadro compacto para canais de baixa largura.
- **Por que existe:** Ultimato 2.4 e 2.8: "offline não é buffer, é rede"; "implementem o Data Mule de verdade"; o simulador atual (`transbordo_mule_client.py`, 324 linhas) prova a lógica, **não o transporte**.
- **Problemas que resolve:** escolha de canal ad hoc; risco de o Mule apagar da origem antes da entrega; ausência de relatório de atraso/perda por salto; falta de formato compacto para LoRa.
- **Dependências recebidas:** S1-T6 (ACK), S6 (protocolo, capacidade, reconstrução).
- **Entregáveis:** `connectivity/` (interface + managers + providers), protocolo de custódia, Mule sobre HTTP real em rede Docker isolada, relatório de entrega, codec compacto, plano de teste de rádio.
- **Arquivos/módulos afetados:** `simulators/edge_client.py`, `simulators/transbordo_mule_client.py`, novo `connectivity/*`, `api_tcc/services/telemetria.py` (campo `via`), `docs/SYNC_PROTOCOL_V1.md`, `docs/CONECTIVIDADE.md`.
- **Arquitetura:** três responsabilidades (borda, transportador, ingestor) agora com interfaces. **Banco:** `LeituraTelemetria.via` (lista de saltos), `DeliveryHop`. **Backend:** aceitar `source='data_mule'` preservando `device_id` de origem. **Frontend:** mostrar "entregue via transbordo TB-07 com 42 min de atraso". **Hardware:** especifica o que S8 implementa. **ML/IA:** nenhuma. **Infra:** rede Docker `internal: true` simulando "sem internet". **Segurança:** assinatura por dispositivo na mensagem coletada (mule não consegue forjar). **Testes:** integração em rede real. **Docs:** `CONECTIVIDADE.md`.
- **Experimentos:** (a) máquina isolada gera 500 leituras; mule coleta em 3 encontros curtos e entrega; (b) mule reinicia no meio; (c) dois mules coletam o mesmo pacote (duplicata); (d) mule entrega 2 h depois.
- **Critérios de aceitação:** zero perda e zero duplicata em A e B; `device_id` de origem preservado; origem só libera espaço após ACK; relatório de entrega por salto.
- **Métricas:** atraso de entrega por classe; pacotes por encontro; taxa de duplicata nos mules; bytes por salto.
- **Evidências esperadas:** log do cenário e relatório em `docs/evidence/s7/`.
- **Riscos:** parecer que "provamos campo". **Não provamos**: rótulo "simulado em rede local".
- **Decisões:** D-19 (assinatura por mensagem: HMAC com chave do dispositivo vs assinatura assimétrica), D-20 (custódia: mule guarda cópia até ACK).
- **Perguntas abertas:** o transbordo real terá hardware com Wi-Fi/LoRa? Hipótese a validar nas entrevistas (S12-T4).
- **Definition of Done da semana:** cenário Mule executado 3 vezes em rede isolada com relatório.

#### S7-T1 · `ConnectivityProvider` e `ConnectivityManager`
- **Objetivo:** escolher o canal por política, não por `if`.
- **Contexto:** `edge_client` fala só HTTP.
- **Problema atual:** adicionar um canal exige mexer no laço de sincronização.
- **Estado desejado:** interface mínima + política declarativa.
- **Dependências · Pré-requisitos:** S6-T1 · nenhum.
- **Arquivos prováveis:** `connectivity/base.py`, `connectivity/manager.py`, `connectivity/providers/{http,mqtt,mule,lora_stub,sat_sim}.py`, `simulators/edge_client.py`.
- **Implementação esperada:**
```python
class ConnectivityProvider(Protocol):
    name: str
    def available(self) -> bool: ...
    def max_payload_bytes(self) -> int: ...
    def cost_per_msg(self) -> float: ...                 # 0 para wifi/mule; >0 para satélite
    def send(self, batch: list[Envelope]) -> list[Ack]: ...

POLICY = {                                              # declarativo, versionado
  "A": {"order": ["http", "mqtt", "lora", "sat"], "ttl_s": None,   "max_cost_day": 5.0},
  "B": {"order": ["http", "mqtt", "mule"],        "ttl_s": 259200, "batch_s": 60},
  "C": {"order": ["http", "mule"],                "ttl_s": 1209600,"batch_s": 900, "aggregate": True},
}
class ConnectivityManager:
    def tick(self):
        for cls in ("A", "B", "C"):
            for provider in self._candidates(cls):        # disponíveis, na ordem da política
                batch = self.outbox.next_batch(cls, provider.max_payload_bytes())
                acks = provider.send(batch)
                self.outbox.apply(acks)                   # remove só ACK válido (S1-T6)
                if acks: break
```
- **Testes necessários:** classe A usa o primeiro provider disponível; B nunca usa `sat`; orçamento diário de satélite é respeitado; falha de um provider cai para o próximo.
- **Critério de aceite:** testes verdes sem alterar o laço para adicionar o provider de teste.
- **Evidência de conclusão:** testes + diagrama em `CONECTIVIDADE.md`.
- **Risco:** over-engineering. Mantém só 2 providers reais (`http`, `mule`) e 3 stubs.
- **Relação com a estratégia:** "o sistema decide o caminho" (Ultimato 2.4).

#### S7-T2 · Protocolo de custódia do Data Mule
- **Objetivo:** o dado nunca fica "sem dono" durante o transporte.
- **Contexto:** `transbordo_mule_client.py` copia entre buffers.
- **Problema atual:** sem definição de quem pode apagar e quando.
- **Estado desejado:** estados `ORIGEM → COLETADO(mule) → ENTREGUE(backend) → ACKED`; origem apaga **somente** ao receber ACK cumulativo (via mule no próximo encontro ou direto); mule só apaga ao ver ACK do backend; hop limit e TTL.
- **Dependências · Pré-requisitos:** S7-T1 · D-20.
- **Arquivos prováveis:** `simulators/transbordo_mule_client.py`, `edge_client.py`, `docs/SYNC_PROTOCOL_V1.md` (seção custódia).
- **Implementação esperada:** `custody_token` por lote: `{origem, mule_id, coletado_em, ate_sequence, hash_lote}`; origem marca `COLETADO` (mantém cópia); ao receber `ack_ate_sequence` assinado pelo backend, libera.
- **Testes necessários:** mule perdido (nunca entrega): origem **ainda tem** os dados e reenvia depois por outro canal; mule duplicado não duplica no banco; ACK perdido: reenvio resulta em `duplicate`.
- **Critério de aceite:** três testes acima verdes.
- **Evidência de conclusão:** testes e diagrama de estados.
- **Risco:** storage da origem cresce enquanto aguarda ACK. Coberto por S6-T2.
- **Relação com a estratégia:** o que separa "simulação de transbordo" de "protocolo".

#### S7-T3 · Mule sobre rede real (Docker `internal`) e assinatura por mensagem
- **Objetivo:** provar o transporte em processos e redes distintos.
- **Contexto:** hoje a "entrega" é chamada de função/arquivo.
- **Problema atual:** não comprova que o protocolo sobrevive a rede de verdade.
- **Estado desejado:** `edge` expõe `GET /outbox/export?since=` (autenticado) em rede sem uplink; `mule` consome; `mule` entra em outra rede com `web`; mensagem assinada pela origem (HMAC ou Ed25519, D-19) para o mule não conseguir forjar nem alterar.
- **Dependências · Pré-requisitos:** S7-T2, S2-T8 · docker.
- **Arquivos prováveis:** `docker-compose.mule.yml`, `simulators/edge_server.py`, `simulators/transbordo_mule_client.py`, `services/telemetria.py` (verificação de assinatura).
- **Implementação esperada:** redes `field_net` (`internal: true`) e `base_net`; o mule container entra nas duas em fases controladas pelo script (`docker network connect/disconnect`).
- **Testes necessários:** adulteração de 1 byte pelo mule ⇒ rejeição `assinatura_invalida` + DLQ; replay de pacote antigo ⇒ `duplicate`.
- **Critério de aceite:** cenário completo passa e adulteração é detectada.
- **Evidência de conclusão:** log + vídeo curto.
- **Risco:** complexidade de rede no demo. Mitigação: scripts `make mule-demo`.
- **Relação com a estratégia:** a prova que mais convence sobre Data Mule antes do hardware.

#### S7-T4 · Relatório de entrega por salto
- **Objetivo:** responder "quantos chegaram, quantos atrasaram, quantos se perderam" por salto.
- **Contexto:** `SyncReport` (S6-T6).
- **Problema atual:** sem granularidade por salto.
- **Estado desejado:** `DeliveryHop(message, hop_index, node_id, recebido_em, entregue_em)` agregado em relatório (CSV/JSON) e na UI.
- **Dependências · Pré-requisitos:** S7-T3 · nenhum.
- **Arquivos prováveis:** `models.py`, `services/telemetria.py`, `api/views_sync.py`, `SyncPanel.tsx`.
- **Implementação esperada:** `via` na mensagem acumula `[{node, t}]`; servidor persiste.
- **Testes necessários:** 2 saltos produzem 2 registros em ordem.
- **Critério de aceite:** relatório gerado no cenário da S7-T3.
- **Evidência de conclusão:** arquivo.
- **Risco:** privacidade de rota do transbordo (localização). Tratar como dado do cliente.
- **Relação com a estratégia:** métricas de entrega (Ultimato 2.4).

#### S7-T5 · Quadro compacto e plano de teste de rádio (LoRa/ESP-NOW)
- **Objetivo:** preparar canais de baixa largura sem anunciar alcance.
- **Contexto:** ESP-NOW limita payload a 250 bytes; LoRa carrega poucas dezenas a centenas de bytes conforme configuração. Valores exatos **devem ser confirmados no datasheet/biblioteca usados**.
- **Problema atual:** JSON de ~220 B não cabe com folga em quadros pequenos.
- **Estado desejado:** codec binário compacto para classe A (campos fixos), documentado e testado; plano `docs/PLANO_TESTE_RADIO.md` com protocolo de medição (RSSI, PER, distância, obstrução, antena).
- **Dependências · Pré-requisitos:** S6-T1 · nenhum.
- **Arquivos prováveis:** `connectivity/codec_compact.py`, `firmware/lib/codec/*`, `docs/PLANO_TESTE_RADIO.md`.
- **Implementação esperada:**
```text
Quadro A compacto (little-endian), 28 bytes
 0  u8  versao
 1  u8  classe_flags (A/B/C, regime, time_source)
 2  u16 device_idx        (índice registrado no gateway; evita string)
 4  u32 sequence
 8  u32 event_time_unix_s
12  i16 temp_x100
14  u16 vib_x100
16  u16 rpm
18  i32 lat_e5
22  i32 lon_e5   (omitido se sem GPS: flag)
26  u16 crc16
```
Assinatura/HMAC **não cabe** no quadro: o gateway autentica o enlace local e assina no próximo salto (documentar o risco de spoof local e a mitigação).
- **Testes necessários:** round-trip encode/decode idêntico ao JSON em 10 mil amostras aleatórias; `crc` detecta 1 bit alterado.
- **Critério de aceite:** teste de round-trip verde; plano de rádio revisado.
- **Evidência de conclusão:** testes + documento.
- **Risco:** não afirmar "LoRa funciona" até medir (**VALIDATE_NOW**).
- **Relação com a estratégia:** destrava S8-T5 e a futura medição de alcance.

#### S7-T6 · Canal de emergência (satélite) como interface e orçamento simulado
- **Objetivo:** mostrar que a arquitetura comporta um canal caro para classe A sem construir hardware.
- **Contexto:** Ultimato 2.4: "satélite IoT apenas para alertas críticos".
- **Problema atual:** só discurso.
- **Estado desejado:** `sat_sim` com custo por mensagem e orçamento/dia; classe A usa quando nenhum canal barato está disponível; relatório de custo simulado. **Nenhum hardware, nenhuma promessa.**
- **Dependências · Pré-requisitos:** S7-T1 · nenhum.
- **Arquivos prováveis:** `connectivity/providers/sat_sim.py`, teste.
- **Implementação esperada:** payload compacto (S7-T5) e deduplicação por `(device, sequence)`.
- **Testes necessários:** estouro de orçamento: alerta registrado, mensagem fica na fila (não some).
- **Critério de aceite:** teste verde.
- **Evidência de conclusão:** teste.
- **Risco:** parecer funcionalidade real. Rótulo "SIMULADO" obrigatório (S3-T1).
- **Relação com a estratégia:** `ARCHITECT_NOW` sem engolir escopo.

#### S7-T7 · Topologia do gateway: notebook (demo) vs dispositivo (produto)
- **Objetivo:** dizer com precisão onde roda cada coisa.
- **Contexto:** Ultimato 1.1: "raspberry ou ESP32 com broker local não existe no repo"; o gateway da demo é o notebook.
- **Problema atual:** documentação sugere ESP32 #2 como gateway/servidor.
- **Estado desejado:** `docs/CONECTIVIDADE.md` com tabela: **Demo**: notebook + Docker + hotspot; **Protótipo de bancada**: ESP32 #2 apenas retransmite ESP-NOW→MQTT; **Produto**: mini-PC/Raspberry com broker + dashboard local; ESP32 sozinho **não** serve Next.js.
- **Dependências · Pré-requisitos:** nenhuma · nenhum.
- **Arquivos prováveis:** `docs/CONECTIVIDADE.md`, `README.md`.
- **Implementação esperada:** diagramas; pergunta "o que roda sem internet?" respondida por linha.
- **Testes necessários:** revisão.
- **Critério de aceite:** consistente com `CLAIMS_VS_CODE.md`.
- **Evidência de conclusão:** commit.
- **Risco:** a Proposta TCC v4 diz "servidor HTTP embarcado no ESP32 #2 servindo dashboard". Corrigir a proposta (um ESP32 pode servir uma página estática pequena, **não** o Next.js com Chart.js e dados).
- **Relação com a estratégia:** elimina contradição que um avaliador exploraria.

---

### SEMANA 8 · HARDWARE REAL (DO SIMULADOR AO ESP32 NA BANCADA)

> **NOTA V5:** S8-T12 passa a escutar o **motor diesel escolhido em S18-T1** (de preferência o mesmo da campanha). O acelerômetro (S8-T2) ganha uso no corpo da bomba (S18-T12).


> **NOTA V4:** **A S8 executa desde o dia 1, em paralelo (trilha B).** O número 8 é histórico. Tarefas novas: S8-T10 (compras/BOM), T11 (hall e GPS), T12 (CAN real em modo só escuta), T13 (EWMA/CUSUM e alarme local), T14 (escada de integração). S8-T7 (CAN com emissor de teste) vira **pré-teste**; a prova real é S8-T12.


**Camadas:** IMPLEMENTATION · VALIDATION · SECURITY

- **Objetivo estratégico:** pela primeira vez, **um dado nascido de sensor físico percorre o fluxo real** até a decisão na tela, com a internet cortada ao vivo.
- **Objetivo técnico:** firmware C++ versionado em `firmware/` (PlatformIO); 1 ESP32 + DS18B20 publicando MQTT direto no Mosquitto (primeiro passo de menor custo); RTC DS3231; acelerômetro com features (RMS, pico, curtose); outbox em flash com recuperação; ESP-NOW para um segundo ESP32 (gateway de campo); CAN/J1939 em bancada com emissor simulado; plano de segurança do dispositivo.
- **Por que existe:** Ultimato 1.1 (passo 4), 2.6 e 2.7: zero firmware no repo; SW-420 não mede amplitude; ESP32 sem NTP offline; leitura CAN real exige acesso autorizado. Segundo o que foi relatado, a Giovana já montou protoboard com sensores DHT (ambiente), que serve de ponto de partida.
- **Problemas que resolve:** nenhuma prova física; ausência de `.ino`/PlatformIO; demo dependente de simulador; hora no dispositivo; ausência de decisão sobre segurança de borda.
- **Dependências recebidas:** S1 (contrato de tempo), S2 (credencial por dispositivo, ACL), S6/S7 (protocolo, quadro compacto).
- **Entregáveis:** `firmware/` completo (`platformio.ini`, `src/`, `lib/`, `include/`), vídeo de bancada, protocolo de teste físico, `docs/REPOSICIONAMENTO_ESCOPO_HARDWARE.md`, BOM, plano de segurança.
- **Arquivos/módulos afetados:** novo `firmware/**`, `contracts/*` (geração de headers), `docs/HARDWARE.md`, `docs/BOM.md`.
- **Arquitetura:** nó sensor → (MQTT direto | ESP-NOW → gateway) → broker. **Banco:** nenhuma obrigatória. **Backend:** aceitar quadro compacto via gateway. **Frontend:** badge "origem: medido (ESP32)" via `data_origin`. **Hardware:** núcleo. **ML/IA:** features de vibração alimentam IF. **Infra:** hotspot do notebook. **Segurança:** flash encryption (plano), credencial por dispositivo. **Testes:** bancada + testes de host (Unity/PlatformIO `native`). **Docs:** hardware e BOM.
- **Experimentos:** aquecer o DS18B20 de forma **segura** (copo com água morna se for a versão à prova d'água, secador de cabelo a distância; **nunca isqueiro**: derrete o cabo e é risco em sala); cortar o uplink do notebook e o Wi-Fi do gateway; religar.
- **Critérios de aceitação:** leitura real chega ao banco com `data_origin=medido`; alerta local sai em < 3 s sem internet (meta a **medir**); religamento sincroniza sem duplicata.
- **Métricas:** latência sensor → broker; PER do ESP-NOW; consumo (se medido); taxa de reconexão; uso de flash do outbox.
- **Evidências esperadas:** vídeo da bancada, log serial, relatório.
- **Riscos:** hardware atrasar; sensor impreciso; ESP-NOW e Wi-Fi competindo por canal; potenciômetro apresentado como RPM real (se for simulação, **dizer**).
- **Decisões:** D-04, D-21 (MCP2515 vs controlador TWAI nativo do ESP32 + transceiver), D-22 (RPM real por sensor hall/óptico vs simulado e declarado).
- **Perguntas abertas:** acesso a banco de teste J1939 ou emissor simulado? Resposta provisória: **segundo ESP32 emitindo quadros J1939 de teste**.
- **Definition of Done da semana:** vídeo de 60 a 90 s, sem cortes, do fluxo físico completo; firmware compila em CI; documento de reposicionamento publicado.

#### S8-T1 · Estrutura do firmware e primeiro nó (DS18B20 → MQTT)
- **Objetivo:** hardware real publicando no worker real, com o menor número de variáveis.
- **Contexto:** nenhum `.ino`; compose já tem Mosquitto com ACL (S2-T1).
- **Problema atual:** worker nunca viu dado físico.
- **Estado desejado:** projeto PlatformIO versionado; publica em `fieldnode/<device_id>/telemetria`; reconecta; LED de estado; segredos em `include/secrets.h` **fora do Git** (`secrets.example.h` versionado).
- **Dependências · Pré-requisitos:** S2-T1, S1-T1 · ESP32 DevKit, DS18B20 com resistor pull-up de 4,7 kΩ.
- **Arquivos prováveis:** `firmware/platformio.ini`, `firmware/src/main.cpp`, `firmware/include/{config.h,secrets.example.h,severity_contract.h}`, `firmware/lib/*`.
- **Implementação esperada:**
```cpp
// firmware/src/main.cpp (esqueleto; formatação Google C++ Style)
#include <WiFi.h>
#include <PubSubClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "secrets.h"
#include "severity_contract.h"   // GERADO de contracts/severity.v1.json (S1-T1)

static OneWire one_wire(PIN_DS18B20);
static DallasTemperature ds18b20(&one_wire);
static char boot_id[37];          // UUID gerado em cada boot (esp_random)
static uint32_t sequence = 0;     // restaurado de NVS (S8-T4)

void setup() {
  Serial.begin(115200);
  ds18b20.begin();
  generate_boot_id(boot_id);
  load_sequence_from_nvs(&sequence);
  wifi_connect_with_backoff();
  mqtt_connect(MQTT_USER, MQTT_PASS);          // usuário = device_id (ACL)
}

void loop() {
  mqtt_loop_reconnect();
  if (!sample_due(2000)) return;               // 1 amostra a cada 2 s
  ds18b20.requestTemperatures();
  const float t = ds18b20.getTempCByIndex(0);
  if (t == DEVICE_DISCONNECTED_C) { report_sensor_fault(); return; }   // nunca publicar -127 como dado
  const Severity sev = classify_temperature(t);                         // contrato único
  publish_reading(t, sev, ++sequence);          // JSON do contrato com boot_id, uptime_ms, time_source
  persist_sequence(sequence);
}
```
Regra: `-127.0` (sensor desconectado) **não** é leitura; vira evento de falha de sensor.
- **Testes necessários:** teste de host (`pio test -e native`) do classificador gerado do contrato; ensaio de bancada com sensor desconectado.
- **Critério de aceite:** `mosquitto_sub` mostra mensagens; `mqtt_listen` grava com `data_origin=medido`.
- **Evidência de conclusão:** log + captura da tela mostrando o selo "medido".
- **Risco:** WiFi da banca instável. Mitigação: hotspot próprio (S12-T3).
- **Relação com a estratégia:** a prova mais barata e a que mais pesa.

#### S8-T2 · Acelerômetro e features de vibração (substituir SW-420)
- **Objetivo:** vibração com amplitude e conteúdo, não um interruptor.
- **Contexto:** SW-420 dá liga/desliga por limiar (Ultimato 2.6).
- **Problema atual:** o dado `vibracao` não carrega informação de amplitude/frequência.
- **Estado desejado:** MPU6050 (ou ADXL345) amostrando por janela; o firmware envia **features** (RMS, pico, curtose por eixo, energia por faixa quando possível), não bruto; contrato ganha `vibracao_rms_g`, `vibracao_pico_g`, `vibracao_curtose`, `vibracao_unit`.
- **Dependências · Pré-requisitos:** S1-T2, S8-T1 · sensor I2C.
- **Arquivos prováveis:** `firmware/lib/vibration/{features.cpp,features.h}`, `api_tcc/services/telemetria.py` (campos opcionais), `contracts/telemetry.v1.2.json`.
- **Implementação esperada:**
```cpp
struct VibFeatures { float rms_g, peak_g, kurtosis; };
VibFeatures compute(const float* a, size_t n) {          // a[i] em g, já sem componente DC
  double s2 = 0, s4 = 0, pk = 0;
  for (size_t i = 0; i < n; ++i) { const double x = a[i]; s2 += x*x; s4 += x*x*x*x; pk = fmax(pk, fabs(x)); }
  const double ms = s2 / n;
  return { (float)sqrt(ms), (float)pk, (float)((s4 / n) / (ms * ms)) };
}
```
Remover a componente contínua (gravidade) antes; documentar orientação e fixação do sensor (resultado depende de como está montado).
- **Testes necessários:** teste de host com senoide de amplitude conhecida (RMS = A/√2, curtose ≈ 1,5) e ruído gaussiano (curtose ≈ 3).
- **Critério de aceite:** valores batem com os teóricos em tolerância documentada.
- **Evidência de conclusão:** teste nativo + gráfico.
- **Risco:** MPU6050 e a vibração real de colheitadeira têm faixas/frequências diferentes; **é validação de método de bancada**.
- **Relação com a estratégia:** aproxima o IF de um sinal que significa algo.

#### S8-T3 · RTC DS3231 e fonte de tempo
- **Objetivo:** hora válida offline, com proveniência declarada.
- **Contexto:** ESP32 sem NTP offline não tem horário; S1-T5 define `time_source`.
- **Problema atual:** sem hora, o contrato é violado.
- **Estado desejado:** DS3231 por I2C; ajuste inicial por gateway/notebook quando disponível (`time_source=gateway`), depois `rtc`; se RTC ausente ou bateria fraca, `unsynced` + `boot_id` + `uptime_ms`.
- **Dependências · Pré-requisitos:** S1-T5 · módulo DS3231 com pilha.
- **Arquivos prováveis:** `firmware/lib/clock/*`.
- **Implementação esperada:** verificar flag de perda de oscilador (OSF) do chip no boot; se perdida, marcar `unsynced` até novo ajuste.
- **Testes necessários:** desligar tudo por 10 min e religar: hora coerente; remover bateria: `unsynced`.
- **Critério de aceite:** nenhuma leitura sai com `time_source=rtc` se OSF indicar perda.
- **Evidência de conclusão:** log serial.
- **Risco:** deriva; registrar ppm típico do datasheet e medir.
- **Relação com a estratégia:** resolve o problema que o Ultimato apontou antes de ligar o hardware.

#### S8-T4 · Outbox no firmware (flash) com recuperação
- **Objetivo:** não perder leitura em reinício ou queda de energia.
- **Contexto:** `edge_client.py` define semântica; firmware precisa equivalente.
- **Problema atual:** buffer de "30 dias" não existe.
- **Estado desejado:** registros append-only em LittleFS com CRC32, `sequence` persistido em NVS **antes** do envio, varredura de recuperação no boot, 3 filas lógicas A/B/C, política de disco cheio de S6-T2.
- **Dependências · Pré-requisitos:** S6-T1, S6-T2, S8-T1 · partição LittleFS definida.
- **Arquivos prováveis:** `firmware/lib/outbox/{outbox.cpp,outbox.h}`, `firmware/partitions.csv`.
- **Implementação esperada:**
```cpp
struct __attribute__((packed)) Rec { uint32_t seq; uint32_t t_unix; uint8_t cls; uint16_t len; uint8_t body[220]; uint32_t crc32; };
// escrever: append -> fsync -> só então incrementar o "write cursor" persistente
// ler: valida crc32, ignora registro truncado no fim (queda no meio da escrita)
// remover: só avança o "ack cursor" quando o servidor devolve ACK cumulativo
```
Estimar desgaste: ciclos de escrita da flash × bytes/dia (registrar a conta no `docs/HARDWARE.md`; **usar valores do datasheet da flash da placa usada**).
- **Testes necessários:** cortar energia 50 vezes em instantes aleatórios durante escrita; sequência nunca regride; nenhum registro corrompido é enviado.
- **Critério de aceite:** 50/50 recuperações sem perda de registro confirmado.
- **Evidência de conclusão:** log do teste e resumo.
- **Risco:** desgaste da flash. Agregar classe C reduz escrita.
- **Relação com a estratégia:** a promessa de buffer passa a ter mecanismo e número.

#### S8-T5 · ESP-NOW do nó para o gateway de campo
- **Objetivo:** a topologia `ESP32 #1 → ESP32 #2 → broker` funcionando.
- **Contexto:** a proposta cita ESP-NOW; nada existe.
- **Problema atual:** só texto.
- **Estado desejado:** nó envia quadro compacto (S7-T5, ≤ 250 B); gateway valida CRC, converte para o envelope e publica MQTT/HTTP; devolve ACK por ESP-NOW; **canal fixo** igual ao do Wi-Fi do gateway (restrição conhecida de coexistência).
- **Dependências · Pré-requisitos:** S7-T5, S8-T1, S8-T4 · 2 ESP32.
- **Arquivos prováveis:** `firmware/node/`, `firmware/gateway/`, `firmware/lib/espnow_link/*`.
- **Implementação esperada:** `esp_now_register_send_cb` para contar falhas; reenvio por classe; PER medido por distância e obstáculos (tabela no relatório).
- **Testes necessários:** perda induzida (afastar/obstruir): sem perda de registros confirmados pelo ACK.
- **Critério de aceite:** relatório com PER e alcance **medidos** em 3 ambientes; sem afirmar valor de catálogo.
- **Evidência de conclusão:** tabela + vídeo.
- **Risco:** alcance real menor que o de catálogo (o repo já documenta 50 a 200 m como típico; **medir**).
- **Relação com a estratégia:** valida o que a proposta promete.

#### S8-T6 · Demo de bancada: cortar a internet ao vivo
- **Objetivo:** roteiro físico reproduzível e seguro.
- **Contexto:** plano da banca: sensor, alerta local, religar e mostrar sync com números **medidos**.
- **Problema atual:** roteiro cita "0% de perda" antes de medir (Ultimato 1.1).
- **Estado desejado:** passo a passo com tempos e checklist; números do slide **vêm do `teste_resiliencia`** e do ensaio físico.
- **Dependências · Pré-requisitos:** S8-T1 a T5, S6-T5 · hotspot.
- **Arquivos prováveis:** `docs/ROTEIRO_DEMO_BANCA.md` (parte física).
- **Implementação esperada:** (1) tudo online, dado fluindo; (2) cortar uplink do notebook; dashboard local continua; (3) aquecer sensor com método seguro; (4) alerta local no gateway (buzzer/LED/dashboard) em < 3 s (medir); (5) religar; (6) painel de sincronização mostra backlog zerando; (7) decisão na fila; (8) aprovar.
- **Testes necessários:** 3 ensaios cronometrados sem intervenção fora do script.
- **Critério de aceite:** 3 execuções seguidas.
- **Evidência de conclusão:** vídeo da terceira.
- **Risco:** falha ao vivo. Fallback: vídeo gravado (decisão do pitch: o vídeo é o plano A, demo ao vivo na feira).
- **Relação com a estratégia:** o "uau" honesto.

#### S8-T7 · CAN/J1939 em bancada (emissor simulado)
- **Objetivo:** provar o caminho `PGN/SPN → parâmetro canônico` sem depender de máquina real.
- **Contexto:** a pesquisa do grupo afirma que J1939 é a camada de aplicação padrão; acesso real exige ECU compatível e autorização.
- **Problema atual:** `FabricanteMapping` com 2 fabricantes inventados.
- **Estado desejado:** ESP32 com controlador CAN nativo (TWAI) + transceiver (ou MCP2515, D-21) lendo quadros de um **emissor de teste** (outro ESP32/adaptador USB-CAN); decodificação de PGNs comuns; mapeamento para `engine.rpm`, `engine.coolant_temp`, `engine.oil_pressure`, `dtc.active`.
- **Dependências · Pré-requisitos:** S8-T1 · hardware CAN + tabela de PGN/SPN (**a especificação SAE J1939-71 é paga**: usar tabelas públicas e **conferir cada valor** antes de usar; tratar como `VALIDATE_NOW`).
- **Arquivos prováveis:** `firmware/lib/j1939/*`, `api_tcc/services/normalizacao.py`, `FabricanteMapping` (fixture `j1939_v1`).
- **Implementação esperada:**
```cpp
// ID J1939 de 29 bits: prioridade(3) | reservado/DP(2) | PF(8) | PS(8) | SA(8)
uint32_t pgn_from_id(uint32_t id) {
  uint8_t pf = (id >> 16) & 0xFF, ps = (id >> 8) & 0xFF, dp = (id >> 24) & 0x03;
  return (pf < 240) ? ((dp << 16) | (pf << 8)) : ((dp << 16) | (pf << 8) | ps);   // PDU1 x PDU2
}
// exemplos a CONFERIR na tabela pública antes de adotar: PGN 61444 (EEC1, rotação), 65262 (ET1, temperaturas), 65263 (pressão de óleo), 65226 (DM1, falhas ativas)
```
Valor "não disponível" (padrão J1939: campos preenchidos com 0xFF/0xFFFF) **nunca** vira número: vira `ausente`. Conferir os códigos de "erro" e "não disponível" de cada SPN na tabela pública usada.
- **Testes necessários:** teste de host com quadros fixos e resultados esperados; DM1 gera `Event` de falha com `data_origin=medido`, rótulo "bancada".
- **Critério de aceite:** mesmo parâmetro canônico a partir de PGN decodificado e de payload simulado.
- **Evidência de conclusão:** teste + captura.
- **Risco:** afirmar compatibilidade com máquina real. **Proibido**: comunicação diz "bancada com emissor J1939 de teste".
- **Relação com a estratégia:** base verdadeira do Universal Machine Model (S11).

#### S8-T8 · Segurança do dispositivo e reposicionamento de escopo de hardware
- **Objetivo:** declarar o que o hardware protege e o que não.
- **Contexto:** chave gravada em flash é extraível sem flash encryption; risco registrado desde o v2.
- **Problema atual:** sem decisão.
- **Estado desejado:** `docs/REPOSICIONAMENTO_ESCOPO_HARDWARE.md` e `docs/HARDWARE.md`: o que é bancada, o que é roadmap; plano de **flash encryption + secure boot** (`ARCHITECT_NOW`: irreversível em eFuses, só aplicar quando o hardware de demo estiver fechado); credencial por dispositivo (S2-T8); OTA `DEFER`.
- **Dependências · Pré-requisitos:** S8-T1, S2-T8 · nenhum.
- **Arquivos prováveis:** docs, `firmware/README.md`, `docs/BOM.md`.
- **Implementação esperada:** BOM com o que foi comprado, custo real, fornecedor e data (não estimar sem comprar).
- **Testes necessários:** revisão.
- **Critério de aceite:** consistente com `CLAIMS_VS_CODE.md`.
- **Evidência de conclusão:** commit.
- **Risco:** habilitar secure boot sem plano de recuperação inutiliza a placa. Só em placa dedicada.
- **Relação com a estratégia:** maturidade de engenharia.

#### S8-T9 · CI do firmware
- **Objetivo:** firmware que não compila não entra na `main`.
- **Contexto:** nenhum firmware hoje.
- **Problema atual:** sem build automatizado.
- **Estado desejado:** job `pio run` e `pio test -e native` no CI; artefato `.bin`.
- **Dependências · Pré-requisitos:** S8-T1, S10-T1 · nenhum.
- **Arquivos prováveis:** `.github/workflows/firmware.yml`.
- **Implementação esperada:** cache do PlatformIO; `secrets.example.h` copiado para `secrets.h` no job.
- **Testes necessários:** o job.
- **Critério de aceite:** verde.
- **Evidência de conclusão:** badge.
- **Risco:** baixo.
- **Relação com a estratégia:** disciplina de produto.


#### S8-T10 · BOM v2 e compras (sensores certos, lead time de semana 1)
- **Objetivo:** ter na mesa, na semana 1 a 2, o conjunto de hardware que permite sair da simulação sem esperar entrega.
- **Contexto:** o protótipo anterior usa DHT (sensor de **ambiente**, lento) e SW-420 (**interruptor** de vibração). Para máquina, temperatura precisa de sonda adequada, vibração precisa de acelerômetro, rotação de sensor de pulso.
- **Problema atual:** BOM de V3 genérico; sem data, fornecedor ou preço real; compras atrasam todo o caminho crítico (soak de 14 dias).
- **Estado desejado:** `docs/BOM.md` com item, uso, quantidade, fornecedor, **preço e data da cotação**, status (pedido/chegou/testado) e responsável.
- **Dependências · Pré-requisitos:** nenhuma · orçamento do grupo aprovado (decisão D-31).
- **Arquivos prováveis:** `docs/BOM.md`, `docs/HARDWARE.md`.
- **Implementação esperada:** lista da seção 0.7; regra de escolha: **DS18B20 inox** (faixa de uso adequada a fluido/superfície até 125 °C, conferir encapsulamento), **termopar tipo K com MAX31855** (ou MAX6675) para superfície quente e rolamento, **MPU6050** (ou ADXL345) para vibração, **sensor hall/óptico** para RPM, **módulo GPS UART**, **DS3231**, **INA219**, OLED I2C, buzzer e LED, transceptor CAN 3,3 V, 3 placas com LoRa. Comprar **duplicado** de sensores baratos (um quebra). Etiquetar cada peça.
- **Testes necessários:** teste de recebimento: cada peça é ligada isoladamente e lida (sketch mínimo) antes de integrar.
- **Critério de aceite:** BOM completo e **100% das peças com teste de recebimento** registrado.
- **Evidência de conclusão:** foto do kit + planilha de recebimento.
- **Risco:** peça falsificada/defeituosa (sensor "DS18B20" lendo -127 ou 85 fixo). Mitigação: duplicatas e teste de recebimento.
- **Relação com a estratégia:** destrava a trilha B no dia 1.

#### S8-T11 · RPM real (hall/óptico) e GPS (velocidade e posição)
- **Objetivo:** `rpm` e `velocidade` deixam de ser simulados; o regime (S5-T3) passa a ter base física.
- **Contexto:** a regra de regime depende de rotação e velocidade; velocidade vem de GPS.
- **Problema atual:** RPM por potenciômetro seria simulação; sem GPS não há velocidade nem trilha.
- **Estado desejado:** contagem de pulsos por interrupção (com debounce por hardware/software) convertida em RPM; GPS por UART com `TinyGPSPlus` (ou similar), `fix`, `hdop`, `speed_kmh`, `lat`, `lon`; ambos entram no contrato como campos opcionais com `data_origin=medido`.
- **Dependências · Pré-requisitos:** S8-T1 · sensor hall, ímã no eixo (motor do rig ou ventilador), módulo GPS com antena e visada de céu.
- **Arquivos prováveis:** `firmware/lib/rpm/*`, `firmware/lib/gps/*`, `contracts/telemetry.v1.2.json`, `api_tcc/services/telemetria.py`.
- **Implementação esperada:**
```cpp
volatile uint32_t pulses = 0; volatile uint32_t last_us = 0;
void IRAM_ATTR on_pulse() { const uint32_t now = micros(); if (now - last_us > 500) { ++pulses; last_us = now; } }   // 500 us de debounce
float rpm_from(uint32_t pulses_in_window, float window_s, uint8_t pulses_per_rev) { return (pulses_in_window / (float)pulses_per_rev) * (60.0f / window_s); }
// GPS: só marcar velocidade/posição quando fix válido e hdop <= limite; senão enviar "ausente", nunca zero.
```
- **Testes necessários:** frequência conhecida injetada por gerador de pulsos (ou segundo ESP32) em 3 valores; GPS sem fix não publica coordenada falsa.
- **Critério de aceite:** erro de RPM ≤ tolerância documentada em 3 frequências; sem fix ⇒ campo ausente.
- **Evidência de conclusão:** tabela de calibração + vídeo.
- **Risco:** GPS interno não pega fix. Testar ao ar livre e documentar tempo até o primeiro fix.
- **Relação com a estratégia:** o regime operacional é o que impede "IA que alarma tudo".

#### S8-T12 · CAN **real** em modo só escuta (veículo de verdade)
- **Objetivo:** primeira leitura de barramento real, sem risco para a máquina.
- **Contexto:** a V3 usava um segundo ESP32 emissor de teste; isso continua sendo simulação.
- **Problema atual:** o decodificador J1939/OBD nunca viu quadro de equipamento real.
- **Estado desejado:** ESP32 com controlador TWAI nativo + transceptor 3,3 V, **modo `LISTEN_ONLY` (nunca transmite)**, ligado ao conector de diagnóstico de (a) um **carro** (OBD-II, tipicamente 500 kbit/s, **confirmar**) e/ou (b) um **veículo pesado com conector J1939** (tipicamente 250 kbit/s, **confirmar**), **com autorização do dono**. Quadros brutos gravados e decodificados em `services/j1939.py` (S11-T3) e/ou tabela OBD-II.
- **Dependências · Pré-requisitos:** S8-T1 · veículo e autorização, transceptor, cabo de diagnóstico.
- **Arquivos prováveis:** `firmware/lib/can_listen/*`, `data/can_raw/*.log` (fora do Git se sensível), `services/j1939.py`.
- **Implementação esperada:**
```cpp
#include "driver/twai.h"
void can_begin(gpio_num_t tx, gpio_num_t rx, bool j1939_250k) {
  twai_general_config_t g = TWAI_GENERAL_CONFIG_DEFAULT(tx, rx, TWAI_MODE_LISTEN_ONLY);   // NUNCA TWAI_MODE_NORMAL em equipamento de terceiros
  twai_timing_config_t t = j1939_250k ? TWAI_TIMING_CONFIG_250KBITS() : TWAI_TIMING_CONFIG_500KBITS();
  twai_filter_config_t f = TWAI_FILTER_CONFIG_ACCEPT_ALL();
  ESP_ERROR_CHECK(twai_driver_install(&g, &t, &f)); ESP_ERROR_CHECK(twai_start());
}
void can_poll() { twai_message_t m; while (twai_receive(&m, 0) == ESP_OK) { log_frame(m.identifier, m.extd, m.data, m.data_length_code); } }
```
Regra de segurança: **o hardware não tem caminho de TX ligado** (transceptor sem ligação no pino TX do barramento em modo de teste, ou verificação por osciloscópio/analisador), documentado no relatório.
- **Testes necessários:** taxa de bit errada gera erro de bus (documentar sintoma); gravação de 30 min; decodificação de parâmetros comuns com **conferência manual contra scanner/painel** (valor mostrado no painel do veículo × valor decodificado).
- **Critério de aceite:** pelo menos 3 parâmetros (ex.: rotação, temperatura do líquido, velocidade) decodificados e **conferidos** contra uma fonte independente; zero quadros transmitidos.
- **Evidência de conclusão:** log bruto anonimizado + tabela de conferência + foto da instalação.
- **Risco:** conectar em máquina sem autorização ou transmitir por engano. **Proibido.** Sem autorização formal, usar apenas carro próprio.
- **Relação com a estratégia:** base real do Universal Machine Model; substitui o "CAN simulado" da V3 sem arriscar equipamento.

#### S8-T13 · Triagem EWMA/CUSUM no nó, alarme local e prescrição curta no display
- **Objetivo:** o nó decide e **alarma sozinho**, mesmo sem gateway, e escolhe o que merece canal caro.
- **Contexto:** controle estatístico simples (≈ 20 linhas) roda no ESP32; não tem relação com "LLM no ESP32".
- **Problema atual:** o nó só classifica por limiar; sem sinal de tendência; sem saída local.
- **Estado desejado:** por métrica, EWMA para baseline adaptativo e CUSUM para detectar deslocamento sustentado; baseline **congela** durante alarme (para não "aprender" a falha); alarme local (LED, buzzer, OLED) com **código de prescrição curta** (`P03` → "TEMP ALTA: PARAR E INSPECIONAR") vindo de tabela fixa gerada do contrato/playbooks; flag `tendencia_anomala` sobe a classe da mensagem para A.
- **Dependências · Pré-requisitos:** S8-T1, S1-T1 · OLED, buzzer.
- **Arquivos prováveis:** `firmware/lib/spc/{spc.h,spc.cpp}`, `firmware/lib/local_alarm/*`, `firmware/include/prescricao_curta.h` (gerado).
- **Implementação esperada:**
```cpp
struct Spc { float mean=0, var=0, s_hi=0, s_lo=0; bool init=false; bool frozen=false; };
// alpha ~ 0.05 (janela efetiva ~ 20 amostras), k ~ 0.5 sigma, h ~ 5 sigma: PARÂMETROS A CALIBRAR com a campanha S15-T1
int spc_update(Spc& s, float x, float alpha, float k, float h) {
  if (!s.init) { s.mean = x; s.var = 0; s.init = true; return 0; }
  const float d = x - s.mean;
  const float sd = sqrtf(s.var) + 1e-3f;
  const float z = d / sd;
  s.s_hi = fmaxf(0.f, s.s_hi + z - k);
  s.s_lo = fmaxf(0.f, s.s_lo - z - k);
  const bool alarm = (s.s_hi > h) || (s.s_lo > h);
  if (!s.frozen && !alarm) { s.mean += alpha * d; s.var = (1 - alpha) * (s.var + alpha * d * d); }   // só aprende em condição normal
  s.frozen = alarm;
  return alarm ? (s.s_hi > h ? +1 : -1) : 0;
}
```
- **Testes necessários:** teste nativo com séries: degrau sustentado dispara CUSUM; pico isolado **não** dispara; deriva lenta dentro da tolerância não dispara; baseline não aprende durante alarme; alarme local acende com a internet e o gateway desligados.
- **Critério de aceite:** quatro séries de teste com resultado esperado; demonstração física: aquecer a sonda (método seguro) e ver buzzer/OLED sem nenhum gateway ligado.
- **Evidência de conclusão:** vídeo + saída do teste nativo.
- **Risco:** parâmetros arbitrários. São calibrados na campanha (S15-T1) e registrados por versão do contrato.
- **Relação com a estratégia:** pilar OFFLINE-100 (item 1) e "alarme local" que a avaliação externa exigiu.

#### S8-T14 · Protocolo de integração incremental (uma variável por vez)
- **Objetivo:** evitar horas de depuração por misturar sensor, firmware, rádio, broker e backend de uma vez.
- **Contexto:** hardware e firmware "nunca funcionam de primeira".
- **Problema atual:** sem ordem de integração nem critérios de passagem.
- **Estado desejado:** escada de 8 degraus; só sobe o degrau seguinte quando o anterior tem evidência.
- **Dependências · Pré-requisitos:** S8-T10 · nenhum.
- **Arquivos prováveis:** `docs/INTEGRACAO_HARDWARE.md`.
- **Implementação esperada:**

| Degrau | O que liga | Passou quando | Se falhar, suspeitar de |
|---|---|---|---|
| 1 | ESP32 + 1 sensor, serial | leitura estável 10 min | fiação, resistor, alimentação |
| 2 | + Wi-Fi + MQTT para o notebook | `mosquitto_sub` recebe | credencial, rede, hotspot |
| 3 | + backend local | linha no banco com unidade e `device_id` | contrato, validação |
| 4 | + RTC e sequência persistente | reinício não regride sequência | NVS, hora |
| 5 | + outbox em flash | 50 cortes de energia sem perda | LittleFS, CRC |
| 6 | + segundo ESP32 (ESP-NOW) | ACK e PER medidos | canal, distância |
| 7 | + LoRa | RSSI e PER por distância | antena, faixa, SF |
| 8 | + alarme local e sensores extras | alarme sem gateway | pinagem, tensão |

- **Testes necessários:** cada degrau tem um script/checklist curto em `firmware/tests/bancada/`.
- **Critério de aceite:** cada degrau marcado com data, responsável e evidência.
- **Evidência de conclusão:** `INTEGRACAO_HARDWARE.md` preenchido.
- **Risco:** pular degrau "porque funcionou antes". Não pula.
- **Relação com a estratégia:** previsibilidade da trilha B.

---

### SEMANA 9 · OPERATION GRAPH v0.1 E CONSEQUENCE ENGINE v0.1

> **NOTA V5:** O horizonte por tendência da S9-T3 vira **fallback**: quando houver indicador de saúde por componente, o prazo oficial é o **PLM** (S19-T6).


> **NOTA V4:** A S9 mantém o v0.1 sem número inventado e **acrescenta** a visão simples 'a colheitadeira X parou, avise o transbordo Y' como primeira entrega (S9-T6). Custo financeiro continua opcional e sem valor padrão (D-24).


**Camadas:** ARCHITECTURE · IMPLEMENTATION · VALIDATION

- **Objetivo estratégico:** o alerta deixa de ser "a máquina X está quente" e passa a ser "a máquina X está quente **e isto afeta Y e Z**", **sem inventar números**.
- **Objetivo técnico:** modelo relacional de relações entre `Machine` (colhedora, transbordo, caminhão), `Front` e `Site`; propagação de impacto por regras explícitas; incidente que agrupa sintomas correlacionados no tempo; estimativa financeira **só** com premissa fornecida pelo cliente; UI com o diagrama de impacto.
- **Por que existe:** Ultimato 2.4 e 2.8: motor de consequência é o maior buraco entre o que se promete e o que existe; grep confirma que não há código. `agentic.py` declara `operation_graph: indisponivel_na_poc`.
- **Problemas que resolve:** alerta isolado; prescrição genérica; impossibilidade de priorizar por impacto operacional.
- **Dependências recebidas:** S1, S3, S4 (Decision/OS), S5 (regime), S6 (reconstrução).
- **Entregáveis:** `Site`, `Front`, `MachineLink`, `ConsequenceAssessment`, `Incident`, `OrganizationPolicy`, serviço de consequência, UI.
- **Arquivos/módulos afetados:** `models.py`, novo `services/operation_graph.py`, `services/consequence.py`, `services/incidents.py`, `services/agentic.py`, `api/views_consequence.py`, front.
- **Arquitetura:** grafo **relacional** (sem banco de grafos). **Banco:** migrations 0033 a 0037. **Backend:** serviços. **Frontend:** painel de consequência e diagrama. **Hardware:** nenhuma. **ML/IA:** contexto estruturado para o LLM. **Infra:** nenhuma. **Segurança:** isolamento por organização. **Testes:** cenário golden. **Docs:** `docs/CONSEQUENCE_ENGINE.md`.
- **Experimentos:** 3 cenários: colhedora crítica com transbordo associado; transbordo parado; sem relação cadastrada (o sistema **diz** que não sabe).
- **Critérios de aceitação:** em cada cenário, o texto de consequência cita **apenas** o que está cadastrado e calculável; ausência de dado vira "não estimado".
- **Métricas:** % de eventos críticos com consequência calculada; % com premissas completas.
- **Evidências esperadas:** testes, captura do painel.
- **Riscos:** inventar impacto. Regra de ouro: *horizonte e custo só existem se houver premissa configurada*.
- **Decisões:** D-23 (grafo relacional em Django), D-24 (custo da hora parada configurável, sem valor padrão).
- **Perguntas abertas:** a relação colhedora-transbordo é fixa ou muda por turno? Entrevistas decidem; modelo suporta validade temporal.
- **Definition of Done da semana:** cenário golden verde e visível na UI.

#### S9-T1 · Modelo relacional do grafo operacional
- **Objetivo:** representar quem depende de quem.
- **Contexto:** hoje `Transbordo` é tabela legada (Modelo + Capacidade) sem ligação com `Machine`.
- **Problema atual:** não há relação entre ativos.
- **Estado desejado:** `Machine.tipo ∈ {colhedora, transbordo, caminhao, trator, outro}`; `Site`, `Front`; `MachineLink(origem, destino, tipo ∈ {alimenta, transporta_para, depende_de}, front, valido_de, valido_ate)`.
- **Dependências · Pré-requisitos:** S2-T6 · nenhum.
- **Arquivos prováveis:** `models.py`, migrations, `services/operation_graph.py`, migração do legado `Transbordo`.
- **Implementação esperada:**
```python
class MachineLink(models.Model):
    class Tipo(models.TextChoices):
        ALIMENTA = "ALIMENTA"; TRANSPORTA_PARA = "TRANSPORTA_PARA"; DEPENDE_DE = "DEPENDE_DE"
    origem = models.ForeignKey(Machine, on_delete=models.PROTECT, related_name="links_saida")
    destino = models.ForeignKey(Machine, on_delete=models.PROTECT, related_name="links_entrada")
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    front = models.ForeignKey("Front", null=True, on_delete=models.SET_NULL)
    valido_de = models.DateTimeField(); valido_ate = models.DateTimeField(null=True, blank=True)
    class Meta:
        constraints = [models.CheckConstraint(check=~models.Q(origem=models.F("destino")), name="link_sem_autoreferencia")]

def afetados_por(machine, em=None, max_hops=3):
    """BFS limitado, respeita validade temporal e organização."""
```
- **Testes necessários:** BFS respeita `max_hops`, ciclo não trava, vínculo expirado não conta, outra organização não aparece.
- **Critério de aceite:** testes verdes.
- **Evidência de conclusão:** testes.
- **Risco:** modelagem excessiva. Só os 3 tipos de relação.
- **Relação com a estratégia:** fundação do "motor de consequência".

#### S9-T2 · Cadastro e importação das relações
- **Objetivo:** alguém consegue montar o grafo sem SQL.
- **Contexto:** a relação mora em planejamento de frente/turno.
- **Problema atual:** sem entrada de dados.
- **Estado desejado:** tela "Frentes e equipes" (arrastar/associar) + importação CSV (`origem,destino,tipo,front,de,ate`).
- **Dependências · Pré-requisitos:** S9-T1 · nenhum.
- **Arquivos prováveis:** `src/app/frentes/page.tsx`, `management/commands/importar_links.py`.
- **Implementação esperada:** validação com relatório de linhas rejeitadas.
- **Testes necessários:** CSV inválido não persiste parcialmente (transação).
- **Critério de aceite:** E2E associar transbordo a colhedora.
- **Evidência de conclusão:** gravação.
- **Risco:** UX complexa. Primeira versão: formulário simples.
- **Relação com a estratégia:** permite o cenário da demo.

#### S9-T3 · Consequence Engine v0.1 (regras explícitas, sem número inventado)
- **Objetivo:** projetar impacto apenas do que dá para calcular.
- **Contexto:** o exemplo do Ultimato 2.4 mostra "25 a 40 minutos" e "João Silva (18) 99999-9999" como ilustração; **nada disso pode ser gerado sem dado**.
- **Problema atual:** inexistente.
- **Estado desejado:** `ConsequenceAssessment(event, afetados[], risco_parada ∈ {baixo, medio, alto, desconhecido}, horizonte_minutos|null, premissas[], faltantes[], confianca)`.
- **Dependências · Pré-requisitos:** S9-T1, S4-T2 · nenhum.
- **Arquivos prováveis:** `services/consequence.py`, `api/views_consequence.py`.
- **Implementação esperada:** regras versionadas:
```python
def avaliar(event) -> ConsequenceAssessment:
    afetados = afetados_por(event.machine)
    premissas, faltantes = [], []
    risco = "desconhecido"
    if event.severidade == "CRITICO" and event.tipo in {"TEMP_ALTA", "ANOMALIA_ML", "VIBRACAO_ALTA"}:
        risco = "alto" if event.evidence_quality == "boa" else "medio"      # evidência fraca reduz CONFIANÇA, não esconde
    horizonte = None
    tend = tendencia_linear(event.machine, "temperatura", janela_min=30)     # None se R^2 < R2_MIN ou poucos pontos
    limite = limite_critico(event.machine)
    if tend and tend.r2 >= R2_MIN and tend.inclinacao > 0:
        horizonte = (limite - tend.valor_atual) / tend.inclinacao            # extrapolação, rotulada "estimativa"
        premissas.append(f"extrapolação linear, R²={tend.r2:.2f}, janela 30 min")
    else:
        faltantes.append("tendência confiável para estimar tempo até o limite")
    for a in afetados:
        if a.tipo == "transbordo" and not a.capacidade_t:
            faltantes.append(f"capacidade do {a.codigo} para estimar espera")
    return ConsequenceAssessment(..., horizonte_minutos=horizonte, premissas=premissas, faltantes=faltantes)
```
`R2_MIN`, janela e regras documentados em `CONSEQUENCE_ENGINE.md`.
- **Testes necessários:** série sintética crescente produz horizonte coerente (conta feita à mão no teste); série ruidosa não produz horizonte; sem vínculos não inventa afetados; com `evidence_quality` suspeita risco cai um nível e a UI mostra "verificar sensor".
- **Critério de aceite:** nenhum teste gera número sem premissa listada.
- **Evidência de conclusão:** testes.
- **Risco:** extrapolação linear enganar. Rotular "estimativa" e usar só com R² mínimo.
- **Relação com a estratégia:** o diferencial mais forte do Ultimato, feito com honestidade.

#### S9-T4 · Política da organização e custo de parada (opcional, sem valor padrão)
- **Objetivo:** estimativa financeira só quando o cliente fornece a premissa.
- **Contexto:** o professor mandou não falar de finanças no pitch; no produto, custo por hora parada é premissa do cliente.
- **Problema atual:** números como R$ 5 a 15 mil/h estão em documentos sem fonte primária.
- **Estado desejado:** `OrganizationPolicy(custo_hora_parada|null, prazo_sugerido_por_severidade|null, ...)`; sem valor ⇒ a UI não mostra custo.
- **Dependências · Pré-requisitos:** S9-T3 · nenhum.
- **Arquivos prováveis:** `models.py`, `services/consequence.py`, tela de configurações.
- **Implementação esperada:** estimativa = `custo_hora × horizonte/60`, rotulada "estimativa com premissa do cliente".
- **Testes necessários:** sem política não há campo de custo na resposta.
- **Critério de aceite:** teste verde.
- **Evidência de conclusão:** teste.
- **Risco:** número virar manchete. Não usar no pitch (orientação do professor).
- **Relação com a estratégia:** honestidade comercial.

#### S9-T5 · Incidentes: agrupar sintomas correlacionados (sem diagnosticar)
- **Objetivo:** reduzir alertas repetidos e agrupar sintomas próximos.
- **Contexto:** Ultimato 2.5 item 5; só existe cooldown simples.
- **Problema atual:** vários eventos da mesma máquina/frente viram vários cartões.
- **Estado desejado:** `Incident(machine|front, eventos[], aberto_em, fechado_em, hipotese_causa|null, rotulo)`, agrupando por janela e máquina/vínculo; **hipótese é hipótese** (rótulo explícito), nunca diagnóstico confirmado.
- **Dependências · Pré-requisitos:** S9-T1 · nenhum.
- **Arquivos prováveis:** `services/incidents.py`, `models.py`.
- **Implementação esperada:** janela de 10 min configurável; cooldown já existente preservado.
- **Testes necessários:** 3 eventos em 8 min viram 1 incidente; evento a 40 min vira outro.
- **Critério de aceite:** teste verde.
- **Evidência de conclusão:** teste.
- **Risco:** falsa causalidade (correlação ≠ causa). Texto da UI: "sintomas simultâneos", não "causa".
- **Relação com a estratégia:** menos fadiga, mais contexto.

#### S9-T6 · UI de consequência e diagrama de impacto
- **Objetivo:** tornar visível a cadeia colhedora → transbordo → caminhão.
- **Contexto:** o exemplo do Ultimato é o alvo visual.
- **Problema atual:** sem tela.
- **Estado desejado:** no detalhe da decisão: "O que aconteceu · Quem é afetado · O que não sabemos (faltantes) · Ação recomendada"; diagrama simples (SVG) com nós coloridos pela severidade.
- **Dependências · Pré-requisitos:** S9-T3, S3-T5 · nenhum.
- **Arquivos prováveis:** `src/components/ConsequencePanel.tsx`, `ImpactDiagram.tsx`.
- **Implementação esperada:** "O que não sabemos" sempre visível (honestidade como feature).
- **Testes necessários:** E2E com e sem vínculos.
- **Critério de aceite:** gravação do cenário golden.
- **Evidência de conclusão:** vídeo.
- **Risco:** poluir a tela. Painel recolhível.
- **Relação com a estratégia:** "não é dashboard" em uma imagem.

#### S9-T7 · Contexto real para o LLM e teste golden
- **Objetivo:** o campo `operation_graph` de `agentic.py` deixa de ser "indisponível".
- **Contexto:** `agentic.py:37` e `:135`.
- **Problema atual:** prompt sem grafo.
- **Estado desejado:** `contexto.operation_graph` preenchido; validador (S5-T7) rejeita números que não estão em `{evidencias, premissas, limiares}`.
- **Dependências · Pré-requisitos:** S9-T3, S5-T7 · nenhum.
- **Arquivos prováveis:** `services/agentic.py`, `test_agentic.py`.
- **Implementação esperada:** golden: entrada fixa ⇒ saída validada (com LLM mockado) idêntica.
- **Testes necessários:** texto não menciona nome de pessoa/telefone se não houver `MaintenanceContact`.
- **Critério de aceite:** teste verde.
- **Evidência de conclusão:** teste.
- **Risco:** LLM citar responsável inexistente. Validador.
- **Relação com a estratégia:** fecha a camada C do desenho de IA.


---

### SEMANA 10 · OBSERVABILIDADE, CI/CD, BACKUP E CARGA

> **NOTA V4:** **P3** (cortável): S10-T7 (carga extra) e S10-T9. S10-T1 a T6 e T8 são necessárias ao piloto; S10-T8 inclui o pacote do gateway (`make gateway-up`).


**Camadas:** OBSERVABILITY · DEVOPS · SECURITY · TESTING

- **Objetivo estratégico:** responder com evidência "se falhar em produção, vocês sabem onde, quando e por quê, e conseguem voltar?". Transforma 292+ testes em garantia contínua.
- **Objetivo técnico:** CI que roda tudo (backend em SQLite e MySQL, front, contrato, firmware, segredos, migrations, status de docs); métricas Prometheus; logs JSON correlacionados por `device_id`/`message_id`; health em camadas; backup com restore **testado**; retenção e política de dados; teste de carga com números; deploy reprodutível e "pacote de gateway" para a demo.
- **Por que existe:** Ultimato 1.7 seção 8 e 11 (tabela de métricas), `CLAUDE.md` (observabilidade desde o dia 1, setup em < 10 min). Hoje: correlation ID e JSON logging existem; **sem CI, sem métricas, sem restore testado**.
- **Problemas que resolve:** regressões silenciosas; `DLQ` crescer sem ninguém ver; backlog offline invisível; `scripts/` com 6 variações de carga sem resultado; ausência de política de retenção.
- **Dependências recebidas:** todas as anteriores (transversal).
- **Entregáveis:** `.github/workflows/*`, `/metrics`, painel Grafana opcional, `docs/OBSERVABILIDADE.md`, `docs/DEPLOY.md`, `docs/BACKUP_RESTORE.md`, `docs/RETENCAO_DADOS.md`, `docs/RELATORIO_CARGA.md`.
- **Arquivos/módulos afetados:** `.github/workflows/`, `setup/settings.py`, `api_tcc/middleware.py`, `api_tcc/api/views_health.py`, `docker-compose.yml`, `scripts/*`, `Makefile`.
- **Arquitetura:** monólito modular mantido (sem microserviços). **Banco:** índices revisados. **Backend:** métricas e health. **Frontend:** nenhuma. **Hardware:** CI de firmware. **ML/IA:** métrica de versão/latência/falha do LLM e do IF. **Infra:** perfil `observability` no Compose. **Segurança:** gitleaks, `pip-audit`, `npm audit`. **Testes:** carga. **Docs:** quatro documentos.
- **Experimentos:** matar `worker` durante a carga e medir recuperação; restaurar backup em ambiente limpo e comparar contagens.
- **Critérios de aceitação:** CI verde em PR; restore reproduz contagens; relatório de carga com p50/p95/p99.
- **Métricas:** ver S10-T2 (lista); tempo de recuperação (RTO) e perda máxima (RPO) medidos.
- **Evidências esperadas:** URL do workflow verde, saída do restore, relatório de carga.
- **Riscos:** CI lento. Mitigação: matriz mínima, cache.
- **Decisões:** D-25 (Prometheus + Grafana opcional vs apenas logs), D-26 (provedor de deploy).
- **Perguntas abertas:** deploy público é prioridade? Resposta: **não antes de S2 e S10-T8**; o destino de sync na demo pode ser local.
- **Definition of Done da semana:** PR da `main` exige CI verde; restore testado e documentado.

#### S10-T1 · Pipeline de CI completo
- **Objetivo:** nada entra na `main` sem prova.
- **Contexto:** `CLAUDE.md`: PR obrigatório para `main`, Black + Flake8, ESLint + Prettier.
- **Problema atual:** ausência de CI.
- **Estado desejado:** jobs: `backend-sqlite`, `backend-mysql` (service MySQL 8), `lint-py`, `front` (lint, `tsc`, build), `contract-parity`, `firmware` (S8-T9), `security` (gitleaks, pip-audit, npm audit), `migrations-check`, `docs-status`, `e2e` (Compose + Playwright, noturno ou em PR com label).
- **Dependências · Pré-requisitos:** S0-T1 · nenhum.
- **Arquivos prováveis:** `.github/workflows/ci.yml`, `Makefile`, `requirements-dev.txt`.
- **Implementação esperada:**
```yaml
name: ci
on: { pull_request: { branches: [main] }, push: { branches: [main] } }
jobs:
  backend-mysql:
    runs-on: ubuntu-latest
    services:
      mysql: { image: "mysql:8.0", env: { MYSQL_DATABASE: fieldnode_db, MYSQL_USER: fn, MYSQL_PASSWORD: fn, MYSQL_ROOT_PASSWORD: root },
               ports: ["3306:3306"], options: >- --health-cmd="mysqladmin ping -h 127.0.0.1 -uroot -proot" --health-interval=10s --health-retries=10 }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: python manage.py makemigrations --check --dry-run
      - run: python manage.py test api_tcc simulators --parallel
        env: { USE_SQLITE: "False", DB_HOST: 127.0.0.1, DB_NAME: fieldnode_db, DB_USER: root, DB_PASSWORD: root, SECRET_KEY: ci, FIELDNODE_API_KEY: ci }
  docs-status:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: "! grep -R 'Status: ESQUELETO' docs/ || (echo 'doc em esqueleto'; exit 1)"
```
Pinar versões das actions por SHA quando possível.
- **Testes necessários:** abrir PR de teste que quebra de propósito cada job.
- **Critério de aceite:** `main` protegida exige os jobs.
- **Evidência de conclusão:** captura da proteção de branch + execução verde.
- **Risco:** teste de concorrência (SQLite "table is locked" é esperado em SQLite; em MySQL não deve ocorrer). Registrar as diferenças.
- **Relação com a estratégia:** disciplina de produto; mata o "292 testes" sem evidência.

#### S10-T2 · Métricas operacionais (`/metrics`)
- **Objetivo:** enxergar o sistema sem abrir o banco.
- **Contexto:** `docs/OBSERVABILIDADE.md` (esqueleto).
- **Problema atual:** só logs.
- **Estado desejado:** endpoint `/metrics` (restrito à rede interna ou token) com: `fieldnode_ingest_total{status}`, `fieldnode_ingest_latency_seconds`, `fieldnode_dlq_open`, `fieldnode_outbox_pending{device,class}`, `fieldnode_sync_delay_seconds{class}`, `fieldnode_events_created_total{tipo,severidade}`, `fieldnode_decisions_pending`, `fieldnode_llm_latency_seconds`, `fieldnode_llm_failures_total`, `fieldnode_model_version_info`, `fieldnode_worker_last_message_age_seconds`.
- **Dependências · Pré-requisitos:** S6-T6 · nenhum.
- **Arquivos prováveis:** `api_tcc/metrics.py`, `urls.py`, `docker-compose.yml` (perfil `observability` com Prometheus e Grafana).
- **Implementação esperada:** `prometheus_client` com registro multiprocess (gunicorn com 2 workers exige `PROMETHEUS_MULTIPROC_DIR`).
- **Testes necessários:** após 3 ingestões, contador sobe 3; `/metrics` sem credencial = 403.
- **Critério de aceite:** painel com as 8 métricas principais.
- **Evidência de conclusão:** captura do Grafana.
- **Risco:** cardinalidade alta por `device`. Limitar rótulos.
- **Relação com a estratégia:** tabela de métricas do Ultimato 1.7 (seção 11).

#### S10-T3 · Logs estruturados com identidade de mensagem
- **Objetivo:** seguir uma leitura de ponta a ponta.
- **Contexto:** `middleware.py` (correlation ID) e `test_json_logging.py` existem.
- **Problema atual:** `mqtt_listen.py` e o ingestor podem não compartilhar `message_id`/`device_id` nos logs.
- **Estado desejado:** todo log do caminho de ingestão contém `correlation_id`, `device_id`, `message_id`, `sequence`; filtro de segredos (S2-T4).
- **Dependências · Pré-requisitos:** S1-T5 · nenhum.
- **Arquivos prováveis:** `middleware.py`, `services/telemetria.py`, `mqtt_listen.py`, `settings.py`.
- **Implementação esperada:** `contextvars` populados no início do processamento da mensagem MQTT.
- **Testes necessários:** dois logs da mesma mensagem compartilham IDs; mensagens diferentes não.
- **Critério de aceite:** `jq 'select(.message_id=="...")'` reconstitui o caminho.
- **Evidência de conclusão:** amostra de log.
- **Risco:** dado pessoal em log. Revisão (nome de operador **não** entra).
- **Relação com a estratégia:** diagnosticar falha de campo.

#### S10-T4 · Health em camadas (live × ready) e heartbeat do worker
- **Objetivo:** health que sabe quando o sistema está "vivo mas cego".
- **Contexto:** `views_health.py` (47 linhas), `StatusMQTTView`.
- **Problema atual:** health pode dar OK com worker parado.
- **Estado desejado:** `/api/health/live` (processo), `/api/health/ready` (DB, broker, worker com heartbeat recente, modelo carregável, disco), resposta com estado por dependência.
- **Dependências · Pré-requisitos:** S10-T2 · nenhum.
- **Arquivos prováveis:** `views_health.py`, `mqtt_listen.py` (heartbeat em tabela/cache), `docker-compose.yml`.
- **Implementação esperada:** `ready` retorna 503 se heartbeat > 60 s com dispositivos ativos.
- **Testes necessários:** simular worker parado.
- **Critério de aceite:** 503 coerente.
- **Evidência de conclusão:** teste.
- **Risco:** falso positivo sem dispositivos. Condicionar a "dispositivos esperados".
- **Relação com a estratégia:** observabilidade honesta.

#### S10-T5 · Backup e restore **testado**
- **Objetivo:** voltar de um desastre com número medido.
- **Contexto:** nenhum backup definido.
- **Problema atual:** backup não restaurado é suposição.
- **Estado desejado:** `scripts/backup.sh` (`mysqldump --single-transaction`), retenção, criptografia do arquivo; `scripts/restore.sh`; teste que restaura em Compose limpo e compara contagens por tabela e hash de amostra.
- **Dependências · Pré-requisitos:** S10-T1 · nenhum.
- **Arquivos prováveis:** `scripts/{backup,restore}.sh`, `docs/BACKUP_RESTORE.md`.
- **Implementação esperada:** RPO/RTO **medidos** e documentados; backup nunca versionado (`.gitignore`).
- **Testes necessários:** restore em ambiente limpo.
- **Critério de aceite:** contagens idênticas.
- **Evidência de conclusão:** log do restore.
- **Risco:** backup com dado de cliente: criptografar.
- **Relação com a estratégia:** pergunta clássica de CTO.

#### S10-T6 · Retenção e política de dados
- **Objetivo:** saber por quanto tempo guarda o quê e como apaga.
- **Contexto:** Ultimato 1.7: "política de retenção, backup e recuperação"; dados de localização e operação são sensíveis para o cliente.
- **Problema atual:** retenção ilimitada por omissão.
- **Estado desejado:** `docs/RETENCAO_DADOS.md`: classes de dado (bruto, canônico, evento, decisão, auditoria, GPS), prazos configuráveis, comando `purgar_dados_antigos`, exportação e exclusão por organização.
- **Dependências · Pré-requisitos:** S2-T7 · nenhum.
- **Arquivos prováveis:** `management/commands/purgar_dados_antigos.py`, docs.
- **Implementação esperada:** purga em lotes; auditoria da própria purga; nunca apagar decisão com desfecho sem exportar.
- **Testes necessários:** purga respeita prazo e organização.
- **Critério de aceite:** teste verde.
- **Evidência de conclusão:** teste.
- **Risco:** violar contrato futuro com cliente. Prazos são hipótese até haver contrato.
- **Relação com a estratégia:** prontidão para piloto.

#### S10-T7 · Carga, índices e consolidação dos scripts
- **Objetivo:** saber onde quebra primeiro.
- **Contexto:** `scripts/{stress_test,teste_carga,teste_deduplicacao,teste_fluxo_completo,simular_mqtt,seed_data}.py` e `simulators/teste_resiliencia.py`; **cada um com propósito parcialmente sobreposto**.
- **Problema atual:** sem relatório de carga; índices não revisados.
- **Estado desejado:** um `scripts/load/` (k6 ou Locust) com perfis: 10, 50, 200 dispositivos × 0,5 msg/s; lote de 500; replay em massa de 6 h; leituras de dashboard simultâneas. Revisar índices: `(machine, event_time)`, `(device_id, message_id)` único, `(machine, status)` em `Event`/`Decision`.
- **Dependências · Pré-requisitos:** S10-T2 · nenhum.
- **Arquivos prováveis:** `scripts/load/*`, migrations de índice, `docs/RELATORIO_CARGA.md`.
- **Implementação esperada:** `EXPLAIN` das 5 queries mais usadas antes/depois; relatar p50/p95/p99, taxa de erro, ponto de saturação **observado**.
- **Testes necessários:** a própria execução, 3 repetições.
- **Critério de aceite:** relatório com números e gargalo identificado.
- **Evidência de conclusão:** relatório.
- **Risco:** testar em SQLite e extrapolar. Rodar em MySQL do Compose.
- **Relação com a estratégia:** "como escala?" com número.

#### S10-T8 · Deploy reprodutível e pacote de gateway
- **Objetivo:** subir em 10 minutos, local e (se decidido) na nuvem.
- **Contexto:** Compose já existe; falta checklist de produção.
- **Problema atual:** `docs/DEPLOY.md` é esqueleto.
- **Estado desejado:** `make gateway-up` (notebook: Compose + hotspot + broker + front + `preflight`), `make cloud-up` (settings de produção), checklist: `DEBUG=False`, `ALLOWED_HOSTS`, TLS via proxy, segredos, `SECURE_SSL=True` apenas atrás de proxy HTTPS real, CORS exato, `collectstatic`, migrations.
- **Dependências · Pré-requisitos:** S2, S10-T1, D-26 · nenhum.
- **Arquivos prováveis:** `Makefile`, `docs/DEPLOY.md`, `deploy/Caddyfile`, `scripts/preflight.sh`.
- **Implementação esperada:** `preflight.sh` verifica containers saudáveis, usuário de demo, broker aceitando credencial do dispositivo, front servindo, hora do notebook.
- **Testes necessários:** subida em máquina limpa cronometrada.
- **Critério de aceite:** < 10 minutos do clone ao dashboard.
- **Evidência de conclusão:** gravação.
- **Risco:** deploy público antes da segurança. Ordem: S2 → S10-T8.
- **Relação com a estratégia:** onboarding simples (`CLAUDE.md`).

#### S10-T9 · Alertas operacionais para a própria equipe
- **Objetivo:** ser avisado antes do usuário.
- **Contexto:** DLQ, worker e backlog hoje são silenciosos.
- **Problema atual:** falha percebida na banca.
- **Estado desejado:** regras Prometheus/Alertmanager (ou script simples) para: DLQ crescendo, worker sem heartbeat, backlog > limiar, LLM falhando > N%, disco > 85%; notificação por webhook/e-mail.
- **Dependências · Pré-requisitos:** S10-T2, S10-T4 · nenhum.
- **Arquivos prováveis:** `deploy/prometheus/alerts.yml`, script de fallback `scripts/watchdog.py`.
- **Implementação esperada:** `watchdog.py` independente do Prometheus para a demo.
- **Testes necessários:** derrubar worker e receber aviso.
- **Critério de aceite:** aviso em < 2 min.
- **Evidência de conclusão:** captura.
- **Risco:** ruído. Poucos alertas, todos acionáveis.
- **Relação com a estratégia:** operação como produto.

---

### SEMANA 11 · UNIVERSAL MACHINE MODEL REAL E DATA PASSPORT v0.1

> **NOTA V5:** S11-T3 (decodificador J1939) é **pré-requisito** de S18-T2 e S18-T7 e sobe de prioridade para os PGN do motor. S11-T4 e S11-T5 permanecem P3.


> **NOTA V4:** S11-T4 e S11-T5 passam a **P3** até existir segunda fonte real (S8-T12). S11-T3 usa os quadros reais gravados em S8-T12.


**Camadas:** ARCHITECTURE · IMPLEMENTATION · VALIDATION

- **Objetivo estratégico:** tornar "multi-marca" um mecanismo verificável: o resto do sistema não muda quando entra uma nova fonte, e cada valor carrega proveniência.
- **Objetivo técnico:** capability matrix por máquina; proveniência e unidade em todo valor canônico; decodificador J1939 público com vetores de teste; template de adaptador; formato "inspirado em API pública de OEM" **rotulado como tal**; conformidade de adaptadores; Data Passport (exportação portátil); API versionada.
- **Por que existe:** Ultimato 2.5 item 1, 2.6, 2.7, 2.8; v2 S9-T2. Verdade honesta: UMM **desloca** a complexidade para adaptadores; o ganho é contrato único e custo marginal baixo.
- **Problemas que resolve:** `FabricanteMapping` com dois fabricantes inventados; ausência de proveniência; parâmetro ausente preenchido por padrão; sem portabilidade.
- **Dependências recebidas:** S8-T7 (J1939 em bancada), S1 (contrato), S3 (UI de capacidades).
- **Entregáveis:** `Machine.capabilities()`, `services/j1939.py`, `adapters/`, fixtures de conformidade, `DataPassport`, `/api/v1/`.
- **Arquivos/módulos afetados:** `services/normalizacao.py`, `models.py` (`FabricanteMapping`, `CanonicalTelemetry`), novo `adapters/*`, `services/passport.py`, `api/views_passport.py`.
- **Arquitetura:** `Raw → (adaptador) → Canonical (valor, unidade, qualidade, origem, versão do mapeamento)`. **Banco:** campos de proveniência. **Backend:** adaptadores. **Frontend:** "o que esta máquina informa". **Hardware:** J1939 da S8. **ML/IA:** nenhuma. **Infra:** nenhuma. **Segurança:** export por organização, assinado. **Testes:** conformidade. **Docs:** `docs/UNIVERSAL_MACHINE_MODEL.md`.
- **Experimentos:** o mesmo parâmetro (`engine.coolant_temp`) vindo de (a) PGN decodificado, (b) payload de formato OEM-inspirado, (c) sensor DS18B20 externo; comparar valores, unidade e qualidade.
- **Critérios de aceitação:** 3 fontes convergem para o mesmo parâmetro canônico com unidades corretas; parâmetro sem mapeamento fica em `Raw` e aparece como `unsupported`.
- **Métricas:** parâmetros canônicos por fonte; % de leituras com proveniência completa.
- **Evidências esperadas:** testes de conformidade, captura da capability matrix.
- **Riscos:** parecer "integrado com Case/Deere". **Não está.** Frase permitida: *"fundação multi-marca com adaptadores: J1939 público em bancada e dois formatos de exemplo"*.
- **Decisões:** D-27 (rótulo dos formatos "inspirados"), D-28 (versionamento de mapeamentos).
- **Perguntas abertas:** qual OEM expõe API pública acessível ao grupo? Pesquisa de documentação pública é tarefa S11-T4; **não presumir**.
- **Definition of Done da semana:** teste de convergência verde; passaporte exportado e reimportado.

#### S11-T1 · Capability matrix por máquina
- **Objetivo:** dizer o que cada máquina informa **de fato**.
- **Contexto:** v2 previa `Machine.capabilities()`; ausente.
- **Problema atual:** UI assume que toda máquina tem temperatura, vibração e RPM.
- **Estado desejado:** `capabilities()` lista `canonical_parameter`, fonte, taxa média, última leitura, qualidade; UI mostra "não informado por esta máquina" em vez de zero.
- **Dependências · Pré-requisitos:** S8-T7 · nenhum.
- **Arquivos prováveis:** `models.py`, `services/normalizacao.py`, `src/components/CapabilityList.tsx`.
- **Implementação esperada:** agregação sobre `CanonicalTelemetry` dos últimos N dias.
- **Testes necessários:** máquina sem vibração não mostra "0".
- **Critério de aceite:** teste verde.
- **Evidência de conclusão:** captura.
- **Risco:** baixo.
- **Relação com a estratégia:** "nunca preencher parâmetro ausente com valor inventado" (Ultimato 2.5).

#### S11-T2 · Proveniência e unidade em todo valor canônico
- **Objetivo:** cada número carrega de onde veio e como.
- **Contexto:** `CanonicalTelemetry(canonical_parameter, value, unit, quality, mapping_version)`.
- **Problema atual:** falta distinguir medido, calculado, estimado e simulado.
- **Estado desejado:** `origem ∈ {medido, calculado, estimado, simulado}`, `fonte` (sensor, PGN, API), `unidade_original`, `fator_conversao`, `mapping_version`.
- **Dependências · Pré-requisitos:** S3-T1 · nenhum.
- **Arquivos prováveis:** `models.py`, migration, `normalizacao.py`, serializers.
- **Implementação esperada:** conversões em tabela declarativa e testada (°F→°C, psi→kPa, etc.).
- **Testes necessários:** tabela de conversão com valores conhecidos.
- **Critério de aceite:** nenhum valor canônico sem `origem`.
- **Evidência de conclusão:** teste.
- **Risco:** migração de dados antigos: `origem=simulado` por padrão.
- **Relação com a estratégia:** honestidade verificável.

#### S11-T3 · Decodificador J1939 (backend) com vetores de teste
- **Objetivo:** quadro CAN bruto → parâmetros canônicos, no servidor.
- **Contexto:** S8-T7 decodifica no firmware para bancada; o backend precisa aceitar quadros brutos de qualquer gateway.
- **Problema atual:** inexistente.
- **Estado desejado:** `services/j1939.py` puro, sem Django, com tabela de PGN/SPN versionada em JSON e **vetores de teste conferidos** contra fonte pública.
- **Dependências · Pré-requisitos:** S8-T7 · fonte pública verificada (registrar a fonte em `docs/UNIVERSAL_MACHINE_MODEL.md`).
- **Arquivos prováveis:** `services/j1939.py`, `adapters/j1939_pgn_table.json`, `tests/test_j1939.py`.
- **Implementação esperada:**
```python
def decode(can_id: int, data: bytes) -> list[Param]:
    pgn = pgn_from_id(can_id); spec = PGN_TABLE.get(pgn)
    if not spec: return [Param.unsupported(pgn)]           # fica em Raw, sem inventar
    out = []
    for spn in spec["spns"]:
        raw = extract_bits(data, spn["start"], spn["len"])
        if is_not_available(raw, spn["len"]):               # 0xFF.., 0xFE.. (erro) do padrão
            out.append(Param.ausente(spn["name"])); continue
        out.append(Param(spn["canonical"], raw * spn["resolution"] + spn["offset"], spn["unit"], origem="medido"))
    return out
```
- **Testes necessários:** vetores conferidos; valores "não disponível"/"erro" nunca viram número; PGN desconhecido não quebra.
- **Critério de aceite:** testes verdes.
- **Evidência de conclusão:** testes.
- **Risco:** tabela errada. **Revisar por outra pessoa** e marcar cada linha com a fonte.
- **Relação com a estratégia:** base real de interoperabilidade.

#### S11-T4 · SDK de adaptadores e formatos de exemplo
- **Objetivo:** adicionar fonte nova sem tocar no núcleo.
- **Contexto:** `FabricanteMapping` no banco; falta contrato de adaptador em código.
- **Problema atual:** cada novo formato exigiria alterar `normalizacao.py`.
- **Estado desejado:** `adapters/base.py` (`Adapter.parse(payload) -> list[Param]`, `Adapter.fingerprint()`), registro por `manufacturer`; **dois formatos de exemplo rotulados** "exemplo inspirado em formato público de OEM, não é a API do fabricante" (D-27). Pesquisar documentação pública de telemática (inclusive a norma de interoperabilidade de telemática de máquinas, ISO 15143-3/AEMP) e anotar o que é acessível **sem contrato**; adaptador AEMP fica `ARCHITECT_NOW`.
- **Dependências · Pré-requisitos:** S11-T2 · nenhum.
- **Arquivos prováveis:** `adapters/*`, `docs/UNIVERSAL_MACHINE_MODEL.md`.
- **Implementação esperada:** registro com `@register("manufacturer_id")`; toda saída passa por `validar_param` (faixa física de `sensor_limits`).
- **Testes necessários:** adaptador com campo desconhecido preserva em `Raw` e continua.
- **Critério de aceite:** novo adaptador de teste adicionado em < 50 linhas sem tocar no núcleo.
- **Evidência de conclusão:** teste de extensibilidade.
- **Risco:** prometer integração com OEM. Proibido.
- **Relação com a estratégia:** custo marginal baixo por marca (a parte verdadeira da tese).

#### S11-T5 · Conformidade entre fontes
- **Objetivo:** provar convergência.
- **Contexto:** Ultimato 2.5: "mesmo parâmetro de fontes diferentes".
- **Problema atual:** sem teste que cruze fontes.
- **Estado desejado:** teste que alimenta as 3 fontes com o mesmo valor físico e compara `CanonicalTelemetry`.
- **Dependências · Pré-requisitos:** S11-T3, S11-T4 · nenhum.
- **Arquivos prováveis:** `tests/test_umm_conformidade.py`.
- **Implementação esperada:** tolerância por parâmetro documentada.
- **Testes necessários:** o próprio.
- **Critério de aceite:** verde.
- **Evidência de conclusão:** saída.
- **Risco:** baixo.
- **Relação com a estratégia:** a evidência de "multi-marca real" no limite do que existe.

#### S11-T6 · Data Passport v0.1 (portabilidade)
- **Objetivo:** o cliente leva seus dados e o histórico de decisões.
- **Contexto:** dor documentada dos OEMs (portabilidade); no pitch, apenas como princípio.
- **Problema atual:** só relatórios PDF/CSV de leitura.
- **Estado desejado:** pacote ZIP por organização/máquina: `manifest.json` (versão do schema, hashes, intervalo, geração), `telemetry.csv|parquet`, `events.json`, `decisions.json` (com desfecho e evidência), `work_orders.json`, `provenance.json`; assinatura do manifesto; importação que reproduz contagens.
- **Dependências · Pré-requisitos:** S11-T2, S4-T3 · nenhum.
- **Arquivos prováveis:** `services/passport.py`, `api/views_passport.py`, `management/commands/exportar_passport.py`.
- **Implementação esperada:** exportação em streaming; sem segredos; respeita isolamento.
- **Testes necessários:** export → import em banco limpo → contagens e hashes iguais.
- **Critério de aceite:** round-trip verde.
- **Evidência de conclusão:** saída do teste.
- **Risco:** chamar de "moat". **Não é.** Estado: exportação sofisticada (seção 7).
- **Relação com a estratégia:** posiciona independência sem hype.

#### S11-T7 · API versionada e contrato público
- **Objetivo:** estabilidade para integradores.
- **Contexto:** hoje `/api/...` sem versão; rotas legadas duplicadas.
- **Problema atual:** mudança de campo quebra cliente.
- **Estado desejado:** `/api/v1/` com OpenAPI gerado, política de depreciação (cabeçalho `Deprecation`/`Sunset`), tokens por organização com escopos.
- **Dependências · Pré-requisitos:** S2-T6 · nenhum.
- **Arquivos prováveis:** `api_tcc/urls.py`, `setup/urls.py`, `docs/API.md`.
- **Implementação esperada:** `/api/` continua como alias por 1 ciclo.
- **Testes necessários:** contrato (schemathesis ou testes de schema) contra OpenAPI.
- **Critério de aceite:** OpenAPI publicado e testado.
- **Evidência de conclusão:** teste.
- **Risco:** escopo. Só endpoints já usados pelo front e pelo gateway.
- **Relação com a estratégia:** maturidade de produto.

---

### SEMANA 12 · VALIDAÇÃO DE CAMPO, VALIDAÇÃO COMERCIAL, DEMO E NARRATIVA

> **NOTA V5:** Entrevistas passam a incluir **perguntas de laudo e de custo de recomendação errada** (S12-T12, 20.2). A **meta de precisão** é fechada com o analista (D-54). Pitch continua **sem finanças** (S12-T7).


> **NOTA V4:** A S12 ganha **T11** (acesso a máquina e piloto) e **T12** (8 a 10 entrevistas, perguntas de mecânico); ambas **começam na semana 1** e rodam em paralelo. S12-T3 usa HTTPS local (S13-T12) e o QR aponta para o gateway.


**Camadas:** VALIDATION · BUSINESS VALIDATION · DOCUMENTATION

- **Objetivo estratégico:** tudo o que foi construído se torna **defensável**: demonstração ensaiada, 5 a 6 conversas reais por papel, claims verificados, README e pitch alinhados com o que existe.
- **Objetivo técnico:** README novo com GIF, demo com notebook como gateway e hotspot, roteiro e fallback, entrevistas estruturadas, relatório honesto, documento de pressure test, checklist de congelamento.
- **Por que existe:** Ultimato 1.1 (roteiro de demo, furos), pitch (professor: sem finanças, persona, abertura com porcentagem), Leviatã fases 20 a 22 e 25.
- **Problemas que resolve:** QR para cloud contradiz "puxar a internet"; slide com "0% perda" antes de medir; números sem fonte; ausência de validação comercial estruturada; concorrência de grupo com ideia semelhante.
- **Dependências recebidas:** S3, S4, S6, S8 (mínimo); S9 e S11 enriquecem.
- **Entregáveis:** `README.md`, `docs/ROTEIRO_DEMO_BANCA.md`, `docs/INVESTOR_CTO_PRESSURE_TEST.md`, `docs/ROTEIRO_VALIDACAO_COMERCIAL.md`, `docs/RESULTADOS_VALIDACAO_COMERCIAL.md`, `docs/PITCH_FATOS.md`, vídeo de demo, checklist de congelamento.
- **Arquivos/módulos afetados:** `README.md`, `docs/*`, `scripts/preflight.sh`, `docs/evidence/*`.
- **Arquitetura:** nenhuma nova. **Banco:** seed de demo com selo. **Backend:** nada. **Frontend:** modo apresentação opcional (sem mock). **Hardware:** kit de demo fechado. **ML/IA:** relatório S5 citado. **Infra:** `make gateway-up`. **Segurança:** registro desabilitado em demo. **Testes:** 3 ensaios. **Docs:** núcleo.
- **Experimentos:** ensaio com plateia que não conhece o projeto (alguém de fora faz as perguntas do pressure test).
- **Critérios de aceitação:** 3 ensaios seguidos; cada afirmação do pitch mapeada a evidência em `PITCH_FATOS.md`.
- **Métricas:** duração do roteiro; nº de interrupções; nº de perguntas do pressure test respondidas sem consultar anotação.
- **Evidências esperadas:** vídeos, relatório de entrevistas, matriz de fatos.
- **Riscos:** resultado comercial fraco (tratar como informação); falha de hardware ao vivo (vídeo de fallback).
- **Decisões:** D-14 (política de números), D-29 (demo ao vivo vs vídeo; decisão atual do grupo: vídeo narrado no palco e demonstração real na feira).
- **Perguntas abertas:** (resolvidas por entrevista) a dor dominante é multimarca, confiabilidade de alerta, OS manual ou conectividade?
- **Definition of Done da semana:** seção 25 deste documento preenchida com as evidências reais.

#### S12-T1 · README novo (vitrine honesta)
- **Objetivo:** primeira impressão que mostra o diferencial, não "dashboard + IA".
- **Contexto:** README atual descreve Docker/rotas/endpoints; não cita Trust Score, Decision Memory, Data Mule nem tem GIF.
- **Problema atual:** vende o que não é o diferencial.
- **Estado desejado:** estrutura: tagline + problema/solução (3 linhas) · GIF do fluxo central (S3-T11) · **o que é real × o que é simulado × o que é roadmap** (tabela copiada de `CLAIMS_VS_CODE.md`) · arquitetura (Mermaid) · os 3 pilares com link para evidência · quickstart (`make gateway-up`) · métricas medidas (S6, S5) · segurança · roadmap com checkboxes · equipe e contribuição · licença.
- **Dependências · Pré-requisitos:** S0-T3, S3-T11, S5-T2, S6-T5 · nenhum.
- **Arquivos prováveis:** `README.md`, `docs/img/*.gif`.
- **Implementação esperada:** nenhuma afirmação fora da matriz; badges de CI reais (não decorativos).
- **Testes necessários:** `markdownlint`; links válidos (`lychee`).
- **Critério de aceite:** revisão cruzada: cada frase tem evidência.
- **Evidência de conclusão:** PR.
- **Risco:** README bonito mentindo. Regra: se não está na matriz, não entra.
- **Relação com a estratégia:** vitrine para banca, GitHub e recrutador.

#### S12-T2 · Documentos finais da defesa
- **Objetivo:** fechar os documentos esqueleto da S0-T4.
- **Contexto:** `ROTEIRO_DEMO_BANCA`, `INVESTOR_CTO_PRESSURE_TEST`, `PITCH_FATOS`.
- **Problema atual:** esqueletos.
- **Estado desejado:** todos preenchidos, sem `Status: ESQUELETO` (CI falha se sobrar).
- **Dependências · Pré-requisitos:** S12-T3 a T9 · nenhum.
- **Arquivos prováveis:** `docs/*`.
- **Implementação esperada:** `PITCH_FATOS.md`: tabela `frase do pitch → evidência → arquivo/vídeo → número medido → data`.
- **Testes necessários:** CI de status de docs.
- **Critério de aceite:** CI verde.
- **Evidência de conclusão:** CI.
- **Risco:** baixo.
- **Relação com a estratégia:** defesa sob questionamento adversarial.

#### S12-T3 · Arquitetura e roteiro da demo (notebook é o gateway)
- **Objetivo:** demonstração que **prova** offline em vez de contradizê-lo.
- **Contexto:** o QR para deploy em nuvem some a prova quando se corta a internet do notebook (Ultimato 1.1).
- **Problema atual:** roteiro ainda aponta QR para deploy externo.
- **Estado desejado:** notebook = gateway: Compose + hotspot + broker + front; plateia conecta no hotspot e abre `https://fieldnode.local` (HTTPS local, S13-T12) (QR aponta para isso); **cortar o uplink do notebook não afeta a plateia**; cloud é o destino de sincronização na religação (ou o próprio notebook, se não houver nuvem); `scripts/preflight.sh` antes de entrar; vídeo de fallback; DEMO_MODE ligado.
- **Dependências · Pré-requisitos:** S8-T6, S10-T8 · hotspot testado.
- **Arquivos prováveis:** `docs/ROTEIRO_DEMO_BANCA.md`, `scripts/preflight.sh`.
- **Implementação esperada:** linha do tempo de 5 a 7 minutos: (0:00) problema em uma frase; (0:30) sensor real publicando; (1:30) cortar uplink; (2:00) alerta local sem internet; (3:00) decisão na fila com confiança e prioridade; (3:45) aprovar e gerar OS; (4:30) religar e mostrar backlog zerando com os **números medidos** de S6-T5; (5:30) o que **não** fazemos ainda (Data Mule físico, J1939 em máquina real).
- **Testes necessários:** 3 ensaios cronometrados com pessoa de fora operando o celular.
- **Critério de aceite:** 3 execuções seguidas sem intervenção fora do roteiro.
- **Evidência de conclusão:** vídeo da 3ª.
- **Risco:** Wi-Fi da sala interferir. Canal fixo e hotspot dedicado; plano B: vídeo.
- **Relação com a estratégia:** "isqueiro no sensor: não" (Ultimato 1.1): método seguro.

#### S12-T4 · Roteiro de validação comercial por papel
- **Objetivo:** instrumento que não induz resposta.
- **Contexto:** Leviatã fase 22; Ultimato 1.7: validar a dor da frota multimarca e da conectividade antes de assumir.
- **Problema atual:** ausência de roteiro e amostra.
- **Estado desejado:** 5 perfis: gestor de frota, responsável de manutenção, supervisor de frente, operador, analista de TI/dados da usina. Perguntas abertas: "qual decisão você toma hoje com dado atrasado?", "qual alerta mais incomoda?", "quanto tempo se perde quando uma máquina para?", "quem manda o mecânico até a máquina e como?", "quais sistemas usam e exportam dados?", "quais marcas há na frota?", "o que justificaria testar algo novo?". **Nunca**: "você usaria o FieldNode?".
- **Dependências · Pré-requisitos:** nenhuma · contatos (o grupo já tem acesso a pessoas da região de Araçatuba e a professor com experiência em Solinftec).
- **Arquivos prováveis:** `docs/ROTEIRO_VALIDACAO_COMERCIAL.md`.
- **Implementação esperada:** consentimento, anonimização, registro de data, papel, empresa (se autorizado).
- **Testes necessários:** ensaio do roteiro entre integrantes; cortar perguntas indutivas.
- **Critério de aceite:** revisão cruzada.
- **Evidência de conclusão:** documento.
- **Risco:** só falar com amigos. Registrar o viés de seleção.
- **Relação com a estratégia:** validação comercial real (não suposta).

#### S12-T5 · Executar 5 a 6 conversas e relatar com honestidade
- **Objetivo:** evidência, não confirmação de viés.
- **Contexto:** a amostra de 3 foi considerada fraca demais no v2.
- **Problema atual:** nenhuma conversa documentada no repositório.
- **Estado desejado:** 5 a 6 entrevistas cobrindo pelo menos 3 dos 5 papéis; para cada: dor confirmada? sinal de disposição de testar/pagar? objeção principal? comparação espontânea com concorrente? qual dor forte (multimarca, confiabilidade do alerta, OS manual, conectividade)?
- **Dependências · Pré-requisitos:** S12-T4 · agenda de terceiros (**fora do controle técnico**: começar cedo, em paralelo desde a S3).
- **Arquivos prováveis:** `docs/RESULTADOS_VALIDACAO_COMERCIAL.md`.
- **Implementação esperada:** tabela + citações curtas autorizadas + classificação confirmado/hipótese.
- **Testes necessários:** nenhum.
- **Critério de aceite:** 5 a 6 conversas registradas; relatório inclui o que **não** confirmou.
- **Evidência de conclusão:** documento.
- **Risco:** sinal fraco. É dado; ajusta a prioridade (S12-T6).
- **Relação com a estratégia:** única forma de transformar hipótese em fato.

#### S12-T6 · Regra de rebalanceamento pós-entrevistas
- **Objetivo:** decidir o próximo ciclo com base em evidência, não em preferência.
- **Contexto:** seção 23 (questões em aberto).
- **Problema atual:** risco de ignorar resultado desfavorável.
- **Estado desejado:** tabela "se a dor dominante for X, então prioridade Y".

| Dor dominante nas entrevistas | O que sobe | O que desce |
|---|---|---|
| Ordem de serviço manual / digitação | S4 (OS, exportação, integração com sistema da usina) | S7, S11 |
| Frota mista sem visão única | S11 (UMM real, adaptadores), S3 | S9 |
| Falso alarme / fadiga de alerta | S3-T3, S4-T6, S5, S9-T5 | S7 |
| Zona sem sinal | S6, S7, S8 | S11 |
| Nenhuma dor clara | Revisar tese; foco em um caso de uso estreito antes de construir mais | tudo que é novo |

- **Dependências · Pré-requisitos:** S12-T5 · nenhum.
- **Arquivos prováveis:** `docs/PROXIMO_CICLO.md`.
- **Implementação esperada:** decisão registrada em D-30.
- **Testes necessários:** nenhum.
- **Critério de aceite:** documento commitado.
- **Evidência de conclusão:** commit.
- **Risco:** nenhum técnico.
- **Relação com a estratégia:** disciplina do Leviatã: "estratégia mais fácil de defender, não mais impressionante".

#### S12-T7 · Política de números e alinhamento do pitch
- **Objetivo:** nenhum número sem fonte no palco.
- **Contexto:** outra IA sugeriu tirar disclaimers e usar "30–40% (ANATEL 2023)", "R$ 5–15 mil/h (Embrapa 2022)", "40% da frota com mais de 15 anos (ANFAVEA 2023)", "acurácia 73–85%". **Esses números vêm da pesquisa do grupo e não foram verificados em fonte primária.** O professor proibiu falar de finanças.
- **Problema atual:** risco de ser desmontado por pergunta simples ("qual a fonte?").
- **Estado desejado:** D-14: (1) verificar cada número na fonte primária; se não achar, **não usar como fato**; (2) abertura com **porcentagem verificável** ou com dado do próprio sistema (ex.: resultado medido de S6); (3) storytelling com persona **declarada como ilustrativa**; (4) acurácia só do relatório S5, com a frase "em cenários sintéticos"; (5) sem custo, preço ou ROI.
- **Dependências · Pré-requisitos:** S5-T2, S6-T5, S12-T1 · nenhum.
- **Arquivos prováveis:** `docs/PITCH_FATOS.md`.
- **Implementação esperada:** para cada número: `valor · fonte primária (URL/documento) · data de acesso · se não verificado: NÃO USAR`.
- **Testes necessários:** revisão por quem não escreveu o pitch.
- **Critério de aceite:** zero número sem linha na tabela.
- **Evidência de conclusão:** tabela.
- **Risco:** perder impacto emocional. Compensa com cena real e prova mostrada.
- **Relação com a estratégia:** a honestidade **é** o diferencial contra o grupo concorrente.

#### S12-T8 · Pressure test (CTO/investidor/professor)
- **Objetivo:** respostas curtas, honestas e ensaiadas.
- **Contexto:** seção 22 deste documento.
- **Problema atual:** respostas não ensaiadas.
- **Estado desejado:** `docs/INVESTOR_CTO_PRESSURE_TEST.md` com as 15 perguntas da seção 22 + as do professor ("onde está o modelo treinado?", "e se o sensor estiver errado?", "por que não a solução do OEM?").
- **Dependências · Pré-requisitos:** tudo · nenhum.
- **Arquivos prováveis:** `docs/INVESTOR_CTO_PRESSURE_TEST.md`.
- **Implementação esperada:** cada resposta cita o arquivo/número que a sustenta.
- **Testes necessários:** simulação de perguntas com alguém de fora.
- **Critério de aceite:** cada integrante responde 5 perguntas sem consultar.
- **Evidência de conclusão:** gravação do ensaio.
- **Risco:** decorar sem entender. Rodízio de quem responde.
- **Relação com a estratégia:** transforma risco em vantagem.

#### S12-T9 · Validação de campo escalonada (critérios de entrada e saída)
- **Objetivo:** nunca pular degrau da sequência de validação.
- **Contexto:** Leviatã fase 19; `docs/` ainda não define.
- **Problema atual:** risco de prometer piloto.
- **Estado desejado:** 5 degraus com critério objetivo de saída (seção 19); piloto real = **hipótese**.
- **Dependências · Pré-requisitos:** S8, S12-T5 · nenhum.
- **Arquivos prováveis:** `docs/VALIDACAO_DE_CAMPO.md`.
- **Implementação esperada:** tabela degrau → como validar → métrica → estado atual.
- **Testes necessários:** nenhum.
- **Critério de aceite:** estado atual honesto (`log local ✔`, `bancada ✔ (se S8 fechada)`, `simulação de campo parcial`, `hardware em máquina real ✘`, `piloto ✘`).
- **Evidência de conclusão:** documento.
- **Risco:** nenhum.
- **Relação com a estratégia:** defesa contra "já foi testado em campo?".

#### S12-T10 · Congelamento, release e plano de contingência
- **Objetivo:** não quebrar nada na véspera.
- **Contexto:** `CLAUDE.md` (resumo de sessão, deploy).
- **Problema atual:** sem ritual de congelamento.
- **Estado desejado:** code freeze 72 h antes (só `fix:` com PR); tag `v1.0.0-banca`; backup do banco de demo; imagem Docker salva localmente; vídeo de fallback; segunda máquina com tudo pré-carregado; checklist físico (cabos, fontes, extensão, hotspot, adaptadores) e **plano de falha** por componente (hardware, rede, Docker, projetor).
- **Dependências · Pré-requisitos:** S12-T3 · nenhum.
- **Arquivos prováveis:** `docs/CHECKLIST_FINAL.md`, `scripts/preflight.sh`.
- **Implementação esperada:** `docker save` das imagens; `make demo-reset` recria o estado de demo.
- **Testes necessários:** ensaio de falha: derrubar cada componente e executar o plano.
- **Critério de aceite:** recuperação em < 2 min por componente no ensaio.
- **Evidência de conclusão:** vídeo/ata.
- **Risco:** mudar algo no último dia. Congelamento.
- **Relação com a estratégia:** disciplina de produto.



#### S12-T11 · Acesso a máquina real e carta de intenção de piloto (começa na semana 1)
- **Objetivo:** transformar "piloto" de hipótese em compromisso por escrito, ou descobrir cedo que não vai existir.
- **Contexto:** avaliação externa: "pronto para vender" só existe depois de um piloto real; software não resolve isso, **conversa** resolve.
- **Problema atual:** o piloto aparece só no fim do roadmap, marcado como não feito.
- **Estado desejado:** lista de 5 a 10 contatos (usina, oficina, professor com experiência em Solinftec, concessionária, cooperativa), pedido formal e curto, **carta de intenção** assinada por pelo menos um parceiro **ou** registro honesto de que não houve; plano de piloto de 2 semanas com métricas de sucesso e termos de segurança.
- **Dependências · Pré-requisitos:** nenhuma · material de uma página (problema, o que será instalado, o que **não** será tocado: sem escrita no barramento, sem alterar a máquina).
- **Arquivos prováveis:** `docs/PILOTO.md`, `docs/CARTA_DE_INTENCAO_MODELO.md`.
- **Implementação esperada:** plano com: máquina, local, duração, dados coletados, quem aprova instalação, como remover, métricas (tempo até reconhecer alerta, falso alarme, % de OS abertas, disponibilidade do enlace), critério de interrupção imediata.
- **Testes necessários:** revisão por professor/mentor antes de enviar.
- **Critério de aceite:** pelo menos 5 pedidos enviados na semana 1 a 2 e status de cada um registrado.
- **Evidência de conclusão:** `PILOTO.md` com tabela de contatos e respostas.
- **Risco:** zero resposta. É informação: o resultado vira pauta de `PROXIMO_CICLO.md`.
- **Relação com a estratégia:** única forma de sair do "bancada" para "máquina real".

#### S12-T12 · Amostra de entrevistas ampliada (8 a 10) e perguntas de prescrição
- **Objetivo:** amostra mínima menos frágil e conteúdo para os playbooks.
- **Contexto:** 5 a 6 conversas dão direção, não prova de mercado.
- **Problema atual:** roteiro focado em dor comercial; sem perguntas sobre o que o mecânico **faz**.
- **Estado desejado:** 8 a 10 conversas; bloco extra para mecânicos: "o que você verifica primeiro quando a temperatura sobe?", "quais peças mais falham?", "qual checklist usa?", "quanto tempo leva?", "como registra a OS hoje?" Respostas alimentam S16-T1 e S16-T10.
- **Dependências · Pré-requisitos:** S12-T4 · contatos.
- **Arquivos prováveis:** `docs/ROTEIRO_VALIDACAO_COMERCIAL.md`, `docs/RESULTADOS_VALIDACAO_COMERCIAL.md`, `playbooks/rascunhos/*`.
- **Implementação esperada:** gravação com consentimento, transcrição resumida, anonimização; cada resposta técnica vira **rascunho de playbook** marcado `fonte: entrevista X`.
- **Testes necessários:** nenhum.
- **Critério de aceite:** ≥ 8 conversas, ≥ 3 com perfil de manutenção, ≥ 2 com operador.
- **Evidência de conclusão:** relatório + pasta de rascunhos.
- **Risco:** só pessoas próximas. Registrar viés.
- **Relação com a estratégia:** playbook de verdade nasce de quem faz o serviço.


---

### SEMANA 13 · GATEWAY-NÚCLEO E REPLICAÇÃO (OFFLINE COMPLETO)

**Camadas:** ARCHITECTURE · IMPLEMENTATION · VALIDATION · SECURITY · TESTING
**Pilares:** P3 OFFLINE-100 (principal), P1 PRESCRIÇÃO-100, P2 IA-100

- **Objetivo estratégico:** o FieldNode **continua sendo FieldNode sem internet**: ver, avaliar, detectar, decidir, aprovar, abrir OS, executar, registrar e reavaliar, tudo no campo. A nuvem deixa de ser requisito e vira réplica.
- **Objetivo técnico:** perfil `edge` do Compose com a pilha completa e banco persistente; login e permissões offline; PWA offline-first via hotspot; `DomainChange` com relógio lógico híbrido (HLC) e IDs determinísticos; replicação bidirecional gateway ↔ nuvem; regras de autoridade e resolução de conflito; inferência de ML local com degradação controlada; teste de **apagão total**; gateway móvel; relógio e backup locais.
- **Por que existe:** a avaliação externa foi direta: a V3 deixava Trust, Event e Decision "na sede/nuvem", o que é o "sincroniza depois" que a Paola não quer. O diferencial é a **decisão nascer offline**.
- **Problemas que resolve:** decisão só depois da volta da internet; login dependente da nuvem; PWA sem dados locais; risco de decisão duplicada na replicação; modelo de ML ausente no campo.
- **Dependências recebidas:** S1 (contrato, tempo, ACK), S2 (credencial, isolamento, auditoria), S3 (front), S4 (Decision/OS), S6 (protocolo).
- **Entregáveis:** `docker-compose.edge.yml`, `NODE_ROLE`, `DomainChange`, `Proposal`, `ReplicationPeer`, comandos `replicate`, `edge-up`, `edge-backup`, `docs/GATEWAY_NUCLEO.md`, `docs/REPLICACAO.md`, vídeo do apagão total.
- **Arquivos/módulos afetados:** `docker-compose.yml` (perfil `edge`), `setup/settings.py`, `api_tcc/models.py`, `api_tcc/services/replication.py`, `api_tcc/services/hlc.py`, `api_tcc/services/model_sync.py`, `api_tcc/api/views_replication.py`, `frontend-next/public/sw.js`, `frontend-next/src/lib/offline/*`.
- **Arquitetura:** mesmo código, dois papéis (`NODE_ROLE=edge|cloud`). **Banco:** `DomainChange`, `Proposal`, `ReplicationPeer`, `ConflictLog`, `Event.id`/`Decision.id` determinísticos. **Backend:** replicação e autoridade. **Frontend:** PWA offline com fila de ações idempotentes. **Hardware:** mini-PC/Raspberry com SSD e RTC. **ML/IA:** distribuição de modelos assinados. **Infra:** perfil `edge`, hotspot, systemd. **Segurança:** usuários replicados com hash, tokens locais, assinatura de modelo. **Testes:** apagão total, reboot, conflito. **Docs:** dois documentos.
- **Experimentos:** (a) desligar a WAN e rodar o fluxo de 8 passos; (b) reiniciar o gateway no meio de uma aprovação; (c) criar decisões nos dois lados durante a desconexão e reconciliar; (d) 10 mil `DomainChange` acumulados e replicados.
- **Critérios de aceitação:** fluxo completo sem internet; após reboot, estado intacto; reconciliação sem duplicata nem perda; autoridade respeitada.
- **Métricas:** tempo de boot do gateway até "pronto"; latência de replicação por 1 mil mudanças; conflitos por 10 mil mudanças (meta 0 em operação normal); decisões duplicadas (meta 0).
- **Evidências esperadas:** vídeo contínuo do apagão total; `ConflictLog` vazio ou explicado; relatório de replicação.
- **Riscos:** complexidade de replicação (mitigação: escopo **apenas** domínio, não telemetria; telemetria segue o protocolo de S6); cartão SD corrompendo (mitigação: SSD, WAL, backup S13-T11).
- **Decisões:** D-32 (HLC só para domínio, telemetria segue append-only), D-33 (autoridade: nasceu no gateway, pertence ao gateway), D-34 (hardware do gateway: mini-PC vs Raspberry).
- **Perguntas abertas:** vários gateways editando a mesma OS? Resposta: regra de autoridade por `origin_node` + `Proposal`; edição concorrente na mesma entidade fica registrada em `ConflictLog`.
- **Definition of Done da fatia:** S13-T8 aprovado em 3 execuções seguidas e documentado.

#### S13-T1 · Perfil `edge` do Compose: a pilha inteira no gateway
- **Objetivo:** subir tudo com um comando, sem internet, e voltar sozinho após queda de energia.
- **Contexto:** `docker-compose.yml` já tem `db`, `web`, `worker`, `mosquitto` e healthchecks; o front é Next.js.
- **Problema atual:** o compose assume nuvem e notebook de desenvolvimento.
- **Estado desejado:** `docker compose --profile edge up -d` inicia: Mosquitto (ACL), MySQL com volume persistente, `web` (gunicorn), `worker` (mqtt_listen), `ml-runner` (inferência local), front standalone, `hotspot` (script de host); `restart: unless-stopped`; unidade `systemd` que sobe o compose no boot; `NODE_ROLE=edge`, `NODE_ID`.
- **Dependências · Pré-requisitos:** S2-T1, S10-T8 (parcial) · mini-PC ou Raspberry com SSD, Docker.
- **Arquivos prováveis:** `docker-compose.edge.yml`, `deploy/edge/fieldnode-edge.service`, `deploy/edge/hotspot.sh`, `setup/settings.py`.
- **Implementação esperada:**
```yaml
# docker-compose.edge.yml (sobrepõe o base com: docker compose -f docker-compose.yml -f docker-compose.edge.yml up -d)
services:
  web:     { restart: unless-stopped, environment: { NODE_ROLE: edge, NODE_ID: "${NODE_ID}", OFFLINE_AUTH: "true" } }
  worker:  { restart: unless-stopped, environment: { NODE_ROLE: edge } }
  db:      { restart: unless-stopped, volumes: ["/srv/fieldnode/mysql:/var/lib/mysql"], command: ["--innodb-flush-log-at-trx-commit=1", "--sync-binlog=1"] }
  ml-runner: { build: ./ml, restart: unless-stopped, volumes: ["/srv/fieldnode/models:/models:ro"] }
```
```ini
# deploy/edge/fieldnode-edge.service
[Unit] Description=FieldNode Edge; After=docker.service; Requires=docker.service
[Service] WorkingDirectory=/opt/fieldnode; ExecStart=/usr/bin/docker compose -f docker-compose.yml -f docker-compose.edge.yml up; ExecStop=/usr/bin/docker compose down; Restart=always
[Install] WantedBy=multi-user.target
```
Hotspot: `nmcli device wifi hotspot ifname wlan0 ssid FieldNode-<NODE_ID> password <...>` (ou `hostapd`). Escolher **banco**: manter MySQL (paridade com a nuvem). `innodb_flush_log_at_trx_commit=1` para durabilidade após queda de energia.
- **Testes necessários:** puxar a tomada 20 vezes em momentos aleatórios; ao religar, `/api/health/ready` verde e dados íntegros; sem internet o boot completa.
- **Critério de aceite:** 20/20 recuperações; tempo de boot até "pronto" medido e registrado.
- **Evidência de conclusão:** log de 20 ciclos.
- **Risco:** MySQL em Raspberry com pouca RAM. Medir uso; ajustar `innodb_buffer_pool_size`; D-34 decide hardware.
- **Relação com a estratégia:** o gateway deixa de ser "retransmissor".

#### S13-T2 · Autenticação e permissões offline
- **Objetivo:** o operador faz login e age **sem internet**.
- **Contexto:** hoje token DRF com TTL de 24 h e usuários na nuvem.
- **Problema atual:** login depende do servidor central.
- **Estado desejado:** usuários, `Membership` e papéis **replicados** (hash de senha, nunca senha); login local; token validado localmente com relógio do gateway; revogação/expiração aplicadas ao replicar; auditoria local.
- **Dependências · Pré-requisitos:** S2-T5, S13-T5 · nenhum.
- **Arquivos prováveis:** `api_tcc/authentication.py`, `api_tcc/services/replication.py`, `api_tcc/models.py`.
- **Implementação esperada:** usuário criado na nuvem aparece no gateway no próximo sync; **usuário criado só no gateway** (modo emergência) fica `pendente_confirmacao` até a central aceitar; lockout local (S2-T2) continua valendo; `OFFLINE_AUTH=true` mantém TTL por relógio local e registra `time_source`.
- **Testes necessários:** login com WAN cortada; usuário revogado na nuvem perde acesso após replicar; usuário de outra organização não loga no gateway errado.
- **Critério de aceite:** testes verdes e gravação.
- **Evidência de conclusão:** vídeo de login sem internet.
- **Risco:** hash replicado é dado sensível. Canal autenticado e cifrado; nunca em log.
- **Relação com a estratégia:** sem login offline, o "offline" é só leitura.

#### S13-T3 · PWA offline-first do operador (dados, ações e mapa)
- **Objetivo:** o celular do supervisor, conectado ao hotspot, usa o app inteiro e **não perde ação** se o gateway cair por instantes.
- **Contexto:** `sw.js` cacheia telemetria; falta app shell, dados de leitura, mapa e fila de **ações** do usuário.
- **Problema atual:** sem mapa offline; ações (aprovar, rejeitar) perdem-se se a requisição falhar.
- **Estado desejado:** app shell e rotas em cache; dados recentes em IndexedDB; **tiles do mapa** da área pré-carregados; fila de ações com `Idempotency-Key`; reaplicação automática ao reconectar ao gateway; indicador "dados de X min atrás".
- **Dependências · Pré-requisitos:** S1-T4, S3-T1, S2-T5, **S13-T12 (HTTPS local: Service Worker e Web Bluetooth só funcionam em contexto seguro)** · nenhum.
- **Arquivos prováveis:** `frontend-next/public/sw.js`, `frontend-next/src/lib/offline/{db.ts,actions.ts,tiles.ts}`, `MapClient.tsx`, `manifest.json`.
- **Implementação esperada:**
```ts
// actions.ts: toda mutação passa pela fila
export async function enqueueAction(a: {type: 'decision.approve'|'decision.reject'|'wo.update'; id: string; body: unknown}) {
  const key = crypto.randomUUID();                              // Idempotency-Key
  await db.actions.add({ ...a, key, state: 'pending', attempts: 0, createdAt: Date.now() });
  await trySync();                                              // tenta já; se falhar, fica na fila
}
// o servidor devolve 200 com o mesmo resultado se a mesma Idempotency-Key chegar de novo
```
Tiles: pré-carregar a bounding box da fazenda em níveis de zoom úteis, respeitando o **termo de uso do provedor de tiles** (verificar; para uso offline em massa pode exigir servidor próprio).
- **Testes necessários:** com o gateway desligado e religado, a ação enfileirada é aplicada **uma vez**; mapa abre sem rede; reinstalar PWA não perde ação pendente.
- **Critério de aceite:** E2E com corte de rede no meio de uma aprovação.
- **Evidência de conclusão:** vídeo.
- **Risco:** licença de tiles. Registrar a decisão e a fonte.
- **Relação com a estratégia:** experiência offline de verdade na mão de quem decide.

#### S13-T4 · `DomainChange`, relógio lógico híbrido e IDs determinísticos
- **Objetivo:** gateway e nuvem **nunca** geram duplicata do mesmo fato.
- **Contexto:** Event/Decision têm UUID aleatório; dois nós que processam a mesma leitura gerariam dois eventos.
- **Problema atual:** sem identidade determinística nem ordem causal entre nós.
- **Estado desejado:** `Event.id = UUIDv5(NS, machine|regra|inicio_da_janela)`; `Decision.id` derivado do evento+regra; toda mudança de domínio vira `DomainChange(node_id, hlc, entidade, entidade_id, op, payload_hash, payload)`; **HLC** garante ordem sem depender de relógios perfeitos.
- **Dependências · Pré-requisitos:** S4-T2, S1-T5 · nenhum.
- **Arquivos prováveis:** `services/hlc.py`, `services/eventos.py`, `services/decisions.py`, `models.py`, migration.
- **Implementação esperada:**
```python
# services/hlc.py: relógio lógico híbrido (físico + contador), monotônico por nó
class HLC:
    def __init__(self, node_id): self.l = 0; self.c = 0; self.node = node_id
    def now(self):
        pt = int(time.time() * 1000)
        if pt > self.l: self.l, self.c = pt, 0
        else: self.c += 1
        return (self.l, self.c, self.node)
    def update(self, remote):                           # ao receber mudança de outro nó (algoritmo HLC padrão)
        rl, rc, _ = remote; pt = int(time.time() * 1000)
        l_old = self.l
        self.l = max(l_old, rl, pt)
        if self.l == l_old and self.l == rl: self.c = max(self.c, rc) + 1
        elif self.l == l_old:                self.c += 1
        elif self.l == rl:                   self.c = rc + 1
        else:                                self.c = 0
        return (self.l, self.c, self.node)

NS = uuid.UUID("6f1d2b1e-0000-4000-8000-00000000f1e1")       # namespace fixo do FieldNode
def event_id(machine_id, regra, inicio_janela):               # janela arredondada ao passo do contrato
    return uuid.uuid5(NS, f"{machine_id}|{regra}|{inicio_janela:%Y%m%dT%H%M}")
```
- **Testes necessários:** mesma leitura processada em dois nós produz o **mesmo** `Event.id`; HLC monotônico com relógio voltando; ordenação total estável por `(l, c, node)`.
- **Critério de aceite:** teste de duplicata cruzada verde.
- **Evidência de conclusão:** saída do teste.
- **Risco:** janela de arredondamento diferente entre nós. A janela vem do contrato versionado.
- **Relação com a estratégia:** pré-requisito da replicação segura.

#### S13-T5 · Replicação bidirecional gateway ↔ nuvem
- **Objetivo:** o que aconteceu em um lado aparece no outro, uma vez só, em qualquer ordem de chegada.
- **Contexto:** `SyncCursor` e o protocolo da S6 já cobrem telemetria (dispositivo → servidor).
- **Problema atual:** sem canal de domínio nos dois sentidos.
- **Estado desejado:** `POST /api/v1/replication/push` (peer envia `DomainChange` desde o seu cursor) e `GET /api/v1/replication/pull?since=<hlc>` com ACK cumulativo por peer; lote, compressão, `payload_hash`, retry exponencial; telemetria continua pelo caminho de S6.
- **Dependências · Pré-requisitos:** S13-T4, S6-T1 · `ReplicationPeer` cadastrado com credencial.
- **Arquivos prováveis:** `api/views_replication.py`, `services/replication.py`, `management/commands/replicate.py`, `models.py`.
- **Implementação esperada:**
```python
def apply_change(ch):                                     # idempotente
    if DomainChange.objects.filter(node_id=ch.node_id, hlc=ch.hlc).exists(): return "duplicate"
    with transaction.atomic():
        entity = resolve(ch.entidade, ch.entidade_id)
        outcome = merge(entity, ch)                       # regras de S13-T6
        DomainChange.objects.create(**ch.as_dict(), aplicado=outcome)
    return outcome
# replicate: loop com backoff; só avança o cursor do peer após ACK; falha vai para DLQ contexto=REPLICATION
```
- **Testes necessários:** push duplicado = `duplicate`; queda no meio do lote retoma pelo cursor; 10 mil mudanças replicam em ordem; ida e volta não gera eco infinito (mudança carrega `origin_node`).
- **Critério de aceite:** testes verdes; relatório de latência por 1 mil mudanças.
- **Evidência de conclusão:** relatório.
- **Risco:** loop de replicação. `origin_node` impede reenvio ao nó de origem.
- **Relação com a estratégia:** "nuvem é réplica".

#### S13-T6 · Regras de autoridade e resolução de conflito
- **Objetivo:** duas pessoas, dois lugares, uma verdade.
- **Contexto:** a V3 recusou CRDT para telemetria (correto); **edição de domínio offline** é o caso onde um mecanismo de reconciliação se justifica.
- **Problema atual:** sem política de conflito.
- **Estado desejado:** (1) o que **nasceu** no gateway pertence ao gateway; edição da nuvem sobre essa entidade vira `Proposal(pendente)` que o gateway aceita ou rejeita; (2) estados de `Decision` têm precedência: `EXECUTADA > EM_EXECUCAO > APROVADA > ADIADA > PENDENTE`, `REJEITADA` e `CANCELADA` só por ator com papel; (3) empate decide por HLC e depois `node_id`; (4) todo conflito escreve `ConflictLog` com as duas versões.
- **Dependências · Pré-requisitos:** S13-T5 · nenhum.
- **Arquivos prováveis:** `services/replication.py`, `models.py` (`Proposal`, `ConflictLog`), `docs/REPLICACAO.md`.
- **Implementação esperada:** matriz de casos em `docs/REPLICACAO.md` (quem ganha em cada combinação) e função `merge` que a implementa.
- **Testes necessários:** matriz completa: aprovar no gateway × rejeitar na nuvem; ambos aprovam; OS reagendada nos dois lados; exclusão × edição.
- **Critério de aceite:** nenhum caso da matriz fica sem teste; `ConflictLog` explica cada empate.
- **Evidência de conclusão:** testes.
- **Risco:** UX de proposta confusa. Mostrar "proposta da central aguardando decisão".
- **Relação com a estratégia:** "decisão nascida no gateway é do gateway".

#### S13-T7 · Inferência de ML local, distribuição de modelo e degradação controlada
- **Objetivo:** a IA **funciona sem internet** e falha de forma honesta.
- **Contexto:** `model_registry.py` guarda artefato e metadados; treino ocorre na central ou na campanha.
- **Problema atual:** gateway não recebe modelo e não define o que fazer sem ele.
- **Estado desejado:** `ml-runner` carrega o **modelo ativo** de `/models`; sincronização de modelos pela replicação (artefato + assinatura + metadados); verificação de assinatura antes de ativar; **quatro estados** com selo na UI: `modelo_ok`, `modelo_ausente`, `modelo_invalido`, `dados_insuficientes`; em qualquer falha usa EWMA/CUSUM + regras do contrato e marca "baseline estatístico".
- **Dependências · Pré-requisitos:** S5-T1, S15-T9 · nenhum.
- **Arquivos prováveis:** `services/model_sync.py`, `ml/runner.py`, `ia/model_registry.py`.
- **Implementação esperada:**
```python
def activate(model_dir):
    meta = json.loads((model_dir/"meta.json").read_text())
    if not verify_signature(model_dir/"model.bin", meta["sig"], PUBKEY): raise ModelInvalid("assinatura")
    if meta["feature_spec"] != FEATURE_SPEC_VERSION: raise ModelInvalid("feature_spec incompatível")
    return load(model_dir)
def infer(window):
    try:
        m = registry.active()
    except ModelMissing: return fallback(window, selo="modelo_ausente")
    except ModelInvalid: return fallback(window, selo="modelo_invalido")
    if len(window) < m.min_window: return fallback(window, selo="dados_insuficientes")
    return m.score(window)
```
- **Testes necessários:** com internet cortada, 100 novas leituras recebem score local; arquivo de modelo corrompido ⇒ `modelo_invalido` e fallback; remover modelo ⇒ `modelo_ausente`.
- **Critério de aceite:** os quatro estados reproduzidos em teste e visíveis na UI.
- **Evidência de conclusão:** testes + captura.
- **Risco:** modelo grande demais para o hardware. Medir latência (S15-T6/T13).
- **Relação com a estratégia:** pilar IA-100 e OFFLINE-100.

#### S13-T8 · Teste "APAGÃO TOTAL" (aceite dos pilares P1 e P3)
- **Objetivo:** provar o ciclo completo sem internet, com reboot.
- **Contexto:** é o critério de ponta a ponta exigido pela avaliação externa.
- **Problema atual:** nenhum teste executa o ciclo inteiro com WAN cortada.
- **Estado desejado:** script `scripts/apagao_total.py` + roteiro gravado.
- **Dependências · Pré-requisitos:** S13-T1 a T7, S8-T13, S16-T2/T3 (versões mínimas) · hardware físico.
- **Arquivos prováveis:** `scripts/apagao_total.py`, `docs/evidence/s13/apagao_total.*`, `docs/PROTOCOLO_APAGAO_TOTAL.md`.
- **Implementação esperada:** passos (cada um com verificação automática):
  1. WAN desligada (`iptables`/desligar uplink) e **registro do instante**;
  2. leitura **real** (aquecer sonda de forma segura) chega ao gateway;
  3. evento criado localmente com Trust e evidência;
  4. prescrição gerada com playbook e evidências;
  5. operador aprova pelo celular via hotspot;
  6. OS criada, executada (checklist com foto e medição) e resultado registrado;
  7. reavaliação por telemetria posterior;
  8. **reboot** do gateway **e** do ESP32 no meio do passo 6;
  9. verificar persistência: nenhuma etapa perdida, sequência sem regressão;
  10. WAN religada: replicação, 0 duplicata, 0 perda, `ConflictLog` explicado.
- **Testes necessários:** 3 execuções seguidas; uma delas com queda de energia do gateway no passo 5.
- **Critério de aceite:** 3/3 com verificação automática verde e vídeo contínuo.
- **Evidência de conclusão:** vídeo + log + relatório.
- **Risco:** flakiness de hotspot. Canal fixo, cabo para o notebook de controle.
- **Relação com a estratégia:** é **a** prova do diferencial.

#### S13-T9 · Gateway móvel (nó de replicação no transbordo/caminhão)
- **Objetivo:** a decisão nasce perto da máquina e o dado viaja com o veículo.
- **Contexto:** o transbordo anda entre a frente e a base; um Raspberry na cabine pode rodar o perfil `edge`.
- **Problema atual:** o Mule só carrega buffer, não decide.
- **Estado desejado:** perfil `edge` no veículo, com HLC e `ReplicationPeer` para a base; quando o veículo chega na base, replica; antes, atende o operador da frente por hotspot da cabine.
- **Dependências · Pré-requisitos:** S13-T5, S13-T6 · segundo mini-PC/Raspberry.
- **Arquivos prováveis:** `deploy/edge/mobile.env`, `docs/GATEWAY_MOVEL.md`.
- **Implementação esperada:** `NODE_ID` distinto; peers `veiculo ↔ base ↔ nuvem` (cadeia).
- **Testes necessários:** dois gateways editam coisas diferentes; ao se encontrar, convergem.
- **Critério de aceite:** convergência sem duplicata em 3 rodadas.
- **Evidência de conclusão:** log.
- **Risco:** alimentação do Raspberry no veículo (queda no desligamento). Usar UPS pequena/supercap e desligamento seguro.
- **Relação com a estratégia:** replicação em cadeia é rara em protótipos.

#### S13-T10 · Tempo confiável no gateway
- **Objetivo:** o gateway é a **fonte de hora** dos nós quando não há NTP.
- **Contexto:** S1-T5 e S8-T3 definem `time_source`; o gateway precisa de relógio bom.
- **Problema atual:** gateway sem RTC perde a hora no boot.
- **Estado desejado:** RTC no gateway (DS3231 ou RTC da placa), `chrony` com fontes locais, serviço de hora para nós (`/api/v1/time`/MQTT retained), monitor de deriva e alerta se a hora do gateway divergir do NTP ao reconectar.
- **Dependências · Pré-requisitos:** S8-T3 · RTC.
- **Arquivos prováveis:** `deploy/edge/chrony.conf`, `services/time_service.py`.
- **Implementação esperada:** nós ajustam hora ao ver mensagem de tempo do gateway e marcam `time_source=gateway`.
- **Testes necessários:** boot sem internet mantém hora; ao reconectar, ajuste gradual sem saltos para trás.
- **Critério de aceite:** nenhum `event_time` regride após reconexão.
- **Evidência de conclusão:** teste.
- **Risco:** salto de relógio. Usar slew, não step.
- **Relação com a estratégia:** integridade temporal (pilar 1 da tese).

#### S13-T11 · Backup local e recuperação do gateway
- **Objetivo:** cartão/SSD corrompido não perde decisão nem OS.
- **Contexto:** S10-T5 cobre backup central; o gateway precisa do seu.
- **Problema atual:** sem rotina local.
- **Estado desejado:** dump incremental diário para disco USB, restauração guiada, verificação de integridade (`PRAGMA`/`CHECK TABLE`), política de disco cheio do gateway (alerta a 80 %, rotação de classe C bruta antes de tocar em decisões).
- **Dependências · Pré-requisitos:** S10-T5 · disco USB.
- **Arquivos prováveis:** `scripts/edge_backup.sh`, `docs/GATEWAY_NUCLEO.md`.
- **Implementação esperada:** restore em máquina limpa e comparação de contagens e hash da cadeia de auditoria (S16-T8).
- **Testes necessários:** corromper o volume de propósito e restaurar.
- **Critério de aceite:** restore recupera 100 % das decisões e OS.
- **Evidência de conclusão:** log.
- **Risco:** backup no mesmo disco. Disco separado.
- **Relação com a estratégia:** pergunta de CTO: "e se o gateway morrer no campo?".


#### S13-T12 · HTTPS no gateway (contexto seguro para PWA e Bluetooth) · **substitui a decisão D-12 da V3**
- **Objetivo:** o PWA instala e o Service Worker e o Web Bluetooth funcionam quando o celular acessa o gateway **sem internet**.
- **Contexto:** a V3 (D-12) aceitava "HTTP no hotspot isolado". **Isso quebra a V4:** Service Worker e Web Bluetooth exigem contexto seguro (HTTPS, ou `localhost`). Em `http://192.168.x.x` o navegador não registra o Service Worker nem expõe a API Bluetooth.
- **Problema atual:** gateway serve HTTP puro; PWA offline do S13-T3 e o mule BLE do S14-T6 não funcionariam no celular.
- **Estado desejado:** o gateway serve `https://fieldnode.local` (ou nome fixo) com certificado **confiável no celular**, sem depender de internet na hora do uso.
- **Dependências · Pré-requisitos:** S13-T1 · decisão D-35 (abaixo).
- **Arquivos prováveis:** `deploy/edge/Caddyfile` (ou nginx), `deploy/edge/dnsmasq.conf`, `docs/GATEWAY_NUCLEO.md`.
- **Implementação esperada:** duas opções, escolher uma e documentar:
  - **(a) CA local (recomendada para demo e piloto):** gerar uma CA própria com ferramenta de CA local (ex.: `mkcert`/`step-ca`), emitir certificado para `fieldnode.local`/IP do gateway, **instalar a CA raiz uma vez no celular do operador** (procedimento no kit, S17-T4), `dnsmasq` no gateway resolve o nome para o IP do hotspot.
  - **(b) Domínio público + certificado emitido com antecedência:** certificado válido para um domínio seu, renovado quando houver internet e copiado para o gateway; DNS local do hotspot resolve o domínio para o IP do gateway; celular confia sem instalar CA. Exige domínio próprio e rotina de renovação (certificados de CA pública expiram em poucos meses; **verificar a validade vigente**).
- **Testes necessários:** celular novo, sem internet, instala o PWA e registra o Service Worker; Web Bluetooth abre o seletor de dispositivo.
- **Critério de aceite:** `navigator.serviceWorker.ready` resolve e `navigator.bluetooth` existe no celular de teste, ambos **sem internet**.
- **Evidência de conclusão:** captura do DevTools remoto/`chrome://inspect` + vídeo.
- **Risco:** certificado expirar no dia da banca. Checklist de validade em `preflight.sh` (S10-T8).
- **Relação com a estratégia:** sem isso, o offline do celular é teórico. Esta tarefa corrige uma suposição da V3.

---

### SEMANA 14 · ENLACES REAIS DE LONGO ALCANCE E SOAK DE 14 DIAS

**Camadas:** IMPLEMENTATION · VALIDATION · OBSERVABILITY · SECURITY
**Pilar:** P3 OFFLINE-100 (sincronização "em tempo real" enquanto a máquina está longe)

- **Objetivo estratégico:** provar, com números medidos, que **durante até 14 dias fora de qualquer internet** os dados continuam chegando e os alertas críticos chegam em minutos, por mais de um caminho físico.
- **Objetivo técnico:** LoRa real (rádio, firmware, quadro compacto, ACK, campanha de alcance em campo alto), relay no transbordo, mule físico com 3 ESP32, celular do operador como mule BLE, satélite real, Connectivity Manager com enlaces reais e failover, autenticação e cifragem dos quadros, energia e autonomia medidas, painel de cobertura, **soak test de 14 dias**.
- **Por que existe:** pedido central da Paola: "ao longo dessas duas semanas, enquanto ela estiver longe, os dados continuarem sincronizando de alguma forma (LoRa, Data Mule, qualquer outra) em tempo real". As avaliações externas pediram enlace real em vez de simulador Docker.
- **Problemas que resolve:** Mule só em Docker; LoRa só plano; satélite só simulado; nenhum número de alcance; autonomia desconhecida; nenhum teste de longa duração.
- **Dependências recebidas:** S6 (protocolo, capacidade), S7 (custódia, quadro compacto, manager), S8 (nó real, outbox, ESP-NOW), S13 (gateway, HTTPS).
- **Entregáveis:** firmware de enlaces, `connectivity/providers/{lora,espnow_mule,ble,sat}.py`, planilha e mapa de alcance, relatório do soak, `docs/COBERTURA_E_ENLACES.md`, `docs/PLANO_TESTE_RADIO.md` executado.
- **Arquivos/módulos afetados:** `firmware/lib/{lora,relay,ble_gatt,sat_modem}/*`, `connectivity/*`, `api_tcc/services/telemetria.py` (`via`, `transport`), `docs/*`.
- **Arquitetura:** `ConnectivityProvider` (S7-T1) com 4 providers reais. **Banco:** `LinkSample(rssi, snr, per, lat, lon, enlace, t)`, `DeliveryHop`. **Backend:** aceitar `transport ∈ {lora, relay, ble, sat, espnow_mule}`. **Frontend:** painel de cobertura. **Hardware:** LoRa, BLE, modem, bateria/solar. **ML/IA:** nenhuma. **Infra:** gateway LoRa no notebook/mini-PC. **Segurança:** MAC truncado e cifragem AES por dispositivo. **Testes:** hardware-in-the-loop e soak. **Docs:** cobertura e rádio.
- **Experimentos:** alcance por distância e obstrução (campo aberto, canavial, mata baixa, atrás de prédio); relay em movimento; BLE com celular passando; satélite em área aberta; 14 dias corridos.
- **Critérios de aceitação:** OFF-14 (seção 0.2) com números; zero perda em A e B; latência por enlace publicada.
- **Métricas:** PER e RSSI por distância; latência fim a fim p50/p95 por enlace e classe; mensagens por encontro de mule; consumo médio (mA) e autonomia (dias); reinícios espontâneos; backlog máximo.
- **Evidências esperadas:** planilha + mapa de alcance, log do soak, vídeos dos três mules.
- **Riscos:** LoRa alcance menor que o esperado em cultura alta; atraso de entrega de peças; modem satelital caro/indisponível; interferência do canal Wi-Fi.
- **Decisões:** D-36 (topologia: gateway LoRa fixo na sede/silo vs no veículo), D-37 (satélite: modelo e plano após estudo; gate de compra), D-38 (Android-first para BLE).
- **Perguntas abertas:** a faixa/potência de LoRa permitida e os requisitos de certificação do módulo no Brasil (verificar na norma vigente da Anatel antes de transmitir ao ar livre).
- **Definition of Done da fatia:** relatório de 14 dias aprovado + tabela de latência por enlace.

#### S14-T1 · Requisito de cobertura e SLA de latência por classe e enlace
- **Objetivo:** definir o que significa "tempo real" **em número**, por enlace.
- **Contexto:** sem enlace não existe tempo real; cada enlace tem latência e disponibilidade diferentes.
- **Problema atual:** "tempo real" é adjetivo, não requisito.
- **Estado desejado:** tabela de **metas de projeto (hipóteses a medir)** e coluna de resultado medido.
- **Dependências · Pré-requisitos:** S6-T1 · nenhum.
- **Arquivos prováveis:** `docs/COBERTURA_E_ENLACES.md`.
- **Implementação esperada:**

| Classe | Enlace | Meta de projeto (hipótese) | Medido (preencher em S14-T9) |
|---|---|---|---|
| A | Alarme local (nó) | imediato, sem rede | |
| A | LoRa até gateway/relay no alcance | p95 ≤ 30 s | |
| A | BLE via celular do operador | depende do celular estar a poucos metros; meta: ≤ 5 min após o celular aparecer | |
| A | Satélite | meta definida após estudo do modem (S14-T7) | |
| B | LoRa/relay em lote | ≤ 15 min | |
| B/C | Mule físico (ESP-NOW/Wi-Fi) | ≤ próximo encontro | |
| C | Qualquer enlace barato | ≤ 24 h | |

Regra: **meta sem medição não vai para o pitch**.
- **Testes necessários:** nenhum (documento); a medição é S14-T9.
- **Critério de aceite:** tabela revisada pelo grupo.
- **Evidência de conclusão:** documento.
- **Risco:** metas irreais. São revistas após S14-T3.
- **Relação com a estratégia:** requisito mensurável.

#### S14-T2 · LoRa real: hardware, firmware, quadro compacto, ACK e retransmissão
- **Objetivo:** primeiro pacote de telemetria viajando por LoRa de verdade.
- **Contexto:** `S7-T5` define o quadro de 28 bytes; módulos SX1276/SX1262 com ESP32.
- **Problema atual:** nenhum rádio de longo alcance no projeto.
- **Estado desejado:** nó transmite quadro compacto; receptor LoRa ligado ao gateway (USB/UART/placa LoRa+ESP32 publicando no MQTT local); ACK curto de volta; retransmissão com backoff aleatório; classe A tem prioridade de ar.
- **Dependências · Pré-requisitos:** S7-T5, S8-T1 · 3 placas com LoRa e antenas **na faixa certa**.
- **Arquivos prováveis:** `firmware/lib/lora/*`, `firmware/gateway_lora/*`, `connectivity/providers/lora.py`.
- **Implementação esperada:**
```cpp
#include <RadioLib.h>
SX1276 radio = new Module(PIN_NSS, PIN_DIO0, PIN_RST, PIN_DIO1);
void lora_begin() {
  // frequência, largura de banda (kHz), SF, CR, sync word, potência (dBm), preâmbulo: CONFERIR faixa e limites vigentes antes de transmitir ao ar livre
  int s = radio.begin(915.0, 125.0, 9, 5, 0x12, 14, 8);
  if (s != RADIOLIB_ERR_NONE) fatal("lora init", s);
}
bool lora_send_with_ack(const uint8_t* f, size_t n, uint8_t tries) {
  for (uint8_t i = 0; i < tries; ++i) {
    radio.transmit(f, n);
    if (wait_ack(/*timeout_ms=*/400 + random(0, 300))) return true;   // jitter evita colisão entre nós
  }
  return false;                                                         // mantém no outbox (S8-T4)
}
```
```python
# time-on-air (fórmula do datasheet Semtech) para dimensionar duty/atraso
def toa(pl, sf, bw=125e3, cr=1, preamble=8, crc=True, ih=False):
    t_sym = (2 ** sf) / bw; de = 1 if (sf >= 11 and bw == 125e3) else 0
    num = 8*pl - 4*sf + 28 + 16*(1 if crc else 0) - 20*(1 if ih else 0)
    n_payload = 8 + max(math.ceil(num / (4*(sf - 2*de))) * (cr + 4), 0)
    return (preamble + 4.25 + n_payload) * t_sym
```
- **Testes necessários:** 1.000 quadros a 3 distâncias: PER; ACK perdido ⇒ reenvio ⇒ `duplicate` no servidor; colisão entre dois nós simulados.
- **Critério de aceite:** pacote A do nó ao gateway com ACK, deduplicado, em bancada; tabela de time-on-air por SF.
- **Evidência de conclusão:** log + vídeo.
- **Risco:** antena errada para a faixa (danifica ou não funciona): antena **sempre** conectada antes de transmitir.
- **Relação com a estratégia:** o primeiro enlace de longo alcance real.

#### S14-T3 · Campanha de alcance LoRa em campo (canavial/mata baixa incluídos)
- **Objetivo:** número medido de alcance onde importa.
- **Contexto:** cultura alta absorve sinal; catálogo de módulo vale para campo aberto.
- **Problema atual:** nenhum dado.
- **Estado desejado:** planilha e mapa com RSSI, SNR, PER por distância, altura da antena, SF/BW e cobertura vegetal; decisão de topologia (D-36).
- **Dependências · Pré-requisitos:** S14-T2 · permissão do local, GPS (S8-T11), bateria.
- **Arquivos prováveis:** `docs/PLANO_TESTE_RADIO.md`, `data/radio/*.csv`, mapa no front (S14-T11).
- **Implementação esperada:** passos de 100 m até perda total; 3 alturas de antena (1 m, 2 m, 4 m); 3 SFs; 4 ambientes (campo aberto, canavial, atrás de construção, dentro de galpão); 5 amostras por ponto.
- **Testes necessários:** repetir 2 pontos em outro dia (variação).
- **Critério de aceite:** tabela completa + alcance utilizável por classe (A exige PER baixo).
- **Evidência de conclusão:** CSV + fotos + mapa.
- **Risco:** chuva/vento alteram resultado. Registrar clima.
- **Relação com a estratégia:** "o número medido é argumento de pitch".

#### S14-T4 · Relay no transbordo/caminhão (LoRa ↔ ESP-NOW/LoRa)
- **Objetivo:** estender o alcance usando o veículo que passa.
- **Contexto:** mesh completo é escopo grande; **um salto** de relay resolve o caso "máquina longe, transbordo perto".
- **Problema atual:** sem retransmissão.
- **Estado desejado:** nó no veículo recebe quadro LoRa/ESP-NOW, guarda com custódia (S7-T2), repete ao gateway quando o gateway estiver ao alcance; `via` registra o salto; limite de 1 salto (anti-loop).
- **Dependências · Pré-requisitos:** S14-T2, S7-T2 · placa extra.
- **Arquivos prováveis:** `firmware/relay/*`, `connectivity/providers/relay.py`.
- **Implementação esperada:** `hop_count` no quadro; descarta `hop_count > 1`; ACK da origem só após ACK do gateway (custódia).
- **Testes necessários:** relay em movimento passando entre origem e gateway; pacote duplicado por dois relays.
- **Critério de aceite:** 0 perda e 0 duplicata em 3 passagens.
- **Evidência de conclusão:** log do `DeliveryHop`.
- **Risco:** tempestade de retransmissão. Limite de salto e jitter.
- **Relação com a estratégia:** extensão de alcance real sem malha complexa.

#### S14-T5 · Data Mule **físico** com 3 ESP32 (origem, mule, gateway)
- **Objetivo:** a demonstração que derruba o queixo: dados atravessando fisicamente.
- **Contexto:** S7-T3 prova o protocolo em Docker; aqui o transporte é rádio.
- **Problema atual:** só simulação.
- **Estado desejado:** **Origem** (flash, offline) → **Mule** (aproxima, ESP-NOW/Wi-Fi) → **Gateway** (mesa, internet); custódia, assinatura, ACK de volta; o front atualiza quando o mule "chega".
- **Dependências · Pré-requisitos:** S8-T4, S8-T5, S7-T2 · 3 ESP32.
- **Arquivos prováveis:** `firmware/mule/*`, `firmware/node/*`, `docs/evidence/s14/mule.*`.
- **Implementação esperada:** mule anuncia "estou aqui"; origem envia lote por classe; mule confirma custódia; ao chegar, entrega e recebe ACK; no próximo encontro devolve o ACK à origem, que só então libera a flash.
- **Testes necessários:** mule desliga no meio; mule duplicado; origem reinicia no meio.
- **Critério de aceite:** vídeo contínuo e relatório de entrega com 0 perda/0 duplicata.
- **Evidência de conclusão:** vídeo + `DeliveryHop`.
- **Risco:** coexistência Wi-Fi/ESP-NOW no mesmo canal. Fixar canal.
- **Relação com a estratégia:** prova física do mule.

#### S14-T6 · Celular do operador como mule (BLE) + PWA
- **Objetivo:** usar o aparelho que o operador já tem.
- **Contexto:** o nó fala BLE; uma PWA com Web Bluetooth coleta e despeja quando houver sinal.
- **Problema atual:** inexistente.
- **Estado desejado:** serviço GATT (tipo UART) no nó com fragmentação, janela deslizante e ACK; PWA em Chrome/Android conecta, baixa o outbox, guarda no IndexedDB e envia ao gateway/nuvem quando houver rede; custódia igual à do mule; **iPhone não suporta Web Bluetooth** (D-38: Android-first; alternativa nativa fica fora do escopo).
- **Dependências · Pré-requisitos:** S13-T12 (HTTPS), S7-T2, S8-T4 · celular Android.
- **Arquivos prováveis:** `firmware/lib/ble_gatt/*`, `frontend-next/src/lib/ble/muleClient.ts`, `src/app/mule/page.tsx`.
- **Implementação esperada:**
```ts
const NUS = '6e400001-b5a3-f393-e0a9-e50e24dcca9e';
export async function collect() {
  const dev = await navigator.bluetooth.requestDevice({ filters: [{ services: [NUS] }] });   // exige gesto do usuário e HTTPS
  const srv = await dev.gatt!.connect();
  // ler lotes fragmentados, remontar, validar payload_hash, gravar em IndexedDB e só então enviar ACK ao nó
}
```
- **Testes necessários:** 500 registros transferidos; desconexão no meio retoma; pacote adulterado é rejeitado.
- **Critério de aceite:** 0 perda e 0 duplicata em 3 coletas com celular real.
- **Evidência de conclusão:** vídeo no celular.
- **Risco:** limites de MTU e de segundo plano do navegador. Documentar.
- **Relação com a estratégia:** mule barato e real.

#### S14-T7 · Satélite real (estudo, compra, integração e medição)
- **Objetivo:** alerta crítico em minutos **em qualquer lugar**, medido.
- **Contexto:** onde nem LoRa nem celular alcançam, só satélite alcança. A V3 deixava simulado "por falta de estudo"; o estudo é a tarefa.
- **Problema atual:** sem modem, sem custo conhecido, sem latência medida.
- **Estado desejado:** (1) **estudo comparativo** com checklist; (2) **compra** conforme gate; (3) integração por UART/AT; (4) classe A com orçamento diário; (5) latência medida.
- **Dependências · Pré-requisitos:** S7-T5 (quadro compacto), S14-T1 · orçamento (D-37).
- **Arquivos prováveis:** `docs/ESTUDO_SATELITE.md`, `firmware/lib/sat_modem/*`, `connectivity/providers/sat.py`.
- **Implementação esperada:** checklist **a preencher com dado atual na hora da compra** (preços e coberturas mudam):

| Critério | O que registrar (fonte e data) |
|---|---|
| Cobertura no Brasil rural | mapa oficial do provedor, teste em campo aberto |
| Tamanho máximo de mensagem | bytes por mensagem (o quadro compacto cabe?) |
| Latência típica e janelas de passagem | medir, não confiar só em folheto |
| Preço do modem, do plano e por mensagem | cotação datada |
| Consumo e alimentação | mA em TX/RX, pico |
| Antena e instalação | exigência de visada de céu |
| Homologação/regulação no Brasil | exigência da Anatel para o modem |
| API/integração | AT commands, webhook, formato de entrega |
| Disponibilidade e prazo de entrega | lead time |

Candidatos a **pesquisar** (confirmar existência, cobertura e preço atuais): serviços de mensagens curtas por constelação em órbita baixa ou por constelação de órbita iridiana, e módulos de IoT com suporte a redes não terrestres. **Nenhuma escolha está fixada neste documento.**
- **Testes necessários:** 20 mensagens classe A em campo aberto em horários diferentes; orçamento diário respeitado; deduplicação por `(device, sequence)`.
- **Critério de aceite:** latência p50/p95 medida e registrada; se o modem não chegar a tempo, a tarefa fica `BLOQUEADA_POR_COMPRA` com data e **o pilar OFF-14 continua fechado por LoRa + relay + BLE** (seção 0.6).
- **Evidência de conclusão:** CSV de latência + foto da instalação.
- **Risco:** custo recorrente e prazo. Gate de decisão na semana 3.
- **Relação com a estratégia:** o "e se não há nada por perto?" respondido.

#### S14-T8 · Connectivity Manager com enlaces reais e failover
- **Objetivo:** a escolha do caminho passa a acontecer com hardware real.
- **Contexto:** S7-T1 criou a interface e providers de teste.
- **Problema atual:** providers `lora`, `ble`, `sat`, `relay` não existem de verdade.
- **Estado desejado:** política por classe, custo e latência medidos (S14-T1); **failover**: se o enlace preferido falha, tenta o próximo sem perder custódia; registro de qual enlace entregou cada mensagem.
- **Dependências · Pré-requisitos:** S14-T2, S14-T4, S14-T6, S14-T7 · nenhum.
- **Arquivos prováveis:** `connectivity/manager.py`, `connectivity/providers/*`, firmware do nó (política espelhada).
- **Implementação esperada:** política declarativa em `contracts/connectivity.v1.json` lida por firmware (header gerado) e Python.
- **Testes necessários:** hardware-in-the-loop: desligar LoRa ⇒ cai para relay/BLE/satélite; religar ⇒ volta; classe A nunca fica esperando enlace barato se o caro está disponível e o orçamento permite.
- **Critério de aceite:** 3 cenários de failover verdes com log.
- **Evidência de conclusão:** logs + vídeo.
- **Risco:** divergência entre política do nó e do gateway. Fonte única.
- **Relação com a estratégia:** "o sistema decide o caminho".

#### S14-T9 · **Soak test de 14 dias** (a prova do offline)
- **Objetivo:** provar OFF-14 com 14 dias corridos de dado real.
- **Contexto:** ninguém acelera 14 dias; por isso começa cedo (sem 4) e roda duas vezes.
- **Problema atual:** nenhum teste de longa duração.
- **Estado desejado:** nó real instalado num local sem internet (com permissão), coletando continuamente; enlaces alternativos ativos; gateway-núcleo operando; registro automático de tudo.
- **Dependências · Pré-requisitos:** S8-T4, S14-T2, S14-T10 · local e energia.
- **Arquivos prováveis:** `scripts/soak_report.py`, `docs/RELATORIO_SOAK_14D.md`.
- **Implementação esperada:** métricas coletadas por script: mensagens geradas/recebidas por classe e enlace, duplicatas, latência fim a fim, reinícios do nó, backlog máximo, ocupação da flash, tensão da bateria, eventos de alarme local, quedas de enlace; **eventos reais provocados** em dias definidos (aquecer sonda, desbalancear rig) para medir latência do alerta crítico por enlace.
- **Testes necessários:** soak #1 (semanas 4 a 7, firmware parcial); soak #2 (semanas 9 a 11, pilha completa).
- **Critério de aceite:** 0 perda em A e B; 0 duplicata; latência A p95 dentro da meta do enlace usado; relatório sem "embelezar".
- **Evidência de conclusão:** `RELATORIO_SOAK_14D.md` + CSVs.
- **Risco:** falha de energia no dia 9. É resultado: documentar causa, corrigir e **recomeçar o relógio**.
- **Relação com a estratégia:** é o número que separa o FieldNode de dashboard.

#### S14-T10 · Energia e autonomia
- **Objetivo:** saber quantos dias o nó vive sem tomada.
- **Contexto:** nó pode estar em máquina com bateria própria, mas o soak e o piloto exigem dimensionamento.
- **Problema atual:** sem medição de consumo.
- **Estado desejado:** perfil de consumo (ativo, rádio TX, deep sleep) com INA219; orçamento por ciclo; dimensionamento de bateria/solar; estratégia: amostrar a 0,5 Hz apenas quando em operação, `deep sleep` fora dela, acordar por pulso do hall/RTC.
- **Dependências · Pré-requisitos:** S8-T1 · INA219.
- **Arquivos prováveis:** `docs/ENERGIA.md`, `firmware/lib/power/*`.
- **Implementação esperada:**
```text
autonomia_dias = (capacidade_Ah * eficiência) / (I_media_A * 24)
I_media = (t_ativo*I_ativo + t_tx*I_tx + t_sleep*I_sleep) / t_ciclo        # medir cada termo com o INA219
```
- **Testes necessários:** 24 h de medição real, projeção para 14 dias, confronto com o soak.
- **Critério de aceite:** projeção dentro de tolerância do medido no soak.
- **Evidência de conclusão:** planilha de consumo.
- **Risco:** pico de TX derrubar a tensão. Capacitor e bateria adequada.
- **Relação com a estratégia:** viabilidade em campo.

#### S14-T11 · Painel de cobertura e enlaces + mapa de cobertura
- **Objetivo:** o operador vê por onde cada máquina está "falando".
- **Contexto:** o roadmap prevê "mapa de cobertura de campo".
- **Problema atual:** invisível.
- **Estado desejado:** por máquina: enlace ativo, último contato **por enlace**, latência medida, backlog; mapa com pontos de RSSI/PER (S14-T3) e trilha GPS; alerta quando uma máquina fica sem **nenhum** enlace por mais de N min.
- **Dependências · Pré-requisitos:** S14-T8, S6-T6 · nenhum.
- **Arquivos prováveis:** `src/components/LinkPanel.tsx`, `CoverageMap.tsx`, `api/views_links.py`, `LinkSample`.
- **Implementação esperada:** consumo de `/api/v1/links/`; cores por qualidade; selo "medido".
- **Testes necessários:** desligar um enlace e ver o painel mudar em um ciclo.
- **Critério de aceite:** E2E.
- **Evidência de conclusão:** captura.
- **Risco:** baixo.
- **Relação com a estratégia:** torna o offline **visível**.

#### S14-T12 · Autenticação e cifragem dos enlaces
- **Objetivo:** ninguém forja nem lê pacote de rádio.
- **Contexto:** o quadro compacto não comporta assinatura completa; LoRa e BLE são meios abertos.
- **Problema atual:** sem proteção no ar.
- **Estado desejado:** **MAC truncado** (HMAC-SHA256 truncado em 4 a 8 bytes) e **contador monotônico** anti-replay no quadro; cifragem **AES-128 por dispositivo** (aceleração por hardware do ESP32); chave por dispositivo derivada do `DeviceCredential` (S2-T8); rotação documentada.
- **Dependências · Pré-requisitos:** S14-T2, S2-T8 · nenhum.
- **Arquivos prováveis:** `firmware/lib/secure_frame/*`, `connectivity/secure_frame.py`.
- **Implementação esperada:**
```text
quadro = cabeçalho(device_idx, seq) || AES-CTR(chave_dev, nonce=device_idx||seq, payload) || MAC_trunc(chave_mac_dev, cabeçalho||cifrado)
servidor: rejeita MAC inválido, rejeita seq <= último aceito (replay), registra tentativa na DLQ contexto=RADIO_AUTH
```
Documentar o **limite do MAC truncado** (probabilidade de falsificação por tentativa) e a mitigação (limite de taxa por device).
- **Testes necessários:** 1 bit alterado ⇒ rejeição; replay ⇒ rejeição; chave errada ⇒ rejeição.
- **Critério de aceite:** testes verdes (Python) e em bancada.
- **Evidência de conclusão:** testes + log.
- **Risco:** chave em flash (ver S8-T8: flash encryption).
- **Relação com a estratégia:** segurança honesta do enlace.


---

### SEMANA 15 · IA PROFISSIONAL: DADOS REAIS, MODELOS COMPARADOS, MLOPS E COPILOTO

> **NOTA V5:** S15-T4 (resíduo) e S15-T10 (diagnóstico) passam a ser **por componente** (bomba, filtro, injetores). S15-T7 (calibração) alimenta o **PR** (S19-T5); S15-T11 e os **laudos** (S19-T2) são as duas fontes de rótulo.


**Camadas:** VALIDATION · IMPLEMENTATION · TESTING · DOCUMENTATION
**Pilar:** P2 IA-100

- **Objetivo estratégico:** a IA do FieldNode deixa de ser "um arquivo Python que treina" e vira um **sistema de modelos medidos**, com dado real próprio, comparação honesta, explicação, versão, drift, rollback, diagnóstico e um copiloto que roda sem internet. É o que uma equipe de produto faria: *dados → baseline simples → modelos → avaliação rigorosa → implantação controlada → monitoramento*.
- **Objetivo técnico:** campanha de sessões reais e rig de falhas controladas; especificação única de features; 5 detectores comparados em split temporal por sessão; incerteza calibrada; SHAP; registro e gates; diagnóstico assistido; aprendizado a partir do feedback; copiloto com RAG e ferramentas; LLM local; avaliação e red-team; teste de IA offline; acústica opcional.
- **Por que existe:** a avaliação externa disse "a S5 mede em dado sintético e valida em dataset público; é defensável, mas o IF por regime é o mínimo, não o diferencial". A Paola pediu IA de nível sênior e, se possível, chatbot e o que startup high-tech faria.
- **Problemas que resolve:** dado só sintético; um único detector; limiares sem incerteza; ausência de MLOps; sem diagnóstico; sem copiloto.
- **Dependências recebidas:** S1 (contrato), S5 (harness, regime, guardrails), S8 (sensores reais), S13-T7 (inferência local).
- **Entregáveis:** `data/campaign/*` (manifesto e hashes), `ml/features/spec_v1.json`, `ml/eval/*`, relatório `AVALIACAO_ANOMALIA.md` v2, `ml/registry/*`, `knowledge/falhas.yml`, `copilot/*`, `docs/MODEL_CARD_*.md`.
- **Arquivos/módulos afetados:** `ml/*`, `api_tcc/services/anomaly_detection.py`, `ia/model_registry.py`, `services/agentic.py`, `services/assistant_tools.py`, `firmware/lib/spc`, `firmware/lib/features`.
- **Arquitetura:** pipeline único de features (nó, gateway, backend) → detectores → decisão determinística → prescrição; LLM só redige/explica. **Banco:** `ModelVersion`, `FeatureSpec`, `DriftReport`, `LabeledWindow`, `KnowledgeDoc`. **Backend:** MLOps e copiloto. **Frontend:** "por que o alerta", painel de modelos. **Hardware:** rig e campanha. **ML/IA:** núcleo. **Infra:** `make eval`, `make train`. **Segurança:** guardrails e isolamento do copiloto. **Testes:** golden de features, avaliação, injeção. **Docs:** model cards.
- **Experimentos:** 5 detectores × 3 tipos de falha (desbalanceamento, superaquecimento controlado, sensor travado) × sessões; ablação de features; deriva induzida (mudar carga/ambiente).
- **Critérios de aceitação:** relatório reproduzível com `make eval`; modelo escolhido por **gate**, não por preferência; IA funcionando sem internet.
- **Métricas:** PR-AUC, recall@FPR fixo, tempo até detecção, falso alarme por hora, latência de inferência no gateway, tamanho do modelo, cobertura da explicação.
- **Evidências esperadas:** relatório, notebooks salvos, vídeos do rig, saída de `make eval`.
- **Riscos:** poucos dados reais (mitigação: campanha + rig + augmentação documentada); overfitting ao benchmark (cenários fixados antes); LLM local lento (benchmark real).
- **Decisões:** D-39 (critério de adoção de modelo), D-40 (embeddings vs BM25 no RAG), D-41 (LLM local: modelo e hardware após benchmark).
- **Perguntas abertas:** qual a carga real de uma colheitadeira durante a safra? (entrevistas e piloto definem os regimes).
- **Definition of Done da fatia:** checklist P2 (seção 0.2) 100% marcado.

#### S15-T1 · Campanha de dados reais (≥ 5 sessões de motor real, rotuladas)
- **Objetivo:** dataset **próprio**, real, versionado.
- **Contexto:** a V3 só tinha dado sintético e dataset público.
- **Problema atual:** o modelo nunca viu um motor de verdade com o seu sensor.
- **Estado desejado:** ≥ 5 sessões (marcha lenta, carga progressiva, partida a quente, desligamento, anomalia provocada **com segurança e supervisão de mecânico/oficina**), cada sessão com metadados (regime, carga, ambiente, sensor, operador, notas) e rótulos de intervalo; todos os sensores do nó + CAN escuta (S8-T12) quando houver.
- **Dependências · Pré-requisitos:** S8-T1, S8-T2, S8-T11 · local seguro, mecânico, autorização.
- **Arquivos prováveis:** `data/campaign/manifest.json`, `data/campaign/sessions/*.parquet`, `docs/CAMPANHA_DADOS.md`.
- **Implementação esperada:**
```json
{ "session_id": "S-2026-11-03-01", "machine": "motor-oficina-A", "sensors": ["ds18b20_inox","mpu6050","hall","gps"],
  "regimes": [{"t0":"...","t1":"...","regime":"marcha_lenta"},{"t0":"...","t1":"...","regime":"trabalhando","carga":"media"}],
  "labels": [{"t0":"...","t1":"...","tipo":"anomalia_provocada","descricao":"..." , "seguranca":"supervisionada"}],
  "ambiente": {"temp_c": 29.5, "umidade": 60}, "hash_dados": "sha256:...", "responsavel": "..." }
```
Procedimento de segurança escrito (EPI, extintor, limite de temperatura de corte, quem pode interromper). **Nunca** provocar condição perigosa sem acompanhamento.
- **Testes necessários:** validação do manifesto; hash confere; sem lacunas de tempo não explicadas.
- **Critério de aceite:** ≥ 5 sessões, ≥ 20 h acumuladas (meta), rótulos revisados por duas pessoas.
- **Evidência de conclusão:** manifesto + relatório de qualidade dos dados.
- **Risco:** acesso ao motor. Começar com motor/gerador pequeno e o rig (S15-T2).
- **Relação com a estratégia:** base de tudo que vem depois e da "previsão" futura.

#### S15-T2 · Rig de falhas controladas (motor DC + MPU6050) e de degradação
- **Objetivo:** gerar falha **física, repetível e segura** em bancada.
- **Contexto:** a avaliação externa propôs o "harness físico": motor DC pequeno, MPU6050 colado, desbalanceamento por massa/fita.
- **Problema atual:** falha só existe em CSV sintético.
- **Estado desejado:** rig com 4 cenários rotulados: (1) **desbalanceamento** com massa crescente; (2) **superaquecimento controlado** (resistor/ventilador bloqueado em ambiente seguro, com corte automático em temperatura limite); (3) **sensor travado/desconectado**; (4) **degradação progressiva** (carga crescente) para validar "tempo até o limite".
- **Dependências · Pré-requisitos:** S8-T2, S8-T11 · motor DC, bateria, massas, relé de corte, sonda.
- **Arquivos prováveis:** `docs/RIG_FALHAS.md`, `data/rig/*.parquet`, `firmware/rig/*`.
- **Implementação esperada:** cada corrida: baseline limpo (≥ 10 min), degraus de falha com **início/fim registrados por marcador** (botão ou comando serial); repetir cada cenário ≥ 5 vezes em dias diferentes; corte automático por temperatura/corrente.
- **Testes necessários:** corte de segurança acionado de propósito; marcadores sincronizados com o relógio do nó.
- **Critério de aceite:** ≥ 5 repetições por cenário com rótulos; mudança de vibração visível nas features (RMS/curtose) entre baseline e falha.
- **Evidência de conclusão:** gráficos + vídeos + manifesto.
- **Risco:** segurança elétrica/térmica. Protocolo e supervisão.
- **Relação com a estratégia:** prova de que o modelo vê falha **física** (e "validado no rig" é a formulação correta).

#### S15-T3 · Especificação única de features (nó, gateway, backend)
- **Objetivo:** as mesmas contas em C++ e Python, com vetores de teste.
- **Contexto:** features de vibração (S8-T2), regime (S5-T3), janelas.
- **Problema atual:** risco de o firmware calcular RMS de um jeito e o Python de outro.
- **Estado desejado:** `ml/features/spec_v1.json` define janela, passo, features (média, desvio, mínimo, máximo, derivada, RMS, pico, **fator de crista**, curtose, energia por bandas via FFT) e `spec_version`; implementações em C++ e Python passam nos **mesmos vetores de teste**.
- **Dependências · Pré-requisitos:** S8-T2 · nenhum.
- **Arquivos prováveis:** `ml/features/spec_v1.json`, `ml/features/features.py`, `firmware/lib/features/*`, `ml/features/golden/*.json`.
- **Implementação esperada:**
```python
def extract(win: np.ndarray, fs: float) -> dict:          # win em unidades do contrato
    x = win - win.mean()
    rms = float(np.sqrt(np.mean(x**2))); pk = float(np.max(np.abs(x)))
    kurt = float(np.mean(x**4) / (np.mean(x**2) ** 2 + 1e-12))
    crest = pk / (rms + 1e-12)
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2; f = np.fft.rfftfreq(len(x), 1/fs)
    bands = {f"E_{lo}_{hi}": float(spec[(f >= lo) & (f < hi)].sum()) for lo, hi in BANDS}
    return {"mean": float(win.mean()), "std": float(win.std()), "rms": rms, "peak": pk, "kurtosis": kurt, "crest": crest, **bands}
```
- **Testes necessários:** vetores dourados (senoide, ruído, impulso) iguais em C++ (teste nativo) e Python dentro de tolerância.
- **Critério de aceite:** paridade nas duas linguagens.
- **Evidência de conclusão:** saída dos testes.
- **Risco:** diferença numérica de ponto flutuante. Tolerância documentada.
- **Relação com a estratégia:** o modelo treinado em Python roda **igual** no gateway e no nó.

#### S15-T4 · Modelo de resíduo (temperatura esperada dado rpm, carga e ambiente)
- **Objetivo:** "5 °C acima do esperado **para esta carga**".
- **Contexto:** temperatura alta sob carga é normal; a mesma em marcha lenta não é. O IF puro não explica isso.
- **Problema atual:** alerta sem comparação com o esperado.
- **Estado desejado:** regressor que prevê `T_esperada = f(rpm, carga/velocidade, T_ambiente, regime, T_anterior)` com **intervalo de predição**; alerta pelo resíduo normalizado; explicação textual pronta.
- **Dependências · Pré-requisitos:** S15-T1, S15-T3 · nenhum.
- **Arquivos prováveis:** `ml/models/residual.py`, `ml/train_residual.py`.
- **Implementação esperada:**
```python
from sklearn.ensemble import HistGradientBoostingRegressor
q50 = HistGradientBoostingRegressor(loss="quantile", quantile=0.5).fit(Xtr, ytr)
q95 = HistGradientBoostingRegressor(loss="quantile", quantile=0.95).fit(Xtr, ytr)
def score(x, t_obs):
    esp, lim = q50.predict([x])[0], q95.predict([x])[0]
    return {"esperada": esp, "limite_p95": lim, "excesso": t_obs - esp, "alerta": t_obs > lim,
            "texto": f"{t_obs-esp:+.1f} °C em relação ao esperado para esta carga"}
# treino SOMENTE com sessões normais; avaliação em sessões não vistas (split por sessão)
```
- **Testes necessários:** em sessões normais não vistas, taxa de falso alarme ≤ meta; no rig de superaquecimento, detecta antes do limiar fixo.
- **Critério de aceite:** tempo até detecção menor que o do limiar fixo **ou** relatório honesto de que não foi.
- **Evidência de conclusão:** gráfico esperado × observado.
- **Risco:** regimes não vistos no treino. Estado `fora_da_distribuicao` ⇒ não alerta como anomalia, alerta como "regime desconhecido".
- **Relação com a estratégia:** explicabilidade que o IF não dá.

#### S15-T5 · Comparação formal de detectores (split temporal por sessão)
- **Objetivo:** escolher por evidência.
- **Contexto:** 5 candidatos: limiar fixo (contrato), EWMA/CUSUM, Isolation Forest por regime, resíduo, autoencoder.
- **Problema atual:** sem comparação em dado real.
- **Estado desejado:** protocolo: treino em sessões A, validação em sessões B, teste em sessões C **nunca vistas** (nunca embaralhar janelas da mesma sessão); métricas fixas; relatório com intervalos de confiança (bootstrap por sessão); **se o limiar fixo vencer, publica que venceu**.
- **Dependências · Pré-requisitos:** S15-T1 a T4, S5-T2 · nenhum.
- **Arquivos prováveis:** `ml/eval/compare.py`, `docs/AVALIACAO_ANOMALIA.md`.
- **Implementação esperada:**
```python
from sklearn.model_selection import GroupKFold
for tr, te in GroupKFold(n_splits=min(5, n_sessoes)).split(X, y, groups=session_id):   # grupos = sessões
    for nome, det in DETECTORES.items():
        det.fit(X[tr][y[tr] == 0])                                                      # treina só com normal
        s = det.score(X[te]); res[nome].append(avaliar(y[te], s, tempo[te]))            # PR-AUC, recall@FPR, TTD
publicar(tabela_com_ic(res))                                                            # inclui limiar fixo como baseline
```
- **Testes necessários:** vazamento de sessão impossível (teste que falha se uma sessão aparecer em treino e teste); reprodutibilidade por semente.
- **Critério de aceite:** relatório com os 5 detectores e decisão D-39 aplicada.
- **Evidência de conclusão:** relatório + `make eval`.
- **Risco:** poucas sessões ⇒ IC largo. Dizer.
- **Relação com a estratégia:** a resposta mais forte ao professor.

#### S15-T6 · Autoencoder (challenger) exportado em ONNX para o gateway
- **Objetivo:** modelo neural **só se ganhar**.
- **Contexto:** a V3 dizia `DEFER` por falta de dado; a campanha cria a base.
- **Problema atual:** sem challenger de aprendizado profundo.
- **Estado desejado:** autoencoder 1D-conv (pequeno) treinado em janelas normais; erro de reconstrução como score; exportado para ONNX; `onnxruntime` no gateway; **medida de latência e memória no hardware real do gateway**; adotado só se bater o campeão no gate.
- **Dependências · Pré-requisitos:** S15-T1, S15-T3, S15-T5 · nenhum.
- **Arquivos prováveis:** `ml/models/autoencoder.py`, `ml/export_onnx.py`.
- **Implementação esperada:** arquitetura mínima (2 a 3 camadas conv, bottleneck pequeno); `torch.onnx.export`; teste de paridade PyTorch × ONNX.
- **Testes necessários:** paridade numérica; latência por janela no gateway (meta: bem abaixo do passo da janela).
- **Critério de aceite:** relatório diz se foi adotado e por quê.
- **Evidência de conclusão:** tabela de latência e métrica.
- **Risco:** custo/benefício ruim. É resultado.
- **Relação com a estratégia:** "tentou-se o mais avançado e mediu".

#### S15-T7 · Incerteza calibrada (conformal / quantis)
- **Objetivo:** confiança do modelo com garantia estatística, não heurística.
- **Contexto:** `confianca` em `Decision` hoje é heurística.
- **Problema atual:** número sem calibração.
- **Estado desejado:** **conformal split** sobre resíduos de validação para limiares com cobertura nominal; reliability plot; a confiança exibida vem da calibração.
- **Dependências · Pré-requisitos:** S15-T4, S15-T5 · nenhum.
- **Arquivos prováveis:** `ml/calibration.py`.
- **Implementação esperada:**
```python
def conformal_threshold(resid_val: np.ndarray, alpha=0.05):
    n = len(resid_val); q = np.ceil((n + 1) * (1 - alpha)) / n
    return np.quantile(np.abs(resid_val), min(q, 1.0), method="higher")        # cobertura ≥ 1-alpha sob trocabilidade
```
Documentar a hipótese de trocabilidade e o que acontece em deriva (S15-T9).
- **Testes necessários:** cobertura empírica em sessões de teste próxima da nominal.
- **Critério de aceite:** reliability plot publicado.
- **Evidência de conclusão:** gráfico.
- **Risco:** cobertura cai com deriva. Monitorar.
- **Relação com a estratégia:** "confiança" com lastro.

#### S15-T8 · Explicabilidade por alerta (SHAP) e UI "por que o alerta"
- **Objetivo:** cada alerta mostra **quais variáveis** o causaram.
- **Contexto:** `contributing_feature` existe de forma simples.
- **Problema atual:** explicação superficial.
- **Estado desejado:** valores SHAP (TreeExplainer para modelos de árvore) por janela; top-3 variáveis com direção e magnitude; guardado em `decision.v1.modelo.explicacao`; UI com barras.
- **Dependências · Pré-requisitos:** S15-T4, S15-T5 · `shap`.
- **Arquivos prováveis:** `ml/explain.py`, `src/components/WhyAlert.tsx`.
- **Implementação esperada:** cálculo no gateway **só sob demanda** (caro), cache por `event_id`.
- **Testes necessários:** soma das contribuições + valor base ≈ score; feature mais influente coerente com o cenário do rig.
- **Critério de aceite:** no rig de desbalanceamento, a feature de vibração lidera a explicação.
- **Evidência de conclusão:** captura + teste.
- **Risco:** latência. Sob demanda.
- **Relação com a estratégia:** confiança do usuário.

#### S15-T9 · MLOps: registro, gates, modo sombra, drift, retreino e rollback
- **Objetivo:** modelo em produção é **gerenciado**, não um arquivo.
- **Contexto:** `model_registry.py` guarda artefato e metadados; falta ciclo de vida.
- **Problema atual:** sem promoção controlada, sem drift, sem rollback.
- **Estado desejado:** `ModelVersion(nome, versao, dataset_hash, feature_spec, metricas, assinatura, estado∈{treinado, sombra, campeao, aposentado})`; **gate** de promoção (precisa vencer o campeão em dados não vistos e não piorar falso alarme); **modo sombra** (roda sem decidir, compara); **drift** (PSI/KS das features); retreino por comando agendável; rollback em 1 comando; sincronização com gateway (S13-T7).
- **Dependências · Pré-requisitos:** S15-T5, S13-T7 · nenhum.
- **Arquivos prováveis:** `ml/registry/*`, `management/commands/{treinar,promover,reverter_modelo}.py`, `services/drift.py`.
- **Implementação esperada:**
```python
def pode_promover(chal, camp, dados_teste):
    m_ch, m_ca = avaliar(chal, dados_teste), avaliar(camp, dados_teste)
    return (m_ch.pr_auc >= m_ca.pr_auc * 1.0 and m_ch.fpr_h <= m_ca.fpr_h and m_ch.ttd <= m_ca.ttd * 1.10)   # regras do gate documentadas (D-39)
def psi(ref, cur, bins=10): ...                         # PSI por feature; > 0.25 = drift forte (limiar a validar)
```
- **Testes necessários:** challenger pior não promove; drift induzido (mudar carga) dispara relatório; rollback restaura o anterior e o gateway segue funcionando.
- **Critério de aceite:** ciclo completo demonstrado (treinar → sombra → promover → reverter).
- **Evidência de conclusão:** log do ciclo.
- **Risco:** gate frouxo. Revisão por pares.
- **Relação com a estratégia:** nível de equipe de produto.

#### S15-T10 · Diagnóstico assistido (hipóteses ranqueadas com evidência)
- **Objetivo:** do "algo estranho" para "as causas mais prováveis e o que checar".
- **Contexto:** a avaliação externa separou **detecção**, **diagnóstico** e **previsão**.
- **Problema atual:** só detecção.
- **Estado desejado:** base de conhecimento (`knowledge/falhas.yml`) com falhas, sintomas, condições, códigos de falha (DTC/SPN) e verificações; motor que combina sintomas, regime, DTC e histórico e devolve **hipóteses com pontuação, evidências a favor/contra e dados faltantes**; **hipótese ≠ fato**; revisada por mecânico.
- **Dependências · Pré-requisitos:** S15-T8, S16-T1 · mecânico.
- **Arquivos prováveis:** `knowledge/falhas.yml`, `services/diagnostico.py`.
- **Implementação esperada:**
```yaml
- id: sensor_temp_travado
  sintomas: [{campo: temperatura, condicao: "valor_repetido >= 30"}]
  contra:   [{campo: rpm, condicao: "variacao > 10%"}]
  verificar: ["conferir conector da sonda", "comparar com sonda redundante (S17-T2)"]
  revisado_por: "mecânico X"      # obrigatório para entrar em produção
```
Pontuação por regras ponderadas (ou rede bayesiana pequena) **declarada como tal**; sempre listar `dados_faltantes`.
- **Testes necessários:** cenários do rig produzem a hipótese correta no topo; ausência de dado reduz confiança e aparece na lista.
- **Critério de aceite:** ≥ 80 % dos cenários do rig com hipótese correta entre as 2 primeiras (meta; medir).
- **Evidência de conclusão:** tabela de acerto.
- **Risco:** falsa certeza. UI sempre diz "hipótese".
- **Relação com a estratégia:** diferencial entre "alarme" e "ajuda".

#### S15-T11 · Aprendizado a partir do feedback e curva de falso alarme
- **Objetivo:** mostrar **num gráfico** que o sistema melhora com o uso.
- **Contexto:** S4-T6 ajusta limiar com feedback do mecânico; S5-T9 define rótulo fraco.
- **Problema atual:** o "aprendizado" não é mensurável.
- **Estado desejado:** métrica semanal `falso_alarme_por_hora` e `% alertas acionáveis`; curva ao longo das rodadas de feedback; quando houver ≥ N rótulos, treina um classificador de **priorização de alerta** (gate D-39) que reordena a fila.
- **Dependências · Pré-requisitos:** S4-T6, S5-T9, S15-T9 · feedback acumulado (sessões do rig e campanha geram os primeiros).
- **Arquivos prováveis:** `services/feedback_metrics.py`, `ml/train_priority.py`, `src/components/FalseAlarmCurve.tsx`.
- **Implementação esperada:** classificador simples (regressão logística/árvore) com validação por sessão; **só reordena**, nunca esconde evento CRÍTICO.
- **Testes necessários:** curva reproduzível; classificador não rebaixa CRÍTICO.
- **Critério de aceite:** gráfico com ≥ 4 rodadas de feedback.
- **Evidência de conclusão:** gráfico no relatório.
- **Risco:** poucos rótulos. Declarar N.
- **Relação com a estratégia:** aprendizado visível.

#### S15-T12 · Copiloto FieldNode (RAG + ferramentas), fora do caminho crítico
- **Objetivo:** perguntar ao sistema em linguagem natural e **agir com segurança**.
- **Contexto:** `ChatFAB.tsx` existe; S5-T8 define 4 ferramentas de leitura.
- **Problema atual:** sem base de conhecimento nem ação controlada.
- **Estado desejado:** RAG sobre **playbooks, manuais cadastrados, histórico de OS e decisões** (recuperação híbrida: BM25 + embeddings locais opcionais, D-40); **ferramentas**: leitura (`maquinas_criticas`, `explicar_decisao`, `saude_maquina`, `eventos_recentes`, `buscar_playbook`) e **propostas** (`propor_os`, `propor_adiamento`) que **exigem aprovação humana**; **toda resposta cita fontes** (id do playbook/decisão); recusa quando não há fonte.
- **Dependências · Pré-requisitos:** S5-T7, S5-T8, S16-T1, S2-T6 · nenhum.
- **Arquivos prováveis:** `copilot/{retriever.py,tools.py,agent.py}`, `api/views_copilot.py`, `ChatFAB.tsx`.
- **Implementação esperada:**
```python
def answer(user, question):
    ctx = retriever.search(question, org=user.org, k=5)                  # BM25 (+ embeddings se disponíveis)
    if not ctx: return Refuse("Não encontrei fonte para isso nos playbooks/histórico.")
    plan = llm.plan(question, ctx, tools=TOOLS_SCHEMA)                   # só ferramentas permitidas pelo papel do usuário
    results = [tools.run(c, user) for c in plan.calls]                   # filtro de organização DENTRO da ferramenta
    reply = llm.write(question, ctx, results)
    assert cites_all_sources(reply, ctx, results)                        # validador (S5-T7)
    return reply
```
Ações que mudam estado **nunca** executam: viram `Proposal` na fila de aprovação.
- **Testes necessários:** pergunta sem fonte ⇒ recusa; pergunta sobre outra organização ⇒ "não encontrada"; texto malicioso em campo de decisão não dispara ferramenta; proposta de OS exige aprovação.
- **Critério de aceite:** conjunto de ≥ 50 perguntas com fonte esperada (S15-T14) passa nas metas.
- **Evidência de conclusão:** relatório de avaliação.
- **Risco:** alucinação. Validador de citações e recusa.
- **Relação com a estratégia:** o chatbot que startup séria faria: fundamentado, com ferramentas e auditável.

#### S15-T13 · LLM local no gateway (explicação e copiloto offline)
- **Objetivo:** copiloto e explicações **sem internet**.
- **Contexto:** o LLM não está no caminho crítico; quando houver hardware, roda local.
- **Problema atual:** só Gemini em nuvem.
- **Estado desejado:** benchmark de modelos pequenos quantizados (runtime tipo `llama.cpp`/Ollama) **no hardware real do gateway**: latência por resposta, memória, qualidade em português (conjunto S15-T14), licença do modelo; escolha (D-41); **fallback em cascata**: local → Gemini (se houver internet) → texto por template.
- **Dependências · Pré-requisitos:** S13-T1, S15-T12 · mini-PC/Raspberry.
- **Arquivos prováveis:** `copilot/llm_local.py`, `docs/LLM_LOCAL.md`.
- **Implementação esperada:** interface `LLM.generate(prompt, max_tokens, timeout)`; circuito de proteção (timeout curto, 1 retry); tabela de benchmark **medida** (não estimada). Verificar licença e disponibilidade do modelo na data da escolha.
- **Testes necessários:** internet cortada ⇒ copiloto responde local; timeout ⇒ fallback para template.
- **Critério de aceite:** resposta local dentro do tempo-alvo definido pelo grupo no hardware escolhido; senão, `desligado_por_hardware` com selo (o produto continua).
- **Evidência de conclusão:** tabela de benchmark.
- **Risco:** hardware fraco. Mini-PC com mais RAM como opção (D-34).
- **Relação com a estratégia:** IA offline de verdade, sem depender de nuvem.

#### S15-T14 · Avaliação do copiloto e red-team
- **Objetivo:** copiloto com número e testado contra abuso.
- **Contexto:** copiloto é superfície nova.
- **Problema atual:** sem conjunto de avaliação.
- **Estado desejado:** ≥ 50 perguntas com fonte esperada e resposta de referência; métricas: **fidelidade** (afirmações apoiadas na fonte), **cobertura de citação**, **taxa de recusa correta**; 30 prompts adversariais (injeção em campo de texto, pedido de outra organização, pedido de executar ação sem aprovação, vazamento de prompt).
- **Dependências · Pré-requisitos:** S15-T12 · nenhum.
- **Arquivos prováveis:** `copilot/eval/*.jsonl`, `docs/AVALIACAO_COPILOTO.md`.
- **Implementação esperada:** avaliação automática por regras (citação presente e válida) + revisão manual de amostra.
- **Testes necessários:** execução em CI nightly.
- **Critério de aceite:** 0 execução de ação não aprovada; 0 vazamento entre organizações; fidelidade acima da meta registrada.
- **Evidência de conclusão:** relatório.
- **Risco:** meta frouxa. Fixar antes de medir.
- **Relação com a estratégia:** copiloto defensável.

#### S15-T15 · **Teste de IA offline** (aceite do pilar P2)
- **Objetivo:** provar que a IA continua funcionando sem internet e degrada bem.
- **Contexto:** exigência explícita da avaliação externa.
- **Problema atual:** nenhum teste dedicado.
- **Estado desejado:** `scripts/ia_offline.py`: (1) WAN cortada; (2) 200 leituras novas entram; (3) inferência local produz score, explicação e prescrição; (4) copiloto responde (local ou template); (5) **modelo removido** ⇒ `modelo_ausente` + fallback; (6) **modelo corrompido** ⇒ `modelo_invalido` + fallback; (7) **janela curta** ⇒ `dados_insuficientes`; (8) reboot ⇒ estado preservado.
- **Dependências · Pré-requisitos:** S13-T7, S15-T9, S15-T12 · nenhum.
- **Arquivos prováveis:** `scripts/ia_offline.py`, `docs/evidence/s15/ia_offline.*`.
- **Implementação esperada:** asserts por etapa; vídeo.
- **Testes necessários:** 3 execuções seguidas.
- **Critério de aceite:** 3/3 verdes.
- **Evidência de conclusão:** vídeo + log.
- **Risco:** baixo.
- **Relação com a estratégia:** fecha o P2 na dimensão offline.

#### S15-T16 · Assinatura acústica (microfone I2S), opcional e medida
- **Objetivo:** mais um sinal físico para rolamento/correia que vibração sozinha pode perder.
- **Contexto:** microfone MEMS I2S (ex.: INMP441) barato; acústica complementa vibração.
- **Problema atual:** só vibração e temperatura.
- **Estado desejado:** features espectrais e de envelope calculadas no nó (janelas curtas), enviadas como features (não áudio bruto: privacidade e banda); avaliada no rig (ruído de atrito adicionado) contra os outros detectores.
- **Dependências · Pré-requisitos:** S15-T3, S15-T5 · microfone.
- **Arquivos prováveis:** `firmware/lib/audio_features/*`, `ml/features/audio.py`.
- **Implementação esperada:** nunca gravar fala: só energia por banda; documentar privacidade.
- **Testes necessários:** ruído de máquina vs ambiente.
- **Critério de aceite:** adotado **só se** melhorar métrica no gate; senão, documentado como "testado e descartado".
- **Evidência de conclusão:** tabela de ablação.
- **Risco:** ruído de ambiente. Medição em campo aberto.
- **Relação com a estratégia:** diferencial opcional com método de adoção claro.


---

### SEMANA 16 · PRESCRIÇÃO PROFISSIONAL (O QUE FAZER, QUEM FAZ, QUANDO, COM O QUÊ E O QUE ACONTECEU)

> **NOTA V5:** Playbooks passam a ter **escada de confirmação** por componente (S19-T7). O otimizador (S16-T6) usa o **PLM** como prazo máximo; o what-if (S16-T7) usa PLM e PR.


**Camadas:** ARCHITECTURE · IMPLEMENTATION · VALIDATION · TESTING
**Pilar:** P1 PRESCRIÇÃO-100

- **Objetivo estratégico:** **prescrição, não predição.** O FieldNode diz *o que fazer*, com procedimento, ferramentas, peças, tempo, segurança, ordem ótima, responsável e verificação depois. É o que transforma o sistema de "alarme com texto" em **instrumento de manutenção**.
- **Objetivo técnico:** biblioteca de playbooks versionada e revisada por mecânico; motor que compõe a prescrição (`prescription.v2`) a partir do achado, da hipótese e do contexto; checklist executável com evidências; estoque; reincidência; **otimizador de janela de manutenção**; cenário "e se adiar?"; cadeia de auditoria à prova de adulteração; teste de aceite do pilar.
- **Por que existe:** a Paola foi explícita: "não é prescrição de verdade, é só predição". A avaliação externa pediu playbooks, checklist, ligação entre recomendação e resultado real. A V3 tinha a **estrutura** (Decision, WorkOrder, desfecho) sem o **conteúdo** (o que o mecânico faz).
- **Problemas que resolve:** texto genérico ("agende inspeção"); ausência de procedimento, peças e tempo; ausência de ordem de execução entre várias pendências; ausência de verificação e de reincidência.
- **Dependências recebidas:** S4 (Decision/OS), S5 (guardrails), S9 (grafo/consequência), S13 (offline), S15 (diagnóstico e explicação).
- **Entregáveis:** `playbooks/*.yml` + validador + revisão, `prescription.v2`, checklist offline com evidências, `Part`/`StockItem`, `Reincidence`, `scheduler/optimizer.py`, `services/whatif.py`, `AuditChain`, `scripts/prescricao_100.py`.
- **Arquivos/módulos afetados:** `services/decisions.py`, `services/workorders.py`, novo `playbooks/`, `services/prescricao_v2.py`, `scheduler/*`, `models.py`, `src/app/decisoes/*`, `src/app/agenda/*`.
- **Arquitetura:** `Achado → Hipótese → Playbook → Adaptação ao contexto → Prescrição → Aprovação → OS → Checklist → Verificação → Reincidência`, tudo no gateway. **Banco:** `Playbook`, `PlaybookVersion`, `ChecklistRun`, `Evidence`, `Part`, `StockItem`, `Reincidence`, `AuditChain`. **Backend:** motor, otimizador, cadeia. **Frontend:** checklist mobile, agenda otimizada, what-if. **Hardware:** câmera do celular para evidência. **ML/IA:** diagnóstico (S15-T10) escolhe playbook. **Infra:** OR-Tools no gateway. **Segurança:** revisão obrigatória do playbook. **Testes:** aceite de ponta a ponta. **Docs:** `PLAYBOOKS.md`.
- **Experimentos:** 10 prescrições do rig e da campanha executadas por pessoa que **não** escreveu o código; medir tempo e erros; comparar agenda manual × otimizada em 5 cenários.
- **Critérios de aceitação:** checklist P1 (seção 0.2) 100 % marcado e `prescricao_100.py` verde **offline e após reboot**.
- **Métricas:** tempo evento → prescrição → aprovação → OS → execução; % de prescrições com playbook revisado; % de checklists concluídos; ganho da agenda otimizada em horas de parada evitadas (**medido em cenário de teste, rotulado como simulação**); taxa de reincidência.
- **Evidências esperadas:** vídeos de execução por terceiros, relatório de comparação de agenda, `playbooks/` revisado.
- **Riscos:** inventar procedimento de reparo (**proibido**: conteúdo escrito por humano e revisado por mecânico; o LLM só reescreve); otimizador "bonito" com premissa falsa (dados de entrada vêm de cadastro real).
- **Decisões:** D-42 (formato de playbook), D-43 (política de revisão e validade do playbook), D-44 (função objetivo do otimizador).
- **Perguntas abertas:** quais peças e tempos são realistas por modelo? (entrevistas S12-T12 e oficina).
- **Definition of Done da fatia:** S16-T9 aprovado em 3 execuções.

#### S16-T1 · Biblioteca de playbooks (esquema, validador, conjunto inicial)
- **Objetivo:** cada achado do sistema aponta para um procedimento escrito por quem faz.
- **Contexto:** sem playbook, a "prescrição" é frase bonita.
- **Problema atual:** textos curtos em `prescricoes.py`/`decisions.py`.
- **Estado desejado:** diretório `playbooks/` com um arquivo por `regra_id`/hipótese, **versionado em Git**, com `revisado_por`, `data_revisao`, `validade` e `status ∈ {rascunho, revisado, vigente, aposentado}`; **só `vigente` entra em produção**.
- **Dependências · Pré-requisitos:** S4-T2 · mecânico para revisão.
- **Arquivos prováveis:** `playbooks/*.yml`, `playbooks/schema.json`, `services/playbooks.py`, `docs/PLAYBOOKS.md`.
- **Implementação esperada:** formato (**exemplo de estrutura; o conteúdo técnico deve ser escrito e revisado por mecânico, não copiado deste documento**):
```yaml
id: TEMP_ALTA_CRITICA
versao: 1
status: rascunho            # só vira "vigente" após revisão assinada
gatilhos: [{evento: TEMP_ALTA, severidade: CRITICO}]
seguranca: ["Desligar o equipamento e aguardar resfriamento antes de tocar em componentes quentes", "EPI conforme norma da usina"]
passos:
  - id: 1
    texto: "Confirmar a leitura em segunda sonda ou instrumento"
    medicao: {campo: temperatura, unidade: C}
    evidencia: [foto, valor]
  - id: 2
    texto: "Inspecionar [itens definidos pelo mecânico revisor]"
    ferramentas: ["[definir]"]
tempo_estimado_min: null     # preencher com valor da oficina
pecas_possiveis: []          # preencher; vira reserva de estoque (S16-T4)
verificacao: {regra: "temperatura <= limiar por 30 min em regime equivalente", janela_min: 30}
escalar_se: ["sintoma persiste após execução", "reincidência em 7 dias"]
fonte: "entrevista S12-T12 #3 + revisão do mecânico"
revisado_por: null
```
Validador: bloqueia `vigente` sem `revisado_por`; bloqueia passo sem evidência exigida; bloqueia peça sem `Part` cadastrada.
- **Testes necessários:** schema; playbook `rascunho` nunca é usado em prescrição de produção (aparece com selo "rascunho, não revisado"); todo `regra_id` do motor tem playbook ou cai em prescrição genérica **rotulada**.
- **Critério de aceite:** ≥ 8 playbooks `vigente` cobrindo: temperatura alta crítica e de atenção, vibração alta, sensor falho/travado, perda de comunicação, tendência de superaquecimento, risco térmico (S17-T1), falha CAN/DTC.
- **Evidência de conclusão:** `PLAYBOOKS.md` + revisões assinadas.
- **Risco:** conteúdo errado. Revisão por mecânico e validade.
- **Relação com a estratégia:** o que transforma recomendação em prescrição.

#### S16-T2 · Motor de prescrição `prescription.v2`
- **Objetivo:** compor a prescrição completa, sem inventar.
- **Contexto:** `decision.v1` (S4-T2) guarda observação e evidência; falta playbook, adaptação e plano.
- **Problema atual:** `acao_recomendada` é um texto.
- **Estado desejado:** `prescription.v2` referencia a `Decision`, escolhe o **playbook** pela regra e pela hipótese diagnóstica (S15-T10), **adapta** ao contexto (horas desde a última manutenção, modelo, histórico de reincidência, regime, peças em estoque) e produz: problema observado, evidências, hipótese (separada), passos, tempo, peças, urgência com justificativa, responsável/prazo sugeridos **só se houver política**, verificação.
- **Dependências · Pré-requisitos:** S16-T1, S15-T10, S5-T10 · nenhum.
- **Arquivos prováveis:** `services/prescricao_v2.py`, `api/views_prescricao.py`.
- **Implementação esperada:**
```python
def compose(decision) -> Prescription:
    hip = diagnostico.rank(decision)[:3]                          # hipóteses com evidência e dados faltantes
    pb = playbooks.select(decision.regra_id, hip)                 # só 'vigente'
    ctx = contexto(decision.machine)                              # horas, histórico, estoque, regime
    passos = adaptar(pb.passos, ctx)                              # remove/ordena passos por contexto, nunca inventa
    return Prescription(observado=decision.detalhes["observado"], evidencias=decision.detalhes["evidencias"],
        hipoteses=hip, playbook=(pb.id, pb.versao), passos=passos, pecas=reservaveis(pb, ctx.estoque),
        urgencia=urgencia(decision, ctx), justificativa=justificar(decision, ctx),
        verificacao=pb.verificacao, rotulo="estimativa" if pb.tempo_estimado_min is None else "")
# LLM (se disponível) apenas reescreve o texto final, validado por S5-T7 (números e ids devem existir)
```
- **Testes necessários:** playbook `rascunho` ⇒ rótulo na prescrição; sem playbook ⇒ prescrição genérica **rotulada**; texto reescrito pelo LLM não altera número, peça ou passo.
- **Critério de aceite:** golden test: cenário do rig produz prescrição idêntica (modo determinístico).
- **Evidência de conclusão:** testes.
- **Risco:** adaptação remover passo de segurança. Passos `seguranca` são intocáveis.
- **Relação com a estratégia:** o coração do pilar.

#### S16-T3 · Checklist executável com evidências (offline)
- **Objetivo:** executar a prescrição com prova do que foi feito.
- **Contexto:** a OS hoje termina em "concluída" sem registro do como.
- **Problema atual:** sem passos, medições, fotos ou assinatura.
- **Estado desejado:** tela mobile por passo: marcar, **medir** (campo com unidade), **foto**, observação, tempo, peça usada, assinatura de quem executou e de quem verificou; tudo salvo **localmente** (IndexedDB) e sincronizado com idempotência; funciona sem rede.
- **Dependências · Pré-requisitos:** S16-T2, S13-T3 · câmera do celular.
- **Arquivos prováveis:** `src/app/os/[id]/checklist/page.tsx`, `ChecklistRun`/`Evidence`, `api/views_checklist.py`.
- **Implementação esperada:** fotos comprimidas no cliente, hash por arquivo, armazenadas no gateway; evidência de medição (valor + unidade + instante); passo com medição fora da faixa exige justificativa.
- **Testes necessários:** E2E offline completo; fechar o app no meio e retomar; foto grande não trava a fila.
- **Critério de aceite:** checklist concluído em celular real sem internet.
- **Evidência de conclusão:** vídeo.
- **Risco:** armazenamento de fotos. Política de retenção (S10-T6).
- **Relação com a estratégia:** a ligação entre recomendação e o que **realmente aconteceu**.

#### S16-T4 · Estoque de peças e disponibilidade
- **Objetivo:** não agendar o que não dá para fazer.
- **Contexto:** playbook lista peças possíveis.
- **Problema atual:** sem cadastro de peças e estoque.
- **Estado desejado:** `Part`, `StockItem(qtd, local)`, reserva ao aprovar a OS, alerta de falta e `SolicitacaoCompra` simples; entrada/saída registradas na execução (S16-T3).
- **Dependências · Pré-requisitos:** S16-T1 · nenhum.
- **Arquivos prováveis:** `models.py`, `services/estoque.py`, tela `src/app/estoque`.
- **Implementação esperada:** importação CSV; sem integração externa de ERP nesta fase.
- **Testes necessários:** reserva atômica; peça faltante muda prazo sugerido e vira solicitação.
- **Critério de aceite:** OS com peça faltante **não** é agendada como pronta.
- **Evidência de conclusão:** testes.
- **Risco:** estoque desatualizado. Contagem periódica (campo `ultima_contagem`).
- **Relação com a estratégia:** prescrição executável.

#### S16-T5 · Verificação pós-reparo, reincidência e escalonamento
- **Objetivo:** saber se **funcionou**.
- **Contexto:** S4-T5 criou a reavaliação; aqui ela usa o critério do playbook.
- **Problema atual:** reavaliação genérica; sem reincidência.
- **Estado desejado:** verificação automática segundo `verificacao` do playbook; **reincidência** (mesmo sintoma na mesma máquina em N dias) abre `Reincidence`, **troca de playbook/escala** (ex.: "peça diferente", "chamar especialista") e eleva prioridade; indicadores por máquina (MTBF-lite: tempo entre decisões do mesmo tipo).
- **Dependências · Pré-requisitos:** S4-T5, S16-T3 · nenhum.
- **Arquivos prováveis:** `services/reevaluation.py`, `services/reincidence.py`.
- **Implementação esperada:** estados `SINTOMA_CESSOU | PERSISTE | DADOS_INSUFICIENTES | REINCIDENTE`; UI separa "resultado informado" de "verificado por telemetria".
- **Testes necessários:** rig: reaplicar desbalanceamento após "conserto" gera reincidência e escalonamento.
- **Critério de aceite:** teste do rig verde.
- **Evidência de conclusão:** teste.
- **Risco:** afirmar eficácia. Rótulos separados.
- **Relação com a estratégia:** ciclo realmente fechado.

#### S16-T6 · Otimizador de janela de manutenção (OR-Tools CP-SAT)
- **Objetivo:** com várias prescrições pendentes, **qual fazer primeiro, quando e com quem**, minimizando risco e parada de colheita.
- **Contexto:** isso é **análise prescritiva** de verdade (otimização), não texto.
- **Problema atual:** agenda manual por ordem de chegada.
- **Estado desejado:** modelo de restrições: duração, mecânicos elegíveis e disponíveis, peças disponíveis, janelas proibidas por máquina (colheita crítica/turno), dependências do grafo (S9: transbordo associado), prazos máximos por urgência; objetivo: minimizar **risco ponderado por atraso** + horas de parada em janela crítica; saída: agenda proposta + **explicação** (por que esta ordem, o que foi sacrificado); humano aprova; roda **local**.
- **Dependências · Pré-requisitos:** S16-T2, S16-T4, S9-T1 · `ortools` (conferir roda em arm64 se o gateway for Raspberry).
- **Arquivos prováveis:** `scheduler/optimizer.py`, `scheduler/explain.py`, `api/views_schedule.py`, `src/app/agenda/otimizada`.
- **Implementação esperada:**
```python
from ortools.sat.python import cp_model
def otimizar(jobs, mecanicos, proibidas, H=7*48):                      # horizonte de 7 dias em fatias de 30 min
    m = cp_model.CpModel(); S, X, mech_iv = {}, {}, {k: [] for k in mecanicos}
    for j in jobs:
        S[j.id] = m.NewIntVar(j.cedo, min(j.tarde, H - j.dur), f"s{j.id}")          # 'tarde' vem da urgência
        for k in j.elegiveis:
            X[j.id, k] = m.NewBoolVar(f"x{j.id}_{k}")
            mech_iv[k].append(m.NewOptionalFixedSizeIntervalVar(S[j.id], j.dur, X[j.id, k], f"iv{j.id}_{k}"))
        m.AddExactlyOne(X[j.id, k] for k in j.elegiveis)
        for (a, b) in proibidas.get(j.machine, []):                                  # janelas de colheita crítica
            m.AddNoOverlap([m.NewFixedSizeIntervalVar(S[j.id], j.dur, "j"), m.NewIntervalVar(a, b - a, b, "p")])
    for k in mecanicos: m.AddNoOverlap(mech_iv[k])
    m.Minimize(sum(j.peso_risco * S[j.id] for j in jobs))                           # D-44: peso vem de severidade × consequência
    solver = cp_model.CpSolver(); solver.parameters.max_time_in_seconds = 5; solver.parameters.num_workers = 4
    status = solver.Solve(m)
    return montar_agenda(solver, S, X, jobs) if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else inviabilidade(jobs)
```
Explicação: para cada tarefa, registrar restrição ativa (peça, mecânico, janela) e comparar com a ordem "por chegada".
- **Testes necessários:** 5 cenários com solução conhecida; inviabilidade vira mensagem útil ("falta peça X", "sem mecânico na janela"); mesma entrada, mesma saída; tempo de solução curto no hardware do gateway.
- **Critério de aceite:** agenda otimizada reduz o **custo da função objetivo** nos 5 cenários **ou** relatório honesto de que não reduziu.
- **Evidência de conclusão:** relatório de comparação (rotulado como cenário de teste).
- **Risco:** premissas inventadas. Dados de entrada vêm de cadastro (S16-T4, S9, agenda real).
- **Relação com a estratégia:** diferencial de prescrição que um dashboard não tem.

#### S16-T7 · "E se eu adiar?" (cenários com incerteza, rotulados como estimativa)
- **Objetivo:** apoiar a decisão de **quando** agir.
- **Contexto:** consequência (S9-T3) e incerteza (S15-T7) já existem.
- **Problema atual:** só "agir agora".
- **Estado desejado:** três cenários (agora, +4 h, +24 h) com: probabilidade estimada de cruzar o limite antes da ação, tempo até o limite com intervalo, consequência no grafo; **recusa** quando o ajuste de tendência é fraco ("sem estimativa confiável").
- **Dependências · Pré-requisitos:** S9-T3, S15-T7 · nenhum.
- **Arquivos prováveis:** `services/whatif.py`, `src/components/WhatIf.tsx`.
- **Implementação esperada:**
```python
def p_cruzar(serie, limite, horizonte_h, n=2000, rng=np.random.default_rng(0)):
    a, b, resid, r2 = ajuste_linear(serie)                       # tendência local
    if r2 < R2_MIN or len(serie) < N_MIN: return None            # sem estimativa confiável
    cruz = 0
    for _ in range(n):
        slope = b + rng.choice(resid_slope_bootstrap(serie), 1)[0]   # bootstrap da inclinação
        t = (limite - serie[-1]) / max(slope, 1e-9) if slope > 0 else np.inf
        cruz += (t <= horizonte_h)
    return cruz / n
```
Texto fixo: "estimativa por extrapolação de tendência; não é garantia".
- **Testes necessários:** série com tendência conhecida ⇒ probabilidade coerente; série ruidosa ⇒ `None`.
- **Critério de aceite:** testes verdes; UI mostra "sem estimativa" quando aplicável.
- **Evidência de conclusão:** captura.
- **Risco:** passar falsa precisão. Rótulo e recusa.
- **Relação com a estratégia:** prescrição com horizonte, honesta.

#### S16-T8 · Cadeia de auditoria à prova de adulteração
- **Objetivo:** **provar** que nenhuma decisão ou OS foi alterada depois.
- **Contexto:** Decision Memory é o ativo central; integridade importa.
- **Problema atual:** `AuditLog` é append-only por convenção, não verificável.
- **Estado desejado:** cada fato (decisão, aprovação, OS, passo concluído, evidência) entra em `AuditChain` com `hash = SHA256(hash_anterior + JSON canônico)`; comando `verificar_cadeia` e endpoint de prova; âncora periódica (hash exportado/replicado entre gateway e nuvem).
- **Dependências · Pré-requisitos:** S2-T7, S13-T4 · nenhum.
- **Arquivos prováveis:** `models.py` (`AuditChain`), `services/chain.py`.
- **Implementação esperada:**
```python
def append(entity, entity_id, payload: dict, hlc):
    prev = AuditChain.objects.select_for_update().order_by("-seq").first()
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    h = hashlib.sha256((prev.hash if prev else "GENESIS").encode() + body).hexdigest()
    return AuditChain.objects.create(seq=(prev.seq + 1 if prev else 1), entity=entity, entity_id=entity_id,
                                     payload_hash=hashlib.sha256(body).hexdigest(), prev_hash=(prev.hash if prev else "GENESIS"), hash=h, hlc=hlc)
```
- **Testes necessários:** alterar um registro (SQL direto) ⇒ `verificar_cadeia` aponta o primeiro elo quebrado; réplica na nuvem confere a âncora.
- **Critério de aceite:** adulteração detectada em 100 % dos casos testados.
- **Evidência de conclusão:** teste + demonstração.
- **Risco:** concorrência na escrita. `select_for_update` e fila serial por nó.
- **Relação com a estratégia:** "decisão rastreável" com prova matemática, diferencial raro.

#### S16-T9 · Aceite do pilar P1: ciclo de prescrição de ponta a ponta (offline, após reboot)
- **Objetivo:** provar PRESCRIÇÃO-100.
- **Contexto:** critério exigido: leitura real → evento → prescrição fundamentada → aprovação → OS executada → resultado registrado, sem internet e após reboot.
- **Problema atual:** nenhum teste único cobre o ciclo.
- **Estado desejado:** `scripts/prescricao_100.py` com asserts e roteiro gravado, executado por **pessoa que não escreveu o código**.
- **Dependências · Pré-requisitos:** S16-T1 a T8, S13-T8 · nenhum.
- **Arquivos prováveis:** `scripts/prescricao_100.py`, `docs/evidence/s16/*`.
- **Implementação esperada:** (1) leitura real aquecida; (2) evento; (3) prescrição com playbook `vigente`, evidências, hipótese, passos, peças reservadas; (4) otimizador propõe janela; (5) supervisor aprova pelo celular via hotspot; (6) mecânico executa checklist com foto e medição; (7) verificação automática; (8) reboot do gateway no passo 6; (9) cadeia de auditoria verificada; (10) replicação para a nuvem sem duplicata.
- **Testes necessários:** 3 execuções, uma com reboot e uma com troca de usuário.
- **Critério de aceite:** 3/3 verdes e vídeo contínuo.
- **Evidência de conclusão:** vídeo + log + relatório de métricas.
- **Risco:** passo depender de dado de cadastro faltante. Seed documentado.
- **Relação com a estratégia:** fecha o P1.

#### S16-T10 · Revisão e ciclo de vida dos playbooks com mecânico
- **Objetivo:** conteúdo confiável e mantido.
- **Contexto:** playbook é conteúdo técnico; precisa de dono.
- **Problema atual:** nenhuma política de revisão.
- **Estado desejado:** fluxo `rascunho → revisão (mecânico) → vigente → reavaliação periódica → aposentado`; histórico de versões; feedback do executor ("passo confuso", "peça diferente") volta como sugestão; métricas por playbook (tempo real × estimado, reincidência).
- **Dependências · Pré-requisitos:** S16-T1, S12-T12 · mecânico parceiro.
- **Arquivos prováveis:** `docs/PLAYBOOKS.md`, `services/playbooks.py`.
- **Implementação esperada:** `validade` obrigatória (ex.: 12 meses), alerta de vencimento.
- **Testes necessários:** playbook vencido volta a `rascunho` com selo.
- **Critério de aceite:** ≥ 8 playbooks com revisão registrada.
- **Evidência de conclusão:** histórico de revisão.
- **Risco:** mecânico indisponível. Registrar e manter selo "não revisado".
- **Relação com a estratégia:** sustentabilidade do conteúdo.

---

### SEMANA 17 · DIFERENCIAIS EXTRAS DE PRODUTO

> **NOTA V5:** S17-T5 a T11 passam a **P3**. S17-T1 (risco térmico) e S17-T2 (redundância de sensor) permanecem. S17-T10 permanece, e o relatório do investidor (S21-T2) o complementa.


**Camadas:** IMPLEMENTATION · VALIDATION · SECURITY · DOCUMENTATION
**Pilar:** extras que tornam o projeto **diferente** do de qualquer outro grupo

- **Objetivo estratégico:** o FieldNode não pode "parecer igual ao de todo mundo". Cada item aqui é **demonstrável**, ligado ao problema real (as palestras) e **medido**.
- **Objetivo técnico:** risco térmico de incêndio (rolamento/esteira), redundância e verificação cruzada de sensor, OTA assinada, kit instalável com provisionamento por QR, modo cabine, relatório de turno offline, trilha GPS e cerca virtual offline, benchmark entre máquinas, painel executivo, modo replay.
- **Por que existe:** a palestra da Case citou sensor térmico perto da esteira para reduzir **incêndios por superaquecimento de rolamento**; a Paola quer diferenciais além do básico; a avaliação externa recomendou provas físicas e produto instalável.
- **Problemas que resolve:** ausência de módulo de incêndio, sensor único (sem verificação), firmware sem atualização segura, instalação artesanal, interface de escritório em cabine, relatório que a proposta prometia e não existe offline.
- **Dependências recebidas:** S8 (sensores), S13 (gateway), S15/S16 (modelos e playbooks).
- **Entregáveis:** módulo térmico, verificação cruzada, OTA, kit e guia, modo cabine, relatório de turno, geofence, benchmark, painel executivo, modo replay.
- **Arquivos/módulos afetados:** `firmware/lib/thermal/*`, `firmware/lib/ota/*`, `services/fire_risk.py`, `services/benchmark.py`, `src/app/cabine/*`, `src/app/executivo/*`.
- **Arquitetura:** módulos plugáveis sobre o contrato e o gateway. **Banco:** `FireRiskIndex`, `Geofence`, `ReportRun`, `ReplaySession`. **Backend:** serviços. **Frontend:** telas. **Hardware:** termopares, caixa, QR. **ML/IA:** resíduo e comparação entre pares. **Infra:** OTA via gateway. **Segurança:** imagens assinadas. **Testes:** rig térmico. **Docs:** guia de instalação.
- **Experimentos:** aquecimento controlado com rampa conhecida; atualização OTA com queda de energia no meio; instalação por pessoa de fora com cronômetro.
- **Critérios de aceitação:** cada tarefa tem demo curta e métrica.
- **Métricas:** tempo até alarme térmico; falso alarme térmico por hora; taxa de sucesso de OTA; tempo de instalação por pessoa de fora.
- **Evidências esperadas:** vídeos curtos por item.
- **Riscos:** escopo. Ordem de corte na seção 0.6 (S17-T1/T2 permanecem).
- **Decisões:** D-45 (índice de risco térmico), D-46 (OTA: assinatura e rollout).
- **Perguntas abertas:** quantos pontos térmicos por máquina são realistas? (entrevistas e piloto).
- **Definition of Done da fatia:** demos gravadas dos itens executados.

#### S17-T1 · Módulo de risco térmico de incêndio (multi-ponto, dT/dt)
- **Objetivo:** avisar **antes** do rolamento/esteira virar fogo, no próprio nó.
- **Contexto:** palestra da Case: sensor térmico na esteira para reduzir incêndios por desgaste e superaquecimento.
- **Problema atual:** temperatura única e limiar fixo; sem taxa de subida nem comparação entre pontos.
- **Estado desejado:** 2 a 4 termopares tipo K (MAX31855) em pontos de interesse; **Índice de Risco Térmico** = função de temperatura absoluta, **taxa de subida (dT/dt)** e **diferença entre pontos** em relação ao baseline por regime; alarme local imediato; prescrição "parar e inspecionar" (playbook).
- **Dependências · Pré-requisitos:** S8-T13, S15-T4, S16-T1 · termopares e MAX31855.
- **Arquivos prováveis:** `firmware/lib/thermal/*`, `services/fire_risk.py`, `playbooks/RISCO_TERMICO.yml`.
- **Implementação esperada:**
```cpp
struct ThermalPoint { float t, prev_t, t_baseline; uint32_t prev_ms; };
float rate_c_per_min(float t, float prev, uint32_t dt_ms) { return (t - prev) * 60000.0f / dt_ms; }
// risco local: absoluta acima do limite OU taxa sustentada acima do limite OU delta entre pontos acima do limite; limites do contrato (versão) e calibrados no rig
bool fire_risk(const ThermalPoint& a, const ThermalPoint& b, const Limits& L) {
  return (a.t >= L.abs_crit) || (rate_c_per_min(a.t, a.prev_t, a.dt) >= L.rate_crit) || (fabsf(a.t - b.t) >= L.delta_crit);
}
```
**Aviso explícito na UI e no manual:** é **indicador de risco**, **não** substitui extintor nem sistema de supressão.
- **Testes necessários:** rig com aquecimento em rampa conhecida: alarme antes do limiar absoluto quando a taxa for alta; ruído de leitura não dispara (filtro).
- **Critério de aceite:** tempo até alarme medido; falso alarme medido em 2 h de operação normal.
- **Evidência de conclusão:** vídeo + gráfico.
- **Risco:** acidente durante teste. Protocolo e supervisão (S15-T2).
- **Relação com a estratégia:** ligação direta com o problema da palestra.

#### S17-T2 · Redundância e verificação cruzada de sensor
- **Objetivo:** distinguir "máquina quente" de "sensor mentindo" com **evidência física**.
- **Contexto:** Trust Score hoje é heurístico; com dois sensores ele fica verificável.
- **Problema atual:** sensor único.
- **Estado desejado:** DS18B20 e termopar medindo o mesmo ponto/ponto próximo; divergência acima da tolerância ⇒ `sensor_suspeito` com qual lado discordou do modelo de resíduo; **deriva** de sensor detectada por diferença sistemática ao longo de dias; entra em `evidence_quality`.
- **Dependências · Pré-requisitos:** S8-T1, S17-T1, S1-T3 · segundo sensor.
- **Arquivos prováveis:** `services/data_health.py`, `firmware/lib/sensor_check/*`.
- **Implementação esperada:** `delta = |T_a - T_b|`; tolerância por par documentada (diferença de tempo de resposta entre sondas conta); média móvel do delta para deriva.
- **Testes necessários:** desconectar uma sonda ⇒ `sensor_falho`; deriva induzida ⇒ alerta de calibração.
- **Critério de aceite:** testes verdes e demo.
- **Evidência de conclusão:** gráfico.
- **Risco:** pontos de medição diferentes geram delta legítimo. Calibrar par a par.
- **Relação com a estratégia:** confiança operacional com base física.

#### S17-T3 · OTA assinada com rollback
- **Objetivo:** atualizar firmware em campo sem cabo e sem risco de "tijolo".
- **Contexto:** firmware versionado (S8-T1).
- **Problema atual:** só atualização por USB.
- **Estado desejado:** partições OTA A/B; imagem **assinada**, verificada antes de ativar; atualização distribuída pelo gateway (HTTPS local); rollback automático se o novo firmware não se confirmar; versão reportada na telemetria; **rollout escalonado** (1 dispositivo primeiro).
- **Dependências · Pré-requisitos:** S8-T8, S13-T12, S2-T8 · ESP32 com partição OTA.
- **Arquivos prováveis:** `firmware/lib/ota/*`, `firmware/partitions.csv`, `scripts/sign_firmware.py`, `api/views_firmware.py`.
- **Implementação esperada:** `esp_https_ota` com verificação de assinatura; `esp_ota_mark_app_valid_cancel_rollback()` só após autoteste (sensor, Wi-Fi, MQTT); se não confirmar em N minutos, volta à versão anterior.
- **Testes necessários:** queda de energia no meio da atualização; imagem com assinatura inválida é recusada; firmware que trava no boot volta sozinho.
- **Critério de aceite:** 10 atualizações com falhas induzidas sem perder dispositivo.
- **Evidência de conclusão:** log.
- **Risco:** secure boot/flash encryption irreversíveis. Aplicar só em placa dedicada (S8-T8).
- **Relação com a estratégia:** maturidade de produto.

#### S17-T4 · Kit instalável e guia de instalação (instalação por pessoa de fora)
- **Objetivo:** instalar sem o autor do código.
- **Contexto:** a avaliação externa pede procedimento repetível.
- **Problema atual:** montagem artesanal.
- **Estado desejado:** caixa, fixação (magnética ou abraçadeira), conectores, etiqueta com QR, guia ilustrado, checklist de comissionamento, instalação do certificado do gateway no celular (S13-T12), teste de recebimento do kit.
- **Dependências · Pré-requisitos:** S17-T5, S8-T10 · caixa e peças.
- **Arquivos prováveis:** `docs/GUIA_INSTALACAO.md`, `docs/COMISSIONAMENTO.md`, `hardware/caixa/*`.
- **Implementação esperada:** cronometrar instalação por pessoa de fora; corrigir o guia até caber na meta (a definir pelo grupo).
- **Testes necessários:** 3 instalações por 3 pessoas diferentes.
- **Critério de aceite:** instalação concluída sem ajuda em tempo-alvo.
- **Evidência de conclusão:** vídeo.
- **Risco:** proteção contra poeira/água. Registrar o **grau de proteção real testado**, não o desejado.
- **Relação com a estratégia:** do protótipo ao produto.

#### S17-T5 · Provisionamento por QR (PWA/BLE) em 10 minutos
- **Objetivo:** registrar dispositivo no campo sem notebook.
- **Contexto:** `scripts/provision_device.py` (S2-T1) é linha de comando.
- **Problema atual:** exige terminal.
- **Estado desejado:** QR na etiqueta (`device_id`, `chave_inicial` de uso único, endpoint do gateway); PWA lê o QR (câmera), conecta por BLE, grava Wi-Fi do hotspot e credencial; dispositivo aparece no painel; chave de uso único é trocada por chave definitiva.
- **Dependências · Pré-requisitos:** S2-T8, S14-T6, S13-T12 · nenhum.
- **Arquivos prováveis:** `src/app/provisionar/page.tsx`, `firmware/lib/provision_ble/*`, `api/views_provision.py`.
- **Implementação esperada:** QR contém token de uso único com expiração; gateway confirma e emite credencial definitiva.
- **Testes necessários:** QR reutilizado é recusado; token expirado é recusado.
- **Critério de aceite:** dispositivo novo operando em menos de 10 minutos por pessoa de fora.
- **Evidência de conclusão:** vídeo.
- **Risco:** QR fotografado por terceiro. Uso único e expiração curta.
- **Relação com a estratégia:** onboarding simples (`CLAUDE.md`).

#### S17-T6 · Modo cabine (operador/supervisor em movimento)
- **Objetivo:** interface para quem está no veículo, com luva e poeira.
- **Contexto:** o painel é de escritório.
- **Problema atual:** botões pequenos, muita informação.
- **Estado desejado:** tela única com estado da máquina (grande), alerta sonoro/vibração, **aprovar/adiar** em um toque, cores de alto contraste, texto curto vindo da prescrição curta, funciona offline.
- **Dependências · Pré-requisitos:** S3-T3, S13-T3 · nenhum.
- **Arquivos prováveis:** `src/app/cabine/page.tsx`.
- **Implementação esperada:** alvos de toque grandes; dispositivo com tela sempre ligada (Wake Lock quando disponível).
- **Testes necessários:** teste de usabilidade com 3 pessoas: achar e agir em um alerta sem explicação.
- **Critério de aceite:** 3/3 concluem a ação sem ajuda.
- **Evidência de conclusão:** vídeo.
- **Risco:** distração ao dirigir. Interação só com veículo parado (aviso).
- **Relação com a estratégia:** produto de campo, não de escritório.

#### S17-T7 · Relatório de turno/sessão **offline**
- **Objetivo:** cumprir a promessa da proposta ("relatório automático com horários de pico, duração em risco e recomendação").
- **Contexto:** `views_relatorio.py` e `services/relatorios.py` existem; falta geração local e conteúdo de decisão.
- **Problema atual:** relatório depende da nuvem e não inclui prescrição/OS.
- **Estado desejado:** geração no gateway: período, máquinas, picos, tempo em risco, eventos, decisões, OS e resultado, qualidade dos dados, enlaces usados; exportação PDF/HTML/CSV; marca "SIMULADO/medido".
- **Dependências · Pré-requisitos:** S16-T9, S14-T11 · nenhum.
- **Arquivos prováveis:** `services/relatorios.py`, `api/views_relatorio.py`.
- **Implementação esperada:** gerar sem internet (sem fontes remotas); assinar o relatório com hash da cadeia (S16-T8).
- **Testes necessários:** relatório idêntico antes/depois do reboot.
- **Critério de aceite:** relatório gerado offline com todos os campos.
- **Evidência de conclusão:** arquivo de exemplo.
- **Risco:** baixo.
- **Relação com a estratégia:** entrega prometida.

#### S17-T8 · Trilha GPS e cerca virtual (geofence) offline
- **Objetivo:** alertas por posição sem internet.
- **Contexto:** GPS entra em S8-T11; mapa offline em S13-T3.
- **Problema atual:** posição só exibida.
- **Estado desejado:** trilha armazenada; **cerca virtual** (talhão, base, zona de risco) com evento `ENTROU/SAIU`; alerta de máquina parada fora de área de manutenção; tudo local.
- **Dependências · Pré-requisitos:** S8-T11, S13-T3 · nenhum.
- **Arquivos prováveis:** `services/geofence.py`, `models.py`.
- **Implementação esperada:** teste ponto-em-polígono com histerese para evitar oscilação na borda.
- **Testes necessários:** trilha sintética cruzando a borda gera 1 evento, não vários.
- **Critério de aceite:** teste verde.
- **Evidência de conclusão:** teste + captura.
- **Risco:** erro de GPS. Considerar `hdop`.
- **Relação com a estratégia:** utilidade operacional sem nuvem.

#### S17-T9 · Benchmark entre máquinas do mesmo modelo
- **Objetivo:** "esta máquina está 8 °C mais quente que as outras do mesmo modelo na mesma carga".
- **Contexto:** baseline de grupo (S5-T4) já é prevista.
- **Problema atual:** só comparação consigo mesma.
- **Estado desejado:** distribuição por modelo/regime; posição da máquina (percentil) e desvio; destaque de outliers; limitação: exige ≥ 3 máquinas comparáveis.
- **Dependências · Pré-requisitos:** S15-T4, S11-T1 (capabilities) · frota com mais de uma máquina (rig + campanha simulam grupo).
- **Arquivos prováveis:** `services/benchmark.py`, `src/components/PeerCompare.tsx`.
- **Implementação esperada:** estatística robusta (mediana e MAD), nunca média simples.
- **Testes necessários:** outlier injetado aparece; grupo com menos de 3 mostra "sem base de comparação".
- **Critério de aceite:** testes verdes.
- **Evidência de conclusão:** captura.
- **Risco:** comparar máquinas com cargas diferentes. Comparar **por regime**.
- **Relação com a estratégia:** contexto que dashboard simples não dá.

#### S17-T10 · Painel executivo com métricas **medidas**
- **Objetivo:** a usina enxerga o resultado, não o gráfico.
- **Contexto:** Decision Memory permite KPIs reais.
- **Problema atual:** KPIs inventados nos documentos.
- **Estado desejado:** MTTA (tempo até reconhecer), MTTR (até concluir), % alertas acionáveis, falso alarme/hora, % OS com verificação positiva, disponibilidade do enlace por máquina; todos calculados do banco, com fórmula visível e selo de amostra pequena quando N < limite.
- **Dependências · Pré-requisitos:** S16-T5, S14-T11 · dados acumulados.
- **Arquivos prováveis:** `services/kpis.py`, `src/app/executivo/page.tsx`.
- **Implementação esperada:** nenhuma meta inventada; só o que foi medido.
- **Testes necessários:** KPI recalculado de dataset de teste bate com valor manual.
- **Critério de aceite:** 6 KPIs corretos em teste.
- **Evidência de conclusão:** captura.
- **Risco:** KPI com N pequeno enganar. Selo.
- **Relação com a estratégia:** valor para o comprador.

#### S17-T11 · Modo replay de sessão (estande e banca)
- **Objetivo:** reproduzir uma sessão **real gravada** quando o hardware ao vivo falhar.
- **Contexto:** feira de negócios e plano B da banca.
- **Problema atual:** só vídeo.
- **Estado desejado:** reproduz leituras gravadas (campanha/soak) na velocidade escolhida pela pilha real, **com selo "REPLAY"** visível, sem tocar no banco de produção (perfil `demo`).
- **Dependências · Pré-requisitos:** S15-T1, S13-T1 · sessões gravadas.
- **Arquivos prováveis:** `scripts/replay_session.py`, `ReplaySession`.
- **Implementação esperada:** replay injeta no mesmo caminho de ingestão (`registrar_leitura`) em banco isolado.
- **Testes necessários:** replay produz os mesmos eventos/decisões da sessão original.
- **Critério de aceite:** equivalência em teste.
- **Evidência de conclusão:** teste.
- **Risco:** confundir replay com ao vivo. Selo permanente e logs.
- **Relação com a estratégia:** plano B honesto.


---

### SEMANA 18 · FOCO DIESEL: SISTEMA DE COMBUSTÍVEL DE ALTA PRESSÃO A FUNDO

**Camadas:** FOUNDATION · ARCHITECTURE · IMPLEMENTATION · VALIDATION · TESTING
**Pilar:** P4 DIESEL-100

- **Objetivo estratégico:** deixar de condenar uma máquina inteira com 3 medidas e passar a **analisar a fundo uma parte** (o **sistema de combustível diesel de alta pressão**, onde mora a **bomba de alta**), usando **muitos sinais do próprio motor** e **códigos de falha**, com **padrão de normalidade por sinal** e **dado irreal descartado**. É o diferencial que o analista pediu.
- **Objetivo técnico:** escolher e acessar um motor diesel com ECU; descobrir quais sinais o motor **realmente publica**; modelar componentes e sinais; ingerir ≥ 10 canais com qualidade; construir perfil de normalidade por sinal e regime; classificar e **desclassificar** dado; decodificar e correlacionar DTC; calcular **indicadores de saúde** por componente; obter rótulos reais de oficina; coletar campanha no motor; testar falhas **reversíveis e supervisionadas**; fechar com `diesel_100`.
- **Por que existe:** feedback do analista: "o dashboard usa apenas três medidas para condenar uma máquina inteira; maquinário pode ter cerca de 10 módulos com informações contínuas e código de erro; foque em uma parte, analise a fundo cada sensor, tendências e padrões de normalidade; padrões irreais são facilmente identificados e desclassificados".
- **Problemas que resolve:** diagnóstico raso; ausência de DTC como evidência; média contaminada por dado ruim; falta de contexto por regime.
- **Dependências recebidas:** S1 (contrato), S8-T12 (escuta CAN), S13 (gateway), S15-T3 (features), S16-T1 (playbooks).
- **Entregáveis:** `docs/MOTOR_E_ACESSO.md`, `docs/CATALOGO_SINAIS_MOTOR.md`, modelos `Component`/`Signal`/`ComponentSignal`, contrato `telemetry.v2`, `NormalityProfile`, `SignalQuality`, `DtcEvent`, `HealthIndicator`, dataset da campanha e do banco de provas, `scripts/diesel_100.py`.
- **Arquivos/módulos afetados:** `api_tcc/models.py`, `contracts/telemetry.v2.json`, `services/{signals,normality,quality,dtc,health_indicators}.py`, `firmware/lib/can_listen/*`, `ml/features/*`, `docs/*`.
- **Arquitetura:** `barramento do motor (J1939/OBD, só escuta) → nó → gateway → catálogo de sinais → qualidade → perfil de normalidade → indicadores de saúde → evidência (S19)`. **Banco:** `Component`, `Signal`, `ComponentSignal`, `NormalityProfile`, `SignalQuality`, `DtcEvent`, `HealthIndicator`, `SessionManifest`. **Backend:** serviços acima. **Frontend:** painel do componente (S20-T5). **Hardware:** transceptor CAN, sensores não invasivos. **ML/IA:** perfis e indicadores alimentam S19. **Infra:** armazenamento de séries multicanal. **Segurança:** só escuta; nenhum acesso à linha de alta pressão. **Testes:** golden de decodificação, desclassificação, perfis. **Docs:** catálogo e protocolo.
- **Experimentos:** (a) 30 min de escuta passiva para inventariar PGN/SPN; (b) degraus de carga controlados (gerador com banco de carga) para construir perfis por regime; (c) comparação de indicadores entre bomba boa e bomba reprovada na oficina; (d) injeção de dado irreal para testar a desclassificação.
- **Critérios de aceitação:** ≥ 8 sinais do subsistema de combustível com unidade, qualidade e perfil; ≥ 5 indicadores de saúde calculados; DTC decodificado e ligado a componente; 100 % do dado irreal injetado desclassificado no teste.
- **Métricas:** nº de sinais publicados/usados; % de amostras por classe de qualidade; cobertura de regime nos perfis; taxa de decodificação de DTC; separação entre bomba boa e reprovada nos indicadores.
- **Evidências esperadas:** catálogo de sinais, gráficos de perfil, relatório de qualidade, vídeo do `diesel_100`.
- **Riscos:** motor não publica o sinal desejado; acesso ao motor atrasar; dado de oficina escasso. Mitigação em 0-A.8.
- **Decisões:** D-47 (subsistema-âncora), D-57 (qual motor/acesso), D-58 (falhas reversíveis permitidas), D-59 (sensores só em baixa pressão).
- **Perguntas abertas:** o motor disponível publica pressão do trilho? (S18-T2 responde na semana 2).
- **Definition of Done da fatia:** checklist P4 (seção 0-A.4) 100 % marcado e `diesel_100.py` verde 3×.

#### S18-T1 · Escolha do motor diesel e do acesso (gate da semana 1 a 2)
- **Objetivo:** ter **um motor diesel com ECU** acessível, com autorização, e saber o que se pode (e não se pode) fazer nele.
- **Contexto:** o foco profundo só é real se os sinais vierem de um motor de verdade.
- **Problema atual:** nenhum motor definido; hardware de bancada usa motor DC de brinquedo.
- **Estado desejado:** decisão registrada com critérios e plano B.
- **Dependências · Pré-requisitos:** nenhuma · contatos (oficina, usina, professor, família/conhecidos com gerador ou trator).
- **Arquivos prováveis:** `docs/MOTOR_E_ACESSO.md`.
- **Implementação esperada:** matriz de opções:

| Opção | Vantagem | Risco | Observação |
|---|---|---|---|
| **Gerador diesel com banco de carga resistivo** | permite **degraus de carga controlados** (perfil por regime) | motor pode ser antigo/sem ECU eletrônica | verificar se tem ECU e conector de diagnóstico |
| Trator/colhedora de parceiro | mais próximo do cliente final | autorização formal; disponibilidade | só escuta passiva |
| Caminhão/veículo diesel de oficina | ECU moderna, conector padrão | disponibilidade | só escuta; com autorização |
| Banco de provas de oficina (bomba isolada) | rótulos de estado do componente | sem motor completo | combina com S18-T9 |
| Emulador de ECU em bancada | disponível sempre | **é simulação** | rotulado SIMULADO; só para desenvolvimento |

Critérios de escolha: ECU com barramento acessível; sinais do subsistema de combustível publicados; possibilidade de variar carga; autorização por escrito; segurança do local. **Plano B:** oficina de injeção + gerador/veículo disponível; tudo que for simulado leva selo.
- **Testes necessários:** nenhum (decisão); validação posterior em S18-T2.
- **Critério de aceite:** motor (ou combinação) definido, autorização por escrito e data da primeira escuta.
- **Evidência de conclusão:** `MOTOR_E_ACESSO.md` assinado.
- **Risco:** não conseguir motor. Plano B ativado sem declarar P4 fechado.
- **Relação com a estratégia:** é o novo caminho crítico.

#### S18-T2 · Descoberta de sinais publicados (escuta passiva) e catálogo do motor
- **Objetivo:** descobrir **o que o motor realmente publica**, em vez de assumir.
- **Contexto:** J1939 tem milhares de parâmetros possíveis; cada motor publica um subconjunto. Em OBD-II, os PIDs suportados são descobertos por bitmap.
- **Problema atual:** o decodificador cita `rpm`, `coolant_temp`, `oil_pressure`, nada do combustível.
- **Estado desejado:** inventário `PGN/SPN → taxa → unidade → faixa observada`, e conjunto mínimo de ≥ 8 sinais do subsistema de combustível (ou o máximo que o motor permitir).
- **Dependências · Pré-requisitos:** S8-T12, S18-T1 · nó CAN em modo **só escuta**.
- **Arquivos prováveis:** `scripts/inventario_can.py`, `docs/CATALOGO_SINAIS_MOTOR.md`, `adapters/j1939_pgn_table.json`.
- **Implementação esperada:** gravar 30 min em marcha lenta e 30 min com carga; contar quadros por ID; decodificar com a tabela pública; produzir o catálogo. **Sinais candidatos a procurar (conferir cada SPN/PID na tabela pública e no que o motor publicar; nada aqui está garantido):** rotação do motor (SPN 190), carga percentual (SPN 92), posição do acelerador (SPN 91), **pressão do trilho de injeção (SPN 157)**, pressão de entrega de combustível/baixa pressão (SPN 94), temperatura do combustível (SPN 174), consumo de combustível (SPN 183), ΔP do filtro de combustível (SPN 95), água no combustível (SPN 97), pressão de óleo (SPN 100), temperatura do líquido de arrefecimento (SPN 110), pressão de turbo (SPN 102), temperatura do coletor (SPN 105), horas totais do motor (SPN 247), mais **DM1/DM2** (falhas ativas e anteriores). Em OBD-II (veículo leve): descobrir PIDs suportados (bitmaps 00/20/40) e procurar, por exemplo, rotação, carga, temperatura do líquido, **pressão do trilho**, taxa de combustível, modo 03/07/0A para DTC e freeze frame (modo 02).
```python
def inventario(frames):                       # frames: (t, can_id, data)
    por_pgn = defaultdict(lambda: {"n": 0, "t0": None, "t1": None, "ex": None})
    for t, cid, d in frames:
        pgn = pgn_from_id(cid)
        r = por_pgn[pgn]; r["n"] += 1; r["t0"] = r["t0"] or t; r["t1"] = t; r["ex"] = d
    return {pgn: {**r, "hz": r["n"] / max(r["t1"] - r["t0"], 1e-6), "spns": decode_known(pgn, r["ex"])} for pgn, r in por_pgn.items()}
```
- **Testes necessários:** inventário idêntico em duas gravações do mesmo regime; valor decodificado **conferido** contra painel/scanner para ≥ 3 sinais.
- **Critério de aceite:** catálogo publicado com ≥ 8 sinais do subsistema, **ou** relatório honesto do que o motor não publica e plano B.
- **Evidência de conclusão:** `CATALOGO_SINAIS_MOTOR.md` + gravações brutas (fora do Git se sensíveis).
- **Risco:** motor não publica pressão do trilho. Então S18-T8 usa indicadores indiretos e S18-T12 sensores complementares.
- **Relação com a estratégia:** define o que "analisar a fundo" significa neste motor.

#### S18-T3 · Modelo de dados por componente e sinal
- **Objetivo:** representar "bomba de alta", "injetores", "filtros" e seus sinais, não só "máquina".
- **Contexto:** hoje o modelo é `Machine` + leituras com 3 campos.
- **Problema atual:** sem entidade de componente, não há prescrição por peça nem laudo por peça.
- **Estado desejado:** `Component(machine, tipo, nome, serie, horas_instalacao)`, `Signal(canonical_name, unit, origem, spn_pid)`, `ComponentSignal(component, signal, papel)`, `ComponentHealth(component, estado, pr, plm, t)`.
- **Dependências · Pré-requisitos:** S18-T2 · nenhum.
- **Arquivos prováveis:** `models.py`, migrations, `services/signals.py`, `fixtures/diesel_components.json`.
- **Implementação esperada:** componentes iniciais do subsistema: **bomba de alta pressão**, **trilho/regulador**, **injetores**, **filtro de combustível**, **linha/bomba de baixa pressão (alimentação)**; nomes canônicos de sinal em `docs/CATALOGO_SINAIS_MOTOR.md`; relação N:N entre sinais e componentes (um sinal alimenta vários indicadores).
```python
class Component(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=40)            # bomba_alta, injetor, filtro_comb, linha_baixa, trilho
    nome = models.CharField(max_length=80); serie = models.CharField(max_length=80, blank=True)
    horas_instalacao = models.FloatField(null=True)   # para idade do componente na análise
```
- **Testes necessários:** componente isolado por organização; sinal sem mapeamento fica `unsupported` sem quebrar.
- **Critério de aceite:** modelo migrado e fixtures carregadas.
- **Evidência de conclusão:** testes.
- **Risco:** modelar demais. Só o subsistema-âncora.
- **Relação com a estratégia:** base de prescrição e laudo por componente.

#### S18-T4 · Contrato `telemetry.v2` multicanal e armazenamento de séries
- **Objetivo:** ingerir **dezenas de sinais** sem estourar banco nem rede.
- **Contexto:** o contrato v1.x carrega `temperatura`, `vibracao`, `rpm` (+ GPS opcional).
- **Problema atual:** um campo por sinal não escala; 10 sinais a 1 Hz por 14 dias são milhões de amostras.
- **Estado desejado:** envelope com **janela de N amostras** e metadados por sinal; armazenamento em duas camadas: **bruto comprimido em arquivos por sessão** (no gateway) e **tabelas de janela/feature** no banco; retenção por classe; compatibilidade com v1.
- **Dependências · Pré-requisitos:** S1-T5, S18-T2 · nenhum.
- **Arquivos prováveis:** `contracts/telemetry.v2.json`, `services/telemetria.py`, `services/series_store.py`, `models.py` (`SignalWindow`).
- **Implementação esperada:**
```json
{ "schema_version": "2.0", "device_id": "GEN-01", "message_id": "uuid", "sequence": 18422,
  "event_time": "2026-11-10T14:00:00Z", "boot_id": "uuid", "time_source": "rtc", "regime_hint": "carga_media",
  "window": { "start_ms": 0, "step_ms": 1000, "n": 10 },
  "signals": { "rpm": [1498, 1501, ...], "rail_kpa": [152000, 151800, ...], "fuel_temp_c": [41.5, ...] },
  "meta": { "rail_kpa": { "spn": 157, "unit": "kPa", "source": "can", "quality": "ok" } },
  "dtc": [ { "spn": 0, "fmi": 0, "oc": 0, "state": "active" } ] }
```
(os valores de `spn/fmi` acima são marcadores de formato, não dados.) Cálculo de volume: `bytes ≈ n_sinais × taxa_Hz × bytes_por_amostra × segundos`; medir com compressão e registrar em `docs/CAPACIDADE.md`. Armazenamento: bruto em Parquet/ZSTD por sessão; `SignalWindow` guarda estatísticas por janela (min, máx, média, desvio, n, qualidade) para consulta rápida.
- **Testes necessários:** v1 e v2 coexistem; janela com amostra faltante é marcada, não preenchida; volume de 14 dias cabe no disco do gateway com a política de S6-T2.
- **Critério de aceite:** ≥ 10 sinais a ≥ 1 Hz ingeridos e consultáveis; relatório de volume.
- **Evidência de conclusão:** testes + relatório de capacidade.
- **Risco:** MySQL crescer demais. Agregação e arquivos de sessão.
- **Relação com a estratégia:** viabiliza "10 módulos informando continuamente".

#### S18-T5 · Perfil de normalidade por sinal e por regime
- **Objetivo:** cada sinal tem **seu** padrão de normal, condicionado à situação do motor.
- **Contexto:** pressão do trilho, temperatura e consumo mudam com rotação e carga; "normal" depende disso.
- **Problema atual:** limiares globais e média simples.
- **Estado desejado:** `NormalityProfile(signal, regime_cell, mediana, MAD, q01, q99, n, versao, sessoes_origem)`; células por faixa de rotação × carga; só dados **saudáveis e de qualidade `usavel`** entram; célula sem amostra suficiente vira `fora_da_distribuicao` (não é "anomalia").
- **Dependências · Pré-requisitos:** S18-T4, S18-T6 (para filtrar), S15-T1 · sessões saudáveis.
- **Arquivos prováveis:** `services/normality.py`, `ml/normality_fit.py`, `models.py`.
- **Implementação esperada:**
```python
def ajustar_perfil(df, sinal, rpm_edges, carga_edges, min_n=200):
    df = df[df.quality == "usavel"]                                  # dado desclassificado não entra
    perfil = {}
    for (rb, cb), g in df.groupby([pd.cut(df.rpm, rpm_edges), pd.cut(df.load_pct, carga_edges)], observed=True):
        x = g[sinal].dropna()
        if len(x) < min_n: continue
        med = x.median(); mad = 1.4826 * (x - med).abs().median()
        perfil[(rb.left, cb.left)] = dict(med=med, mad=mad, q01=x.quantile(.01), q99=x.quantile(.99), n=len(x))
    return perfil
def desvio(perfil, rpm, carga, valor, rpm_edges, carga_edges):
    cel = celula(rpm, carga, rpm_edges, carga_edges)
    p = perfil.get(cel)
    if p is None: return {"estado": "fora_da_distribuicao"}
    return {"estado": "ok", "z_robusto": (valor - p["med"]) / (p["mad"] + 1e-9), "fora_q99": valor > p["q99"] or valor < p["q01"]}
```
Versionar o perfil; atualizar só com sessões saudáveis; **nunca** atualizar durante evento aberto.
- **Testes necessários:** perfil ajustado em sessões A avalia sessão B saudável com baixa taxa de falso desvio; célula rara marca `fora_da_distribuicao`; deriva lenta não é "aprendida" durante alarme.
- **Critério de aceite:** perfis para ≥ 8 sinais com cobertura de ≥ 3 regimes; relatório de falso desvio.
- **Evidência de conclusão:** gráficos de banda por regime.
- **Risco:** poucas sessões. Declarar `n` por célula.
- **Relação com a estratégia:** "padrões de normalidade apresentados" do pedido do analista.

#### S18-T6 · Qualidade por sinal e **desclassificação de dado irreal**
- **Objetivo:** dado irreal **não entra** na métrica, na média, na tendência nem no prognóstico, e o descarte é **visível**.
- **Contexto:** sensor travado, queda de comunicação, pico impossível, valor fora do físico, incoerência entre sinais.
- **Problema atual:** o Trust Score avalia leitura única; falta classificação por sinal e por janela.
- **Estado desejado:** cada amostra/janela recebe `usavel | duvidoso | descartado` com **motivo**; apenas `usavel` alimenta perfil, indicadores, PR e PLM; `duvidoso` aparece com selo e **não** entra em tendência; painel "X % descartado, por quê".
- **Dependências · Pré-requisitos:** S18-T4, S1-T3 · nenhum.
- **Arquivos prováveis:** `services/quality.py`, `models.py` (`SignalQuality`), `src/components/QualityPanel.tsx`.
- **Implementação esperada:**
```python
def classificar(janela, meta, ctx):
    motivos = []
    x = janela.valores
    if np.any((x < meta.min_fisico) | (x > meta.max_fisico)): motivos.append("fora_do_limite_fisico")
    if np.ptp(x) == 0 and ctx.rpm_varia: motivos.append("sensor_travado")                     # valor constante com motor variando
    if np.max(np.abs(np.diff(x))) > meta.max_taxa_por_s * janela.step_s: motivos.append("salto_impossivel")
    if janela.faltantes / janela.n > 0.2: motivos.append("lacuna")
    if ctx.rpm > 600 and meta.nome == "rail_kpa" and np.median(x) < meta.min_operacional: motivos.append("incoerente_com_rotacao")   # plausibilidade cruzada
    if motivos: return ("descartado" if {"fora_do_limite_fisico", "sensor_travado", "salto_impossivel"} & set(motivos) else "duvidoso", motivos)
    return ("usavel", [])
```
Limites físicos e taxas máximas vêm do **catálogo** (S18-T2) e da documentação do sinal; **nada é inventado**: sem limite documentado, a regra fica desligada e o sinal é marcado "sem verificação física".
- **Testes necessários:** dado irreal injetado (pico impossível, travado, lacuna, incoerência) é descartado/duvidoso em 100 % dos casos; **descartado nunca aparece em média, perfil, tendência, PR ou PLM** (teste que falha se aparecer).
- **Critério de aceite:** testes verdes; painel mostra motivos.
- **Evidência de conclusão:** teste + captura.
- **Risco:** regra severa demais descartando dado bom. Métrica de descarte por regra e revisão.
- **Relação com a estratégia:** "padrões irreais e irregulares são facilmente identificados e desclassificados".

#### S18-T7 · DTC (SPN-FMI), DM1/DM2, correlação e ligação a componente
- **Objetivo:** código de falha vira **evidência estruturada**, ligada ao componente e ao playbook.
- **Contexto:** J1939 publica falhas ativas (DM1) e anteriores (DM2) com SPN, FMI e contagem de ocorrência; OBD-II tem modos 03/07/0A e freeze frame.
- **Problema atual:** o sistema não decodifica DTC de motor.
- **Estado desejado:** `DtcEvent(machine, spn, fmi, oc, estado, primeiro_visto, ultimo_visto, freeze_frame)`; mapeamento `DTC → componente → playbook` (curado por mecânico); correlação com variação dos sinais **antes** do código; contagem de reincidência.
- **Dependências · Pré-requisitos:** S18-T2, S18-T3, S16-T1 · tabela de FMI/descrições de fonte pública.
- **Arquivos prováveis:** `services/dtc.py`, `knowledge/dtc_map.yml`, `models.py`.
- **Implementação esperada:** decodificar DM1 (lamp status + lista de DTC); guardar mudanças de estado; **abrir `Event` do tipo `DTC_ATIVO`** com severidade vinda do mapa; mostrar na UI a descrição **da fonte**, sem reescrever. Mapa curado:
```yaml
- dtc: {spn: 157, fmi: 1}          # exemplo de formato: confirmar semântica na tabela pública
  componente: trilho_regulador
  hipoteses: [bomba_alta_baixa_vazao, regulador, vazamento_alta]
  playbook: DTC_PRESSAO_TRILHO_BAIXA
  revisado_por: null
```
- **Testes necessários:** quadro DM1 de teste (vetores públicos) decodifica corretamente; DTC repetido aumenta `oc`; DTC some e reaparece como reincidência.
- **Critério de aceite:** DTC reais do motor (ou de gravação) decodificados e **conferidos** com scanner.
- **Evidência de conclusão:** tabela de conferência.
- **Risco:** descrição errada. Usar texto da fonte e marcar `revisado_por`.
- **Relação com a estratégia:** "código de identificação de erro" pedido pelo analista.

#### S18-T8 · Indicadores de saúde por componente (bomba de alta em destaque)
- **Objetivo:** transformar muitos sinais em **poucos indicadores interpretáveis** por componente.
- **Contexto:** a bomba de alta deve ser analisada por seu **comportamento**, não por uma temperatura.
- **Problema atual:** sem indicador por componente.
- **Estado desejado:** tabela de indicadores (HIs) com o que exige, como calcula e direção de degradação; cada HI usa **só dado `usavel`**, comparado ao **perfil por regime**.
- **Dependências · Pré-requisitos:** S18-T5, S18-T6, S18-T7 · sinais do catálogo.
- **Arquivos prováveis:** `services/health_indicators.py`, `docs/INDICADORES_DE_SAUDE.md`.
- **Implementação esperada:** **candidatos** (dependem do que o motor publica; o que não houver fica `indisponivel`):

| Componente | Indicador | Sinais necessários | Como calcula | Degrada quando |
|---|---|---|---|---|
| Bomba de alta | **erro de rastreamento da pressão do trilho** | pressão do trilho real e referência/setpoint (se publicada) | `real − referência` em regime estável | média/oscilação cresce |
| Bomba de alta | **oscilação da pressão do trilho** | pressão do trilho | desvio padrão em janelas de regime estável | aumenta |
| Bomba de alta | **tempo de recuperação após degrau de carga** | rotação, carga, pressão do trilho | tempo até a pressão voltar à banda | aumenta |
| Bomba de alta/sistema | **consumo específico** | taxa de combustível, carga, rotação | consumo por potência estimada, em regime equivalente | aumenta |
| Baixa pressão | **queda da pressão de alimentação** | pressão de entrega | desvio em relação ao perfil | diminui |
| Filtro | **ΔP do filtro** | ΔP de filtro (ou pressão a montante/jusante) | tendência em regime equivalente | sobe |
| Combustível | **temperatura do combustível** | temperatura do combustível | desvio vs perfil | sobe |
| Geral | **frequência de DTC relacionados** | DTC | contagem por 100 h | aumenta |
```python
def oscilacao_trilho(janelas_estaveis):                       # só janelas com rpm/carga estáveis e qualidade 'usavel'
    return np.array([w.std() for w in janelas_estaveis])       # HI por janela; tendência e limite em S19-T6
```
Cada HI declara **requisitos**; se faltar sinal, o HI fica `indisponivel` e a UI mostra "não calculado (falta X)".
- **Testes necessários:** HI não é calculado com dado descartado; HI reage a falha reversível (S18-T11) na direção esperada; HI estável em sessão saudável.
- **Critério de aceite:** ≥ 5 HIs calculados com dado real e separação mensurável entre estado bom e reprovado quando houver rótulo (S18-T9).
- **Evidência de conclusão:** gráficos por HI.
- **Risco:** HI sem significado físico. Revisão por mecânico.
- **Relação com a estratégia:** "analisar a fundo os dados de cada sensor e as tendências".

#### S18-T9 · Banco de provas de oficina: rótulos reais de estado do componente
- **Objetivo:** ter **componente com estado conhecido** para calibrar indicadores e PR.
- **Contexto:** oficinas de injeção costumam testar bomba e bicos em banco de provas e emitir laudo com medições (confirmar disponibilidade na região).
- **Problema atual:** sem rótulo real de estado.
- **Estado desejado:** parceria para (a) acompanhar testes em bancada de bombas **boas e reprovadas**, (b) registrar medições do banco (vazão, pressão, retorno) e o laudo, (c) quando possível, instrumentar a bancada com o nó FieldNode, (d) obter laudos de motores que passaram pela oficina.
- **Dependências · Pré-requisitos:** S18-T1 · oficina parceira, autorização.
- **Arquivos prováveis:** `data/oficina/*`, `docs/PARCERIA_OFICINA.md`.
- **Implementação esperada:** formulário de laudo (S19-T2) preenchido pela oficina; fotos; medições; `estado_componente ∈ {bom, degradado, reprovado}` com critério **da oficina**; hash dos arquivos.
- **Testes necessários:** nenhum automatizado; revisão de consistência dos laudos.
- **Critério de aceite:** ≥ 10 laudos (meta) de bombas/bicos com medições, ou relatório honesto do que foi possível.
- **Evidência de conclusão:** planilha anonimizada de laudos.
- **Risco:** oficina não colabora. Plano B: laudos retroativos e campanha no motor.
- **Relação com a estratégia:** única origem de rótulo real a curto prazo.

#### S18-T10 · Campanha de dados no motor diesel (degraus de carga e regimes)
- **Objetivo:** construir os perfis de normalidade com dado real e controlado.
- **Contexto:** gerador com banco de carga permite carga constante e degraus.
- **Problema atual:** sem dado do motor.
- **Estado desejado:** sessões com protocolo: partida a frio, marcha lenta, degraus de carga (25/50/75/100 % do possível), regime estável por ≥ 10 min por degrau, desligamento; repetir em dias diferentes (≥ 5 sessões saudáveis); manifestos (S15-T1) com tudo anotado.
- **Dependências · Pré-requisitos:** S18-T1, S18-T4, S15-T1 · acesso, supervisão.
- **Arquivos prováveis:** `data/campaign/diesel/*`, `docs/CAMPANHA_DIESEL.md`.
- **Implementação esperada:** nó grava o barramento e os sensores complementares; operador anota marcadores (carga, hora); manifesto assinado; relatório de qualidade por sessão.
- **Testes necessários:** perfis construídos em sessões A avaliam sessões B.
- **Critério de aceite:** ≥ 5 sessões saudáveis ≥ 20 h acumuladas (meta) e perfis por regime.
- **Evidência de conclusão:** manifestos + relatório.
- **Risco:** pouca variedade de regime. Planejar degraus.
- **Relação com a estratégia:** base de normalidade real.

#### S18-T11 · Falhas **reversíveis** e supervisionadas
- **Objetivo:** observar o efeito de degradação **sem risco** e sem dano.
- **Contexto:** nunca provocar falha destrutiva em motor de terceiros.
- **Problema atual:** sem exemplo de degradação no dado do motor.
- **Estado desejado:** protocolo de falhas **reversíveis aprovadas pelo mecânico**: ex. substituir filtro por um **filtro novo e outro com restrição conhecida e documentada**, variação de carga além do normal dentro dos limites do fabricante, perda proposital de sinal (desconectar sensor externo) para testar qualidade; **nada** que envolva a linha de alta pressão, combustível contaminado ou componente rotativo exposto.
- **Dependências · Pré-requisitos:** S18-T10 · mecânico presente, extintor, EPI, procedimento escrito.
- **Arquivos prováveis:** `docs/PROTOCOLO_FALHAS_REVERSIVEIS.md`.
- **Implementação esperada:** checklist de segurança (quem pode interromper, condições de parada, local, ventilação); cada falha tem **rollback** definido.
- **Testes necessários:** simulação em papel do protocolo antes da execução.
- **Critério de aceite:** ao menos 2 falhas reversíveis registradas com rótulo e rollback, ou registro de que o mecânico não autorizou nenhuma (nesse caso, só dados naturais e de oficina).
- **Evidência de conclusão:** manifesto + fotos.
- **Risco:** acidente. Autorização e interrupção imediata.
- **Relação com a estratégia:** evidência de reação dos indicadores.

#### S18-T12 · Sensores complementares **não invasivos** do subsistema
- **Objetivo:** complementar o barramento onde ele não informa, sem tocar na alta pressão.
- **Contexto:** nem todo motor publica todos os sinais.
- **Problema atual:** dependência total do que a ECU publica.
- **Estado desejado:** temperatura do combustível (sonda em contato externo ou na linha de **retorno/baixa**), transdutor **somente de baixa pressão** com faixa adequada e instalação por mecânico, **ΔP de filtro** se houver pontos de medição, **acelerômetro no corpo da bomba** (fixação rígida) para vibração; todos registrados no catálogo com `origem=medido_externo`.
- **Dependências · Pré-requisitos:** S18-T2, S8-T2 · peças.
- **Arquivos prováveis:** `docs/SENSORES_COMBUSTIVEL.md`, `docs/BOM.md`.
- **Implementação esperada:** regra D-59: **alta pressão só via ECU**; instalação de transdutor em baixa pressão exige mecânico, vedação adequada e teste de estanqueidade.
- **Testes necessários:** teste de estanqueidade; leitura coerente com o painel da ECU quando houver o mesmo sinal.
- **Critério de aceite:** ≥ 2 sinais complementares válidos e integrados ao catálogo.
- **Evidência de conclusão:** fotos + leitura.
- **Risco:** vazamento de combustível. Instalação por profissional.
- **Relação com a estratégia:** mais sinais, com segurança.

#### S18-T13 · Aceite do pilar P4: `diesel_100`
- **Objetivo:** provar o foco profundo.
- **Contexto:** critérios do pilar P4.
- **Problema atual:** nenhum teste único cobre o subsistema.
- **Estado desejado:** `scripts/diesel_100.py` com asserts e roteiro gravado.
- **Dependências · Pré-requisitos:** S18-T2 a T10 · motor ou gravação real.
- **Arquivos prováveis:** `scripts/diesel_100.py`, `docs/evidence/s18/*`.
- **Implementação esperada:** (1) catálogo com ≥ 8 sinais; (2) ingestão ≥ 10 canais; (3) perfil por regime aplicado; (4) **dado irreal injetado é desclassificado** e não aparece em nenhuma métrica; (5) DTC decodificado e ligado a componente; (6) ≥ 5 HIs calculados; (7) HI reage a falha reversível (ou a caso de oficina); (8) tudo **offline** no gateway; (9) cadeia de auditoria íntegra.
- **Testes necessários:** 3 execuções, uma com reboot do gateway.
- **Critério de aceite:** 3/3 verdes + vídeo.
- **Evidência de conclusão:** vídeo + log + relatório.
- **Risco:** depender de gravação em vez de motor ao vivo. Declarar qual foi usado.
- **Relação com a estratégia:** fecha P4.


---

### SEMANA 19 · CONFIANÇA: LAUDO, PERCENTUAL DE RECOMENDAÇÃO, PRAZO-LIMITE DE MANUTENÇÃO E PRECISÃO MEDIDA

**Camadas:** ARCHITECTURE · IMPLEMENTATION · VALIDATION · TESTING · DOCUMENTATION
**Pilar:** P5 CONFIANÇA-100

- **Objetivo estratégico:** o gestor precisa de **decisão rápida e assertiva**, com **confiança nas tendências**. A prescrição deve dizer **o que fazer, até quando e com quanta confiança**, e provar com laudos que acerta. Resolve o exemplo do analista: *"recomendou revisar a bomba de alta, mandei ao técnico, voltou com laudo de 70% de vida útil, perdi tempo, disponibilidade e custo."*
- **Objetivo técnico:** definições formais; **laudo estruturado** como verdade de campo; registro de falhas não detectadas; evidência multi-sinal por componente; **PR calibrado**; **PLM** com intervalo; **escada de confirmação** de custo crescente; política de recomendação por organização; painel de precisão; decisão final do técnico; backtest; aceite do cenário "bomba com 70%".
- **Por que existe:** "prescrição em porcentagem de recomendação", "tempo limite para a manutenção e o que deve ser realizado", "decisão final sempre do técnico", "laudo da bomba com 70% de vida".
- **Problemas que resolve:** recomendação sem confiança explícita; remoção desnecessária de peça boa; prazo sem base; ausência de laudo estruturado e de medição de acerto.
- **Dependências recebidas:** S4 (Decision/OS), S15 (calibração, MLOps), S16 (playbooks, checklist), S18 (HIs, qualidade).
- **Entregáveis:** `docs/DEFINICOES_CONFIANCA.md`, modelos `Laudo`, `FailureEvent`, `RecommendationOutcome`, `ComponentEvidence`, `PrCalibration`, `PlmEstimate`, `RecommendationPolicy`, painel de precisão, scripts `confianca_100.py` e `backtest_pr_plm.py`.
- **Arquivos/módulos afetados:** `api_tcc/models.py`, `services/{laudo,evidence,pr,plm,policy,precision}.py`, `ml/calibration.py`, `src/app/laudo/*`, `src/components/{PrGauge,PlmBadge,PrecisionPanel}.tsx`.
- **Arquitetura:** `Evidência multi-sinal → PR (calibrado) + PLM (prognóstico) → política → escada de confirmação → decisão do técnico → laudo → recalibração`. **Banco:** `Laudo`, `FailureEvent`, `RecommendationOutcome`, `PrCalibration`, `PlmEstimate`, `RecommendationPolicy`. **Backend:** serviços de PR, PLM, política e precisão. **Frontend:** medidor, prazo, laudo, painel. **Hardware:** nenhum novo. **ML/IA:** calibração e prognóstico. **Infra:** nada novo. **Segurança:** laudo assinado e auditado. **Testes:** backtest e cenário da bomba. **Docs:** definições.
- **Experimentos:** (a) PR calibrado vs não calibrado nos laudos disponíveis; (b) cobertura do intervalo do PLM em sessões não vistas; (c) efeito da política (τ) na precisão e na cobertura; (d) cenário da bomba.
- **Critérios de aceitação:** PR e PLM exibidos com `n` e intervalo; precisão por nível medida e publicada; cenário "bomba 70%" reproduzido com a escada evitando a remoção desnecessária.
- **Métricas:** precisão por nível (com Wilson), cobertura, taxa de abstenção, erro de calibração (ECE), cobertura do intervalo de PLM, antecedência média do aviso (h de motor), % de divergência do técnico.
- **Evidências esperadas:** relatório de backtest, diagramas de confiabilidade, vídeo do cenário.
- **Riscos:** poucos laudos (PR provisório); PLM sem validação ampla; meta de precisão arbitrária.
- **Decisões:** D-48 (definição de PR), D-49 (quantil e margem do PLM), D-50 (fonte do limite), D-51 (laudo como verdade), D-53 (níveis da escada), D-54 (meta de precisão com o analista).
- **Perguntas abertas:** qual meta de precisão o analista considera aceitável por nível? (fechar na semana 6 a 7).
- **Definition of Done da fatia:** checklist P5 (0-A.4) 100 % e `confianca_100.py` verde 3×.

#### S19-T1 · Definições formais e política de afirmações
- **Objetivo:** todo mundo no projeto fala a mesma língua sobre PR, PLM, precisão e abstenção.
- **Contexto:** "percentual de recomendação" pode virar número bonito sem significado.
- **Problema atual:** `confianca` heurística e sem definição pública.
- **Estado desejado:** `docs/DEFINICOES_CONFIANCA.md` com fórmulas, unidades, o que cada termo **não** significa, e regras de exibição.
- **Dependências · Pré-requisitos:** nenhuma · reunião com o analista.
- **Arquivos prováveis:** `docs/DEFINICOES_CONFIANCA.md`, `docs/CLAIMS_VS_CODE.md`.
- **Implementação esperada:** regras fixas:
  - **PR** = P(laudo confirma o achado | evidência atual), calibrado; sempre acompanhado de **intervalo** e **n**.
  - **PLM** = quantil conservador do tempo até o limite, em **horas de motor**, menos margem; "sem prazo confiável" quando não há base.
  - **Vida útil residual (%)**: **não exibida como fato** até validada; só "estimativa do técnico no laudo".
  - **Nível de evidência**: baixo/médio/alto derivado de qualidade de dado, nº de sinais concordantes, histórico.
  - **Abstenção**: obrigatória abaixo do limiar.
- **Testes necessários:** revisão com o analista e o mecânico.
- **Critério de aceite:** documento aprovado e linkado na matriz de claims.
- **Evidência de conclusão:** ata de aprovação.
- **Risco:** divergência de entendimento. Por isso é a primeira tarefa.
- **Relação com a estratégia:** base da honestidade do pilar.

#### S19-T2 · Laudo estruturado do técnico (a verdade de campo)
- **Objetivo:** cada intervenção termina em um **laudo** que mede se a prescrição acertou.
- **Contexto:** o exemplo do analista é exatamente um laudo ("tinha ainda 70% de vida útil").
- **Problema atual:** só `outcome_texto` livre.
- **Estado desejado:** `Laudo(decision, componente, achado, medicoes, vida_util_estimada_pct, metodo_estimativa, decisao_final, custo_acao (opcional), horas_paradas, anexos, tecnico, assinado_em)` com `achado ∈ {confirmado, parcial, nao_confirmado, inconclusivo}`; formulário **offline** no celular; também importável de oficina.
- **Dependências · Pré-requisitos:** S16-T3, S13-T3 · técnico/oficina.
- **Arquivos prováveis:** `models.py`, `api/views_laudo.py`, `src/app/laudo/[id]/page.tsx`, `services/laudo.py`.
- **Implementação esperada:**
```json
{ "schema": "laudo.v1", "decision_id": "uuid", "componente": "bomba_alta",
  "achado": "nao_confirmado",
  "medicoes": [{"nome": "vazao_banco", "valor": 0, "unidade": "[conforme banco]", "referencia": "[especificação]"}],
  "vida_util_estimada_pct": 70, "metodo_estimativa": "comparação com especificação do fabricante no banco de provas",
  "decisao_final": "devolver_ao_servico", "horas_paradas": 6, "custo_acao": null,
  "tecnico": "nome", "anexos": ["foto1.jpg"], "assinado_em": "..." }
```
`vida_util_estimada_pct` é **opinião fundamentada do técnico**, rotulada assim; `custo_acao` é opcional e vem do cliente. Laudo imutável após assinado (correção vira nova versão), entra na **cadeia de auditoria** (S16-T8).
- **Testes necessários:** laudo offline sincroniza uma vez; edição cria versão; laudo sem decisão vinculada é rejeitado; permissão por organização.
- **Critério de aceite:** técnico real preenche um laudo no celular sem internet.
- **Evidência de conclusão:** vídeo.
- **Risco:** técnico não preencher. Formulário curto, campos opcionais claramente marcados.
- **Relação com a estratégia:** sem laudo, não há precisão medida.

#### S19-T3 · Falhas corretivas e recomendações sem achado (para recall e falsos positivos)
- **Objetivo:** medir **o que o sistema deixou passar** e **o que recomendou à toa**.
- **Contexto:** precisão sozinha não basta; falhas não detectadas importam.
- **Problema atual:** só registramos o que o sistema recomendou.
- **Estado desejado:** `FailureEvent(machine, componente, tipo, data, horas_motor, antecedencia_aviso_h?, detectado_antes: bool)` para falhas/OS corretivas, ligado ao histórico de decisões; `RecommendationOutcome(decision, desfecho ∈ {verdadeiro_positivo, falso_positivo, inconclusivo})` derivado do laudo.
- **Dependências · Pré-requisitos:** S19-T2, S4-T3 · nenhum.
- **Arquivos prováveis:** `models.py`, `services/outcomes.py`.
- **Implementação esperada:** cálculo: `precisao = VP / (VP + FP)`; `sensibilidade = VP / (VP + FN)` onde FN vêm de `FailureEvent` com `detectado_antes=false`; sempre com intervalos.
- **Testes necessários:** casos construídos (VP, FP, FN) produzem métricas esperadas; `inconclusivo` não entra na precisão.
- **Critério de aceite:** testes verdes.
- **Evidência de conclusão:** testes.
- **Risco:** FN subnotificado. Registro simples de OS corretiva.
- **Relação com a estratégia:** métrica honesta dos dois lados.

#### S19-T4 · Evidência multi-sinal por componente
- **Objetivo:** consolidar HIs, DTC, tendência, qualidade e histórico em **uma evidência por componente**, explicável.
- **Contexto:** S18-T8 produz indicadores isolados.
- **Problema atual:** sem consolidação.
- **Estado desejado:** `ComponentEvidence(component, itens[], score, nivel_evidencia, dados_faltantes[], conflitos[])`; cada item cita HI/DTC/tendência com valor, janela e qualidade; conflito entre sinais é **exibido**, não escondido.
- **Dependências · Pré-requisitos:** S18-T6, S18-T8, S15-T8, S15-T10 · nenhum.
- **Arquivos prováveis:** `services/evidence.py`, `models.py`.
- **Implementação esperada:** combinação por regras ponderadas **declaradas** e/ou modelo (regressão logística/árvore) treinado nos laudos, com o mesmo gate de promoção de S15-T9; `nivel_evidencia` baixo quando poucos sinais concordam, dado de qualidade ruim ou histórico curto.
```python
def evidencia(component, hi, dtc, tendencia, qualidade):
    itens = [i for i in (hi + dtc + tendencia) if i.qualidade == "usavel"]
    concordantes = sum(1 for i in itens if i.direcao == "degradando")
    faltantes = [s for s in component.sinais_esperados if s not in {i.sinal for i in itens}]
    nivel = "alto" if concordantes >= 3 and not faltantes else "medio" if concordantes >= 2 else "baixo"
    return Evidencia(itens=itens, score=score_modelo(itens), nivel=nivel, faltantes=faltantes, conflitos=conflitos(itens))
```
- **Testes necessários:** poucos sinais ⇒ nível baixo; sinais concordantes ⇒ nível alto; dado descartado não entra.
- **Critério de aceite:** testes verdes e explicação exibida.
- **Evidência de conclusão:** captura.
- **Risco:** falsa certeza com poucos sinais. Nível e faltantes sempre visíveis.
- **Relação com a estratégia:** "análise a fundo" virando evidência acionável.

#### S19-T5 · **Percentual de recomendação (PR)** calibrado
- **Objetivo:** um número que **significa** "em x% dos casos como este, o técnico confirmou o defeito".
- **Contexto:** o analista pediu "alinhamento da prescrição em porcentagem de recomendação, assim fica visual".
- **Problema atual:** `confianca` heurística.
- **Estado desejado:** `PrCalibration(componente, versao, metodo, n_laudos, tabela, ece, atualizado_em)`; **calibração** do `score` de evidência com os laudos (isotônica quando n suficiente; **Beta/Bayes por faixa de score** quando n pequeno); **intervalo** (posterior ou Wilson); **selo "provisório"** abaixo de N mínimo; exibição: medidor + faixa + `n`.
- **Dependências · Pré-requisitos:** S19-T2, S19-T3, S19-T4, S15-T7 · laudos (bancada/oficina contam, rotulados).
- **Arquivos prováveis:** `services/pr.py`, `ml/calibration.py`, `src/components/PrGauge.tsx`.
- **Implementação esperada:**
```python
from sklearn.isotonic import IsotonicRegression
def calibrar_pr(scores, confirmados, n_min=50):
    n = len(scores)
    if n >= n_min:
        iso = IsotonicRegression(y_min=0, y_max=1, out_of_bounds="clip").fit(scores, confirmados)
        return {"metodo": "isotonica", "f": iso.predict, "provisorio": False, "n": n}
    return {"metodo": "beta_por_faixa", "f": beta_posterior_por_faixa(scores, confirmados, prior=(1, 1)), "provisorio": True, "n": n}
def pr_exibivel(score, cal):
    p = float(cal["f"](score)); lo, hi = intervalo(p, cal["n"])        # Wilson/posterior
    return {"pr": round(100 * p), "ic": (round(100*lo), round(100*hi)), "n": cal["n"], "provisorio": cal["provisorio"]}
```
Regra de exibição: **sempre** `PR% (IC) · n=… · provisório?`; PR **nunca** aparece sem `n`.
- **Testes necessários:** em dado sintético com probabilidade conhecida, PR calibrado ≈ real (ECE baixo); n pequeno ⇒ provisório e intervalo largo; PR monotônico no score.
- **Critério de aceite:** diagrama de confiabilidade publicado; UI com selo.
- **Evidência de conclusão:** gráfico + captura.
- **Risco:** PR inflado com poucos laudos. Intervalo e selo.
- **Relação com a estratégia:** "percentual de recomendação visual" com significado.

#### S19-T6 · **Prazo-limite de manutenção (PLM)** e prognóstico por indicador
- **Objetivo:** dizer **até quando** inspecionar, em **horas de motor**, com intervalo e base explícita.
- **Contexto:** o analista pediu "um tempo limite para a manutenção". A degradação anda com a **operação**, não com o calendário.
- **Problema atual:** horizonte por tendência linear de temperatura (S9-T3).
- **Estado desejado:** para cada HI com tendência crível: distribuição do **tempo até o limite**; **PLM = quantil conservador (ex.: 10 %) menos margem**, em horas de motor, convertido em dias pelo uso médio recente; **"sem prazo confiável"** quando faltam condições (histórico mínimo, cobertura de regime, tendência estatisticamente significativa, qualidade). O **limite** vem do **manual do fabricante** quando houver (D-50); senão do **perfil de normalidade** (ex.: q99 de sessões saudáveis), rotulado.
- **Dependências · Pré-requisitos:** S18-T5, S18-T6, S18-T8, S9-T3 · horas de motor (SPN de horas ou contador próprio).
- **Arquivos prováveis:** `services/plm.py`, `models.py` (`PlmEstimate`), `src/components/PlmBadge.tsx`.
- **Implementação esperada:**
```python
def plm(hi_h, limite, horas_atuais, q=0.10, margem_h=8, n_boot=2000, rng=np.random.default_rng(0)):
    ok, motivo = condicoes(hi_h)            # n mínimo de pontos, ≥ k regimes cobertos, Mann-Kendall p<α, qualidade 'usavel' ≥ X%
    if not ok: return {"prazo_h": None, "motivo": motivo}                    # ABSTENÇÃO: sem prazo confiável
    t_cruz = []
    for _ in range(n_boot):
        amostra = bootstrap_por_blocos(hi_h, rng)                            # blocos preservam autocorrelação
        a, b = theil_sen(amostra)                                            # robusto a outliers
        t_cruz.append((limite - a) / b - horas_atuais if b > 0 else np.inf)
    q10, q50, q90 = np.quantile(t_cruz, [q, .5, .9])
    return {"prazo_h": max(q10 - margem_h, 0), "intervalo_h": (q10, q90), "mediana_h": q50,
            "base": {"limite": limite, "fonte_limite": "manual_fabricante|perfil_q99", "n": len(hi_h)}, "nivel_evidencia": nivel(hi_h)}
```
Mostrar: **"Inspecionar a bomba de alta em até 38 h de motor (≈ 5 dias de uso) · evidência média · PR 72 %"**, com o intervalo e a base ao toque. Conversão em calendário: `dias = horas / média_h_por_dia_últimos_7_dias`.
- **Testes necessários:** série com degradação conhecida produz prazo coerente; série ruidosa ou curta produz "sem prazo confiável"; dado descartado ignorado; mudar a margem altera o prazo na direção esperada.
- **Critério de aceite:** backtest (S19-T11) com cobertura do intervalo próxima da nominal ou relatório honesto.
- **Evidência de conclusão:** gráficos de previsão vs ocorrido.
- **Risco:** passar falsa precisão. Abstenção, quantil conservador e rótulo "estimativa".
- **Relação com a estratégia:** "tempo-limite para manutenção" entregue de forma defensável.

#### S19-T7 · **Escada de confirmação** (o que fazer, do mais barato ao mais caro)
- **Objetivo:** não remover a bomba antes de verificar o que é barato e informativo.
- **Contexto:** o caso da bomba com 70% de vida: o erro foi **pular direto para a ação cara**.
- **Problema atual:** prescrição de um passo só.
- **Estado desejado:** cada playbook de componente define **degraus de custo crescente** com **PR mínimo** por degrau (valores iniciais **conservadores**, calibrados e definidos pela política da organização):

| Degrau | Ação (exemplos de **formato**; conteúdo técnico definido pelo mecânico) | Custo relativo | PR mínimo (inicial, a calibrar) |
|---|---|---|---|
| 0 | Monitorar com tendência e reavaliar em X h | muito baixo | qualquer |
| 1 | **Verificação sem desmontar**: conferir DTC, filtro, alimentação, conexões, leitura de pressão por instrumento | baixo | baixo |
| 2 | **Teste específico no veículo**: medições de diagnóstico definidas pelo mecânico | médio | médio |
| 3 | **Remover e enviar à bancada** | alto | alto |

O sistema **só habilita o degrau seguinte** se (a) o degrau atual foi executado e o resultado persiste, **ou** (b) o PR for suficientemente alto para pular, **e** o técnico decidir. **PR baixo/médio ⇒ degraus 0 a 2, nunca 3.**
```yaml
componente: bomba_alta
escada:
  - {nivel: 0, acao: "monitorar e reavaliar", reavaliar_em_h: 12}
  - {nivel: 1, acao: "verificação sem desmontar [lista do mecânico]", pr_min: 0.40}
  - {nivel: 2, acao: "teste específico no veículo [lista do mecânico]", pr_min: 0.60}
  - {nivel: 3, acao: "remover e enviar à bancada", pr_min: 0.85, exige: [nivel_2_executado_ou_confirmado]}
revisado_por: null          # os pr_min acima são ponto de partida, não verdade
```
Cenário da bomba: PR 62 % ⇒ degraus 1 e 2; o técnico executa; **laudo de campo** diz "sem achado" ⇒ nenhuma remoção, nenhuma bancada, **custo baixo**, e o sistema aprende (PR recalibra).
- **Testes necessários:** PR 62 % bloqueia degrau 3; PR 90 % habilita com confirmação do técnico; degrau 3 exige degrau 2 executado salvo exceção justificada.
- **Critério de aceite:** testes verdes; UI mostra a escada com o degrau atual.
- **Evidência de conclusão:** captura + teste.
- **Risco:** escada excessiva atrasando a ação necessária. Em PR muito alto, pular é permitido com justificativa.
- **Relação com a estratégia:** o que evita o problema real do gestor.

#### S19-T8 · Política de recomendação por organização
- **Objetivo:** cada cliente escolhe o equilíbrio entre **cobertura** e **precisão**.
- **Contexto:** custo de falso positivo e de falso negativo muda por operação.
- **Problema atual:** limiar único.
- **Estado desejado:** `RecommendationPolicy(org, componente, tau_monitorar, tau_inspecionar, tau_remover, meta_precisao, custos_opcionais)`; **curva precisão × cobertura** a partir dos laudos para escolher τ; alteração **auditada** e restrita a papel; padrão conservador.
- **Dependências · Pré-requisitos:** S19-T5, S19-T9 · nenhum.
- **Arquivos prováveis:** `models.py`, `services/policy.py`, tela de configurações.
- **Implementação esperada:**
```python
def curva(scores, confirmados, taus):
    return [{"tau": t, "cobertura": np.mean(scores >= t), "precisao": confirmados[scores >= t].mean() if (scores >= t).any() else None, "n": int((scores >= t).sum())} for t in taus]
```
Meta de precisão: **definida com o analista** (D-54); mostrar o que cada meta custa em cobertura.
- **Testes necessários:** mudar τ muda quem é recomendado; alteração gera `AuditLog`.
- **Critério de aceite:** gestor altera τ e vê o efeito na curva.
- **Evidência de conclusão:** captura.
- **Risco:** gestor baixar τ e inflar falso positivo. A tela mostra o custo.
- **Relação com a estratégia:** assertividade como **escolha explícita**.

#### S19-T9 · Painel de precisão e calibração
- **Objetivo:** o gestor e o investidor veem **se a ferramenta acerta**.
- **Contexto:** confiança precisa de prova contínua.
- **Problema atual:** nenhum painel.
- **Estado desejado:** por componente e nível: precisão (com Wilson), cobertura, abstenção, **diagrama de confiabilidade**, `n` de laudos, cobertura do intervalo do PLM, antecedência média do aviso, divergência do técnico; selos de `n` insuficiente.
- **Dependências · Pré-requisitos:** S19-T3, S19-T5, S19-T6 · nenhum.
- **Arquivos prováveis:** `src/app/precisao/page.tsx`, `src/components/PrecisionPanel.tsx`, `services/precision.py`.
- **Implementação esperada:**
```python
def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 1.0)
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d; h = z * ((p*(1-p)/n + z*z/(4*n*n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))
```
- **Testes necessários:** valores conferidos contra tabela conhecida; `n < N` mostra selo.
- **Critério de aceite:** painel com os 7 indicadores corretos em dataset de teste.
- **Evidência de conclusão:** captura.
- **Risco:** leitura enganosa com n pequeno. Selo e intervalo.
- **Relação com a estratégia:** transparência que investidor valoriza.

#### S19-T10 · **Decisão final do técnico** (override com motivo e aprendizado)
- **Objetivo:** o técnico **decide**; o sistema aprende com a divergência.
- **Contexto:** "a tomada de decisão final sempre será do técnico".
- **Problema atual:** aprovar/rejeitar sem motivo estruturado.
- **Estado desejado:** o técnico pode **seguir, adiar, rebaixar ou ignorar** a recomendação com **motivo** (lista + texto); o sistema registra `RecommendationOverride(decision, acao_tecnico, motivo)`; divergências recorrentes sobem como alerta de **revisão de regra/playbook**; o sistema **nunca executa** sozinho.
- **Dependências · Pré-requisitos:** S3-T5, S19-T2 · nenhum.
- **Arquivos prováveis:** `models.py`, `services/overrides.py`, UI de decisão.
- **Implementação esperada:** motivos padrão: "evidência insuficiente", "já verificado", "peça recém-trocada", "operação crítica agora", "discordo da leitura"; estatística por regra: taxa de divergência; divergência alta ⇒ tarefa de revisão do playbook.
- **Testes necessários:** override é auditado; recomendação não altera estado sozinha; divergência alta gera aviso.
- **Critério de aceite:** E2E.
- **Evidência de conclusão:** vídeo.
- **Risco:** técnico ignorar sempre. A taxa vira sinal para revisar o sistema.
- **Relação com a estratégia:** "decisão final do técnico", com aprendizado.

#### S19-T11 · Backtest e validação de PR e PLM
- **Objetivo:** provar que PR e PLM funcionam em dado **não visto**.
- **Contexto:** sem validação, são números bonitos.
- **Problema atual:** nenhum protocolo.
- **Estado desejado:** `scripts/backtest_pr_plm.py`: divisão **por sessão/máquina/componente**; métricas: ECE do PR, precisão@τ, cobertura, antecedência do aviso (h de motor), **cobertura do intervalo do PLM** (o evento ocorreu dentro do intervalo?), taxa de abstenção; relatório com intervalos.
- **Dependências · Pré-requisitos:** S19-T5, S19-T6, dados de S18-T9/T10 · nenhum.
- **Arquivos prováveis:** `scripts/backtest_pr_plm.py`, `docs/AVALIACAO_PR_PLM.md`.
- **Implementação esperada:** `GroupKFold` por sessão; para PLM, "sondar" o modelo em pontos anteriores a falhas conhecidas (rig, bancada, oficina) e conferir se o intervalo cobriu a ocorrência; declarar **limites** (poucos eventos).
- **Testes necessários:** reprodutibilidade por semente; vazamento impossível (teste de grupos).
- **Critério de aceite:** relatório publicado, inclusive se o resultado for ruim.
- **Evidência de conclusão:** `AVALIACAO_PR_PLM.md`.
- **Risco:** poucos eventos de falha ⇒ intervalos largos. Dizer.
- **Relação com a estratégia:** porta de entrada para qualquer afirmação.

#### S19-T12 · Aceite do pilar P5: cenário **"bomba com 70% de vida"** e `confianca_100`
- **Objetivo:** reproduzir o problema do analista e mostrar o sistema evitando-o.
- **Contexto:** é o exemplo exato dele.
- **Problema atual:** o sistema mandaria revisar a bomba.
- **Estado desejado:** roteiro gravado: (1) sinais da bomba em degradação **leve**; (2) evidência multi-sinal média; (3) **PR 62 % (provisório, n = X)** e **PLM** com intervalo; (4) o sistema recomenda a **escada**, não a remoção; (5) técnico executa degraus 1 e 2; (6) **laudo de campo**: "sem achado; vida útil estimada 70 %"; (7) sistema registra falso positivo **evitado/baixo custo**, recalibra o PR; (8) caso oposto: sinais fortes ⇒ PR alto ⇒ degrau 3 habilitado e **laudo confirma**; (9) tudo **offline**, após reboot, auditado.
- **Dependências · Pré-requisitos:** S19-T1 a T11, S16-T3 · cenários construídos com dado real de oficina/campanha quando possível, **rotulados** quando sintéticos.
- **Arquivos prováveis:** `scripts/confianca_100.py`, `docs/evidence/s19/*`.
- **Implementação esperada:** asserts por etapa; vídeo contínuo; relatório com PR antes/depois da recalibração.
- **Testes necessários:** 3 execuções seguidas, uma com reboot.
- **Critério de aceite:** 3/3 verdes + vídeo; nenhuma remoção de peça recomendada no caso 1.
- **Evidência de conclusão:** vídeo + log.
- **Risco:** cenário muito "arrumado". Declarar a origem de cada dado.
- **Relação com a estratégia:** fecha P5 mostrando o problema real resolvido.


---

### SEMANA 20 · HOME E BI: DECISÃO RÁPIDA EM UMA TELA

**Camadas:** IMPLEMENTATION · VALIDATION · TESTING · DOCUMENTATION
**Pilar:** P6 HOME-100

- **Objetivo estratégico:** "o que todo gestor quer é decisão rápida, mas assertiva". A tela inicial responde em **segundos**: quantos equipamentos estão **críticos, em atenção e normais**, onde estão, e o que fazer, **sem poluição**.
- **Objetivo técnico:** layout dividido (barra de seleção + mapa); cards de situação clicáveis; seleção hierárquica de frota; drill-down de card → lista com prescrição resumida → detalhe com tendências e componente; painel do componente com PR, PLM, tendência, DTC e escada; medidor visual de PR consistente; UI enxuta; mapa com seleção bidirecional; teste de usabilidade.
- **Por que existe:** feedback do analista: "tela inicial mais interativa com o mapa na lateral da barra de seleção; enxugar; abrir dados do equipamento somente após seleção da frota; BI de rápida visualização com cards (3 críticos, 6 atenção, 30 normais) que abrem prescrições e tendências".
- **Problemas que resolve:** home com muitos widgets; dados de equipamento antes de escolher; ausência de caminho crítico → prescrição; prescrição sem PR e prazo na vista.
- **Dependências recebidas:** S3 (Command Center), S14-T11 (cobertura), S18-T8 (HIs), S19-T5/T6 (PR e PLM), S13-T3 (PWA offline).
- **Entregáveis:** novo layout da home, componentes `SelectionSidebar`, `SituationCards`, `FleetList`, `ComponentPanel`, `PrGauge`, `PlmBadge`, E2E `home_100`, relatório de usabilidade, guia de design.
- **Arquivos/módulos afetados:** `frontend-next/src/app/page.tsx` (home), `src/app/dashboard/*`, `src/components/{SelectionSidebar,SituationCards,FleetList,ComponentPanel,PrGauge,PlmBadge,TrendChart}.tsx`, `src/lib/state/selection.ts`.
- **Arquitetura:** estado de seleção como fonte única (URL + store), compartilhado entre barra, mapa e cards. **Banco:** nenhum. **Backend:** endpoint agregado `GET /api/v1/fleet/summary?escopo=...` e `GET /api/v1/fleet/list?estado=...`. **Frontend:** núcleo. **Hardware:** nenhum. **ML/IA:** PR e PLM exibidos. **Infra:** nenhuma. **Segurança:** o resumo respeita organização e escopo. **Testes:** E2E e usabilidade. **Docs:** guia de design.
- **Experimentos:** teste dos 5 s (gestor diz o que exige atenção) e dos 30 s (acha o equipamento crítico e abre a prescrição) com 3 a 5 pessoas; teste de A/B de ordem dos cards.
- **Critérios de aceitação:** home sem dado de equipamento antes da seleção; cards com contagens corretas e clicáveis; caminho card → lista → detalhe em ≤ 3 cliques; `home_100` verde.
- **Métricas:** tempo até identificar o crítico; cliques até a prescrição; SUS (escala de usabilidade); nº de elementos por tela; taxa de erro de leitura do PR.
- **Evidências esperadas:** vídeo, relatório de usabilidade, capturas antes/depois.
- **Riscos:** remover informação que alguém usa (mitigação: "avançado" colapsável); layout quebrar no mobile.
- **Decisões:** D-55 (estrutura da home), D-56 (metas de usabilidade).
- **Perguntas abertas:** frota = grupo de máquinas por quê (modelo, frente, local)? Resposta provisória: **hierarquia Site → Frente → Frota (grupo) → Máquina**, configurável.
- **Definition of Done da fatia:** checklist P6 (0-A.4) 100 %.

#### S20-T1 · Layout novo da tela inicial: barra de seleção + mapa
- **Objetivo:** primeira tela **interativa e enxuta**.
- **Contexto:** hoje a home mistura métricas, gráficos e listas.
- **Problema atual:** informação demais antes de o usuário dizer o que quer ver.
- **Estado desejado:** **desktop:** coluna esquerda estreita (seleção de site/frente/frota + busca) e **mapa** à direita ocupando a área principal; **faixa superior** com os cards de situação; **nenhum dado de equipamento** até haver seleção; **mobile:** mapa em tela cheia, seleção em gaveta, cards no topo, detalhe em bottom sheet.
- **Dependências · Pré-requisitos:** S3-T3, S3-T7, S14-T11 · wireframe aprovado.
- **Arquivos prováveis:** `src/app/page.tsx`, `src/components/{AppShell,SelectionSidebar,FleetMap}.tsx`, `docs/DESIGN_HOME.md`.
- **Implementação esperada:** wireframe (a aprovar com o analista antes de codar):
```text
┌───────────────────────────────────────────────────────────────────────────┐
│  [ 3 Críticos ]  [ 6 Atenção ]  [ 30 Normais ]  [ 2 Sem dados ]   ⟳ 14:02 │  <- cards clicáveis
├──────────────────────┬────────────────────────────────────────────────────┤
│ Selecionar frota     │                                                    │
│  Site ▾  Frente ▾    │                MAPA (clusters coloridos)           │
│  Frota ▾  🔎 buscar  │          seleção ↔ mapa em dois sentidos           │
│  ───────────────     │                                                    │
│  ○ Frota A (12)      │                                                    │
│  ● Frota B (9)       │                                                    │
│  ○ Frota C (20)      │                                                    │
└──────────────────────┴────────────────────────────────────────────────────┘
 (sem seleção: nenhum dado de equipamento; com seleção: lista da frota e do estado escolhido)
```
Estado em URL (`?site=&frente=&frota=&estado=&maquina=`), para compartilhar e voltar.
- **Testes necessários:** carregar a home sem seleção **não** chama endpoints de telemetria de equipamento; mobile 390×844: mapa visível e cards no topo; teclado e leitor de tela.
- **Critério de aceite:** E2E; wireframe aprovado pelo analista.
- **Evidência de conclusão:** capturas e aprovação.
- **Risco:** perder acesso a recurso antigo. Mover para "Avançado" (S20-T7).
- **Relação com a estratégia:** pedidos 1 e 2 do analista.

#### S20-T2 · Cards de situação **clicáveis** (Críticos, Atenção, Normais, Sem dados)
- **Objetivo:** visão de BI em um olhar.
- **Contexto:** a faixa "Atenção agora" (S3-T3) conta eventos; aqui contamos **equipamentos por estado**.
- **Problema atual:** contagem por evento, não por equipamento; sem clique que abra detalhe.
- **Estado desejado:** cada card mostra **contagem de equipamentos** conforme a definição única (contrato S1 + níveis de recomendação S19): **Crítico** (evento crítico aberto ou PR/PLM em nível de ação), **Atenção** (evidência crescente, PLM em janela), **Normal**, **Sem dados** (observabilidade, S3-T6); clique **filtra mapa e lista**; contagens respeitam a seleção de frota.
- **Dependências · Pré-requisitos:** S3-T6, S19-T5/T6 · endpoint de resumo.
- **Arquivos prováveis:** `src/components/SituationCards.tsx`, `api/views_fleet.py`, `contracts/state.v1.json`.
- **Implementação esperada:**
```python
def estado_equipamento(m):
    if m.dados_obsoletos: return "sem_dados"
    if m.evento_critico_aberto or any(c.pr and c.pr >= POL.tau_inspecionar and c.plm_h is not None and c.plm_h <= POL.janela_critica_h for c in m.componentes):
        return "critico"
    if m.evidencia_crescente or any(c.plm_h is not None for c in m.componentes):
        return "atencao"
    return "normal"
```
A **definição de estado é única** (contrato) e a mesma para cards, mapa e lista.
- **Testes necessários:** contagem dos cards = tamanho da lista filtrada; máquina crítica offline continua `critico`; sem dados é `sem_dados`.
- **Critério de aceite:** E2E: clicar "Críticos" mostra exatamente as 3 máquinas do cenário.
- **Evidência de conclusão:** vídeo.
- **Risco:** "atenção" virar saco de gato. Definição no contrato e testada.
- **Relação com a estratégia:** pedido 3 do analista.

#### S20-T3 · Drill-down: card → lista com prescrição resumida → detalhe com tendências
- **Objetivo:** do panorama ao **o que fazer** em poucos cliques.
- **Contexto:** "ao clicar nos críticos, abre as informações detalhadas, com as prescrições e tendências".
- **Problema atual:** detalhe é página com muitos gráficos.
- **Estado desejado:** **nível 1:** lista da seleção, cada linha com **máquina, componente crítico, ação resumida, PR %, PLM, evidência**; **nível 2:** detalhe da máquina com **tendências por sinal** (com banda de normalidade), componentes, DTC e prescrição completa; **breadcrumb** e retorno preservando seleção; máximo de 3 cliques da home até a prescrição.
- **Dependências · Pré-requisitos:** S20-T2, S19-T5/T6, S16-T2 · nenhum.
- **Arquivos prováveis:** `src/components/FleetList.tsx`, `src/app/maquinas/[id]/page.tsx`, `src/components/TrendChart.tsx`.
- **Implementação esperada:** linha da lista:
```text
CH-03 · Bomba de alta · "Verificar alimentação e filtro (degrau 1)" · PR 62 % (n=14, provisório) · Inspecionar em até 38 h de motor · evidência média   [Abrir]
```
- **Testes necessários:** cliques ≤ 3; voltar mantém filtros; lista ordenada por severidade e PLM.
- **Critério de aceite:** E2E e teste dos 30 s.
- **Evidência de conclusão:** vídeo.
- **Risco:** lista longa. Paginação e ordenação.
- **Relação com a estratégia:** pedido 3 do analista.

#### S20-T4 · Seleção hierárquica de frota (site → frente → frota → máquina)
- **Objetivo:** "abrir os dados do equipamento somente após seleção da frota".
- **Contexto:** `Site`/`Front` entram no S9-T1; frota é um agrupamento operacional.
- **Problema atual:** sem hierarquia de seleção.
- **Estado desejado:** modelo `Fleet(site, nome, criterio)` (agrupamento por modelo/frente/local), seleção persistente (URL e preferência do usuário), busca por código; **sem seleção, sem dado de equipamento**.
- **Dependências · Pré-requisitos:** S9-T1 · nenhum.
- **Arquivos prováveis:** `models.py` (`Fleet`), `src/lib/state/selection.ts`, `SelectionSidebar.tsx`.
- **Implementação esperada:** `GET /api/v1/fleets/` retorna árvore; seleção armazenada em URL; mudança de seleção cancela requisições em curso (`AbortController`).
- **Testes necessários:** seleção de outra organização inexistente; trocar frota cancela fetch anterior.
- **Critério de aceite:** E2E.
- **Evidência de conclusão:** vídeo.
- **Risco:** frota mal definida. Configurável por critério.
- **Relação com a estratégia:** pedido 2 do analista.

#### S20-T5 · Painel do componente (bomba de alta): PR, PLM, tendência, DTC, escada
- **Objetivo:** a tela em que o técnico **decide**.
- **Contexto:** núcleo do foco diesel.
- **Problema atual:** detalhe genérico de máquina.
- **Estado desejado:** painel com: **medidor de PR** (S20-T6), **PLM** com intervalo, **tendência dos indicadores de saúde com banda de normalidade** (S18-T5), **sinais usados e descartados** (S18-T6), **DTC ativos/anteriores**, **evidências a favor e contra**, **dados faltantes**, **escada de confirmação com degrau atual**, **laudos anteriores do componente**, botões **seguir, adiar, rebaixar, ignorar** (S19-T10).
- **Dependências · Pré-requisitos:** S18-T8, S19-T4 a T7, S19-T10 · nenhum.
- **Arquivos prováveis:** `src/components/ComponentPanel.tsx`, `src/app/componentes/[id]/page.tsx`.
- **Implementação esperada:** layout em três blocos (Situação, Evidência, Ação); gráfico com banda de normalidade e marca do limite; sempre mostrar **o que não sabemos**.
- **Testes necessários:** componente sem PR mostra "sem recomendação: dados insuficientes" com motivo; descartado aparece como descartado, não como número.
- **Critério de aceite:** técnico decide a partir do painel sem consultar outra tela (teste de usabilidade).
- **Evidência de conclusão:** vídeo.
- **Risco:** excesso de informação. Hierarquia visual e colapsáveis.
- **Relação com a estratégia:** pedidos 5, 7, 8 e 9.

#### S20-T6 · Medidor visual do **percentual de recomendação** e do prazo
- **Objetivo:** "assim fica visual".
- **Contexto:** o PR precisa ser lido em 1 segundo e sem erro.
- **Problema atual:** sem componente de design.
- **Estado desejado:** medidor semicircular com **faixas** (baixa/média/alta, **não** só verde/vermelho), **número e intervalo**, **`n` de laudos**, selo **"provisório"**, e ao lado o **PLM** como contagem em horas de motor e equivalente em dias; tooltip explica em uma frase; versão compacta para linha de lista e mapa; **acessível** (não depende só de cor).
- **Dependências · Pré-requisitos:** S19-T5, S19-T6 · design tokens.
- **Arquivos prováveis:** `src/components/{PrGauge,PlmBadge}.tsx`, `src/lib/design-tokens.ts`.
- **Implementação esperada:**
```tsx
export function PrGauge({ pr, ic, n, provisorio }: Props) {
  const faixa = pr >= 85 ? 'alta' : pr >= 60 ? 'media' : 'baixa';       // faixas vêm da política da organização (S19-T8)
  return (<figure role="img" aria-label={`Recomendação ${pr}% (intervalo ${ic[0]} a ${ic[1]}%), ${n} laudos${provisorio ? ', provisório' : ''}`}>
    <Gauge value={pr} band={faixa} /> <figcaption>{pr}% <small>({ic[0]}–{ic[1]}%) · n={n}</small> {provisorio && <Badge>provisório</Badge>}</figcaption></figure>);
}
```
- **Testes necessários:** nenhum PR sem `n`; leitor de tela lê valor, intervalo e `n`; daltonismo (não só cor).
- **Critério de aceite:** teste de leitura: 5 pessoas dizem o PR e a confiança corretos em 3 s.
- **Evidência de conclusão:** relatório de usabilidade.
- **Risco:** PR lido como "vida útil". Rótulo "chance de o técnico confirmar o defeito".
- **Relação com a estratégia:** pedido 7 do analista.

#### S20-T7 · Enxugar a UI: "Avançado" colapsável e regra de elementos por tela
- **Objetivo:** primeira tela limpa; nada se perde.
- **Contexto:** o dashboard tem telemetria crua, vários gráficos, alertas e tabelas.
- **Problema atual:** poluição; mas há quem use esses dados.
- **Estado desejado:** o que saiu da home vai para **"Avançado"** (telemetria crua, séries, DTC bruto, qualidade por sinal) dentro do detalhe da máquina; regra de design: **máximo de N elementos principais por tela** (N definido em D-55).
- **Dependências · Pré-requisitos:** S20-T1, S20-T3 · nenhum.
- **Arquivos prováveis:** `src/app/dashboard/*`, `src/components/Advanced.tsx`, `docs/DESIGN_HOME.md`.
- **Implementação esperada:** inventário do que existia vs onde está agora (tabela de migração) para provar que **nenhuma funcionalidade foi removida**.
- **Testes necessários:** E2E das telas antigas ainda alcançáveis via "Avançado".
- **Critério de aceite:** home com ≤ N elementos; inventário completo.
- **Evidência de conclusão:** tabela antes/depois.
- **Risco:** esconder demais. Teste de usabilidade (S20-T8).
- **Relação com a estratégia:** pedido 2 do analista.

#### S20-T8 · Teste de usabilidade com gestores e técnicos (duas rodadas)
- **Objetivo:** provar que a home entrega decisão rápida.
- **Contexto:** o analista é o primeiro revisor natural.
- **Problema atual:** nenhuma medição de usabilidade.
- **Estado desejado:** 2 rodadas com 3 a 5 pessoas (gestor, técnico, o analista): tarefas cronometradas: **T1** "o que exige atenção agora?" (≤ 5 s), **T2** "abra a prescrição do equipamento crítico" (≤ 30 s), **T3** "diga o que fazer primeiro e com quanta confiança", **T4** "decida e registre"; questionário SUS; observação de erros; correções entre rodadas.
- **Dependências · Pré-requisitos:** S20-T1 a T7, S19-T12 · participantes.
- **Arquivos prováveis:** `docs/USABILIDADE_HOME.md`.
- **Implementação esperada:** roteiro fixo; gravação com consentimento; relatório com tempos, erros e mudanças feitas.
- **Testes necessários:** nenhum automatizado.
- **Critério de aceite:** metas D-56 atingidas ou relatório honesto com plano.
- **Evidência de conclusão:** relatório.
- **Risco:** só amigos. Incluir o analista e um técnico externo.
- **Relação com a estratégia:** "decisão rápida" medida.

#### S20-T9 · Mapa com seleção bidirecional, clusters e camadas
- **Objetivo:** mapa que **conversa** com a barra e com os cards.
- **Contexto:** há três componentes de mapa (consolidar, D-17); mapa offline em S13-T3.
- **Problema atual:** mapa independente da seleção.
- **Estado desejado:** clique no mapa seleciona a máquina/frota na barra; selecionar na barra centraliza o mapa; **clusters** com cor do pior estado; **camadas** opcionais (cobertura/enlaces de S14-T11, geofence de S17-T8, trilha); popup curto com PR, PLM e botão "abrir"; funciona offline com tiles em cache.
- **Dependências · Pré-requisitos:** S20-T1, S3-T7, S13-T3 · nenhum.
- **Arquivos prováveis:** `FleetMap.tsx` (único), `src/lib/state/selection.ts`.
- **Implementação esperada:** estado único de seleção; debounce de eventos de mapa; clusterização no cliente com limite de pontos.
- **Testes necessários:** seleção bidirecional; 500 pontos sem travar; offline.
- **Critério de aceite:** E2E de seleção nos dois sentidos.
- **Evidência de conclusão:** vídeo.
- **Risco:** performance. Clusters e virtualização.
- **Relação com a estratégia:** pedido 1 do analista.

#### S20-T10 · Aceite do pilar P6: `home_100`
- **Objetivo:** provar a home nova.
- **Contexto:** critérios do pilar P6.
- **Problema atual:** sem teste único.
- **Estado desejado:** E2E Playwright + roteiro de usabilidade.
- **Dependências · Pré-requisitos:** S20-T1 a T9 · nenhum.
- **Arquivos prováveis:** `frontend-next/tests/e2e/home_100.spec.ts`.
- **Implementação esperada:** (1) home sem seleção não mostra dado de equipamento; (2) cards com contagens corretas; (3) clicar "Críticos" filtra mapa e lista; (4) lista mostra PR, PLM e ação; (5) abrir detalhe mostra tendências com banda de normalidade; (6) painel do componente com escada; (7) seleção mapa ↔ barra; (8) funciona offline; (9) teste dos 30 s com pessoa de fora.
- **Testes necessários:** 3 execuções.
- **Critério de aceite:** 3/3 verdes + usabilidade dentro da meta.
- **Evidência de conclusão:** vídeo + relatório.
- **Risco:** baixo.
- **Relação com a estratégia:** fecha P6.

---

### SEMANA 21 · VALOR PARA O INVESTIDOR E PARA O GESTOR

**Camadas:** BUSINESS VALIDATION · DOCUMENTATION · IMPLEMENTATION
**Pilar:** transversal (sustenta o argumento de todos os pilares)

- **Objetivo estratégico:** transformar "ferramenta bonita" em **proposta com prova** para quem decide e investe: menos manutenção desnecessária, aviso antecipado, decisão rastreável, dado confiável e operação offline, tudo **medido**.
- **Objetivo técnico:** ledger de valor por decisão (premissas do cliente, sem valor padrão); relatório do investidor/gestor; data room técnico gerado do repositório; mapa vivo problema → solução → métrica → evidência; demonstração do cenário da bomba; matriz de diferenciais **com fontes**; modelo interno de implantação (fora do pitch).
- **Por que existe:** o analista disse que, como estava, seria "o que qualquer empresa já tem"; a Paola pediu "solução pros problemas reais dos investidores". O professor mandou **não falar de finanças no pitch**; o valor existe **no produto e na conversa de piloto**.
- **Problemas que resolve:** diferencial não demonstrável; ausência de prova de valor; comparação com concorrentes sem fonte.
- **Dependências recebidas:** S19 (precisão, laudo), S16-T8 (auditoria), S14 (offline), S12 (pitch e entrevistas).
- **Entregáveis:** `ValueLedger`, relatório PDF/HTML, `docs/DATA_ROOM/`, `docs/PROBLEMAS_REAIS.md`, `docs/MATRIZ_DIFERENCIAIS.md`.
- **Arquivos/módulos afetados:** `models.py`, `services/{ledger,investor_report,evidence_bundle}.py`, `docs/*`.
- **Arquitetura:** `Laudo + Decision + OS → ledger → relatório`. **Banco:** `ValueLedger`. **Backend:** serviços. **Frontend:** tela do relatório. **Hardware:** nenhum. **ML/IA:** nenhum novo. **Infra:** geração de pacote de evidências. **Segurança:** relatório por organização. **Testes:** cálculo do ledger. **Docs:** data room e matriz.
- **Experimentos:** simular 20 decisões com e sem a escada e comparar custo desperdiçado (cenário de teste rotulado).
- **Critérios de aceitação:** nenhum número financeiro sem premissa do cliente; matriz com fonte em cada linha.
- **Métricas:** precisão, cobertura, MTTA/MTTR, % ações desnecessárias evitadas (medido no ledger), disponibilidade do enlace.
- **Evidências esperadas:** relatório de exemplo, data room, matriz.
- **Riscos:** parecer financeiro inventado (**proibido**); comparação injusta com concorrente.
- **Decisões:** D-24 (custo opcional), D-60 (matriz de diferenciais).
- **Perguntas abertas:** quais custos o cliente aceita informar? (entrevistas).
- **Definition of Done da fatia:** relatório de exemplo gerado com dados de teste e data room completo.

#### S21-T1 · Ledger de valor por decisão
- **Objetivo:** mostrar, **decisão a decisão**, o que a ferramenta evitou ou desperdiçou.
- **Contexto:** o analista descreveu o custo de recomendar errado (tempo, disponibilidade, custo).
- **Problema atual:** sem registro de valor.
- **Estado desejado:** `ValueLedger(decision, classe ∈ {acao_necessaria, acao_desnecessaria, falha_evitada, falha_nao_detectada}, horas_parada_evitadas?, horas_parada_ocorridas?, custo_acao?, custo_evitado_estimado?, fonte_premissa)` preenchido a partir do **laudo** e de premissas **informadas pelo cliente**; **sem valor padrão**; campos vazios ficam vazios.
- **Dependências · Pré-requisitos:** S19-T2, S19-T3, S9-T4 · nenhum.
- **Arquivos prováveis:** `models.py`, `services/ledger.py`.
- **Implementação esperada:** `custo_desperdicado = custo_acao` quando `achado = nao_confirmado`; `custo_evitado_estimado` só com premissa explícita (rótulo "estimativa com premissa do cliente").
- **Testes necessários:** sem premissa, nenhum valor financeiro é calculado; com premissa, cálculo confere à mão.
- **Critério de aceite:** testes verdes.
- **Evidência de conclusão:** testes.
- **Risco:** número virar manchete. Não vai ao pitch.
- **Relação com a estratégia:** prova de valor honesta.

#### S21-T2 · Relatório do investidor e do gestor
- **Objetivo:** um documento que responde "a ferramenta acerta e vale a pena?".
- **Contexto:** gestor e investidor querem precisão, tempo de decisão e disponibilidade.
- **Problema atual:** relatório de turno (S17-T7) não cobre isso.
- **Estado desejado:** relatório por período: **precisão por nível (IC e n)**, cobertura, abstenção, **antecedência média de aviso**, **tempo até a decisão**, ações desnecessárias evitadas (ledger), disponibilidade, qualidade de dado (% descartado), enlaces; PDF/HTML offline, assinado com hash da cadeia.
- **Dependências · Pré-requisitos:** S19-T9, S21-T1, S17-T7 · nenhum.
- **Arquivos prováveis:** `services/investor_report.py`, `src/app/relatorio-executivo/page.tsx`.
- **Implementação esperada:** selo "amostra pequena" quando n < N; nunca esconder o n.
- **Testes necessários:** relatório de dataset de teste confere com cálculo manual.
- **Critério de aceite:** relatório gerado offline.
- **Evidência de conclusão:** arquivo.
- **Risco:** amostra pequena enganar. Selo.
- **Relação com a estratégia:** conversa de piloto e due diligence.

#### S21-T3 · Data room técnico gerado do repositório
- **Objetivo:** responder a due diligence **com evidência**, em um pacote.
- **Contexto:** `CLAIMS_VS_CODE.md`, relatórios, testes.
- **Problema atual:** evidências espalhadas.
- **Estado desejado:** `docs/DATA_ROOM/` gerado por script: arquitetura, matriz de claims, resultados dos testes de aceite (`prescricao_100`, `ia_offline`, `apagao_total`, `diesel_100`, `confianca_100`, `home_100`, soak), segurança, riscos conhecidos, roadmap, versões e hashes.
- **Dependências · Pré-requisitos:** S12-T2 · testes de aceite executados.
- **Arquivos prováveis:** `scripts/build_data_room.py`.
- **Implementação esperada:** o script **falha** se uma evidência referenciada não existir.
- **Testes necessários:** pacote reproduzível a partir do commit.
- **Critério de aceite:** pacote gerado sem links quebrados.
- **Evidência de conclusão:** pasta e hash.
- **Risco:** desatualizar. Gerado no CI.
- **Relação com a estratégia:** confiança do investidor.

#### S21-T4 · Mapa vivo: problema real → solução → métrica → evidência
- **Objetivo:** cada promessa tem prova.
- **Contexto:** tabela 0-A.3.
- **Problema atual:** problemas listados sem link de evidência.
- **Estado desejado:** `docs/PROBLEMAS_REAIS.md` com a tabela, atualizada com resultados das entrevistas (S12-T5/T12) e da medição.
- **Dependências · Pré-requisitos:** S12-T5 · nenhum.
- **Arquivos prováveis:** `docs/PROBLEMAS_REAIS.md`.
- **Implementação esperada:** coluna "validado por entrevista? (sim/não/parcial)".
- **Testes necessários:** revisão cruzada.
- **Critério de aceite:** nenhuma linha sem evidência ou marcada hipótese.
- **Evidência de conclusão:** documento.
- **Risco:** baixo.
- **Relação com a estratégia:** narrativa do pitch sem finanças.

#### S21-T5 · Demonstração do cenário "bomba com 70%"
- **Objetivo:** contar o problema do analista como **história com prova**.
- **Contexto:** `S19-T12`.
- **Problema atual:** demonstração genérica.
- **Estado desejado:** trecho de 90 s do roteiro de demo: antes (alerta que manda remover a bomba) vs depois (escada, laudo de campo, custo baixo, PR recalibrado).
- **Dependências · Pré-requisitos:** S19-T12 · nenhum.
- **Arquivos prováveis:** `docs/ROTEIRO_DEMO_BANCA.md`, vídeo.
- **Implementação esperada:** mesma pilha real; dados rotulados quando sintéticos.
- **Testes necessários:** 3 ensaios.
- **Critério de aceite:** analista reconhece o caso dele no vídeo.
- **Evidência de conclusão:** vídeo.
- **Risco:** caso "arrumado". Origem declarada.
- **Relação com a estratégia:** o diferencial em uma cena.

#### S21-T6 · Modelo interno de implantação (fora do pitch)
- **Objetivo:** saber o custo e o esforço de implantar, sem vender número.
- **Contexto:** professor: sem finanças no pitch.
- **Problema atual:** sem estimativa interna.
- **Estado desejado:** documento **interno** com tempo de instalação medido, peças, suporte, e hipóteses rotuladas; não aparece em slides.
- **Dependências · Pré-requisitos:** S17-T4, S17-T5 · nenhum.
- **Arquivos prováveis:** `docs/INTERNO_IMPLANTACAO.md`.
- **Implementação esperada:** tempos reais da S17-T4; preços do BOM com data.
- **Testes necessários:** nenhum.
- **Critério de aceite:** números vêm de medição ou cotação datada.
- **Evidência de conclusão:** documento.
- **Risco:** vazar para o pitch. Marcado "INTERNO".
- **Relação com a estratégia:** preparo para piloto.

#### S21-T7 · Matriz de diferenciais **com fontes** (o que "qualquer empresa já tem")
- **Objetivo:** responder ao analista com **comparação honesta**.
- **Contexto:** a crítica foi "seria o que qualquer empresa já tem".
- **Problema atual:** diferencial afirmado sem comparação.
- **Estado desejado:** tabela de capacidades (confiança explícita por dado, PR calibrado com laudo, PLM com abstenção, escada de confirmação, normalidade por sinal e regime, offline completo com decisão local, auditoria com hash, laudo estruturado) × produtos públicos de telemetria, **cada célula com fonte e data** ou "sem evidência pública (não significa que não exista)".
- **Dependências · Pré-requisitos:** S12-T7 · pesquisa de documentação pública.
- **Arquivos prováveis:** `docs/MATRIZ_DIFERENCIAIS.md`.
- **Implementação esperada:** nunca afirmar que o concorrente "não tem"; usar "não encontramos evidência pública em [fonte, data]".
- **Testes necessários:** revisão por quem não escreveu.
- **Critério de aceite:** nenhuma célula sem fonte.
- **Evidência de conclusão:** documento.
- **Risco:** comparação injusta. Linguagem controlada.
- **Relação com a estratégia:** defende o diferencial sem exagero.

---

## 16. DECISION REGISTER

| ID | Decisão | Contexto | Opções | Evidência | Trade-offs | Direção recomendada | O que validar | Consequências |
|---|---|---|---|---|---|---|---|---|
| D-01 | Valores do contrato de severidade v1 | 4 conjuntos de limiares divergentes | (a) 85 crítico (backend), (b) 110 (borda/front), (c) por modelo de máquina | `eventos.py:13`, `edge_client.py:44-48`, `metricThresholds.ts`, `limiares.md` | Baixo = mais alertas; alto = alerta tardio | **(a) 75/85 de bancada, com limite por modelo depois**; usar `>=` ou `>` e documentar | Especialista de manutenção por modelo (S12-T5) | Re-seed de demo; atualizar `limiares.md` |
| D-02 | Escala de `vibracao` | 3 escalas (0 a 10, g, 0 a 1) | índice 0-10 · g · RMS em g | `sensor_limits.py`, `metricThresholds.ts`, Proposta TCC | Compatibilidade vs significado físico | **Índice 0-10 no v1**; campos novos `vibracao_rms_g` etc. com acelerômetro | Calibração com MPU6050 (S8-T2) | Migração de unidade; gráfico com unidade correta |
| D-03 | Quando treinar Random Forest de risco | Sem rótulo real | agora com sintético · só com desfecho real | Ultimato 1.7, v2 D-03 | Sintético dá número bonito e falso | **Só com ≥ 200 decisões com desfecho** | Volume real de decisões | RF fica `DEFER`; IF + regras são o discurso |
| D-04 | Escopo de hardware do TCC | Zero firmware | (a) só simulador, (b) bancada física mínima | nenhum `.ino` | Hardware dá credibilidade, custa tempo | **(b) 1 ESP32 + DS18B20 + RTC primeiro**, depois ESP-NOW | Compra de peças e tempo | Comunicação separa bancada de campo |
| D-05 | Sessão do navegador | Token em `localStorage` | (a) manter, (b) cookie HttpOnly via BFF, (c) JWT | `SEGURANCA.md`, `route.ts` | (b) exige SW com `credentials` | **(b)** | SW + cookie funcionam juntos | Mudanças em `authService.ts` |
| D-06 | Credencial por dispositivo | Chave global de ingestão | (a) global, (b) hash por dispositivo, (c) certificado | `permissions.py` | (c) é pesado para a fase | **(b)** | Provisionamento na demo | `DeviceCredential` + script |
| D-07 | Faixas P1/P2/P3 | `priority_score` sem UI | cortes fixos · percentis · só severidade | `eventos.py` | Cortes arbitrários | **P1 ≥ 0,60; P2 ≥ 0,30; qualquer CRITICO é P1** (heurística documentada) | Teste de 5 s com leigos | `attention.v1.json` |
| D-08 | Treino de IF por máquina | 100 leituras | só contagem · critérios de qualidade | `anomaly_detection.py` | Mais critérios = menos máquinas com modelo | **Critérios de S5-T4** + baseline de grupo | Cobertura de máquinas com modelo | `pode_treinar()` exposto |
| D-09 | Agenda de manutenção | Pedido de calendário | interna · Google/Outlook · CMMS | Ultimato 1.7 vs 2.4 | Integração externa exige configuração real | **Interna + `.ics`; adaptador externo depois** | Qual agenda a usina usa | Sem OAuth nesta fase |
| D-10 | WhatsApp | Alertas por mensagem | API paga (Twilio/Z-API) · link `wa.me` · nada | `CLAUDE.md` (integração futura) | API exige custo e política | **Gerar mensagem e link, não enviar** | Interesse nas entrevistas | Sem token de API no repo |
| D-11 | Descarte quando o disco enche | Capacidade limitada | descartar mais antigo · agregar · parar | Ultimato 1.7 | Perder dado é inevitável em algum limite | **Agregar C, descartar C mais antigo registrando; A/B nunca sem alerta** | Capacidade medida (S6-T2) | Evento de perda visível |
| D-12 | TLS no gateway local | Hotspot sem HTTPS | HTTP local · TLS com CA própria | `SEGURANCA.md` | TLS local complica a demo | **SUPERADA pela D-35 (V4): HTTPS local é obrigatório para PWA e BLE** | Risco aceitável na demo | Documentar |
| D-13 | Histórico Git squashado | 1 commit | reescrever · manter + CHANGELOG | `git log` | Reescrever perde auditoria | **Manter + `CHANGELOG.md` e tags** | Nenhum | Narrativa preservada |
| D-14 | Política de números | Números sem fonte primária | usar · omitir · verificar | `pre-banca`, pesquisa referenciada | Impacto vs defensabilidade | **Só números verificados; senão não usar** | Fonte primária de cada um | `PITCH_FATOS.md` |
| D-15 | Confiança e prioridade | Fórmula multiplica | multiplicar · selo separado | `calcular_priority_score` | Ruído de sensor ruim | **Selo `needs_verification`, prioridade sem confiança** | Falso positivo por sensor ruim | `evidence_quality` |
| D-16 | Score de operador | Pedido de grid/score | fazer · adiar | n/a | Injustiça e risco jurídico | **DEFER** | Existência de política da usina | Registrado como decisão |
| D-17 | Três componentes de mapa | `MapClient`, `FleetMap`, `MapaFrota` | consolidar um | árvore de `components/` | Regressão visual | **Consolidar** | Teste visual | Menos código |
| D-18 | Dataset público de validação | Sem rótulo real | CWRU · AI4I · outro | Ultimato 2.6 | Transferência limitada | **Escolher após verificar licença/formato** | Licença, formato | Relatório S5-T5 |
| D-19 | Assinatura de mensagem no Mule | Mule não confiável | HMAC · assimétrica | S7-T3 | HMAC exige segredo compartilhado | **HMAC por dispositivo no v0.1**; assimétrica `ARCHITECT_NOW` | Custo no firmware | Campo `signature` |
| D-20 | Custódia de dados no Mule | Risco de apagar cedo | apagar ao entregar ao mule · ao ACK | S7-T2 | Mais armazenamento na origem | **Apagar só com ACK do backend** | Capacidade | Estados `COLETADO/ACKED` |
| D-21 | CAN no ESP32 | Leitura J1939 | MCP2515 · TWAI nativo + transceiver | Ultimato 2.7 vs hardware | MCP2515 é mais documentado em Arduino; TWAI poupa chip | **TWAI + transceiver** (confirmar suporte da biblioteca/placa); MCP2515 como plano B | Compatibilidade da placa | Dependência de transceiver |
| D-22 | RPM no protótipo | Sem sensor de rotação | sensor hall/óptico · potenciômetro declarado | Ultimato 1.1 | Potenciômetro é simulação | **Sensor real se possível; senão declarar simulação** | Peças | Selo SIMULADO |
| D-23 | Grafo operacional | Relações entre ativos | banco de grafos · tabelas relacionais | S9-T1 | Banco de grafos é overkill | **Relacional em Django** | Volume de relações | `MachineLink` |
| D-24 | Custo da hora parada | Impacto financeiro | valor padrão · premissa do cliente | professor: sem finanças no pitch | Valor padrão é inventado | **Sem padrão; opcional por organização** | Entrevistas | `OrganizationPolicy` |
| D-25 | Métricas | Observabilidade | só logs · Prometheus/Grafana | S10-T2 | Mais peças no Compose | **Prometheus; Grafana em perfil opcional** | Recursos do notebook de demo | `/metrics` |
| D-26 | Provedor de deploy | Render/Railway/VPS | citados em `CLAUDE.md` | n/a | Custo e TLS | **Decidir após S2; demo não depende de nuvem** | Orçamento do grupo | `DEPLOY.md` |
| D-27 | Rótulo dos formatos de exemplo | Risco de parecer integração | rotular · omitir | S11-T4 | Menos "wow" | **Rotular "inspirado em formato público"** | Nenhum | Honestidade |
| D-28 | Versionamento de mapeamento | `mapping_version` | semver · data | `FabricanteMapping` | Complexidade | **semver + changelog** | Nenhum | Reprocessamento possível |
| D-29 | Demo no palco | Pitch com vídeo narrado | ao vivo · vídeo | `pre-banca` | Ao vivo = risco; vídeo = menos prova | **Vídeo narrado no palco; ao vivo na feira** | Ensaio | Dois materiais |
| D-30 | Rebalanceamento do próximo ciclo | Entrevistas | por preferência · por evidência | S12-T6 | Preferência é confortável | **Por evidência** | Resultado das conversas | `PROXIMO_CICLO.md` |
| D-31 | Orçamento e compras de hardware | Hardware desde o dia 1 | pedir tudo agora · por etapa | S8-T10 | Etapas reduzem custo, atrasam o caminho crítico | **Pedir o kit mínimo na semana 1 e o restante na 3** | Orçamento do grupo | Lead time no soak |
| D-32 | HLC só para domínio | Replicação | CRDT geral · HLC + autoridade | S13-T4 | CRDT geral é complexo | **HLC + autoridade para domínio; telemetria append-only** | Casos de conflito reais | `DomainChange` |
| D-33 | Autoridade de dados | Edição nos dois lados | último a escrever · autoridade por origem | S13-T6 | "Último vence" perde decisão | **Quem nasceu, é dono; nuvem propõe** | Aceitação do operador | `Proposal` |
| D-34 | Hardware do gateway | Pilha completa + ML local | Raspberry · mini-PC | S13-T1, S15-T13 | Raspberry é barato; mini-PC aguenta LLM e MySQL melhor | **Mini-PC como alvo da demo; Raspberry testado como variante** | Benchmark de S13-T1 e S15-T13 | Custo e consumo |
| D-35 | HTTPS no gateway (**substitui D-12**) | Service Worker e BLE exigem contexto seguro | HTTP · CA local · domínio+cert | S13-T12 | CA local exige instalar raiz no celular | **CA local no piloto; domínio+cert se houver domínio** | Celular de teste sem internet | Procedimento no kit |
| D-36 | Topologia LoRa | Gateway fixo vs no veículo | silo/torre · veículo · ambos | S14-T3 | Fixo cobre mais; veículo acompanha | **Decidir após campanha de alcance** | Mapa de RSSI | Onde instalar |
| D-37 | Satélite | Modem e plano | candidatos pesquisados | S14-T7 | Custo recorrente | **Gate de compra na semana 3; sem modem, OFF-14 fecha por LoRa+relay+BLE** | Preço e cobertura atuais | Orçamento mensal |
| D-38 | BLE só Android | Web Bluetooth | Android · app nativo | S14-T6 | iPhone não suporta Web Bluetooth | **Android-first** | Aparelhos dos operadores | Limite declarado |
| D-39 | Critério de adoção de modelo | Vários candidatos | melhor métrica · gate multi-critério | S15-T5, T9 | Gate pode barrar modelo bom | **Gate: PR-AUC ≥ campeão, falso alarme ≤, TTD ≤ +10 %** | Sensibilidade do gate | Registro de decisões de modelo |
| D-40 | RAG: BM25 vs embeddings | Copiloto offline | BM25 · embeddings locais · híbrido | S15-T12 | Embeddings pesam no hardware | **BM25 primeiro; embeddings se couberem** | Qualidade no conjunto de 50 perguntas | Dependências extras |
| D-41 | LLM local | Hardware do gateway | modelo/porte | S15-T13 | Modelos maiores = mais lentos | **Escolher após benchmark real e licença** | Tempo de resposta | Selo "desligado por hardware" se não couber |
| D-42 | Formato de playbook | Conteúdo técnico | YAML versionado · banco | S16-T1 | YAML em Git dá histórico | **YAML + schema + revisão** | Facilidade para mecânico | Ferramenta de edição |
| D-43 | Revisão e validade de playbook | Responsabilidade técnica | sem revisão · revisão assinada | S16-T10 | Revisão custa tempo | **Só `vigente` após revisão; validade obrigatória** | Disponibilidade do mecânico | Selos |
| D-44 | Função objetivo do otimizador | Prescrição ótima | menor atraso · menor risco ponderado · menor parada em janela crítica | S16-T6 | Pesos arbitrários | **Risco ponderado por consequência, restrito por janelas** | Aceitação do supervisor | Explicação obrigatória |
| D-45 | Índice de risco térmico | Incêndio | limiar · taxa + delta entre pontos | S17-T1 | Mais sinais, mais calibração | **Absoluta + taxa + delta, calibrado no rig** | Falso alarme em operação | Aviso de não substituir supressão |
| D-46 | OTA | Atualização em campo | USB · OTA assinada com rollback | S17-T3 | Segurança vs conveniência | **OTA assinada, rollout escalonado** | Falha induzida | Partições A/B |
| D-47 | Subsistema-âncora do foco diesel | Analista pediu uma parte a fundo | combustível alta pressão · arrefecimento · lubrificação · admissão/turbo | exemplo da bomba de alta dado pelo analista | Uma parte dá profundidade, mas reduz generalidade | **Sistema de combustível diesel de alta pressão (common rail)** | Que sinais o motor publica (S18-T2) | Catálogo e HIs específicos |
| D-48 | Definição de percentual de recomendação (PR) | "Porcentagem de recomendação" | probabilidade calibrada de confirmação · score arbitrário · vida útil % | exemplo do laudo com 70 % | Calibrado exige laudos; arbitrário engana | **P(laudo confirma o achado \| evidência), calibrado, com IC, `n` e selo provisório** | Volume de laudos | Nunca exibir sem `n` |
| D-49 | Regra do PLM | "Tempo-limite para manutenção" | mediana · quantil conservador · quantil − margem | S19-T6 | Mediana atrasa; conservador antecipa mais | **Quantil 10 % do tempo até o limite menos margem, em horas de motor; "sem prazo confiável" quando faltam condições** | Cobertura do intervalo no backtest | Mais inspeções leves, menos falhas |
| D-50 | Fonte do limite do indicador | Prognóstico precisa de limite | manual do fabricante · perfil de sessões saudáveis (q99) | S18-T5 | Manual é mais forte; nem sempre disponível | **Manual quando houver; senão perfil q99 rotulado** | Acesso ao manual do motor | Rótulo do limite na UI |
| D-51 | Laudo como verdade de campo | Calibrar PR | opinião do sistema · laudo do técnico · bancada | S19-T2 | Laudo é subjetivo, mas é a referência do negócio | **Laudo assinado do técnico; medições de bancada anexadas** | Variação entre técnicos | `laudo.v1` imutável |
| D-52 | Armazenamento de séries multicanal | Mais de 10 sinais a 1 Hz | tudo no MySQL · arquivos por sessão + janelas no banco | S18-T4 | Volume vs consulta | **Bruto em Parquet/ZSTD por sessão + janelas no banco** | Volume medido | `SignalWindow` |
| D-53 | Níveis da escada de confirmação | Evitar remover peça boa | 1 passo · 4 degraus | S19-T7 | Mais degraus = mais atrito | **4 degraus (monitorar, verificar sem desmontar, teste no veículo, remover)** | Aceite do mecânico | `pr_min` por degrau calibrado |
| D-54 | Meta de precisão e política de recomendação | Analista quer assertividade | número fixo · definido com o analista e por laudos | S19-T8 | Número cravado cedo é inventado | **Fechar com o analista e revisar a cada rodada de laudos** | Curva precisão × cobertura | Política por organização |
| D-55 | Estrutura da home | Decisão rápida | layout atual · seleção + mapa + cards | pedido do analista | Menos informação na entrada | **Barra de seleção + mapa + cards; dados só após seleção; máx. N elementos** | Teste de 5 s e 30 s | "Avançado" para o resto |
| D-56 | Metas de usabilidade | "Decisão rápida" medida | sem meta · metas por tarefa | S20-T8 | Meta arbitrária | **T1 ≤ 5 s; T2 ≤ 30 s (a confirmar com o analista)** | Rodadas de teste | Iteração de UI |
| D-57 | Motor e forma de acesso | Foco diesel | gerador+banco de carga · trator · caminhão/oficina · bancada de bomba | S18-T1 | Gerador permite degraus de carga | **Gerador com banco de carga (se houver ECU) + banco de provas de oficina; plano B documentado** | ECU e autorização | Selo SIMULADO quando aplicável |
| D-58 | Falhas permitidas no motor | Segurança | destrutivas · reversíveis supervisionadas | S18-T11 | Reversíveis geram menos exemplos | **Somente reversíveis, aprovadas e supervisionadas pelo mecânico** | Autorização | Poucos rótulos de falha; compensados por oficina |
| D-59 | Sensores na linha de combustível | Mais sinais | qualquer ponto · só baixa pressão | S18-T12 | Segurança vs informação | **Alta pressão apenas pela ECU; sensores externos só em baixa pressão e por mecânico** | Estanqueidade | Regras de instalação |
| D-60 | Matriz de diferenciais | "Qualquer empresa já tem" | afirmar · comparar com fonte | S21-T7 | Comparar com fonte é mais lento | **Cada célula com fonte e data; "sem evidência pública" ≠ "não tem"** | Pesquisa de documentação | Linguagem controlada |

---

## 17. VALIDATION PLAN

| Camada | Como valida | Quando | Evidência |
|---|---|---|---|
| Contrato único | Teste de paridade com fixtures de fronteira | S1 | `test_contract_parity.py` verde |
| Ingestão/idempotência | Testes existentes + queda entre envio e ACK | S1 | S1-T6 |
| Segurança | Matriz de isolamento, abuso (throttle, ACL), varredura de segredo | S2, S10 | S2-T6, gitleaks |
| Trust Score | Casos controlados (sensor travado, lacuna, hora não confiável) | S1, S3 | testes + capturas |
| Front integrado | E2E sem mock + `grep` de `mockData` | S3 | vídeo + CI |
| Decisão/OS | Máquina de estados + exportação `.ics` | S4 | testes + captura |
| IA | `make eval` com cenários e dataset público | S5 | `AVALIACAO_ANOMALIA.md` |
| Offline | Protocolo com falhas, 3 execuções | S6 | `PROTOCOLO_TESTE_RESILIENCIA.md` |
| Mule | Rede isolada real, adulteração detectada | S7 | S7-T3 |
| Hardware | Bancada com sensor físico, 50 cortes de energia, PER por distância | S8 | vídeo + tabelas |
| Consequência | Cenários golden sem número inventado | S9 | testes |
| Operação | CI, restore, carga | S10 | relatórios |
| UMM | Convergência de fontes | S11 | `test_umm_conformidade.py` |
| Comercial | 5 a 6 entrevistas por papel | S12 (iniciar na S3) | relatório |
| Sistema completo | 3 ensaios cronometrados com pessoa de fora | S12 | vídeo |

### 17.1 Plano de validação adicional V4

| Camada | Como valida | Quando | Evidência |
|---|---|---|---|
| Hardware | Escada de integração (S8-T14), 50 cortes de energia | Sem. 1 a 4 | tabela por degrau |
| CAN real | Conferência contra painel/scanner | Sem. 6 | S8-T12 |
| Gateway offline | **Apagão total** com reboot (3×) | Sem. 7 e 11 | S13-T8 |
| Replicação | Matriz de conflitos e ida-e-volta | Sem. 6 | S13-T5/T6 |
| Enlaces | PER/RSSI por distância e ambiente; failover com hardware | Sem. 3 a 8 | S14-T3, T8 |
| Longa duração | **Soak 14 dias** (#1 e #2) | Sem. 4 a 7, 9 a 11 | S14-T9 |
| IA | Comparação por sessão, calibração, drift, **IA offline** | Sem. 4 a 10 | S15-T5, T7, T9, T15 |
| Copiloto | 50 perguntas + 30 adversariais | Sem. 8 a 10 | S15-T14 |
| Prescrição | **prescricao_100** por pessoa de fora | Sem. 8 e 11 | S16-T9 |
| Otimizador | 5 cenários com solução conhecida | Sem. 6 a 8 | S16-T6 |
| Risco térmico | Rampa conhecida no rig | Sem. 9 | S17-T1 |
| OTA | 10 atualizações com falha induzida | Sem. 10 | S17-T3 |

### 17.2 Plano de validação adicional V5

| Camada | Como valida | Quando | Evidência |
|---|---|---|---|
| Acesso ao motor | Autorização e primeira escuta | Sem. 1 a 2 | `MOTOR_E_ACESSO.md` |
| Sinais do motor | Conferência de ≥ 3 sinais contra painel/scanner | Sem. 2 | `CATALOGO_SINAIS_MOTOR.md` |
| Desclassificação | Injeção de dado irreal: 100 % descartado/duvidoso | Sem. 3 | teste S18-T6 |
| Normalidade | Perfil em sessões A, avaliação em B | Sem. 3 a 4 | relatório de falso desvio |
| DTC | Conferência com scanner | Sem. 4 | tabela de conferência |
| Indicadores | Separação bom × reprovado (oficina) | Sem. 5 | gráficos |
| PR | Reliability diagram, ECE | Sem. 6 a 7 | `AVALIACAO_PR_PLM.md` |
| PLM | Cobertura do intervalo em sessões não vistas | Sem. 7 | `AVALIACAO_PR_PLM.md` |
| Escada | Cenário "bomba com 70%" | Sem. 8 e 11 | `confianca_100.py` |
| Home | Teste dos 5 s e 30 s; SUS | Sem. 8 e 9 | `USABILIDADE_HOME.md` |
| `diesel_100` / `confianca_100` / `home_100` | 3 execuções cada | Sem. 9 a 11 | vídeos |

---

## 18. TESTING STRATEGY

- **Unitários:** toda função pura nova (`contracts.py`, `consequence.py`, `j1939.py`, `reconstrucao.py`, `regime.py`) com tabela de casos de fronteira, inclusive valores exatos de limiar.
- **Contrato/paridade:** fixtures únicas consumidas por backend, borda, firmware (teste nativo) e front.
- **Integração:** `APIClient` + MySQL no CI; MQTT com broker de teste; Mule em rede Docker isolada.
- **Sistema/E2E:** Playwright sem mock de resposta; roteiro de demo como teste de sistema; protocolo de resiliência.
- **Resiliência e falha:** kill entre envio e ACK, servidor 500 no meio do lote, disco cheio, hora regressiva, lote de 6 h atrasado, replay em massa, mensagem adulterada.
- **Segurança:** acesso cruzado entre organizações (matriz), anti-spoof de tópico, throttle, injeção de prompt em campo de texto de decisão, segredos em log.
- **ML:** cenários rotulados, reprodutibilidade por semente, separação treino/avaliação, comparação com baseline simples.
- **Frontend:** estados (loading, vazio, desatualizado, offline, erro, inválido), axe (acessibilidade), mobile 390×844.
- **Hardware:** testes nativos do firmware, ensaios de corte de energia, medição de PER.
- **Carga:** perfis de 10, 50, 200 dispositivos; lote de 500; replay de 6 h.
- **Regra:** teste que passa em SQLite e falha em MySQL é falha. Divergências registradas em `docs/BASELINE.md`.
- **Sobre a quantidade:** o número de testes **não** é métrica de qualidade. Métrica é: cenários importantes cobertos e falhas conhecidas reproduzidas.

### 18.1 Estratégia de testes adicional V4

- **Hardware-in-the-loop:** testes que exigem placa ligada ficam em `firmware/tests/bancada/` com roteiro e evidência; testes nativos (host) rodam no CI.
- **Soak:** teste de longa duração com métricas automáticas; reiniciar o relógio quando houver falha corrigível.
- **Apagão total e IA offline:** scripts com asserts por etapa e vídeo contínuo.
- **Divisão por sessão em ML:** teste automático que falha se uma sessão aparecer em treino e teste.
- **Conflito de replicação:** matriz completa de combinações (S13-T6).
- **Segurança de enlace:** adulteração, replay e chave errada (S14-T12).
- **Segurança física:** protocolos escritos antes de qualquer teste com calor, corrente ou veículo.

### 18.2 Estratégia de testes adicional V5

- **Golden de decodificação** de DM1/PGN com vetores públicos e conferência manual.
- **Teste de vazamento:** descartado nunca aparece em média, perfil, tendência, PR ou PLM.
- **Calibração:** dados sintéticos com probabilidade conhecida devem reproduzir ECE baixo; n pequeno ⇒ provisório.
- **Backtest por sessão/componente**, sem embaralhar.
- **Política:** mudar τ muda quem é recomendado e gera auditoria.
- **Usabilidade:** roteiro fixo, gravação, SUS.
- **Segurança de teste físico:** protocolos escritos antes de qualquer ensaio no motor.

---

## 19. FIELD VALIDATION STRATEGY

Sequência obrigatória (Leviatã fase 19). **Estado atual honesto entre colchetes.**

| Degrau | Como validar | Critério de saída | Estado hoje |
|---|---|---|---|
| 1. Log local | Gravação e reprodução de sessões | Sessão reproduz decisões idênticas | **parcial** (simulador) |
| 2. Dispositivo simulador em bancada | `edge_client` + `teste_resiliencia` | Números publicados (S6-T5) | **código existe, resultado não publicado** |
| 3. Simulação de condições de campo | Rede isolada, quedas longas, Mule em rede real | Protocolo S7 verde | **não iniciado** |
| 4. Hardware real em bancada | ESP32 + sensores + RTC + corte de energia | Vídeo e métricas de S8 | **não iniciado (zero firmware)** |
| 5. Hardware em máquina real | Instalação em colhedora, com autorização da usina | Duas semanas de dados reais | **hipótese, depende de S12-T5** |
| 6. Piloto (5 a 10 máquinas) | Uma usina, um problema, métricas de sucesso definidas | Redução de falso alarme e tempo de reação medidos | **hipótese; não prometer** |

Regra: não anunciar um degrau antes de cumprir o critério de saída do anterior.

### 19.1 Validação de campo V4 (estado atual → alvo)

| Degrau | Alvo V4 | Estado atual |
|---|---|---|
| 1. Log local | sessões reais gravadas (S15-T1) | parcial (simulador) |
| 2. Bancada física | S8-T1 a T6 (**semana 1 a 4**) | não iniciado |
| 3. Rede local isolada | S13-T8 (apagão total) | não iniciado |
| 4. Rádio em campo | S14-T3 (alcance LoRa medido) | não iniciado |
| 5. **Soak de 14 dias sem internet** | S14-T9 | não iniciado |
| 6. Escuta de barramento em veículo real | S8-T12 (listen-only) | não iniciado |
| 7. Máquina agrícola real (instalação) | S12-T11 (acesso/piloto) | hipótese |
| 8. Piloto de 2 semanas em operação | S12-T11 | hipótese |

*O degrau 7 e 8 dependem de autorização de terceiros; os degraus 1 a 6 dependem só do grupo.*

### 19.2 Validação de campo V5 (degraus adicionais)

| Degrau | Alvo | Estado atual |
|---|---|---|
| Escuta de barramento de **motor diesel** | S18-T2 | não iniciado |
| Banco de provas de oficina com laudo | S18-T9 | não iniciado |
| Campanha com degraus de carga | S18-T10 | não iniciado |
| Falha reversível supervisionada | S18-T11 | não iniciado |
| Primeiros laudos de campo | S19-T2 | não iniciado |
| Piloto com laudos reais de ≥ 1 operação | S12-T11 | hipótese |

---

## 20. COMMERCIAL VALIDATION STRATEGY

1. **Quem entrevistar:** os 5 papéis de S12-T4. Mínimo 5 a 6 conversas, 3 papéis diferentes.
2. **O que perguntar:** decisões com dado atrasado, alerta que mais incomoda, custo de parada **segundo o entrevistado**, como o mecânico é acionado, quais sistemas usam e se exportam, quais marcas há, o que justificaria testar.
3. **O que **não** fazer:** "você usaria?", mostrar preço, prometer funcionalidade, apresentar número de impacto sem fonte.
4. **Comparações com Solinftec, John Deere, Case IH:** só com fonte documentada; "não encontramos evidência pública" **≠** "eles não têm".
5. **Hipóteses a testar (cada uma com critério de refutação):**

| Hipótese | Refutada se | Efeito no roadmap |
|---|---|---|
| H1: frotas mistas sofrem com portais separados | Nenhum entrevistado cita múltiplos portais | rebaixar S11 |
| H2: existe trecho sem sinal sem visibilidade que gera prejuízo | Todos dizem ter cobertura ou rádio próprio | rebaixar S6 a S8 como argumento comercial |
| H3: alerta com falso positivo é dor | Ninguém reclama de alerta | reduzir S3-T3, S4-T6 |
| H4: OS é digitada manualmente | Já existe CMMS integrado | rebaixar S4-T4 |
| H5: dado com confiança explícita muda decisão | Ninguém se importa com qualidade do dado | revisar o pilar 2 da tese |

6. **Precificação:** tratada como **hipótese interna**; fora do pitch (orientação do professor).
7. **Registro de viés:** entrevistas com pessoas próximas (professor com experiência na Solinftec, contatos da região de Araçatuba) são úteis e **enviesadas**; anotar.

### 20.1 Validação comercial V4

- Meta de amostra: **8 a 10 conversas** com pelo menos 3 de manutenção e 2 de operação (S12-T12), e **busca ativa de carta de intenção/piloto** (S12-T11).
- Hipóteses novas a testar: **H6** o operador aceita alarme local e checklist no celular; **H7** a usina valoriza OS com evidência e verificação por telemetria; **H8** existe sinal de rádio/celular suficiente para LoRa/BLE nas frentes (ou o satélite é o único caminho); **H9** o mecânico reconhece nos playbooks o procedimento real.
- Critério: hipótese refutada rebaixa a fatia correspondente (regra S12-T6).

### 20.2 Validação comercial V5

- Perguntas novas nas entrevistas: **"quanto você aceita de recomendação errada antes de desconfiar da ferramenta?"**, **"o que você faz hoje antes de mandar uma peça para o banco de provas?"**, **"que sinais do motor você consulta?"**, **"você usaria um percentual de confiança? em que faixa agiria?"**.
- Hipóteses novas: **H10** o gestor prefere prescrição com percentual e prazo a alerta simples; **H11** a escada de confirmação reduz envio desnecessário de peça; **H12** o técnico aceita registrar laudo estruturado; **H13** os sinais do motor estão acessíveis na frota real.
- Critério: hipótese refutada rebaixa a fatia (regra S12-T6).

---

## 21. FINAL TARGET STATE (ao fim das fatias S0 a S12)

- **Arquitetura:** monólito modular com fronteiras claras; `contracts/` como fonte única; grafo operacional relacional; adaptadores de fonte.
- **Fluxo de dados:** sensor físico → (ESP-NOW ou MQTT) → outbox → Connectivity Manager → ingestão idempotente → Raw → Canonical (com proveniência) → Trust → Event (severidade + evidência) → Incident → Consequência → Decision estruturada → aprovação humana → OS (`.ics`) → desfecho → reavaliação → rótulo fraco.
- **Confiabilidade de telemetria:** score com fatores legíveis, hora com proveniência, selo "SIMULADO/medido" em toda tela.
- **Offline:** sincronização resiliente medida em simulador e bancada; Mule em rede real isolada; rádio **medido ou ausente das alegações**.
- **Conectividade:** interface `ConnectivityProvider`; `http`, `mqtt`, `mule` reais; `lora` e `sat` como estágio documentado.
- **Multi-OEM:** J1939 público em bancada + 2 formatos de exemplo rotulados; "fundação multimarca com adaptadores".
- **Eventos/correlação:** Event + Incident + consequência por regras explícitas.
- **Decisões:** estruturadas, rastreáveis, com resultado informado e verificação por telemetria.
- **IA:** IF por regime e por critério de dado, avaliado com métricas; LLM só explica com validação; sem alegação de previsão.
- **Interação:** Command Center sem mock, mapa mobile com bottom sheet, busca global, acessibilidade auditada.
- **Observabilidade:** `/metrics`, health em camadas, logs com identidade de mensagem, alertas para a equipe.
- **Segurança:** MQTT com ACL por dispositivo, credencial por dispositivo, throttle global, registro por flag, cookie HttpOnly, auditoria, isolamento **provado**.
- **Testes:** CI completo, E2E, contrato, carga, protocolo de resiliência.
- **Evolução para loop fechado:** ciclo básico fechado e demonstrável; autonomia supervisionada fica para depois, com trilha de auditoria.

### 21.1 Estado final alvo V4

Tudo da seção 21 **mais**: gateway-núcleo com pilha completa sem internet; replicação bidirecional sem duplicata; nó físico com sensores reais, alarme local e outbox em flash; enlaces LoRa, relay, BLE e satélite medidos; soak de 14 dias publicado; IA com dado real, 5 detectores comparados, MLOps e copiloto local; prescrição com playbooks revisados, checklist com evidências, otimizador e cadeia de auditoria; risco térmico, OTA, kit instalável e modo cabine; três pilares verificados por script e vídeo.

### 21.2 Estado final alvo V5

Tudo da V4 **mais**: foco profundo no sistema de combustível diesel de alta pressão com ≥ 8 sinais do motor, perfil de normalidade por sinal e regime, dado irreal descartado e visível, DTC ligado a componente, indicadores de saúde; **PR calibrado com laudos (provisório com n visível)**; **PLM em horas de motor com intervalo e abstenção**; **escada de confirmação**; política por organização; painel de precisão; **decisão final do técnico** registrada; home nova com seleção + mapa + cards clicáveis; ledger e relatório com premissas do cliente; data room e matriz de diferenciais com fonte.

---

## 22. INVESTOR / CTO PRESSURE TEST

| Pergunta difícil | Resposta honesta ao fim do ciclo (cada uma aponta evidência) |
|---|---|
| Qual é o diferencial? | Três coisas verificáveis na tela: o dado diz quão confiável é e por quê; a fila de atenção separa gravidade de qualidade da evidência; cada decisão tem evidência, aprovação, OS e desfecho. Nenhuma é impossível de copiar; a combinação com prova medida é rara. |
| Por que não é só um dashboard? | Porque a decisão é um objeto persistido com estado, responsável, prazo e reavaliação por telemetria (S4). Dashboard mostra estado; aqui há ciclo fechado. |
| Por que não usar a solução do OEM? | Na telemetria básica eles estão à frente. A hipótese é frota mista e áreas sem visibilidade; **só está validada na medida das entrevistas** (S12-T5). |
| Onde está a propriedade tecnológica? | No contrato de identidade e sincronização, no modelo de confiança e na memória de decisão. Não há "algoritmo secreto". |
| Onde está o moat? | Ainda não existe moat. Existe fundação para um histórico portátil de decisões com desfecho; só vira vantagem com dado real e tempo. |
| Os dados são reais? | Parte: dado de bancada com sensor físico (S8), rotulado "medido". Todo o resto de volume é simulado e **rotulado** na interface. |
| A IA é defensável? | Detecção de anomalia não supervisionada com métricas publicadas em cenários sintéticos e validação do método em dataset público. **Não** prevemos falha nem vida útil; modelo supervisionado só com ≥ 200 decisões com desfecho. |
| Como funciona sem internet? | Dispositivo grava local, classifica A/B/C e sincroniza com idempotência; alerta local sai sem nuvem; números de perda/duplicata/recuperação estão no protocolo. O que **não** provamos: alcance de rádio em campo e Mule físico a quilômetros. |
| Como escala? | Monólito modular, ingestão idempotente, índices revisados; relatório de carga com ponto de saturação observado; multi-tenancy por filtro de organização com prova de isolamento; isolamento por schema é `DEFER`. |
| Como protege dados? | MQTT com ACL por dispositivo, credencial por dispositivo, throttle, cookie HttpOnly, auditoria, matriz de isolamento. Não há criptografia ponta a ponta nem secure boot habilitado (documentado). |
| Como lida com múltiplos fabricantes? | Raw → Canonical com adaptadores; J1939 público em bancada e dois formatos de exemplo. Não há integração com API de fabricante. |
| Como prova que as decisões estão certas? | Ainda não prova estatisticamente; **registra** cada decisão, o desfecho informado e a verificação por telemetria, que é o pré-requisito para provar. |
| O que acontece quando o sistema erra? | Fica registrado como rejeitada/falso alarme, ajusta o limiar **daquela máquina** com teto de segurança e trilha, e vira rótulo fraco. |
| Qual parte foi validada em campo? | Nenhuma em máquina real. Validado em bancada física e simulação. |
| E se o sensor estiver mentindo? | O Trust Score cai, o evento aparece marcado "verificar sensor" e **continua visível**; nunca é escondido por baixa confiança. |
| O que o professor perguntou sobre IA? | "Onde está o modelo treinado?" Resposta: IF treinado por máquina com critérios de dado, versão registrada, avaliação com métricas e sem promessa de previsão. |

### 22.1 Pressure test atualizado V4

| Pergunta | Resposta honesta (V4, ao fim do ciclo) |
|---|---|
| "Funciona offline de verdade?" | A pilha inteira roda no gateway: detecção, prescrição, aprovação, OS, checklist e resultado, sem internet, com reboot no meio (S13-T8). Para a máquina a até 14 dias longe, alertas A chegam por LoRa, relay, celular ou satélite, com latência **medida** (S14-T9). |
| "E se não há nenhum sinal?" | O nó alarma localmente e guarda na flash; o satélite cobre o caso extremo para classe A; B e C chegam quando o mule/relay passar. Sem enlace não existe tempo real; o sistema não finge. |
| "A IA é de verdade?" | Cinco detectores comparados em sessões reais não vistas, incerteza calibrada, explicação por alerta, registro/drift/rollback e inferência local testada sem internet. **Não prometemos prever a quebra**; prometemos detecção precoce medida e prescrição. |
| "O chatbot não inventa?" | Responde só com fonte (playbook/histórico), cita a origem, recusa sem fonte, não executa ação sem aprovação; avaliado com 50 perguntas e 30 ataques. |
| "Isso é prescrição ou só alerta?" | Cada achado vira procedimento revisado por mecânico, com peças, tempo, segurança, ordem ótima de execução, verificação depois e detecção de reincidência (S16). |
| "Como garante que o histórico não foi alterado?" | Cadeia de hash verificável e replicada (S16-T8). |
| "O hardware é real?" | Sensores reais, CAN escutado em veículo real (só leitura), LoRa medido em campo. Máquina agrícola real: depende de autorização; hoje está em planejamento de piloto. |
| "Radio é seguro?" | Quadro com MAC truncado, contador anti-replay e cifragem por dispositivo; limite do MAC curto documentado (S14-T12). |
| "E o incêndio por rolamento?" | Módulo térmico multi-ponto com taxa de subida e alarme local (S17-T1); é indicador de risco e **não substitui** extintor/supressão. |

### 22.2 Pressure test atualizado V5

| Pergunta | Resposta honesta (V5) |
|---|---|
| "Qual a precisão?" | Medida em laudos reais, por nível, com intervalo e `n`. Sem laudo suficiente, o PR é **provisório** e a tela diz isso. Não afirmamos 100 %. |
| "E se vocês recomendarem errado?" | A recomendação passa por uma **escada de custo crescente**; o técnico decide; o laudo recalibra o sistema; o erro é registrado e medido. |
| "Quanto tempo de vida a bomba tem?" | **Não afirmamos vida útil.** Mostramos **prazo-limite de inspeção** em horas de motor com intervalo, ou "sem prazo confiável" quando não há base. A vida estimada vem do laudo do técnico. |
| "Por que diesel e por que essa parte?" | Foco pedido pelo analista: o sistema de combustível de alta pressão concentra o caso de custo (bomba) e tem sinais e DTC publicados pela ECU. |
| "Como sabem que o dado é bom?" | Qualidade por sinal e por janela; dado irreal é descartado e **não entra** em métrica; o descarte é visível. |
| "E se o motor não publica o sinal?" | O catálogo mostra o que existe; indicadores sem sinal ficam "não calculados"; sensores complementares não invasivos entram. |
| "O sistema decide?" | **Não.** O técnico decide; o sistema recomenda com evidência e confiança. |
| "O que isso tem que outra empresa não tem?" | Confiança calibrada com laudo, escada de confirmação, abstenção, normalidade por sinal/regime, operação offline completa e auditoria verificável. **Cada comparação tem fonte e data** (matriz S21-T7). |
| "Como vira dinheiro?" | Pelo **ledger com premissas do cliente**; sem valor padrão. Não é tema do pitch. |

---

## 23. OPEN QUESTIONS

1. Qual a **data da banca final**? (Define onde cortar em `[CORTE-BANCA]` e quanto de S7 a S11 cabe antes.)
2. O grupo tem acesso a um **ESP32, DS18B20, DS3231, MPU6050 e transceiver CAN** hoje? Giovana já tem protoboard com DHT (ambiente), que **não** mede temperatura de motor.
3. Há acesso a **um J1939 real** (máquina, simulador ou banco de teste) ou só emissor de bancada?
4. A **dor dominante** nas entrevistas é multimarca, alerta, OS manual ou conectividade? (S12-T6 reordena o próximo ciclo.)
5. A relação colhedora-transbordo é **fixa ou muda por turno**? (Afeta a validade temporal em `MachineLink`.)
6. A usina aceita **exportar** o histórico de manutenção (OS antigas) para criar o primeiro rótulo real? (Sem isso, o modelo supervisionado não existe.)
7. Qual o **critério de aceite do professor** para IA: modelo treinado, métrica, ou ambos? Alinhar antes de S5.
8. Quem mantém `CLAIMS_VS_CODE.md` atualizado a cada PR? (Atribuir um dono; proposta: Paola revisa, Ana confere.)
9. O `ChatFAB` fica na UI sem S5-T8? Regra: **não deixar botão que não faz o prometido.**
10. A outra equipe com ideia semelhante muda alguma decisão? Resposta atual: **não**; o diferencial é o que já está nesta lista, medido.

---

## 24. WHAT SHOULD NOT BE DONE YET (V4: o que continua fora e como a base é construída)

> Diferença para a V3: aqui **não há item "adiado por falta de base"**. O que a V3 adiava virou tarefa (seção 11.1). Ficam fora apenas coisas que o grupo **decidiu** não fazer (risco, custo ou falta de valor medido) e coisas que dependem de **terceiros**.

| Item | Por que continua fora | Condição/gate para entrar | Quando reconsiderar |
|---|---|---|---|
| **Afirmar "prevê a quebra da colheitadeira"** | Exige falhas reais confirmadas, medições anteriores à falha e validação temporal independente | A campanha, o rig e o feedback (S15-T1, T2, T11) começam a base de rótulos; só afirma com relatório | Depois de dados de piloto |
| Score de operador (nota por pessoa) | Risco jurídico e injustiça, **não** falta de base | Política da usina + validação | Se a usina pedir |
| LLM decidindo ou executando ações | Risco de segurança | Nunca sem aprovação humana | Autonomia supervisionada só com trilha completa |
| Integração real com APIs de OEM (Case/Deere/Solinftec) | Exige contrato e acesso | Parceria | Após validação comercial |
| Mesh LoRa com mais de 1 salto | Complexidade e risco de tempestade de pacotes | Medição do relay de 1 salto (S14-T4) justificar | Depois do soak |
| Secure boot e flash encryption **na placa de demo** | Irreversíveis; podem inutilizar a placa | Placa dedicada com plano de recuperação | Depois da banca |
| Microserviços/Kafka/Kubernetes | Não agrega valor medido | Gargalo medido | Só se carga exigir |
| App nativo mobile | PWA cobre; Web Bluetooth é Android-first | Demanda validada em iPhone | Depois das entrevistas |
| Multi-tenancy por schema | Sem cliente pagante | 2+ clientes em conversa | Depois da validação |
| Digital twin completo | O what-if estatístico (S16-T7) cobre a necessidade atual | Histórico e consequência maduros | Ciclos futuros |
| Deploy público antes da segurança | Risco | S2 + S10-T8 concluídos | Depois de S2 |
| Reescrita do front por estética | O problema é integração | n/a | Nunca por estética |


### 24.1 O que continua fora na V5 (e por quê)

| Item | Por que continua fora | Condição para entrar |
|---|---|---|
| Afirmar **"100 % de precisão"** | Não existe e não é defensável | nunca; usar precisão medida com IC |
| Afirmar **vida útil residual em % como fato** | Exige histórico de falha e validação | só após backtest e laudos suficientes (S19-T11) |
| Ação automática sem técnico | Responsabilidade e segurança | nunca; decisão final é do técnico |
| Medir na **linha de alta pressão** | Risco grave | nunca fora da ECU |
| Falha destrutiva em motor de terceiros | Risco e dano | só reversíveis supervisionadas |
| Recomendar remoção com PR baixo | Reproduz o problema do analista | política (S19-T8) bloqueia |
| Números financeiros padrão | Seriam inventados | só premissa do cliente |

---

## 25. FINAL LEVIATHAN VERDICT

### 25.1 Plano por níveis (V4)

- **NÍVEL 1 · Fundação (imprescindível):** S0, S1, S2, S3, S4, **S13**. Contrato único, segurança, front real, decisão → OS, **Gateway-Núcleo**.
- **NÍVEL 2 · Os três pilares (imprescindível, 100 %):** **P1** S16 + S4; **P2** S15 + S5; **P3** S6 + S8 + S13 + S14. Com seus testes de aceite (`prescricao_100`, `ia_offline`, `apagao_total`, soak de 14 dias).
- **NÍVEL 3 · Evolução estratégica:** S7, S9, S10, S12 (inclui piloto e entrevistas).
- **NÍVEL 4 · Diferenciação:** S17 (risco térmico e redundância primeiro), S11 (UMM real e Data Passport), autoencoder e acústica **se vencerem o gate**.
- **NÍVEL 5 · Visão futura:** previsão supervisionada de falha com dado de piloto, integrações reais com OEM, mesh de mais de 1 salto, autonomia supervisionada.

### 25.2 Priorização das tarefas de maior retorno (V4)

| Prioridade | Tarefa | Por quê |
|---|---|---|
| 1 | S8-T10 + S8-T1 (compras e primeira leitura física) | destrava o caminho crítico no dia 1 |
| 2 | S1-T1 (contrato único) | corrige o crítico que sai como classe C |
| 3 | S3-T1 (sem mock) e S3-T3/T4/T5 (Command Center) | diferencial invisível hoje |
| 4 | S8-T13 (EWMA/CUSUM + alarme local) | alarme sem rede |
| 5 | S14-T2/T3 (LoRa medido) e iniciar soak #1 | 14 dias não se aceleram |
| 6 | S13-T1 a T8 (Gateway-Núcleo + apagão total) | P3 e base do P1 |
| 7 | S15-T1/T2 (dados reais e rig) | base de toda a IA |
| 8 | S16-T1 (playbooks) + entrevistas de mecânico | conteúdo da prescrição |
| 9 | S15-T4/T5 (resíduo e comparação) | IA defensável |
| 10 | S16-T2/T3/T6 (prescrição v2, checklist, otimizador) | P1 |
| 11 | S14-T5/T6/T7 (mule físico, BLE, satélite) | camadas de cobertura |
| 12 | S12-T11 (piloto/acesso) | único caminho para "produto" |

### 25.3 Anti-hype e autocrítica deste documento

- **Este roadmap pode estar errado em:** (i) cortes P1/P2/P3 e limiares (são heurísticas de bancada, marcadas como calibráveis); (ii) estimativa de esforço (não há data da banca; as "semanas" são fatias); (iii) disponibilidade de hardware e de acesso a J1939; (iv) detalhes de especificação (PGN/SPN, limites de payload de ESP-NOW/LoRa, desgaste de flash) que **precisam ser conferidos nas fontes** no momento da tarefa; (v) a leitura do repositório foi estática, sem executar testes nem abrir a UI.
- **O que provavelmente falta:** requisitos de LGPD formais para dado de localização/operador; política de suporte a firmware (OTA); estratégia de calibração de sensores em campo; teste de usabilidade com operadores reais.
- **O que pode ser a parte menos útil:** S11 (UMM real) se as entrevistas mostrarem que a dor não é multimarca; S9 se não houver relações cadastráveis na prática; S7 se a conectividade não for a dor dominante. A regra S12-T6 existe para isso.
- **Contradições entre os blocos do Ultimato** foram listadas na seção 4.1 e resolvidas **pelo código**, não por preferência.

### 25.3.1 Autocrítica V4 (o que pode dar errado)

- **Capacidade:** o plano é grande; as quatro pistas exigem as quatro pessoas atuando em paralelo. Se uma pista parar, aplica-se a regra de corte (seção 0.6), **nunca** cortando os pilares.
- **Cadeia de suprimentos:** peças e modem satelital têm prazo; por isso a compra é tarefa da semana 1.
- **Regulação do rádio:** faixa, potência e certificação do módulo LoRa/satélite precisam ser conferidas na norma vigente **antes** de transmitir ao ar livre.
- **Segurança física:** testes com calor, corrente e veículo exigem protocolo escrito e supervisão.
- **Soak:** 14 dias corridos; falha corrigível reinicia o relógio. Por isso há dois soaks.
- **Conteúdo técnico:** playbooks e limiares só valem com revisão de mecânico; sem revisão, aparecem com selo.
- **Números:** metas de latência e limiares são **hipóteses** até medir.
- **Leitura estática:** este documento ainda não executou testes nem abriu a UI; S0-T1 continua sendo o primeiro passo de código.

### 25.4 O que existe ao fim do ciclo (checklist de entrega V4)

**Pilar P1 · PRESCRIÇÃO-100**
- [ ] Playbooks `vigente` revisados, `prescription.v2`, checklist com evidências, estoque, otimizador, what-if, reincidência, cadeia de auditoria.
- [ ] `prescricao_100.py` verde 3× (uma com reboot), vídeo contínuo, executado por pessoa que não escreveu o código.

**Pilar P2 · IA-100**
- [ ] Campanha de dados reais + rig de falhas, versionados.
- [ ] Comparação de 5 detectores por sessão, relatório publicado, gate D-39 aplicado.
- [ ] Incerteza calibrada, SHAP, MLOps (sombra, drift, rollback), diagnóstico, curva de falso alarme.
- [ ] Copiloto local avaliado (50 perguntas, 30 ataques) e **teste de IA offline** verde 3×.

**Pilar P3 · OFFLINE-100**
- [ ] Gateway-Núcleo com HTTPS local, login offline, PWA offline, ML local, replicação bidirecional.
- [ ] **Apagão total** verde 3× (com reboot de gateway e ESP32).
- [ ] Nó físico com sensores reais, EWMA/CUSUM, alarme local, outbox em flash.
- [ ] LoRa medido em campo, relay, mule físico de 3 ESP32, BLE, satélite (ou `BLOQUEADA_POR_COMPRA` documentado).
- [ ] **Soak de 14 dias** concluído (2 execuções) com relatório e latência por enlace.

**Fundação e produto**
- [ ] Contrato único verificado em backend, borda, firmware e front; zero mock em tela; selo SIMULADO/medido.
- [ ] CAN real escutado em veículo (listen-only) com conferência independente.
- [ ] Segurança: ACL por dispositivo, credencial por dispositivo, throttle, cookie HttpOnly, auditoria, isolamento provado.
- [ ] Risco térmico, OTA, kit instalável com QR, modo cabine, relatório de turno offline.
- [ ] CI verde, `/metrics`, backup/restore testado, relatório de carga.
- [ ] 8 a 10 entrevistas, pedidos de piloto enviados (e carta de intenção, se houver), `PROXIMO_CICLO.md`.
- [ ] `README.md` novo com GIF, `CLAIMS_VS_CODE.md` sem contradição, `PITCH_FATOS.md` com fonte por número.
- [ ] 3 ensaios cronometrados com pessoa de fora e plano de contingência.

### 25.1.1 Níveis V5

- **NÍVEL 1 · Fundação:** S0, S1, S2, S3, S4, S13 (V4).
- **NÍVEL 2 · Os seis pilares (100 %):** P1 prescrição, P2 IA, P3 offline (V4) **e P4 DIESEL, P5 CONFIANÇA, P6 HOME (V5)**, com `prescricao_100`, `ia_offline`, `apagao_total`, soak, `diesel_100`, `confianca_100`, `home_100`.
- **NÍVEL 3 · Evolução:** S7, S9, S10, S12, S21.
- **NÍVEL 4 · Diferenciação extra:** S17 (T1 e T2 primeiro), S11, autoencoder e acústica sob gate.
- **NÍVEL 5 · Visão futura:** previsão supervisionada validada por laudos de piloto, integrações com OEM, autonomia supervisionada.

### 25.2.1 Priorização V5 (foco no pedido do analista)

| Prioridade | Tarefa | Por quê |
|---|---|---|
| 1 | **S18-T1** (motor e acesso) | caminho crítico do foco |
| 2 | **S19-T1** (definições) e **S19-T2** (laudo) | sem laudo não há precisão |
| 3 | **S18-T2** (sinais publicados) | define o que dá para analisar |
| 4 | S20-T1/T2 (home e cards) | primeira impressão e pedido direto |
| 5 | **S18-T5/T6** (normalidade e desclassificação) | "padrões irreais descartados" |
| 6 | S18-T8, S19-T4/T5/T6 (HIs, PR, PLM) | o diferencial em si |
| 7 | **S19-T7** (escada) | evita o erro do analista |
| 8 | S19-T9/T10/T12 (painel, decisão, cenário) | prova e confiança |
| 9 | S18-T9 (oficina) | rótulos reais |
| 10 | S21-T7 (matriz) e S21-T1/T2 | resposta ao "qualquer empresa tem" |

### 25.4.1 Checklist de entrega V5 (soma-se ao da V4)

**P4 · DIESEL-100**
- [ ] Motor e autorização; catálogo com ≥ 8 sinais publicados pelo motor (ou plano B declarado).
- [ ] Contrato v2 multicanal; perfis por sinal e regime; qualidade por sinal com dado irreal descartado e visível.
- [ ] DTC decodificado e ligado a componente; ≥ 5 indicadores de saúde; dados de oficina; campanha; falha reversível (ou registro de não autorização).
- [ ] `diesel_100.py` verde 3×.

**P5 · CONFIANÇA-100**
- [ ] `DEFINICOES_CONFIANCA.md` aprovado; laudo estruturado em uso; falhas corretivas registradas.
- [ ] PR calibrado com IC, `n` e selo provisório; PLM com intervalo e abstenção; escada de confirmação; política por organização.
- [ ] Painel de precisão; decisão final do técnico com motivo; backtest publicado.
- [ ] Cenário "bomba com 70%" gravado; `confianca_100.py` verde 3×.

**P6 · HOME-100**
- [ ] Home com seleção + mapa; cards clicáveis; dados só após seleção; drill-down em ≤ 3 cliques.
- [ ] Painel do componente; medidor de PR; UI enxuta com "Avançado".
- [ ] Usabilidade: T1 ≤ 5 s e T2 ≤ 30 s (metas D-56) ou relatório honesto; `home_100` verde 3×.

**Valor**
- [ ] Ledger com premissas do cliente; relatório de precisão; data room; matriz de diferenciais com fontes; `PROBLEMAS_REAIS.md`.

### 25.5 Frase final

> **O FieldNode não precisa de mais uma camada de promessa; precisa que a próxima pessoa que abrir o repositório, a tela e o vídeo encontre exatamente o que o texto diz que existe, com número medido onde houver número e a palavra "simulado" onde for simulação, e essa honestidade, num cenário em que o outro grupo promete mais, é o que vai parecer produto.**

---

## APÊNDICE A · ÍNDICE DE TAREFAS (gerado do próprio documento)

| ID | Tarefa |
|---|---|
| S0-T1 | Baseline reproduzível |
| S0-T2 | Higiene do repositório |
| S0-T3 | Matriz de claims (CLAIMS_VS_CODE.md) |
| S0-T4 | Esqueletos dos documentos faltantes, com dono |
| S0-T5 | `AGENTS.md`: manter como contrato, trocar o cabeçalho |
| S0-T6 | Política de histórico e versionamento |
| S1-T1 | Contrato único de severidade e prioridade de transmissão |
| S1-T2 | Escala e unidade de vibração (resolver as três escalas) |
| S1-T3 | Separar severidade, qualidade da evidência e prioridade de atenção |
| S1-T4 | Fila do Service Worker por item (sem head-of-line blocking) |
| S1-T5 | Contrato de tempo para dispositivo sem relógio |
| S1-T6 | Semântica de ACK e remoção da outbox |
| S1-T7 | Dividir `views_ingestao.py` e impor limites |
| S1-T8 | Teste de contrato cruzado (golden files) |
| S2-T1 | MQTT com ACL por dispositivo e anti-spoof de tópico |
| S2-T2 | Throttle global, lockout e registro por flag |
| S2-T3 | Swagger e documentação fora de dev |
| S2-T4 | Chave do Gemini em header, sem vazar em log |
| S2-T5 | Sessão do navegador sem token em `localStorage` |
| S2-T6 | Matriz de isolamento entre organizações (acesso cruzado) |
| S2-T7 | Trilha de auditoria e normalização de rotas |
| S2-T8 | Credencial de ingestão por dispositivo e modelo de ameaças |
| S3-T1 | Remover mocks, criar `DataStateBoundary` e selo SIMULADO |
| S3-T2 | Clientes tipados e hook de dados |
| S3-T3 | Faixa "Atenção agora" e fila P1/P2/P3 |
| S3-T4 | Trust Score com explicação legível |
| S3-T5 | Central de decisões (lista, detalhe, ação, histórico) |
| S3-T6 | Máquinas: filtros rápidos e separação severidade × observabilidade |
| S3-T7 | Mapa mobile: bottom sheet e filtros em gaveta |
| S3-T8 | Painel "Quem está por trás do FieldNode" |
| S3-T9 | Busca global, tooltips, contraste e redundância de botões |
| S3-T10 | Grid de calor da frota (e por que **não** score de operador) |
| S3-T11 | E2E do fluxo central e evidência em vídeo |
| S4-T1 | Consolidar prescrição em `Decision` e remover o legado |
| S4-T2 | `Decision` estruturada (evidência, regra, janela, confiança, horizonte) |
| S4-T3 | `WorkOrder`, responsável real e prazo |
| S4-T4 | Exportação: `.ics`, JSON/webhook e mensagem pronta |
| S4-T5 | Execução, reavaliação e resultado verificável |
| S4-T6 | Feedback do mecânico ajusta o limiar da máquina (com trilha) |
| S4-T7 | Agenda interna de manutenção |
| S5-T1 | Unificar detectores e registrar versões |
| S5-T2 | Harness de avaliação com cenários reproduzíveis |
| S5-T3 | Regime de operação e baseline contextual |
| S5-T4 | Critérios de treino por máquina e baseline de grupo |
| S5-T5 | Validação do método em dataset público |
| S5-T6 | Model card e `HONESTIDADE_METODOLOGICA_ML.md` |
| S5-T7 | LLM com guardrails de evidência |
| S5-T8 | Assistente com function calling controlado (escopo mínimo) |
| S5-T9 | Plano de dataset rotulado a partir de decisões |
| S5-T10 | Metadados e manutenção por máquina |
| S6-T1 | Sync Protocol v1 (especificação) |
| S6-T2 | Capacidade de armazenamento e política de disco cheio |
| S6-T3 | Compressão, checksum e TTL |
| S6-T4 | Reconstrução temporal no ingestor |
| S6-T5 | Execução do protocolo e publicação dos números |
| S6-T6 | Backlog e saúde de sincronização visíveis |
| S7-T1 | `ConnectivityProvider` e `ConnectivityManager` |
| S7-T2 | Protocolo de custódia do Data Mule |
| S7-T3 | Mule sobre rede real (Docker `internal`) e assinatura por mensagem |
| S7-T4 | Relatório de entrega por salto |
| S7-T5 | Quadro compacto e plano de teste de rádio (LoRa/ESP-NOW) |
| S7-T6 | Canal de emergência (satélite) como interface e orçamento simulado |
| S7-T7 | Topologia do gateway: notebook (demo) vs dispositivo (produto) |
| S8-T1 | Estrutura do firmware e primeiro nó (DS18B20 → MQTT) |
| S8-T2 | Acelerômetro e features de vibração (substituir SW-420) |
| S8-T3 | RTC DS3231 e fonte de tempo |
| S8-T4 | Outbox no firmware (flash) com recuperação |
| S8-T5 | ESP-NOW do nó para o gateway de campo |
| S8-T6 | Demo de bancada: cortar a internet ao vivo |
| S8-T7 | CAN/J1939 em bancada (emissor simulado) |
| S8-T8 | Segurança do dispositivo e reposicionamento de escopo de hardware |
| S8-T9 | CI do firmware |
| S8-T10 | BOM v2 e compras (sensores certos, lead time de semana 1) |
| S8-T11 | RPM real (hall/óptico) e GPS (velocidade e posição) |
| S8-T12 | CAN **real** em modo só escuta (veículo de verdade) |
| S8-T13 | Triagem EWMA/CUSUM no nó, alarme local e prescrição curta no display |
| S8-T14 | Protocolo de integração incremental (uma variável por vez) |
| S9-T1 | Modelo relacional do grafo operacional |
| S9-T2 | Cadastro e importação das relações |
| S9-T3 | Consequence Engine v0.1 (regras explícitas, sem número inventado) |
| S9-T4 | Política da organização e custo de parada (opcional, sem valor padrão) |
| S9-T5 | Incidentes: agrupar sintomas correlacionados (sem diagnosticar) |
| S9-T6 | UI de consequência e diagrama de impacto |
| S9-T7 | Contexto real para o LLM e teste golden |
| S10-T1 | Pipeline de CI completo |
| S10-T2 | Métricas operacionais (`/metrics`) |
| S10-T3 | Logs estruturados com identidade de mensagem |
| S10-T4 | Health em camadas (live × ready) e heartbeat do worker |
| S10-T5 | Backup e restore **testado** |
| S10-T6 | Retenção e política de dados |
| S10-T7 | Carga, índices e consolidação dos scripts |
| S10-T8 | Deploy reprodutível e pacote de gateway |
| S10-T9 | Alertas operacionais para a própria equipe |
| S11-T1 | Capability matrix por máquina |
| S11-T2 | Proveniência e unidade em todo valor canônico |
| S11-T3 | Decodificador J1939 (backend) com vetores de teste |
| S11-T4 | SDK de adaptadores e formatos de exemplo |
| S11-T5 | Conformidade entre fontes |
| S11-T6 | Data Passport v0.1 (portabilidade) |
| S11-T7 | API versionada e contrato público |
| S12-T1 | README novo (vitrine honesta) |
| S12-T2 | Documentos finais da defesa |
| S12-T3 | Arquitetura e roteiro da demo (notebook é o gateway) |
| S12-T4 | Roteiro de validação comercial por papel |
| S12-T5 | Executar 5 a 6 conversas e relatar com honestidade |
| S12-T6 | Regra de rebalanceamento pós-entrevistas |
| S12-T7 | Política de números e alinhamento do pitch |
| S12-T8 | Pressure test (CTO/investidor/professor) |
| S12-T9 | Validação de campo escalonada (critérios de entrada e saída) |
| S12-T10 | Congelamento, release e plano de contingência |
| S12-T11 | Acesso a máquina real e carta de intenção de piloto (começa na semana 1) |
| S12-T12 | Amostra de entrevistas ampliada (8 a 10) e perguntas de prescrição |
| S13-T1 | Perfil `edge` do Compose: a pilha inteira no gateway |
| S13-T2 | Autenticação e permissões offline |
| S13-T3 | PWA offline-first do operador (dados, ações e mapa) |
| S13-T4 | `DomainChange`, relógio lógico híbrido e IDs determinísticos |
| S13-T5 | Replicação bidirecional gateway ↔ nuvem |
| S13-T6 | Regras de autoridade e resolução de conflito |
| S13-T7 | Inferência de ML local, distribuição de modelo e degradação controlada |
| S13-T8 | Teste "APAGÃO TOTAL" (aceite dos pilares P1 e P3) |
| S13-T9 | Gateway móvel (nó de replicação no transbordo/caminhão) |
| S13-T10 | Tempo confiável no gateway |
| S13-T11 | Backup local e recuperação do gateway |
| S13-T12 | HTTPS no gateway (contexto seguro para PWA e Bluetooth) · **substitui a decisão D-12 da V3** |
| S14-T1 | Requisito de cobertura e SLA de latência por classe e enlace |
| S14-T2 | LoRa real: hardware, firmware, quadro compacto, ACK e retransmissão |
| S14-T3 | Campanha de alcance LoRa em campo (canavial/mata baixa incluídos) |
| S14-T4 | Relay no transbordo/caminhão (LoRa ↔ ESP-NOW/LoRa) |
| S14-T5 | Data Mule **físico** com 3 ESP32 (origem, mule, gateway) |
| S14-T6 | Celular do operador como mule (BLE) + PWA |
| S14-T7 | Satélite real (estudo, compra, integração e medição) |
| S14-T8 | Connectivity Manager com enlaces reais e failover |
| S14-T9 | **Soak test de 14 dias** (a prova do offline) |
| S14-T10 | Energia e autonomia |
| S14-T11 | Painel de cobertura e enlaces + mapa de cobertura |
| S14-T12 | Autenticação e cifragem dos enlaces |
| S15-T1 | Campanha de dados reais (≥ 5 sessões de motor real, rotuladas) |
| S15-T2 | Rig de falhas controladas (motor DC + MPU6050) e de degradação |
| S15-T3 | Especificação única de features (nó, gateway, backend) |
| S15-T4 | Modelo de resíduo (temperatura esperada dado rpm, carga e ambiente) |
| S15-T5 | Comparação formal de detectores (split temporal por sessão) |
| S15-T6 | Autoencoder (challenger) exportado em ONNX para o gateway |
| S15-T7 | Incerteza calibrada (conformal / quantis) |
| S15-T8 | Explicabilidade por alerta (SHAP) e UI "por que o alerta" |
| S15-T9 | MLOps: registro, gates, modo sombra, drift, retreino e rollback |
| S15-T10 | Diagnóstico assistido (hipóteses ranqueadas com evidência) |
| S15-T11 | Aprendizado a partir do feedback e curva de falso alarme |
| S15-T12 | Copiloto FieldNode (RAG + ferramentas), fora do caminho crítico |
| S15-T13 | LLM local no gateway (explicação e copiloto offline) |
| S15-T14 | Avaliação do copiloto e red-team |
| S15-T15 | **Teste de IA offline** (aceite do pilar P2) |
| S15-T16 | Assinatura acústica (microfone I2S), opcional e medida |
| S16-T1 | Biblioteca de playbooks (esquema, validador, conjunto inicial) |
| S16-T2 | Motor de prescrição `prescription.v2` |
| S16-T3 | Checklist executável com evidências (offline) |
| S16-T4 | Estoque de peças e disponibilidade |
| S16-T5 | Verificação pós-reparo, reincidência e escalonamento |
| S16-T6 | Otimizador de janela de manutenção (OR-Tools CP-SAT) |
| S16-T7 | "E se eu adiar?" (cenários com incerteza, rotulados como estimativa) |
| S16-T8 | Cadeia de auditoria à prova de adulteração |
| S16-T9 | Aceite do pilar P1: ciclo de prescrição de ponta a ponta (offline, após reboot) |
| S16-T10 | Revisão e ciclo de vida dos playbooks com mecânico |
| S17-T1 | Módulo de risco térmico de incêndio (multi-ponto, dT/dt) |
| S17-T2 | Redundância e verificação cruzada de sensor |
| S17-T3 | OTA assinada com rollback |
| S17-T4 | Kit instalável e guia de instalação (instalação por pessoa de fora) |
| S17-T5 | Provisionamento por QR (PWA/BLE) em 10 minutos |
| S17-T6 | Modo cabine (operador/supervisor em movimento) |
| S17-T7 | Relatório de turno/sessão **offline** |
| S17-T8 | Trilha GPS e cerca virtual (geofence) offline |
| S17-T9 | Benchmark entre máquinas do mesmo modelo |
| S17-T10 | Painel executivo com métricas **medidas** |
| S17-T11 | Modo replay de sessão (estande e banca) |
| S18-T1 | Escolha do motor diesel e do acesso (gate da semana 1 a 2) |
| S18-T2 | Descoberta de sinais publicados (escuta passiva) e catálogo do motor |
| S18-T3 | Modelo de dados por componente e sinal |
| S18-T4 | Contrato `telemetry.v2` multicanal e armazenamento de séries |
| S18-T5 | Perfil de normalidade por sinal e por regime |
| S18-T6 | Qualidade por sinal e **desclassificação de dado irreal** |
| S18-T7 | DTC (SPN-FMI), DM1/DM2, correlação e ligação a componente |
| S18-T8 | Indicadores de saúde por componente (bomba de alta em destaque) |
| S18-T9 | Banco de provas de oficina: rótulos reais de estado do componente |
| S18-T10 | Campanha de dados no motor diesel (degraus de carga e regimes) |
| S18-T11 | Falhas **reversíveis** e supervisionadas |
| S18-T12 | Sensores complementares **não invasivos** do subsistema |
| S18-T13 | Aceite do pilar P4: `diesel_100` |
| S19-T1 | Definições formais e política de afirmações |
| S19-T2 | Laudo estruturado do técnico (a verdade de campo) |
| S19-T3 | Falhas corretivas e recomendações sem achado (para recall e falsos positivos) |
| S19-T4 | Evidência multi-sinal por componente |
| S19-T5 | **Percentual de recomendação (PR)** calibrado |
| S19-T6 | **Prazo-limite de manutenção (PLM)** e prognóstico por indicador |
| S19-T7 | **Escada de confirmação** (o que fazer, do mais barato ao mais caro) |
| S19-T8 | Política de recomendação por organização |
| S19-T9 | Painel de precisão e calibração |
| S19-T10 | **Decisão final do técnico** (override com motivo e aprendizado) |
| S19-T11 | Backtest e validação de PR e PLM |
| S19-T12 | Aceite do pilar P5: cenário **"bomba com 70% de vida"** e `confianca_100` |
| S20-T1 | Layout novo da tela inicial: barra de seleção + mapa |
| S20-T2 | Cards de situação **clicáveis** (Críticos, Atenção, Normais, Sem dados) |
| S20-T3 | Drill-down: card → lista com prescrição resumida → detalhe com tendências |
| S20-T4 | Seleção hierárquica de frota (site → frente → frota → máquina) |
| S20-T5 | Painel do componente (bomba de alta): PR, PLM, tendência, DTC, escada |
| S20-T6 | Medidor visual do **percentual de recomendação** e do prazo |
| S20-T7 | Enxugar a UI: "Avançado" colapsável e regra de elementos por tela |
| S20-T8 | Teste de usabilidade com gestores e técnicos (duas rodadas) |
| S20-T9 | Mapa com seleção bidirecional, clusters e camadas |
| S20-T10 | Aceite do pilar P6: `home_100` |
| S21-T1 | Ledger de valor por decisão |
| S21-T2 | Relatório do investidor e do gestor |
| S21-T3 | Data room técnico gerado do repositório |
| S21-T4 | Mapa vivo: problema real → solução → métrica → evidência |
| S21-T5 | Demonstração do cenário "bomba com 70%" |
| S21-T6 | Modelo interno de implantação (fora do pitch) |
| S21-T7 | Matriz de diferenciais **com fontes** (o que "qualquer empresa já tem") |

**Total:** 215 tarefas em 22 fatias (S0 a S21).

## APÊNDICE B · PROMPT-MESTRE PARA AGENTE DE CÓDIGO (Claude Code, Cursor, Windsurf, Kilo)

Cole no início de cada sessão e troque `<ID>` pela tarefa:

```text
Você é um Staff Engineer trabalhando no repositório FieldNode (Django 5.2 + DRF + MySQL, Next.js 15, ESP32/PlatformIO).
Leia AGENTS.md, CLAUDE.md e FIELDNODE_LEVIATA_ROADMAP_V5.md.
Execute SOMENTE a tarefa <ID>. Antes de codar:
1) reformule o objetivo em 3 linhas; 2) liste arquivos que serão tocados e riscos; 3) aponte inconsistências no pedido.
Regras: uma responsabilidade por vez; reutilize código existente; nenhum arquivo novo > 300 linhas sem justificar;
sem segredo em código; sem TODO sem (quem, por quê, quando); nunca afirmar em README/UI algo ausente de docs/CLAIMS_VS_CODE.md;
nunca inventar número, contato, peça, prazo, horizonte, procedimento de reparo ou valor financeiro (sem dado: campo null e a UI diz "não estimado");
PR (percentual de recomendação) NUNCA aparece sem intervalo e sem n; abaixo do limiar o sistema se ABSTÉM e diz por quê;
PLM só existe com condições mínimas (histórico, regimes, tendência significativa, qualidade); senão "sem prazo confiável";
dado marcado 'descartado' NUNCA entra em média, perfil, tendência, PR ou PLM (há teste que falha se entrar);
vida útil residual em % NÃO é afirmada como fato (só a estimativa do técnico no laudo);
playbook só entra em produção se status=vigente e revisado por mecânico; a decisão final é SEMPRE do técnico;
hardware: nunca transmitir em barramento de terceiros (só escuta); NUNCA medir na linha de alta pressão de combustível;
transmissão de rádio só após conferir faixa/potência vigentes.
Os seis pilares têm testes de aceite: prescricao_100, ia_offline, apagao_total, soak de 14 dias, diesel_100, confianca_100, home_100.
Depois de implementar: rode a suíte, mostre a saída, preencha a "Evidência de conclusão" da tarefa e atualize CLAIMS_VS_CODE.md.
Commits em português (feat:, fix:, refactor:, docs:, test:, chore:), branch feature/<id>-<slug>, abra PR.
Se o critério de aceite não puder ser cumprido, PARE e diga por quê. Não marque como pronto.
```

## APÊNDICE C · O QUE FOI VERIFICADO NO REPOSITÓRIO E O QUE NÃO FOI

| Verificado por leitura de código (2026-10-24) | Não verificado (executar em S0-T1) |
|---|---|
| Mosquitto exige senha; porta publicada em `127.0.0.1` | Se os testes passam (número exato) |
| `eventos.py` usa 85 °C; `edge_client.py` usa 95/110 e vibração 5/8 | Se `docker compose up` sobe limpo em máquina nova |
| Front não referencia decisions/trust/priority; `DashboardMachineData.tsx` usa mocks | Se `npm run build` e `tsc` passam |
| `sw.js` lança erro em não-2xx dentro do laço de sync | Se o Playwright existente roda em CI |
| `RegisterView` é `AllowAny`; `DEFAULT_THROTTLE_CLASSES` vazio | Cobertura real de isolamento entre organizações |
| Gemini com `?key=` em dois módulos | Resultado do `teste_resiliencia.py` |
| Nenhum `.ino`/PlatformIO; sem consequence/graph/passport | Qualquer afirmação de hardware, rádio, satélite, preço ou disponibilidade citada neste documento (**conferir na fonte no momento da tarefa**) |
| `.next/trace` e `.kiro/` versionados | Desempenho do Gateway-Núcleo, do LLM local e do OR-Tools no hardware escolhido |
| O repositório atual **não** tem `diesel`, `laudo`, `PR/PLM` nem componentes de motor | **Quais SPN/PID o motor escolhido realmente publica** (S18-T2); semântica de cada SPN/FMI (tabela pública); limites do fabricante; existência de banco de provas na oficina parceira |

---

## APÊNDICE D · TEXTO ORIGINAL DA V3 DAS SEÇÕES SUBSTITUÍDAS (preservado, nada foi apagado)

> A V4 **substituiu** a execução das seções abaixo (ordem, calendário, o que adiar). O texto original da V3 fica aqui para consulta e rastreabilidade. Em caso de conflito, **vale a V4**.

### D.1 V3 · Seções 13 (grafo de dependências) e 14 (visão geral das 10 fatias)

##### 13. DEPENDENCY GRAPH

```text
S0 baseline ──> S1 contrato único + integridade
                  |
                  ├─> S2 segurança (ACL MQTT, throttle, tenant)
                  |       |
                  |       └─> S8 firmware (precisa de credencial por dispositivo)
                  |
                  ├─> S3 front ligado ao motor ──> S4 prescrição operacional (WorkOrder) ──> S9 consequência
                  |                                   |
                  |                                   └─> S5 IA defensável (feedback do mecânico vira rótulo fraco)
                  |
                  └─> S6 resiliência provada ──> S7 Connectivity Manager + Mule ──> S8 hardware (física)
                                                                         |
S1-T5 (boot_id/time_source) ───────────────────────────────────────────> S8-T3 (RTC/hora do gateway)
S8-T7 (CAN) ──> S11 UMM real ──> S11-T6 Data Passport
S3 + S4 + S6 + S8 ──> S12 demo e validação
S10 (observabilidade) é transversal: instrumenta o que S1 a S9 criam; CI começa em S10-T1 mas roda testes desde S0

Universal Machine Model -> Telemetry Contract -> Data Health -> Event Engine -> Correlation -> Attention -> Decision -> Prescriptive -> Closed Loop
(S11)                      (S1)                  (feito)         (S1-S3)        (S9)           (S1,S3)     (S4)       (S4)           (S12)
```

**Se S1 atrasar:** S1 é a única fase que trava todas as outras (contrato de severidade é consumido por S3, S4, S6, S8 e S9). Ordem de sacrifício, do menos crítico ao mais: **(1)** S11 (UMM real) e S7-T5 (LoRa); **(2)** S10-T4 a T7 (tracing, carga); **(3)** S9 (consequência), mantendo só S9-T1 (grafo mínimo); **(4)** nunca sacrificar S1, S2-T1/T2, S3, S4-T1 a T4 e S6.


---

##### 14. CONSOLIDATED MASTER ROADMAP · VISÃO GERAL (sem limite de tempo)

| Sem. | Tema central | Camadas | Estado dominante | Evidência que fecha a semana |
|---|---|---|---|---|
| **0** | Baseline, higiene do repo e matriz de verdade (claims × código) | FOUNDATION, DOCUMENTATION, TESTING | BUILD_NOW | `docs/BASELINE.md` com testes **executados**, repo limpo, `docs/CLAIMS_VS_CODE.md` |
| **1** | Contrato único de severidade/prioridade/escala, tempo confiável, ACK, fila do SW sem travar | FOUNDATION, ARCHITECTURE, TESTING | BUILD_NOW | Teste de contrato cruzado verde: borda, backend e front classificam igual |
| **2** | Segurança de fronteira e isolamento entre organizações | SECURITY, TESTING | BUILD_NOW | Suíte de segurança verde, MQTT com ACL por dispositivo, 0 segredo em query string |
| **3** | **Command Center**: front ligado a decisões, trust, prioridade, sem mock | IMPLEMENTATION, VALIDATION | BUILD_NOW | Gravação: leitura → evento → decisão → aprovação visível na UI |
| **4** | Prescrição operacional: Decision estruturada → WorkOrder → resultado | ARCHITECTURE, IMPLEMENTATION | BUILD_NOW | Decisão aprovada gera OS exportável (`.ics`/JSON/webhook) e outcome |
| **[CORTE-BANCA]** | *Neste ponto o sistema já é demonstrável sem hardware e sem promessa falsa* | | | |
| **5** | IA defensável: harness de avaliação, regime de operação, model card | VALIDATION, TESTING | BUILD_NOW | `docs/AVALIACAO_ANOMALIA.md` com precisão, recall, falso positivo, tempo de detecção |
| **6** | Resiliência offline provada com métricas e capacidade calculada | VALIDATION, OBSERVABILITY | BUILD_NOW | `docs/PROTOCOLO_TESTE_RESILIENCIA.md` com números reais, não desejados |
| **7** | Connectivity Manager + Data Mule como motor de sync | ARCHITECTURE, IMPLEMENTATION | PROTOTYPE_NOW | Mule entrega pacote preservando `device_id`, ACK cumulativo, relatório de entrega |
| **8** | Hardware real: firmware, RTC, acelerômetro, ESP-NOW, CAN em bancada | IMPLEMENTATION, VALIDATION | BUILD_NOW / VALIDATE_NOW | Vídeo e log: ESP32 físico → MQTT real → decisão na tela, internet cortada ao vivo |
| **9** | Operation Graph v0.1 + Consequence Engine v0.1 | ARCHITECTURE, IMPLEMENTATION | PROTOTYPE_NOW | Evento crítico mostra ativos afetados e horizonte (regra simples, sem inventar) |
| **10** | Observabilidade, CI/CD, backup, carga | OBSERVABILITY, DEVOPS | BUILD_NOW | Painel de métricas, CI verde, restore testado, relatório de carga |
| **11** | Universal Machine Model real (J1939 público) + Data Passport v0.1 | ARCHITECTURE, IMPLEMENTATION | PROTOTYPE_NOW | Mesmo parâmetro canônico a partir de PGN real e de payload simulado, export portátil |
| **12** | Validação de campo e comercial, demo, README, pressure test | VALIDATION, BUSINESS VALIDATION, DOCUMENTATION | VALIDATE_NOW | 5 a 6 entrevistas documentadas, 3 ensaios cronometrados, claims verificados |

### D.2 V3 · Seção 24 (o que não fazer ainda)

##### 24. WHAT SHOULD NOT BE DONE YET

| Iniciativa | Por que é tentadora | Por que é prematura | Pré-requisito faltante | Quando reconsiderar |
|---|---|---|---|---|
| Chatbot de conversa livre | Parece "IA de verdade" | Sem validação, vira fonte de afirmações sem evidência | Decisões com volume + guardrails (S5-T7/T8) | Depois de S5 e de uso real; só ferramentas de leitura antes |
| Previsão de vida útil (RUL) / "vai quebrar em X" | Argumento forte de venda | Sem rótulo de falha real; IF não dá probabilidade | ≥ 200 decisões com desfecho + histórico de falhas | Ciclo seguinte, com dado de usina |
| LSTM autoencoder / deep learning | "Mais avançado" | Sem dado nem baseline que o justifique | Dataset rotulado + IF avaliado | Depois do relatório S5 e do dataset real |
| SHAP/LIME | Explicabilidade | O IF já expõe `contributing_feature`; custo alto | Modelo estável e avaliado | Se a banca/cliente pedir |
| Satélite NTN/TVWS/Swarm | Resolveria "duas semanas offline" | Zero validação de custo/hardware | Estudo dedicado | Só como `ConnectivityProvider` simulado (S7-T6) |
| LoRa mesh anunciado | Alcance de km | Nenhuma medição | Teste de rádio (S7-T5, S8) | Quando houver PER medido |
| CRDT / vector clock | "Sincronização avançada" | Telemetria é append-only; conflito inexistente | Edição offline concorrente real | Configuração editável offline, se um dia existir |
| Digital Twin / What-if | Impressiona | Depende de consequência madura e histórico | S9 + dados reais | Ciclos futuros |
| Edge AI com LLM no ESP32 | "De outro nível" | Hardware inviável | Outra plataforma | Só com hardware dedicado |
| Multi-tenancy por schema | Venda B2B | Sem cliente pagante | Validação comercial positiva | 2+ clientes em conversa avançada |
| Microserviços / Kafka / Kubernetes | "Parecer enterprise" | Monólito resolve com folga | Volume | Nunca por estética |
| App nativo mobile | Experiência | PWA basta; já existe protótipo Flutter separado | Demanda validada | Depois de S12-T5 |
| Score de operador | Pedido de gamificação | Injusto e sensível juridicamente | Política da usina | Depois de política e validação (D-16) |
| Integração real com Case/Deere/Solinftec | Argumento comercial | Exige contrato e acesso | Parceria | Após validação comercial |
| Deploy público como objetivo isolado | QR code | Segurança antes (S2) | S2 + S10-T8 | Depois de S2 |
| Reescrita do front por estética | "Novo visual" | Problema é integração, não aparência | n/a | Nunca por estética |

---


### D.3 V3 · Seções 25.1 e 25.2 (níveis e priorização)

##### 25.1 Plano por níveis (dependência arquitetural, não dificuldade)

- **NÍVEL 1 · Fundação (imprescindível):** S0, S1, S2, S3, S4. Contrato único, integridade, segurança, front ligado ao motor, decisão → OS → desfecho.
- **NÍVEL 2 · Validação (imprescindível):** S5 (IA avaliada), S6 (offline medido), S8 (hardware físico mínimo), S10 (CI/observabilidade/backup).
- **NÍVEL 3 · Evolução estratégica:** S7 (Connectivity Manager e Mule em rede real), S9 (consequência e grafo), S12 (validação comercial e demo).
- **NÍVEL 4 · Diferenciação tecnológica:** S11 (UMM real com J1939), Data Passport, RF supervisionado (quando houver dado), isolamento por schema.
- **NÍVEL 5 · Visão futura:** LoRa/satélite em campo, digital twin, what-if, autonomia supervisionada, integrações reais com OEM.

##### 25.2 Priorização das tarefas de maior retorno

Escala 1 (baixo) a 5 (alto). Retorno = impacto na defesa e na prova do diferencial ÷ esforço.

| Tarefa | Impacto na defesa | Risco que remove | Esforço | Prioridade |
|---|---|---|---|---|
| S1-T1 contrato único | 5 | Crítico sai como classe C | 2 | **1** |
| S3-T1 remover mocks + selo | 5 | Dado falso na demo | 2 | **2** |
| S3-T3/T4/T5 Command Center | 5 | Diferencial invisível | 4 | **3** |
| S1-T4 fila do SW | 4 | Mensagem presa para sempre | 2 | **4** |
| S1-T3 evidência × prioridade | 4 | Evento grave escondido | 2 | **5** |
| S0-T2 higiene do repo | 4 | Primeira impressão | 1 | **6** |
| S6-T5 protocolo com números | 5 | "0% de perda" sem medida | 3 | **7** |
| S5-T2 harness de avaliação | 5 | "IA sem modelo" (professor) | 3 | **8** |
| S8-T1 ESP32 + DS18B20 → MQTT | 5 | Zero hardware | 3 | **9** |
| S2-T1/T2/T6 segurança e isolamento | 4 | QR vira porta aberta | 3 | **10** |
| S4-T3/T4 OS exportável | 4 | Prescrição genérica | 3 | **11** |
| S9-T3 consequência v0.1 | 4 | "Não é só dashboard" | 4 | **12** |
| S12-T4/T5 entrevistas | 5 | Hipótese comercial não testada | 3 | **13 (começar cedo, em paralelo)** |
| S12-T7 política de números | 4 | Pergunta de fonte | 1 | **14** |


### D.4 V3 · Seção 25.4 (checklist de entrega)

##### 25.4 O que existe ao fim do ciclo (checklist de entrega)

- [ ] Contrato único de severidade/escala, verificado em backend, borda, firmware e front.
- [ ] Zero mock em tela; selo "SIMULADO/medido".
- [ ] Command Center: fila P1/P2/P3, Trust com fatores, central de decisões, OS exportável, desfecho com verificação.
- [ ] `AVALIACAO_ANOMALIA.md`, `HONESTIDADE_METODOLOGICA_ML.md` e model card publicados.
- [ ] `PROTOCOLO_TESTE_RESILIENCIA.md` com números reais e `CAPACIDADE.md`.
- [ ] Mule em rede real isolada com custódia e assinatura.
- [ ] Firmware versionado e vídeo de bancada (sensor físico → decisão na tela, internet cortada).
- [ ] J1939 decodificado em bancada com vetores conferidos.
- [ ] Operation Graph + Consequence v0.1 sem número inventado.
- [ ] CI verde, `/metrics`, restore testado, relatório de carga.
- [ ] 5 a 6 entrevistas documentadas e `PROXIMO_CICLO.md`.
- [ ] `README.md` novo com GIF, `CLAIMS_VS_CODE.md` sem contradição, `PITCH_FATOS.md` com fonte para cada número.
- [ ] 3 ensaios cronometrados com pessoa de fora e plano de contingência.


### D.5 V3 · Item 2 de 'Como ler este arquivo'

2. **"Semana N" aqui é uma fatia de execução ordenada por dependência, não um prazo.** O framework Leviatã proíbe comprimir escopo para caber em calendário. Se uma semana levar 4 dias ou 12, tudo bem. O que não pode acontecer é pular a ordem. A data da banca final não foi informada, então nenhuma fatia foi cortada por data. O marcador **[CORTE-BANCA]** indica o ponto onde, se o tempo apertar, o sistema já está demonstrável (ver seção 14).

### D.6 V3 · Tabela 'Onde cada responsabilidade mora' (seção 6)

**Onde cada responsabilidade mora (resposta do Leviatã):**

| Responsabilidade | Mora em | Sobrevive offline? |
|---|---|---|
| Captura, carimbo de tempo, triagem A/B/C, outbox | Edge node (firmware) | **Sim** |
| Alerta local imediato (limiar de segurança) | Edge node/gateway, regra determinística | **Sim** |
| Dashboard local e broker | Gateway de campo | **Sim** |
| Roteamento de canal e protocolo de sync | Gateway (Connectivity Manager) | **Sim** |
| Dedup final, normalização, Trust Score, Event, Decision | Ingestão (sede/nuvem) | Não |
| IF por máquina | Sede (treino) e opcionalmente gateway (inferência com modelo exportado) | Inferência sim, treino não |
| Operation Graph e consequência | Sede | Não (v0.1); regra simplificada no gateway = `ARCHITECT_NOW` |
| LLM | Sede, assíncrono, nunca no caminho crítico | Não |


### D.7 V3 · Linhas editadas em lugar (texto original)

- **D-12 (V3):** `| D-12 | TLS no gateway local | Hotspot sem HTTPS | HTTP local · TLS com CA própria | SEGURANCA.md | TLS local complica a demo | **HTTP no hotspot isolado; TLS no deploy cloud** | ...` → **superada pela D-35 (V4)**: Service Worker e Web Bluetooth exigem contexto seguro.
- **S12-T3 (V3):** "plateia conecta no hotspot e abre `http://<ip>:3000`" → na V4: `https://fieldnode.local` com HTTPS local (S13-T12).
- **S0-T5 (V3):** referência a `FIELDNODE_LEVIATA_ROADMAP_V3.md` → na V4: `..._V4.md`.

---

## APÊNDICE E · TEXTO ORIGINAL DA V4 DAS SEÇÕES SUBSTITUÍDAS (preservado, nada foi apagado)

> A V5 **substituiu** a execução das seções 13 (grafo de dependências) e 14 (visão geral e calendário). O texto da V4 fica aqui. Em caso de conflito, **vale a V5**. A regra de corte da V4 (seção 0.6) permanece no lugar, marcada como substituída pela 0-A.7.

### E.1 V4 · Seções 13 e 14

##### 13. DEPENDENCY GRAPH (V4: duas pistas em paralelo, três pilares)

```text
PISTA SOFTWARE (A)                                  PISTA FÍSICA (B)                              DADOS/IA (C)                 PRODUTO (D)
------------------                                  ----------------                              ------------                 -----------
S0 baseline ──► S1 contrato único                   S8-T10 compras (dia 1)                        S15-T1 campanha (planejar)   S12-T4 roteiro
   │               │                                   │                                          S15-T2 rig (montar)           S12-T11 acesso/piloto
   │               ├─► S2 segurança ───────────────►  S8-T1 DS18B20→MQTT  (dia 1-2)                    │
   │               │       │                           │                                               │
   │               ├─► S3 front real ──┐               ├─► S8-T2/T3/T11/T13 (MPU, RTC, hall/GPS,      │
   │               │                   │               │       EWMA/CUSUM + alarme)                    ▼
   │               └─► S4 decisão→OS ──┤               ├─► S8-T4 outbox flash ─► S8-T5 ESP-NOW      S15-T3 features ─► S15-T4/T5/T6
   │                                   │               │                           │                      │ (resíduo, comparação, AE)
   │                                   ▼               │                           ▼                      ▼
   │                          S13 GATEWAY-NÚCLEO ◄─────┘                  S14-T2/T3 LoRa medido     S15-T7/T8/T9 (incerteza,
   │                          (perfil edge, login,                         S14-T4 relay                SHAP, MLOps)
   │                           replicação, ML local)                       S14-T5 mule físico              │
   │                                   │                                   S14-T6 BLE mule               S15-T10/T11 (diagnóstico,
   │                                   ▼                                   S14-T7 satélite real           feedback) 
   │                          S13-T8 APAGÃO TOTAL ◄───────────────────────  S14-T8 manager ─► S14-T9 SOAK 14 dias
   │                                   │                                                                   │
   │                                   ├───────────────► S16 PRESCRIÇÃO PROFISSIONAL ◄── S15-T12/T13 copiloto
   │                                   │                  (playbooks, checklist, estoque,
   │                                   │                   otimizador, what-if, auditoria)
   │                                   ▼
   └────────────► S9 consequência ──► S17 diferenciais ──► S10 observabilidade/CI ──► S11 UMM/Passport ──► S12 demo/validação
                                                               (transversal, P3 primeiro a cortar)

 PILARES:  P1 PRESCRIÇÃO-100 = S4 + S16 + S13-T8       P2 IA-100 = S5 + S15 + S13-T7       P3 OFFLINE-100 = S6 + S8 + S13 + S14
```

**Dependências duras (não negociáveis):**
- S1-T1 (contrato) antes de S8-T13 (triagem no nó) e S3 (front): o limiar nasce de **uma** fonte. *(Os valores v1 podem ser reajustados depois com dados reais da S15-T1, por versão do contrato.)*
- S2-T1/T8 (credencial por dispositivo) antes de S8-T1 em ambiente compartilhado; para a **primeira prova de bancada no notebook**, usar perfil `demo` local.
- S13-T4 (ID determinístico) antes de S13-T5 (replicação).
- S14-T1 (SLA por enlace) antes de S14-T8 (manager).
- S14-T9 (soak) precisa de nó + enlace + energia prontos: **iniciar o primeiro soak assim que S8-T4 e S14-T2 estiverem de pé**, porque são 14 dias corridos que não se aceleram.
- S15-T1/T2 (dados reais) antes de S15-T4 a T6 (treino e comparação).
- S16-T1 (playbooks) antes de S16-T2; entrevistas com mecânico (S12-T10/S16-T10) **começam na semana 2**.

**Caminho crítico em tempo corrido:** compra de hardware → primeira leitura física → outbox → LoRa → soak de 14 dias → relatório. Qualquer atraso nas compras atrasa o soak, que não pode ser comprimido.

**Se S1 atrasar:** a pista B (hardware) **não espera**: usa o contrato v0 (limiares atuais do backend) e migra para o v1 por versão. S1 trava S3, S4, S13 e S16, mas não trava S8, S14 e S15-T1/T2.

---

##### 14. CONSOLIDATED MASTER ROADMAP · VISÃO GERAL (V4)

##### 14.1 Fatias (S0 a S17) e estado

| Fatia | Tema | Pilar | Trilha | Estado dominante | Evidência que fecha |
|---|---|---|---|---|---|
| S0 | Baseline, higiene, matriz de verdade | transversal | A | BUILD_NOW | `BASELINE.md`, repo limpo |
| S1 | Contrato único, tempo, ACK, fila do SW | P3 | A | BUILD_NOW | teste de paridade verde |
| S2 | Segurança e isolamento | transversal | A | BUILD_NOW | suíte de segurança |
| S3 | Command Center sem mock | P1 | A/D | BUILD_NOW | gravação do fluxo |
| S4 | Decisão → OS → desfecho | **P1** | A | BUILD_NOW | OS exportável |
| S5 | IA: harness, regime, model card, guardrails | **P2** | C | BUILD_NOW | relatório de avaliação |
| S6 | Resiliência offline provada (simulador) | **P3** | A/B | BUILD_NOW | protocolo com números |
| S7 | Connectivity Manager (interface e protocolo de custódia) | **P3** | A/B | BUILD_NOW | custódia testada |
| **S8** | **Hardware real (agora desde o dia 1)** | **P3** | **B** | **BUILD_NOW** | vídeo de bancada, CAN real |
| S9 | Operation Graph e consequência v0.1 | P1 | A/D | PROTOTYPE_NOW | cenário golden |
| S10 | Observabilidade, CI, backup, carga | transversal | A | BUILD_NOW (parte P3) | CI verde, restore |
| S11 | UMM real e Data Passport | extra | A | PROTOTYPE_NOW (P3) | convergência de fontes |
| S12 | Validação, demo, README, piloto | todos | D | VALIDATE_NOW | ensaios, entrevistas |
| **S13** | **Gateway-Núcleo e replicação** | **P3/P1/P2** | **A** | **BUILD_NOW** | **apagão total** |
| **S14** | **Enlaces reais e soak de 14 dias** | **P3** | **B** | **BUILD_NOW** | **relatório de 14 dias** |
| **S15** | **IA profissional, MLOps, copiloto** | **P2** | **C** | **BUILD_NOW / PROTOTYPE_NOW** | **comparação + teste de IA offline** |
| **S16** | **Prescrição profissional** | **P1** | **D/A** | **BUILD_NOW** | **ciclo completo offline** |
| **S17** | **Diferenciais extras** | extra | B/D | BUILD_NOW / PROTOTYPE_NOW | demos por item |

##### 14.2 Calendário de 12 semanas em 4 trilhas paralelas

*Cada célula lista IDs de tarefa. "Gate" = marco que precisa estar verde para a semana seguinte.*

| Sem. | A · Core (Paola, Ana no front) | B · Hardware e enlaces (Giovana, Vinícius) | C · IA e dados | D · Prescrição, produto, validação | **Gate da semana** |
|---|---|---|---|---|---|
| **1** | S0-T1, S0-T2, S0-T3 · S1-T1, S1-T2, S1-T3 | **S8-T10 (compras)** · **S8-T1 (DS18B20 → MQTT, bancada)** | S15-T1 (protocolo), S15-T2 (montar rig) | S12-T4 (roteiro), S12-T11 (acesso/piloto), S16-T10 (contato com mecânico) | Primeira leitura física no banco local |
| **2** | S1-T4 a T8 · S2-T1, S2-T2 | S8-T2 (MPU), S8-T3 (RTC), S8-T11 (hall+GPS), **S8-T13 (EWMA/CUSUM + alarme)** | S15-T1 (sessões 1 e 2), S15-T2 (rig pronto) | S12-T5 (entrevistas começam), S16-T1 (rascunho playbooks) | Alarme local sem internet funcionando |
| **3** | S2-T3 a T8 · S3-T1, S3-T2, S3-T3, S3-T4 | **S8-T4 (outbox flash)** · **S14-T2 (LoRa bring-up)** · iniciar encomenda satélite (S14-T7 gate de compra) | S15-T3 (features), S5-T1, S5-T2 (harness) | S12-T5 (cont.), S16-T1 | Dado real fluindo com contrato v1 |
| **4** | S3-T5 a T7 · S4-T1, S4-T2, S4-T3 | S8-T5 (ESP-NOW) · **S14-T5 (mule físico, 3 ESP32)** · **iniciar SOAK #1 (S14-T9)** | S15-T4 (resíduo), S15-T5 (comparação) | S16-T2 (motor de prescrição) | **Soak #1 rodando (14 dias corridos)** |
| **5** | **S13-T1, T2, T4** (gateway-núcleo, login offline, ID determinístico) · S4-T4, T5 | S14-T3 (campanha LoRa em campo) · S14-T10 (energia) | S15-T6 (autoencoder), S15-T7 (incerteza) | S16-T3 (checklist), S16-T4 (estoque) | Gateway sobe com `compose --profile edge` |
| **6** | S13-T3 (PWA offline), S13-T5, S13-T6 (replicação e autoridade) · S4-T6, T7 | S14-T4 (relay no transbordo) · S8-T12 (CAN real listen-only) | S15-T8 (SHAP), S15-T9 (MLOps) | S16-T5 (reincidência), S16-T6 (otimizador) | Replicação bidirecional sem duplicata |
| **7** | **S13-T7, T8 (ML local, APAGÃO TOTAL)** · S5-T3 a T6 | S14-T6 (BLE mule), **S14-T7 (satélite integração)**, S14-T12 (autenticação dos enlaces) · **SOAK #1 termina → relatório** | S15-T10 (diagnóstico), S15-T11 (feedback) | S16-T7 (what-if), S16-T8 (cadeia hash) | **Apagão total aprovado (P3 e P1 base)** |
| **8** | S6-T1 a T6 (protocolo com números) · S9-T1, T2, T3 | **S14-T8 (Connectivity Manager)**, S14-T11 (painel de cobertura) | **S15-T12 (copiloto)**, S5-T7, S5-T8 | S16-T9 (prescrição-100) · S3-T9 | Manager com failover real |
| **9** | S9-T5, T6, T7 · S13-T9 (gateway móvel) | **iniciar SOAK #2 (stack completa, 14 dias)** · S17-T1, T2 (risco térmico, redundância) | S15-T13 (LLM local), S15-T14 (avaliação do copiloto) | S12-T5 (entrevistas 8 a 10), S17-T6 (modo cabine) | Soak #2 rodando |
| **10** | S10-T1 a T6, T8 · S13-T11 | S17-T3 (OTA), S17-T4 (kit) | S15-T15 (**teste de IA offline**), S15-T16 (acústico, se houver tempo) | S17-T7, T9 | CI verde e restore testado |
| **11** | S11 (T1 a T3, T6) · S13-T8 (reexecutar) | S14-T9 (soak #2 termina), S8-T6 (demo de bancada) | P2 checklist fechado | S16-T9 (reexecutar), S12-T6, S12-T7, S12-T12 | **Três pilares verificados** |
| **12** | S12-T1, T2, T3, T8, T9, T10 · README, pitch, 3 ensaios | kit de demo fechado, fallback em vídeo | model card final | S12-T5 (relatório), PROXIMO_CICLO | **Freeze e ensaios** |

**Ordem de leitura do calendário:** o que está em negrito é caminho crítico. Soak #1 (sem 4 a 7) valida o desenho com firmware parcial; Soak #2 (sem 9 a 11) valida a pilha completa.

##### 14.3 O que precisa de gente de fora (começar na semana 1)

- **Mecânico/oficina** para revisar playbooks (S16-T10) e permitir sessões de motor real (S15-T1).
- **Contato da usina/professor com experiência em Solinftec** para entrevistas e acesso a máquina (S12-T11).
- **Veículo para escuta CAN** com autorização do dono (carro próprio/oficina; veículo pesado só com autorização formal) (S8-T12).
- **Local de campo** para campanha LoRa e soak (um terreno aberto/canavial com permissão) (S14-T3, S14-T9).
