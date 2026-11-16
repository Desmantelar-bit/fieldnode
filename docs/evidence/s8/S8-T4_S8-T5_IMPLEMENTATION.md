# S8-T4 / S8-T5 — implementação parcial

## Verificado no checkout

- `firmware/lib/outbox/outbox.h/.cpp`: registro fixo `Rec` de 235 bytes, CRC32,
  três filas LittleFS (`A`, `B`, `C`), recuperação que ignora registros
  inválidos/truncados e cursores cumulativos em NVS.
- `firmware/partitions.csv`: partição `littlefs` reservada.
- `firmware/lib/espnow_link`: quadro de 28 bytes e CRC-16/CCITT-FALSE.
- `firmware/node` e `firmware/gateway`: fronteiras de integração e contrato do
  canal compartilhado com o Wi-Fi do gateway.

## Não verificado

Não houve placa identificada, compilação ESP32, integração do outbox ao fluxo
DS18B20/MQTT, ACK de aplicação do servidor, callback físico de ESP-NOW, teste
de reenvio, teste de 50 quedas, medição de PER/alcance ou vídeo. Portanto não
há critério 50/50 nem retenção de 30 dias comprovados.

O desgaste também não recebe número inventado: o alvo `esp32dev` não informa o
part number da flash instalada. A conta em `docs/HARDWARE.md` fica pendente do
datasheet e da taxa de amostragem reais.
