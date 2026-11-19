# S12-T8 · Pressure test técnico e estratégico

Status: DOCUMENTO DE PREPARAÇÃO CONCLUÍDO; ENSAIOS EXTERNOS PENDENTES

Este documento prepara respostas curtas, honestas e rastreáveis. Não é texto
para decorar. Toda resposta separa implementação, teste, simulação e roadmap.
Quando a evidência não existe, a resposta assume a lacuna. É menos glamouroso
que improvisar, mas costuma sobreviver melhor ao primeiro “mostra onde?”.

## 1. Estado real usado nas respostas

- Há software Django/DRF, frontend e contratos de telemetria com testes locais.
- A bancada Python tem outbox, retry, ACK e prioridades; isso não prova um
  gateway físico ESP32 em campo.
- Isolation Forest é detector não supervisionado; regras e thresholds fazem
  triagem. Não há base para dizer que o sistema prevê falha ou RUL.
- S5 tem benchmark sintético documentado. S5-T5 ainda não tem resultados reais
  CWRU publicados.
- S6-T2 tem uma medição de armazenamento em SQLite. S6-T5 não tem rodadas
  oficiais nem `resultados.json` publicado.
- Não há evidência no checkout de validação em máquina agrícola, piloto,
  cliente, carta de intenção ou ensaio externo concluído.
- A decisão operacional permanece pendente e sujeita a revisão humana.

Fontes de controle: `docs/PITCH_FATOS.md`, `docs/CLAIMS_VS_CODE.md`,
`docs/evidence/s5/`, `docs/evidence/s6/`, `docs/evidence/s8/`,
`docs/evidence/s10/` e `FIELDNODE_LEVIATA_ROADMAP_V5.md`.

## 2. Como responder

Use esta sequência: resposta curta, evidência, limite, pergunta complementar e
resposta complementar. Se pedirem um número, abra `docs/PITCH_FATOS.md`. Se ele
não tiver linha autorizada, diga “não temos esse número verificado”.

## 3. As 15 perguntas originais da seção 22

### 1. Qual é o diferencial?

**O que investigam:** se existe algo demonstrável além de uma tela bonita.

**Resposta curta:** O diferencial demonstrável é juntar qualidade da evidência,
fila de atenção e decisão persistente com revisão humana. Não alegamos que isso
seja impossível de copiar nem que já seja um moat. A vantagem só poderá ser
defendida com dados reais e histórico de desfechos.

**Evidência:** `docs/PITCH_FATOS.md`, claims autorizadas;
`docs/OPERATIONAL_DECISION_MEMORY.md`.

**Limitação:** não há validação comercial ou moat comprovado.

**Complementar:** “O que impede um OEM de fazer isso?”

**Resposta complementar:** Nada impede em princípio. A hipótese é complementar
soluções existentes em uma operação específica; ainda não temos comparação
experimental contra OEM.

**Status:** PARCIALMENTE EVIDENCIADA.

### 2. Por que não é só um dashboard?

**O que investigam:** se há fluxo operacional real.

**Resposta curta:** Porque a telemetria é persistida, eventos são registrados e
decisões têm estado, evidência e revisão. O dashboard exibe o estado; ele não é
a única camada. Isso demonstra o ciclo de software, não prova que a recomendação
mecânica esteja correta.

**Evidência:** `docs/OPERATIONAL_DECISION_MEMORY.md` e testes do fluxo.

**Limitação:** utilidade em campo ainda depende de validação externa.

**Complementar:** “Qual desfecho fecha o ciclo?”

**Resposta complementar:** O sistema registra aprovação, rejeição ou pendência;
o desfecho mecânico real ainda precisa ser coletado e auditado.

**Status:** EVIDENCIADA para o fluxo de software; PARCIALMENTE EVIDENCIADA para operação.

### 3. Por que não usar a solução do OEM?

**O que investigam:** se a equipe entende o mercado e não está atacando um
espantalho.

**Resposta curta:** Não afirmamos que OEM seja ruim ou insuficiente em todo
contexto. OEMs têm vantagens em integração e telemetria própria. O FieldNode
explora a hipótese de complementar frotas mistas e zonas com visibilidade
limitada, mas essa hipótese ainda depende de entrevistas e validação de campo.

**Evidência:** `FIELDNODE_LEVIATA_ROADMAP_V5.md`, seção 22;
`docs/ROTEIRO_VALIDACAO_COMERCIAL.md`.

