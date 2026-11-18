# S8-T14 - Protocolo de integração incremental do hardware

## Objetivo e regra de passagem

Este documento é o registro operacional da integração física do FieldNode. A
integração avança em oito degraus, isolando sensor, conectividade, persistência,
rádio e alarme local.

**Regra central:** um degrau só pode ser aprovado com procedimento executado,
resultado registrado e evidência rastreável. Código compilado, teste host e
documentação não substituem bancada física.

## Estado atual

Estado da execução deste protocolo: **PENDENTE DE VALIDAÇÃO FÍSICA**.

A auditoria do checkout encontrou documentação e firmware para os blocos de
S8-T10 a S8-T13, mas não encontrou inventário físico comprovado, foto de kit,
placa identificada, vídeo ou logs de ensaio físico. Portanto, nenhum degrau é
marcado como aprovado apenas por inferência.

| Degrau | Escopo | Estado atual | Evidência disponível | Próximo teste |
|---|---|---|---|---|
| D1 | ESP32 + um sensor + Serial | PENDENTE | firmware e testes host; bancada ausente | identificar placa e DS18B20; manter 10 min |
| D2 | Wi-Fi + MQTT | PENDENTE | código de conexão MQTT; publicação física ausente | publicar do ESP32 e capturar `mosquitto_sub` |
| D3 | backend + persistência | PENDENTE | contrato e consumidor existentes; origem física não comprovada | comparar payload físico com linha no banco |
| D4 | RTC + sequência | PENDENTE | implementação de RTC/sequence no firmware; reinício físico ausente | registrar antes/depois de reboot |
| D5 | outbox em flash | PENDENTE/BLOQUEADO | biblioteca `outbox` presente; interrupção física não executada | executar bancada controlada com 50 interrupções |
| D6 | segundo ESP32 + ESP-NOW | PENDENTE | biblioteca de enlace presente; gateway físico ausente | medir ACK de recepção, custódia e backend |
| D7 | LoRa | BLOQUEADO | nenhum módulo físico comprovado no inventário | identificar módulos, frequência e autorização |
| D8 | alarme local + sensores extras | PENDENTE | S8-T13: 11/11 testes nativos; periféricos não conectados | estímulo físico com gateway desligado |

Datas e responsáveis permanecem `NÃO REGISTRADOS` até uma execução real.

## Topologia prevista

```text
sensor/ESP32 nó
  ├─ Serial / RTC / outbox flash
  └─ Wi-Fi + MQTT                 ──> broker local ──> consumidor Django ──> banco
       ou ESP-NOW ──> gateway ────┘

ESP32 nó ──> LED/buzzer/OLED local, independente do gateway
ESP32 nó ──> LoRa, somente após o teste de rádio isolado
```

Pinagem documentada no checkout, ainda sujeita à confirmação da placa real:

| Função | GPIO/configuração | Observação |
|---|---:|---|
| DS18B20 | 4 | confirmar resistor e alimentação |
| LED | 2 | confirmação física pendente |
| buzzer | 26 | configuração de bancada, não aceite físico |
| I2C SDA/SCL | 21/22 | confirmar endereço do módulo |
| RPM | 27 | Hall/óptico ainda não comprovado |
| GPS RX/TX | 16/17 | 9600 baud configurado |

## Pré-requisitos gerais

- placa, sensores, módulos e fonte identificados por modelo e número interno;
- firmware, commit e configuração registrados;
- fonte limitada e montagem sem risco de curto;
- broker local, credenciais individuais e ACL preparados;
- banco de desenvolvimento restaurável;
- instrumentos e procedimento de desligamento seguro disponíveis;
- nenhum segredo, endereço privado desnecessário ou identificador sensível
  anexado às evidências públicas.

## Critérios comuns

- `APROVADO` exige todos os critérios do degrau e evidência anexada;
- `REPROVADO` preserva a tentativa e bloqueia os degraus seguintes;
- correção exige reexecução do degrau afetado;
- mudança em hardware, firmware, contrato ou configuração pode invalidar
  evidências posteriores;
- teste host não substitui teste físico;
- teste físico isolado não substitui fluxo ponta a ponta;
- etapa não executada ou sem evidência permanece `PENDENTE`;
- uma etapa aprovada não valida o produto inteiro.

## Registro por degrau

Cada execução deve preencher: identificador, status, data/hora, responsável,
placa, componentes, firmware/commit, configuração, critério, resultado,
evidências, falhas, correções e reexecução. Tentativas antigas não devem ser
apagadas.

### D1 - ESP32 + um sensor + Serial

**Procedimento:** conectar um sensor por vez, conferir alimentação e pinagem,
iniciar firmware mínimo e observar a Serial por pelo menos 10 minutos.

**Passa quando:** leitura estável, sem reboot inesperado, valores inválidos
identificados e unidade/faixa documentadas.

