# S8-T3 — Reposicionamento honesto do escopo de hardware

Este documento é a fonte de referência para README, landing pages, propostas,
apresentações e pitches do FieldNode. Ele separa implementação, teste de
software, ensaio de bancada, validação em campo e roadmap. A regra é simples:
uma capacidade só deve ser anunciada como entregue quando houver evidência
correspondente no repositório.

## 1. Resumo executivo

O FieldNode é um protótipo de telemetria e inteligência operacional para
máquinas agrícolas. O checkout contém uma API Django para ingestão e validação
de leituras, persistência em banco, deduplicação, análise de anomalias e uma
interface Next.js. Também contém um cliente Python de borda com outbox SQLite,
retry, prioridades e sincronização posterior.

O que foi comprovado neste repositório é o fluxo de software em bancada. O
ensaio não comprova um dispositivo ESP32 operando em campo, sensores
industriais, ESP-NOW, autonomia energética, alcance de rádio ou armazenamento
físico por 30 dias. Essas capacidades continuam como etapas de integração e
validação física. A visão de longo prazo permanece válida; só não deve ser
apresentada como produto já demonstrado.

## 2. Matriz de maturidade

| Capacidade | Estado | Evidência | Limitação atual | Próxima validação |
| --- | --- | --- | --- | --- |
| API de ingestão e validação | Implementado | `api_tcc/api/views_ingestao.py`, `api_tcc/services/telemetria.py` e testes em `api_tcc/tests/` | Não representa, por si só, um dispositivo físico | Ensaio integrado com hardware identificado |
| Cliente offline-first | Testado em software | `simulators/edge_client.py` e `simulators/test_edge_client.py` | Cliente Python de bancada, não firmware ESP32 | Repetir o protocolo em hardware-alvo |
| Buffer local | Testado em software | Outbox SQLite em `simulators/edge_client.py`; resultados S8-T1/S8-T2 | Capacidade física depende de armazenamento, taxa de amostragem e reinicializações | Medir armazenamento e recuperação no dispositivo físico |
| Sincronização após reconexão | Testado em software | `docs/PROTOCOLO_TESTE_RESILIENCIA_OFFLINE.md` e `artifacts/resilience/` | R3 tem interferência concorrente documentada | Repetir a janela prolongada com isolamento comprovado |
| Prioridades A/B/C | Testado em software | Classificação no cliente e sequência observada nos resultados S8-T1/S8-T2 | Ordem por prioridade não é ordenação global estrita | Validar política no hardware e no canal escolhido |
| ESP32 físico | Não comprovado | Não foi localizado firmware, registro de ensaio ou evidência de execução com ESP32 neste checkout | RAM, flash, energia, reboot, temperatura e armazenamento físico não foram ensaiados | Montar e registrar ensaio reproduzível com o dispositivo-alvo |
| ESP-NOW | Planejado / não comprovado | A tecnologia aparece em documentação de comunicação; o campo `transport` do contrato lista os valores `http`, `mqtt` e `ble` — ESP-NOW não consta entre os transportes documentados no contrato | Não há alcance, estabilidade ou operação de rádio demonstrados | Implementar e medir em bancada antes de comunicar como capacidade entregue |
| Sensores industriais | Não comprovado | O contrato define campos de telemetria e limites de payload; não identifica sensores industriais instalados | Dados podem ser simulados ou de prototipagem; precisão e adequação agrícola não foram demonstradas | Identificar componentes e executar calibração e ensaios ambientais |
| CAN/J1939 | Planejado / não comprovado | `docs/SEGURANCA.md` menciona "máquinas antigas sem barramento J1939 acessível" como lacuna de piloto real; não há integração, adaptador, driver ou ensaio localizado | Nenhum adaptador, driver ou ensaio foi localizado | Definir escopo e validar com equipamento compatível |
| ISOBUS | Planejado / não comprovado | Não foi localizada menção a ISOBUS em `docs/SEGURANCA.md` nem em qualquer outro arquivo do checkout; a referência a barramento naquele documento é exclusivamente a J1939 | Nenhuma evidência de integração, adaptador ou ensaio | Avaliar escopo separadamente de CAN/J1939 antes de comunicar como capacidade |
| Operação em campo | Não comprovado | Não foi localizado registro de ensaio em campo acessível no repositório | Não há base para declarar alcance, autonomia ou confiabilidade em condições reais | Ensaio progressivo com telemetria, rádio, energia e ambiente registrados |
| Autonomia de 30 dias | Planejado / não comprovado | O protocolo S8-T2 afirma explicitamente que não prova armazenamento por 30 dias | Não há cálculo físico ou medição específica no hardware-alvo | Medir capacidade, retenção, falhas e reinicializações com premissas publicadas |