**Limitação:** não há comparação documentada nem integração OEM real.

**Complementar:** “Então por que alguém adotaria vocês?”

**Resposta complementar:** Ainda não sabemos; vamos testar o caso de uso com
comportamento observado, não com promessa de compra.

**Status:** BLOQUEADA para conclusão de mercado.

### 4. Onde está a propriedade tecnológica?

**Resposta curta:** No contrato de identidade e sincronização, na qualidade e
proveniência da telemetria e na memória de decisões. Não existe algoritmo
secreto sendo apresentado como barreira competitiva.

**Evidência:** `docs/CONTRATO_TELEMETRIA_V1.md`,
`docs/evidence/s6/S6-T4_REPORT.md` e `docs/OPERATIONAL_DECISION_MEMORY.md`.

**Limitação:** código verificável não equivale a propriedade defensável de
mercado.

**Complementar:** “Qual parte exige mais prova?”

**Resposta complementar:** A transferência para dados reais, o desfecho das
decisões e a utilidade em uma operação concreta.

**Status:** PARCIALMENTE EVIDENCIADA.

### 5. Onde está o moat?

**Resposta curta:** Ainda não existe moat comprovado. Existe uma base para
construir histórico portátil de decisões com desfecho. Isso só vira vantagem
quando houver dados reais, tempo e uso repetido.

**Evidência:** `FIELDNODE_LEVIATA_ROADMAP_V5.md`, seção 22;
`docs/PITCH_FATOS.md`.

**Limitação:** não há cliente, escala ou exclusividade de dados verificada.

**Complementar:** “Então o que vocês têm hoje?”

**Resposta complementar:** Uma fundação técnica auditável e hipóteses de produto,
não uma vantagem de mercado já provada.

**Status:** ROADMAP.

### 6. Os dados são reais?

**Resposta curta:** São mistos. Há código e testes de software, medições de
bancada como a de armazenamento S6-T2 e dados sintéticos no benchmark S5. Não
temos evidência suficiente para chamar a solução de validada em máquina
agrícola real.

**Evidência:** `docs/evidence/s6/S6-T2_REPORT.md`,
`docs/AVALIACAO_ANOMALIA.md`, `docs/REPOSICIONAMENTO_ESCOPO_HARDWARE.md`.

**Limitação:** sem validação física e laudo de campo.

**Complementar:** “Por que não chamar tudo de medido?”

**Resposta complementar:** Porque origem é parte do dado; simulação, bancada e
campo respondem perguntas diferentes.

**Status:** EVIDENCIADA com contexto.

### 7. A IA é defensável?

**Resposta curta:** Hoje, não no sentido de uma barreira de mercado. O que existe
é detecção de anomalia não supervisionada, regras de triagem e benchmark
sintético. Não afirmamos previsão de falha nem vida útil.

**Evidência:** `docs/HONESTIDADE_METODOLOGICA_ML.md`,
`docs/evidence/s5/S5-T2_REPORT.md` e `docs/evidence/s5/S5-T5_REPORT.md`.

**Limitação:** CWRU real e dados de campo ainda não geraram resultados
publicados.

**Complementar:** “O score é probabilidade de falha?”

**Resposta complementar:** Não. É um sinal de comportamento atípico dentro do
detector; a interpretação exige contexto, qualidade e triagem humana.

**Status:** PARCIALMENTE EVIDENCIADA.

### 8. Como funciona sem internet?

**Resposta curta:** Na bancada, o cliente local mantém dados em outbox, tenta
novamente e só remove após ACK válido. Serviços locais podem continuar sem
uplink. Isso não prova alcance de rádio, gateway embarcado ou operação de campo.

**Evidência:** `docs/evidence/s8/S8-T4_S8-T5_IMPLEMENTATION.md`,
`docs/CONECTIVIDADE.md` e `docs/evidence/s6/S6-T5_EXECUCAO.md`.

**Limitação:** S6-T5 não tem rodada oficial publicada.

**Complementar:** “E se a máquina ficar sem qualquer enlace?”

**Resposta complementar:** O sistema pode preservar localmente o que estiver
implementado na topologia testada; não prometemos sincronização em tempo real
sem enlace.

**Status:** PARCIALMENTE EVIDENCIADA.

### 9. Como escala?

**Resposta curta:** A arquitetura separa API, worker, banco e frontend, e a
ingestão tem idempotência. Ainda não medimos carga representativa nem definimos
um ponto de saturação para uma operação industrial.

