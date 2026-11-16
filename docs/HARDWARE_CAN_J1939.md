# Hardware CAN/J1939 - S8-T7

O alvo atual do PlatformIO é `esp32dev`, mas este checkout não identifica o
part number da placa nem registra transceiver CAN disponível. A decisão de
hardware está **PENDENTE**: o ESP32 pode usar TWAI nativo com transceiver
externo compatível, mas não deve ser ligado diretamente ao barramento CAN.
MCP2515 só deve ser escolhido se a placa/transceiver disponíveis exigirem
controlador externo.

O decodificador puro em `firmware/lib/j1939` e seus testes host-side estão
implementados. Leitura elétrica, velocidade do barramento, terminação, captura
serial e compatibilidade com máquina real continuam **VALIDATE_NOW**.