**Suspeitos em falha:** alimentação, fio, resistor, GPIO, I2C, biblioteca ou
sensor.

### D2 - Wi-Fi + MQTT para o notebook

**Procedimento:** manter D1, conectar o ESP32 à rede, autenticar com credencial
individual, publicar no tópico contratado e observar com `mosquitto_sub`.

**Passa quando:** a mensagem vem do ESP32, tem payload válido, `device_id`
correto, ACL aceita, reconexão é observada e nenhum segredo aparece no log.

### D3 - Backend local + persistência

**Procedimento:** manter D2, ativar o consumidor MQTT real, enviar uma leitura,
validar o contrato e consultar a linha persistida no banco.

**Passa quando:** origem, unidade, `device_id` e conteúdo persistido batem com o
payload físico; duplicidade e rejeição inválida ficam registradas.

### D4 - RTC + sequência persistente

**Procedimento:** registrar leituras, reiniciar a placa e registrar novamente.
Comparar `boot_id`, sequência, `uptime_ms`, `event_time` e `time_source`.

**Passa quando:** sequência não regride, novo boot é distinguido e horário não
confiável não é inventado. Sequência crescente não prova horário confiável.

### D5 - Outbox persistente em flash

**Procedimento:** verificar persistência antes do envio, CRC, ordem de ACK e
recuperação. A meta física é 50 interrupções controladas de alimentação.

**Passa quando:** registros confirmados sobrevivem, incompletos não são tratados
como válidos, não há duplicidade e falhas de gravação são registradas.

Teste host ou reinício por software deve ser marcado separadamente e não conta
como interrupção física de alimentação.

### D6 - Segundo ESP32 + ESP-NOW

**Procedimento:** identificar nó e gateway, transmitir, registrar tentativas,
recepção, falhas e ACKs, encaminhar ao broker e confirmar no banco.

**Passa quando:** origem é preservada, ACK de enlace é distinto de ACK de
custódia/backend, PER tem denominador explícito e a cópia da origem só é
removida conforme o protocolo.

Callback de envio não é recebimento confirmado. A rede adora essa pegadinha.

### D7 - LoRa

**Procedimento:** testar módulos reais isoladamente, registrar frequência,
antena, parâmetros, RSSI, SNR, pacotes enviados/recebidos/perdidos e repetir
em distâncias documentadas.

**Passa quando:** configuração é reproduzível, PER tem método explícito e as
limitações de alcance estão registradas. Uma única medição não é alcance de
campo.

### D8 - Alarme local + sensores extras

**Procedimento:** integrar sensores já aprovados, conferir barramentos e
alimentação, conectar periféricos, desligar gateway e aplicar estímulo seguro.

**Passa quando:** leituras são válidas, alarme e código vêm da lógica local,
evento é preservado para sincronização e qualidade/origem permanecem corretas.

## Matriz de reexecução

| Mudança | Repetir |
|---|---|
| sensor, GPIO ou alimentação | D1 e todos os degraus dependentes |
| credencial, SSID, broker ou tópico | D2 e D3; D4-D8 se o caminho mudar |
| schema, consumidor ou persistência | D3 e validações ponta a ponta |
| RTC, NVS ou sequência | D4-D6 e D8 se o evento local mudar |
| outbox, CRC ou política de ACK | D5-D6 |
| rádio ESP-NOW, gateway ou canal | D6 |
| módulo/parâmetro de LoRa | D7 |
| sensor extra, alarme ou prescrição local | D8 |

## Checklist de segurança

- [ ] fonte limitada e polaridade conferida;
- [ ] alimentação desligada antes de alterar fios;
- [ ] antena conectada antes de transmitir rádio;
- [ ] nenhum teste de CAN/rádio fora da autorização e faixa aplicável;
- [ ] credenciais individuais, nunca secretas em foto/log;
- [ ] banco de teste identificado e sem dados de produção;
- [ ] estímulo físico seguro e sem simular condição perigosa em máquina real;
- [ ] botão/procedimento de desligamento conhecido.

## Histórico de execuções

| Data/hora | Degrau | Responsável | Configuração | Resultado | Evidência | Falhas/correção |
|---|---|---|---|---|---|---|
| não registrada | D1-D8 | não registrado | não registrado | não executado fisicamente | não disponível | inventário físico ausente |

## Pendências e bloqueios

1. comprovar aquisição e recebimento dos componentes da BOM;
2. identificar placa, sensores e módulos reais;
3. executar D1-D4 em bancada;
4. executar o teste físico de 50 interrupções de D5, se seguro e possível;
5. montar segundo ESP32 para D6;
6. identificar e autorizar o conjunto LoRa para D7;
7. confirmar GPIO do buzzer e periféricos para D8.

Este protocolo não declara validação de campo, compatibilidade elétrica ou
integração física concluída.