**Evidência:** `docker-compose.yml`, `docs/evidence/s10/S10-T8_REPORT.md` e
`docs/OBSERVABILIDADE.md`.

**Limitação:** não extrapolar testes pequenos para produção.

**Complementar:** “Qual seria o primeiro gargalo?”

**Resposta complementar:** Precisamos medir ingestão, consultas e fila de
processamento com volume representativo antes de escolher uma mudança de
infraestrutura.

**Status:** PARCIALMENTE EVIDENCIADA.

### 10. Como protege dados?

**Resposta curta:** Há credenciais por dispositivo, validações, autorização no
backend e trilhas de auditoria em partes do fluxo. Não alegamos segurança total:
TLS de MQTT, proteção física, Secure Boot e Flash Encryption continuam limites
documentados.

**Evidência:** `docs/SEGURANCA.md`, `docs/evidence/s8/S8-T8_REPORT.md` e
`docs/CONTRATO_TELEMETRIA_V1.md`.

**Limitação:** revisão de segurança de produção ainda não está concluída.

**Complementar:** “A UI impede acesso indevido?”

**Resposta complementar:** Não sozinha. A autorização precisa ser aplicada no
backend, por identidade, organização e recurso.

**Status:** PARCIALMENTE EVIDENCIADA.

### 11. Como lida com múltiplos fabricantes?

**Resposta curta:** O desenho preserva dado bruto e normaliza por adaptadores
para um modelo canônico. Há fixtures e código de mapeamento; não há integração
real com API de fabricante nem compatibilidade de campo comprovada.

**Evidência:** `docs/UNIVERSAL_MACHINE_MODEL.md`,
`docs/evidence/s9/S9-T2_T3_REPORT.md` e `docs/evidence/s8/S8-T7_REPORT.md`.

**Limitação:** exemplos de protocolo não equivalem a integração OEM.

**Complementar:** “E se o sinal não existir?”

**Resposta complementar:** O indicador deve ficar não calculado; ausência não
deve virar zero nem leitura válida inventada.

**Status:** PARCIALMENTE EVIDENCIADA.

### 12. Como prova que as decisões estão certas?

**Resposta curta:** Hoje não provamos estatisticamente que estão certas. O
sistema registra evidências, estado, responsável e desfecho; isso cria a trilha
necessária para medir depois, mas não substitui laudo ou validação de campo.

**Evidência:** `docs/OPERATIONAL_DECISION_MEMORY.md` e
`docs/HONESTIDADE_METODOLOGICA_ML.md`.

**Limitação:** não há conjunto de desfechos reais suficiente.

**Complementar:** “Então por que mostrar uma recomendação?”

**Resposta complementar:** Como proposta pendente para triagem humana, nunca
como ordem automática ou fato mecânico.

**Status:** PARCIALMENTE EVIDENCIADA.

### 13. O que acontece quando o sistema erra?

**Resposta curta:** A resposta precisa ser registrada como rejeição, falso
alarme ou desfecho divergente, conforme o fluxo disponível. O sistema não deve
esconder o erro nem transformá-lo em certeza. Recalibração só entra após regra,
dados e revisão suficientes.

**Evidência:** `docs/OPERATIONAL_DECISION_MEMORY.md` e
`docs/evidence/s5/S5-T7_REPORT.md`.

**Limitação:** não há série real de erros e acertos de campo.

**Complementar:** “Vocês já mediram taxa de falso alarme em máquina?”

**Resposta complementar:** Não temos essa medição autorizada no checkout.

**Status:** PARCIALMENTE EVIDENCIADA.

### 14. Qual parte foi validada em campo?

**Resposta curta:** Nenhuma claim de validação em máquina agrícola real está
autorizada. O checkout sustenta software, simuladores e partes de bancada; campo
e piloto permanecem pendentes.

**Evidência:** `docs/REPOSICIONAMENTO_ESCOPO_HARDWARE.md`,
`docs/evidence/s8/S8-T14_REPORT.md` e `docs/PITCH_FATOS.md`.

**Limitação:** acesso a máquina, coleta e laudo ainda não estão comprovados.

**Complementar:** “Então o que a demo prova?”

**Resposta complementar:** Prova o fluxo de software no ambiente executado, não
o comportamento da operação agrícola.

**Status:** EVIDENCIADA como limite.

### 15. E se o sensor estiver mentindo?