### Categorias usadas

- **Implementado:** existe código funcional correspondente.
- **Testado em software:** o comportamento foi executado de forma reproduzível,
  sem provar hardware.
- **Demonstrado em bancada:** há ensaio controlado com o componente físico
  relevante.
- **Validado em campo:** há registros de execução em condições reais.
- **Parcial:** somente parte da capacidade está disponível.
- **Planejado:** consta como evolução, mas não foi implementado ou comprovado.
- **Não comprovado:** não há evidência acessível suficiente para sustentar a
  alegação.

## 3. O que S8-T1 e S8-T2 realmente demonstram

O cliente Python grava leituras em uma outbox SQLite antes da sincronização,
usa `message_id`, `sequence_number` e `payload_hash`, classifica mensagens em
prioridades A/B/C, tenta reenvio com backoff e só avança o cursor local quando
não há lacunas. O backend aceita o contrato existente e mantém a deduplicação.

No resultado registrado de S8-T1, 50 leituras ficaram pendentes com a API
indisponível e depois foram sincronizadas, com 50 ACKs correspondentes, zero
duplicatas por `message_id` e `sequence_number` e cursor local final 50.

O S8-T2 registrou três rodadas automatizadas:

| Cenário | Indisponibilidade | Resultado | Observação |
| --- | ---: | --- | --- |
| R1 | 35,360 s | 100/100 recebidas, zero perdidas e zero duplicatas | Validada |
| R2 | 305,532 s | 100/100 recebidas, zero perdidas e zero duplicatas | Validada |
| R3 | 1808,062 s | 100/100 recebidas, zero perdidas e zero duplicatas | Documentada com ressalva por processo concorrente no Compose |

As três rodadas preservaram o conjunto de sequências e uma persistência por
leitura. A métrica de 87 ocorrências fora de ordem não é perda de dados: resulta
do despacho deliberado por prioridade A > B > C. Os resultados e as ressalvas
estão em `docs/PROTOCOLO_TESTE_RESILIENCIA_OFFLINE.md` e nos JSONs de
`artifacts/resilience/`.

Isso é evidência de um protocolo de outbox em cliente Python de bancada. Não é
evidência de operação em ESP32, persistência em flash, autonomia energética,
rádio, perda de energia, ambiente agrícola ou segurança física da credencial.

## 4. Buffer de 30 dias

“Buffer de 30 dias” não deve ser usado como capacidade comprovada. A duração
depende de taxa de geração, tamanho dos payloads, frequência de amostragem,
quantidade de dispositivos, espaço disponível, política de retenção,
reinicializações e comportamento diante de falhas.

O repositório comprova buffer local em SQLite no cliente Python e ensaios de
recuperação nas janelas descritas acima. Não comprova 30 dias no hardware
físico. A formulação autorizada é:

> O protótipo possui buffer local de telemetria em software, testado nos
> cenários documentados. A capacidade de armazenamento por 30 dias no
> hardware-alvo permanece como objetivo de desenvolvimento e exige validação
> específica.

## 5. ESP-NOW, sensores e campo

ESP-NOW aparece em materiais de comunicação, mas não consta entre os transportes documentados no contrato de telemetria (que lista `http`, `mqtt` e `ble`) e não foi localizada implementação física executada, medição de alcance, teste de estabilidade ou registro de uso em campo. Portanto, a redação correta é:

> A integração via ESP-NOW permanece como etapa de desenvolvimento e validação
> física.

