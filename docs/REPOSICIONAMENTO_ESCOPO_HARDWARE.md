# REPOSICIONAMENTO_ESCOPO_HARDWARE

**Responsável:** A CONFIRMAR  
**Semana:** S8  
**Status:** ESQUELETO  
**Tarefa de preenchimento:** S8-Tx (confirmar identificador exato; S8-T5 mencionado no roadmap para ESP-NOW)  
**Última atualização:** 2026-11-04 — criação do esqueleto (S0-T4)

> **Atenção:** o status deste documento só poderá mudar de `ESQUELETO` para outro quando:
> - as seções obrigatórias estiverem preenchidas com evidências de S8;
> - as evidências físicas estiverem anexadas ou referenciadas;
> - os critérios de conclusão forem atendidos;
> - a revisão da semana S8 for realizada.

---

## 1. Objetivo

Delimitar com precisão o que o hardware do FieldNode realmente comprova em
cada estágio de desenvolvimento, e o que permanece como evolução futura —
protegendo a defesa acadêmica e qualquer apresentação pública de afirmações
não sustentadas por evidências físicas.

TODO(responsável-S8, por quê: a banca pode questionar especificamente o que foi testado em hardware real vs. simulador, quando: início de S8): definir o objetivo técnico específico após a realização dos experimentos físicos de S8.

---

## 2. Escopo

### Incluído

TODO(responsável-S8, por quê: delimitar o que será documentado aqui, quando: S8): listar os componentes físicos, os testes planejados e o que pode ser afirmado após S8.

### Fora do escopo

TODO(responsável-S8, por quê: evitar que este documento seja interpretado como validação de campo, quando: S8): registrar o que não será tratado (ex: validação de campo em condições reais de colheita, integração CAN/J1939, múltiplas máquinas simultâneas).

---

## 3. Contexto atual do FieldNode

**Estado verificado em 2026-11-04 (S0-T3):**

**Não há firmware, código ESP32, biblioteca ESP-IDF, PlatformIO ou arquivo `.ino`/`.c`/`.cpp` no repositório.**

- `simulators/edge_client.py` — cliente Python de bancada (HTTP, não hardware)
- `simulators/transbordo_mule_client.py` — simulador de Data Mule (Python-only, sem rádio)
- O termo "ESP32" aparece apenas como string em `device_id` de fixtures de teste
- README afirma: "ESP32/ESP-NOW permanecem como integração física a validar"
- AGENTS.md lista ESP32 e ESP-NOW como componentes a serem validados

TODO(responsável-S8, por quê: atualizar com o estado real após S8, quando: início de S8): complementar com o protótipo físico adquirido, montado e testado.

---

## 4. Especificação e conteúdo técnico

### 4.1 Escopo atual do protótipo (preencher após S8)

TODO(responsável-S8, por quê: o escopo determina o que pode ser afirmado publicamente, quando: S8): descrever o protótipo físico: placa, sensores, fonte de energia, invólucro.

### 4.2 Componentes físicos

TODO(responsável-S8, por quê: lista de componentes permite reproduzir o protótipo, quando: S8): listar modelo exato de cada componente com referência de datasheet.

### 4.3 Microcontrolador

TODO(responsável-S8, por quê: o modelo exato do ESP32 afeta as capacidades de comunicação, quando: S8): especificar: ESP32-S3? ESP32-C3? Versão do SDK? Framework (ESP-IDF, Arduino, PlatformIO)?

### 4.4 Sensores

TODO(responsável-S8, por quê: cada sensor tem faixa, precisão e protocolo específicos, quando: S8): documentar cada sensor: modelo, grandeza medida, faixa, protocolo (I2C, SPI, ADC), calibração realizada.

### 4.5 Firmware

TODO(responsável-S8, por quê: o firmware é a evidência primária de que o hardware funciona, quando: S8): referenciar o diretório do firmware no repositório, versão, e comandos de build/flash.

### 4.6 Comunicação implementada

TODO(responsável-S8, por quê: o tipo de comunicação determina o que pode ser afirmado sobre alcance e confiabilidade, quando: S8): documentar qual protocolo foi implementado (HTTP, MQTT, ESP-NOW) e o que foi verificado.