**Resposta curta:** A entrada precisa preservar qualidade, origem, timestamp e
estado inválido. Uma leitura ausente ou fora de faixa não pode virar zero. O
Trust Score pode sinalizar baixa confiança, mas não afirmamos detectar todo
defeito de sensor automaticamente.

**Evidência:** `docs/CONTRATO_TELEMETRIA_V1.md`, `docs/limiares.md` e
`docs/evidence/s8/S8-T1_REPORT.md`.

**Limitação:** diagnóstico físico de sensor e cobertura de ruído em campo não
foram validados.

**Complementar:** “Um alerta de temperatura alta prova falha?”

**Resposta complementar:** Não. Prova que uma regra ou sinal merece triagem;
sensor, contexto e procedimento precisam ser verificados.

**Status:** PARCIALMENTE EVIDENCIADA.

## 4. Perguntas adicionais do professor

### 16. Onde está o modelo treinado?

**Resposta curta:** O modelo usado no fluxo é um detector Isolation Forest; o
código e o harness estão no repositório. Os resultados do benchmark são
sintéticos e o relatório não autoriza dizer que o modelo prevê falhas. Antes de
afirmar um artefato treinado para a banca, é preciso apontar o arquivo, comando,
dados, versão, avaliação e fallback observáveis no ambiente da demonstração.

**Evidência:** `ml/eval/`, `docs/evidence/s5/S5-T1_REPORT.md`,
`docs/evidence/s5/S5-T2_REPORT.md` e `docs/MODEL_CARD_ANOMALIA.md`.

**Limitação:** não confundir código de treinamento, `.pkl` e eficácia validada;
o estado do artefato da demo deve ser conferido antes do ensaio.

**Complementar:** “Qual dado treinou o modelo?”

**Resposta complementar:** O benchmark S5 usa séries sintéticas; não temos
dataset de falhas agrícolas rotulado que sustente previsão supervisionada.

**Status:** PARCIALMENTE EVIDENCIADA.

### 17. E se o sensor estiver errado?

**Resposta curta:** Validamos formato, faixa quando justificada, timestamp,
origem e qualidade. Ausência, leitura inválida e falha de comunicação precisam
permanecer distinguíveis. O sistema pode sinalizar baixa confiança e manter o
evento visível, mas não promete corrigir automaticamente qualquer defeito.

**Evidência:** `docs/CONTRATO_TELEMETRIA_V1.md`, `docs/limiares.md` e
`docs/evidence/s8/S8-T1_REPORT.md`.

**Limitação:** não há ensaio físico abrangente de sensor desconectado, ruidoso e
mal calibrado em máquina real.

**Complementar:** “A leitura inválida entra no modelo?”

**Resposta complementar:** A política deve impedir que dado inválido seja
tratado como leitura normal; a cobertura exata de cada caminho deve ser
demonstrada nos testes correspondentes.

**Status:** PARCIALMENTE EVIDENCIADA.

### 18. Por que não a solução do OEM?

**Resposta curta:** A resposta equilibrada é: OEM pode ser a melhor solução em
contextos com máquina, dados e integração já disponíveis. O FieldNode não se
declara substituto superior; investiga se existe espaço complementar em frotas
mistas e conectividade limitada. Ainda não temos comparação ou integração real.

**Evidência:** `FIELDNODE_LEVIATA_ROADMAP_V5.md`, seção 22, e
`docs/ROTEIRO_VALIDACAO_COMERCIAL.md`.

**Limitação:** não afirmar preço, fechamento ou inferioridade de OEM.

**Complementar:** “Qual hipótese precisa ser provada primeiro?”

**Resposta complementar:** Que um usuário real tem uma decisão recorrente não
atendida pela solução disponível e aceita testar o fluxo com critérios claros.

**Status:** ROADMAP/BLOQUEADA para conclusão.

## 5. Banco adicional por especialidade

As respostas abaixo são cartões de estudo. A pessoa deve explicar a razão, não
recitar a frase.

### Arquitetura e backend