Os campos `temperatura`, `vibracao` e `rpm` comprovam um contrato de dados e
limites de aceitação, não a existência de sensores industriais nem a precisão
das medições. Também não foi encontrada evidência suficiente para afirmar
integração com CAN/ISOBUS, alcance de 50–200 m ou operação em máquina agrícola
real neste checkout. Números presentes em uma proposta acadêmica devem manter o
status e as limitações declarados naquele documento, sem serem promovidos a
capacidade validada do repositório.

## 6. Segurança e integridade

O contrato atual usa `X-API-Key` na ingestão. Isso autentica a chamada conforme
a aplicação, mas não prova identidade individual do dispositivo nem assinatura
criptográfica do payload. Uma chave global gravada em hardware físico poderia
ser extraída por acesso físico.

Credenciais por dispositivo, rotação de chaves e assinatura assimétrica são
evoluções futuras. Este bloco apenas registra o limite; não implementa esses
mecanismos.

## 7. Roadmap de validação física

1. manter o cliente Python e a persistência local reproduzíveis;
2. repetir interrupção e recuperação com ambiente de teste isolado;
3. medir capacidade, retenção e integridade do armazenamento;
4. executar ensaio com ESP32 físico identificado;
5. testar comunicação, alcance e estabilidade em bancada;
6. avançar para condições progressivamente próximas do campo;
7. avaliar CAN/ISOBUS ou outro protocolo quando houver escopo aprovado;
8. medir autonomia e operação prolongada.

Nenhuma etapa acima deve ser descrita como concluída antes de possuir registro
verificável.

## 8. Linguagem autorizada

### Sustentada pela evidência atual

> O protótipo possui um cliente Python com persistência local de telemetria,
> retry, prioridades e sincronização após o retorno da conectividade, testado
> em bancada nos cenários documentados.

### Exige validação adicional

- “Armazena 30 dias de dados no ESP32.”
- “Opera por ESP-NOW em ambiente rural.”
- “Está validado em campo.”
- “Garante zero perda de dados.”
- “Usa sensores industriais.”
- “Integra-se a colheitadeiras por CAN/ISOBUS.”
- “Tem alcance de 50–200 m.”

## 9. Materiais inspecionados e lacunas

Foram inspecionados `README.md`, `simulators/edge_client.py`,
`simulators/test_edge_client.py`, `simulators/teste_resiliencia.py`,
`docs/PROTOCOLO_TESTE_RESILIENCIA_OFFLINE.md`, os artefatos JSON de
`artifacts/resilience/`, `docs/SEGURANCA.md`, o contrato de telemetria,
os testes relacionados, `docs/faq_banca.md`, `DEMO.md`, `faq_banca.md`
(raiz), `docs/SEQ_ID.md` e `docs/archive/GUIA-UUID-VS-SEQID.md`.

**Estado após revisão S8-T3:**

| Arquivo | Alteração | Estado |
| --- | --- | --- |
| `docs/faq_banca.md` | Revisado nesta rodada | Alegações de hardware reescritas como proposta/roadmap |
| `DEMO.md` | Revisado na rodada anterior | Referências a ESP32 como fonte substituídas por simulador Python |
| `faq_banca.md` (raiz) | Revisado nesta rodada | Filtro de média móvel, ESP-NOW, buffer no hardware, UUID no sensor e instalação em máquinas antigas reescritos como proposta/roadmap |
| `docs/SEQ_ID.md` | Revisado nesta rodada | "Gerado no ESP32" corrigido para "simulador Python; firmware é etapa futura" |
| `docs/archive/GUIA-UUID-VS-SEQID.md` | Revisado nesta rodada | Cabeçalho de arquivo histórico adicionado; referências a ESP32 contextualizadas como intenção de design da época |

`frontend/index.html` não existe neste checkout. Também não foi localizada a
`FieldNode_Proposta_TCC_v4.docx` no repositório ou entre os arquivos acessíveis
nesta inspeção. Por isso, não foram feitas alterações nesses materiais e não se
atribui a eles conteúdo além do contexto fornecido para esta tarefa.

A ausência de evidência aqui significa apenas que a alegação não pode ser
sustentada por este checkout.