### 4.7 Topologia de testes

TODO(responsável-S8, por quê: a topologia determina as condições de validade dos resultados, quando: S8): descrever a configuração do ensaio (bancada, sala, distância, número de dispositivos).

### 4.8 Diferenças entre bancada e campo

TODO(responsável-S8, por quê: essa distinção é o núcleo deste documento, quando: S8): tabela comparando o que foi testado na bancada e o que ainda precisaria de campo.

| Critério | Bancada (após S8) | Campo (não validado) |
|---|---|---|
| Distância de comunicação | A preencher | Não testado |
| Interferência RF | A preencher | Não testado |
| Temperatura ambiente | A preencher | Não testado |
| Vibração mecânica | A preencher | Não testado |
| Fonte de energia em campo | A preencher | Não testado |
| Múltiplos dispositivos simultâneos | A preencher | Não testado |

### 4.9 ESP-NOW e seus limites de validação

TODO(responsável-S8, por quê: ESP-NOW é uma afirmação específica que exige evidência de S8-T5 antes de ser citada, quando: S8-T5): documentar:
- se ESP-NOW foi implementado
- distância testada
- condições do teste
- taxa de sucesso
- o que não foi testado

**Regra:** não declarar ESP-NOW funcional antes das evidências de S8-T5.

### 4.10 Requisitos para comunicação entre máquinas

TODO(responsável-S8, por quê: listar o que é necessário para evoluir de bancada para comunicação real entre máquinas, quando: S8): definir os requisitos técnicos e as evidências necessárias.

### 4.11 Riscos e limitações

TODO(responsável-S8, por quê: documentar riscos antes da defesa evita surpresas, quando: S8): listar os riscos técnicos e as limitações conhecidas do protótipo.

### 4.12 Evolução futura

TODO(responsável-S8, por quê: separar o que é validado do que é roadmap protege a defesa, quando: S8): listar os próximos passos necessários para evolução do protótipo para operação real.

### 4.13 Evidências físicas e registros de teste

TODO(responsável-S8, por quê: evidências físicas são o único meio de sustentar afirmações de hardware, quando: S8): referenciar fotos, vídeos, logs de serial, capturas de osciloscópio ou analisador de protocolo.

---

## 5. Evidências e validação

TODO(responsável-S8, por quê: evidências verificáveis são o que separa afirmação de fato, quando: após execução de S8): adicionar:
- foto do protótipo montado
- vídeo de demonstração (opcional, mas valioso)
- log de serial durante operação
- resultado do protocolo de comunicação
- arquivo de firmware (referência no repositório)

**Evidências atuais (S0):** Sem evidência física. Apenas simuladores de software.

---

## 6. Limitações e riscos

TODO(responsável-S8, por quê: registro antecipado de limitações protege a defesa, quando: S8): complementar.

**Limitações conhecidas em S0:**
- Nenhum hardware adquirido ou montado no repositório atual
- Nenhum firmware presente
- Simuladores de software não provam comportamento de hardware
- Comunicação entre máquinas (ESP-NOW) requer validação específica (S8-T5)
- Operação em campo (vibração, temperatura, RF) não pode ser inferida de bancada

---

## 7. Critérios de conclusão

TODO(responsável-S8, por quê: critérios claros permitem verificação objetiva, quando: S8): definir critérios verificáveis.

**Critérios propostos (a confirmar em S8):**
- [ ] Protótipo físico montado e documentado
- [ ] Firmware no repositório com instruções de build/flash
- [ ] Evidências físicas (foto/vídeo/log) referenciadas
- [ ] Tabela bancada vs. campo preenchida
- [ ] ESP-NOW documentado com evidência de S8-T5 (ou marcado como não implementado)
- [ ] Revisão por outro membro realizada

---

## 8. Histórico de alterações

| Data | Responsável | Alteração |
|---|---|---|
| 2026-11-04 | S0-T4 (Antigravity) | Criação do esqueleto com estado verificado em S0 |