| Pergunta | Resposta curta | Evidência | Status |
| --- | --- | --- | --- |
| Por que Django? | É a base efetivamente usada para API, persistência e autorização; não alegamos que seja a única escolha possível. | `requirements.txt`, `api_tcc/`, testes | EVIDENCIADA |
| Como evita duplicidade? | Usa identidade da mensagem e contrato de ingestão; repetição deve ser tratada idempotentemente. | `docs/CONTRATO_TELEMETRIA_V1.md` | EVIDENCIADA |
| Como separa organizações? | A autorização deve filtrar organização e recurso no backend; a cobertura de cada operação sensível precisa ser testada. | `docs/SEGURANCA.md`, testes de autorização | PARCIALMENTE EVIDENCIADA |
| O que acontece com o banco indisponível? | O serviço deve falhar de forma observável; a fila local é a alternativa na borda testada, não uma garantia de disponibilidade total. | `docs/evidence/s6/`, `docs/evidence/s8/` | PARCIALMENTE EVIDENCIADA |
| Quais gargalos existem? | Não há dimensionamento representativo publicado; medir ingestão, consultas e worker antes de trocar a arquitetura. | `docs/evidence/s10/S10-T8_REPORT.md` | NÃO EVIDENCIADA |

### IoT, hardware e offline

| Pergunta | Resposta curta | Evidência | Status |
| --- | --- | --- | --- |
| O que está fisicamente implementado? | O checkout sustenta código e testes de host; compra, montagem e ensaio físico devem ser comprovados separadamente. | `docs/evidence/s8/S8-T10_REPORT.md`, `S8-T14_REPORT.md` | PARCIALMENTE EVIDENCIADA |
| Qual é o alcance medido? | Não há alcance de rádio autorizado no checkout. | `docs/evidence/s8/S8-T4_S8-T5_IMPLEMENTATION.md` | NÃO EVIDENCIADA |
| Como funciona a fila local? | Persiste, tenta novamente, valida ACK e evita apagar antes da confirmação no fluxo testado. | `docs/evidence/s8/S8-T4_S8-T5_IMPLEMENTATION.md` | EVIDENCIADA em software |
| O que acontece depois de reboot? | Há contratos e componentes previstos, mas o reboot físico precisa de ensaio e evidência própria. | `docs/evidence/s8/S8-T3_RTC_REPORT.md` | PARCIALMENTE EVIDENCIADA |
| O que é simulação? | Fixtures, séries sintéticas e host não são sensor, rádio ou máquina agrícola. | `docs/CLAIMS_VS_CODE.md` | EVIDENCIADA como limite |

### Machine Learning

| Pergunta | Resposta curta | Evidência | Status |
| --- | --- | --- | --- |
| Por que Isolation Forest? | Para sinalizar comportamento atípico sem rotular cada falha; é complemento, não diagnóstico. | `docs/HONESTIDADE_METODOLOGICA_ML.md` | EVIDENCIADA |
| Como avaliaram? | O harness fixa cenários, sementes e métricas; o resultado é sintético e não de campo. | `docs/evidence/s5/S5-T2_REPORT.md`, `docs/AVALIACAO_ANOMALIA.md` | EVIDENCIADA com limite |
| Existe previsão de falha? | Não há evidência autorizada para essa afirmação. | `docs/evidence/s5/S5-T5_REPORT.md` | NÃO EVIDENCIADA |
| Existe RUL? | Não. Vida útil residual exige dados e validação que não estão disponíveis. | `docs/HONESTIDADE_METODOLOGICA_ML.md` | ROADMAP |
| Como tratam falsos positivos? | O benchmark os expõe; em produção, a triagem precisa de contexto e desfecho real para calibrar. | `docs/AVALIACAO_ANOMALIA.md` | PARCIALMENTE EVIDENCIADA |

### IA generativa e decisões

| Pergunta | Resposta curta | Evidência | Status |
| --- | --- | --- | --- |
| Qual é o papel do LLM? | Propor texto ou decisão pendente com evidências permitidas; não executar manutenção. | `api_tcc/services/agentic.py`, `docs/OPERATIONAL_DECISION_MEMORY.md` | PARCIALMENTE EVIDENCIADA |
| Como evitam invenção? | Guardrails, evidências vinculadas e recusa quando falta suporte; a execução real com serviço externo continua dependente de configuração. | `docs/evidence/s5/S5-T7_REPORT.md`, `S5-T8_REPORT.md` | PARCIALMENTE EVIDENCIADA |
| Quem decide? | A pessoa autorizada; a recomendação fica pendente. | `docs/OPERATIONAL_DECISION_MEMORY.md` | EVIDENCIADA |
| O que acontece em timeout? | Deve seguir o fallback documentado e preservar a falha; não inventar resposta. Conferir a rota antes da banca. | `api_tcc/services/agentic.py` | PARCIALMENTE EVIDENCIADA |

### Segurança e privacidade

