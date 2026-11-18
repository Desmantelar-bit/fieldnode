# BOM v2 e rastreabilidade de recebimento

Este documento separa necessidade técnica de compra comprovada. Nenhum preço,
fornecedor, data, pedido, recebimento ou teste é inferido do código. O aceite
integral só existe quando cada peça recebida e necessária ao escopo tem registro
individual de teste.

## Itens aprovados para cotação

| ID | Item/especificação | Uso | Qtd. | Fornecedor | Preço unit. | Data da cotação | Status | Responsável | Etiqueta/evidência |
|---|---|---|---:|---|---:|---|---|---|---|
| T01 | DS18B20 inox, encapsulamento confirmado, até 125 °C no uso previsto | Temperatura de fluido/superfície | 2 | não informado | não informado | não informado | não comprado | não atribuído | pendente |
| T02 | Termopar tipo K + MAX31855 ou MAX6675 | Superfície quente/rolamento | 2 kits | não informado | não informado | não informado | não comprado | não atribuído | pendente |
| V01 | MPU6050 ou ADXL345 | Vibração | 2 | não informado | não informado | não informado | não comprado | não atribuído | pendente |
| R01 | Sensor Hall ou óptico + ímã/elemento de referência | RPM por pulso | 2 | não informado | não informado | não informado | não comprado | não atribuído | pendente |
| G01 | Módulo GPS UART com antena | Fix, velocidade e posição | 1 | não informado | não informado | não informado | não comprado | não atribuído | pendente |
| C01 | DS3231 | Relógio de bancada | 1 | não informado | não informado | não informado | não comprado | não atribuído | pendente |
| I01 | INA219 | Corrente/tensão | 1 | não informado | não informado | não informado | não comprado | não atribuído | pendente |
| D01 | OLED I2C | Visualização local | 1 | não informado | não informado | não informado | não comprado | não atribuído | pendente |
| A01 | Buzzer + LED | Sinalização | 1 kit | não informado | não informado | não informado | não comprado | não atribuído | pendente |
| N01 | Transceptor CAN 3,3 V | Fronteira CAN | 1 | não informado | não informado | não informado | não comprado | não atribuído | pendente |
| L01 | Placa LoRa compatível | Comunicação | 3 | não informado | não informado | não informado | não comprado | não atribuído | pendente |

**Total cotado:** não calculável. **Recebido:** 0 registrado. **Testado:** 0
registrado. Percentual testado: `NÃO APLICÁVEL` até existir inventário físico; não é 100%.

## Registro individual de recebimento

Preencher uma linha por unidade, usando a etiqueta física (`T01-01`, `T01-02`, etc.).
A foto do kit e a planilha original devem ser anexadas em `docs/evidence/s8/`.

| Etiqueta | ID BOM | Modelo/lote | Recebida em | Teste isolado em | Resultado | Evidência | Observação |
|---|---|---|---|---|---|---|---|
| nenhuma unidade registrada | - | - | - | - | pendente | - | inventário físico não fornecido |

## Teste de recebimento

Antes da integração, ligar cada peça isoladamente e registrar alimentação,
interface, leitura válida e comportamento de falha. DS18B20 com `-127` ou `85`
fixo reprova o recebimento até investigação. Para RPM, registrar pulsos por
volta e referência do gerador. Para GPS, registrar primeiro fix, HDOP,
satélites e condição de céu aberto. Este teste não é calibração metrológica nem
validação em máquina.

## Estado de aceite

`PENDENTE`: não há acesso, nesta revisão, a notas, pedidos, peças recebidas,
etiquetas, planilha de recebimento ou foto do kit. O software e os procedimentos
podem avançar, mas a trilha física B continua bloqueada para aceite integral.