| Pergunta | Resposta curta | Evidência | Status |
| --- | --- | --- | --- |
| O frontend protege operação sensível? | Não sozinho; a autorização precisa estar no backend. | `docs/SEGURANCA.md` | EVIDENCIADA |
| Há TLS e secure boot comprovados? | Não apresentar como comprovados; há pendências documentadas. | `docs/evidence/s8/S8-T8_REPORT.md` | EVIDENCIADA como limite |
| O que não entra em log? | Segredos, tokens e credenciais não devem ser registrados. | `AGENTS.md`, `docs/SEGURANCA.md` | EVIDENCIADA como política |

### Produto, operação e estratégia

| Pergunta | Resposta curta | Evidência | Status |
| --- | --- | --- | --- |
| Quem compra? | Ainda é hipótese; as entrevistas devem investigar papéis e decisões concretas. | `docs/ROTEIRO_VALIDACAO_COMERCIAL.md` | BLOQUEADA |
| Há cliente ou piloto? | Não afirmar sem documento verificável no checkout. | `docs/PITCH_FATOS.md` | NÃO EVIDENCIADA |
| Qual o próximo experimento? | Fechar validação física, coletar desfechos e executar o ensaio externo antes de ampliar claims. | `FIELDNODE_LEVIATA_ROADMAP_V5.md`, seções 22 e 23 | ROADMAP |

## 6. Matriz provisória de responsabilidade

Os papéis abaixo vêm do roteiro fornecido e precisam ser confirmados pelo grupo
antes de virarem distribuição definitiva.

| Integrante | Área principal | Áreas secundárias | Perguntas prioritárias | Lacunas a cobrir |
| --- | --- | --- | --- | --- |
| Paola | Liderança, integração e decisões | Arquitetura, produto | 1, 2, 12, 13, 18 | Limites de ML e hardware |
| Vinícius | Backend e IA | Segurança, dados | 4, 7, 9, 16, 17 | Estado exato dos artefatos da demo |
| Ana | Frontend e UI/UX | Operação e acessibilidade | 2, 6, 10, 12 | Contratos backend e autorização |
| Giovana | Hardware e IoT | Offline e conectividade | 6, 8, 14, 15, 17 | Evidência física, alcance e ensaio |

Regra de rodízio: ninguém é a única pessoa capaz de responder pela própria
área. Todos devem saber explicar arquitetura, fluxo, limites, origem dos dados
e o que a demo realmente prova.

## 7. Ensaio com pessoa de fora

Procedimento:

1. Escolher uma pessoa que não escreveu este documento.
2. Sortear cinco perguntas por integrante, misturando áreas e incluindo uma
   complementar inesperada.
3. Responder sem consultar o arquivo; pedir evidência sempre que surgir número.
4. Registrar pergunta, integrante, tempo, clareza, precisão, evidência citada,
   contradição, consulta necessária e avaliação.
5. Repetir as perguntas que geraram respostas decoradas ou vagas.

Critério individual: cada integrante responde cinco perguntas sem consulta,
incluindo uma da própria área, uma de outra área, uma de arquitetura, uma de
limitação/evidência e uma inesperada. Consulta não é escondida; vira lacuna.

## 8. Registro de ensaio e gravação

| Item | Estado |
| --- | --- |
| Pessoa externa identificada | PENDENTE |
| Data e participantes | PENDENTE |
| Cinco respostas sem consulta por integrante | PENDENTE |
| Ata com perguntas complementares | PENDENTE |
| Gravação autorizada e armazenada | PENDENTE |
| Revisão de contradições | PENDENTE |

Antes de gravar: obter autorização dos participantes, evitar segredos e dados
identificáveis, registrar contexto e não editar erros relevantes para parecer
que o grupo respondeu melhor do que respondeu.

## 9. Checklist final

- [x] As 15 perguntas originais da seção 22 foram recuperadas.
- [x] As três perguntas adicionais do professor foram incluídas.
- [x] As respostas citam arquivos e limites.
- [x] As áreas técnicas estão cobertas.
- [x] A matriz de responsabilidade está disponível como provisória.
- [ ] Simulação externa realizada.
- [ ] Cinco respostas sem consulta por integrante.
- [ ] Lacunas atualizadas após o ensaio.
- [ ] Gravação disponível.
- [ ] Revisão independente do pitch registrada.

O documento está pronto para ser usado no preparo. Os itens de ensaio não estão
marcados como concluídos porque não há ata, gravação ou resultado observável no
checkout. Isso não é burocracia; é a diferença entre treinamento e fanfic com
planilha.
