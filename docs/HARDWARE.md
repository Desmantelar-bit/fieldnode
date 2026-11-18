# Hardware e retenção local

## S8-T10/S8-T11: sensores físicos e rastreabilidade

A BOM técnica aprovada para a próxima bancada está em [`BOM.md`](BOM.md). Ela
substitui o uso indevido de DHT como temperatura de máquina e SW-420 como
medição de vibração: DS18B20 inox e termopar tipo K atendem temperaturas em
contextos diferentes; MPU6050/ADXL345 mede aceleração; Hall/óptico mede pulsos;
GPS UART fornece velocidade e posição somente com qualidade aceita.

O firmware possui módulos independentes em `firmware/lib/rpm` e
`firmware/lib/gps`. A configuração atual de bancada usa, sem comprovar a placa
física, GPIO 27 para RPM e UART1 em RX16/TX17 a 9600 baud. O debounce de 500 us
é configurável e deve ser confrontado com a maior rotação e pulsos por volta.

RPM ausente não é publicado como zero. GPS sem fix, com HDOP acima de 5 ou dado
mais velho que 3 s não fornece posição/velocidade utilizável. Aquisição, foto,
cotação, recebimento, primeiro fix, calibração e validação em máquina permanecem
**NÃO VERIFICADOS** sem hardware e registros físicos.

## S8-T4: outbox em flash

O firmware agora contém uma outbox append-only em três arquivos LittleFS,
com registros fixos de 235 bytes, CRC32, recuperação que ignora somente o
registro truncado/corrompido no fim e cursores de ACK cumulativo em NVS.
Registro sem ACK continua no arquivo; `File.flush()` é o limite de persistência
oferecido pela API Arduino-ESP32 usada neste checkout.

As classes são lógicas: A e B preservam espaço antes de C. A política de
compressão/agregação/descarte de C ainda depende do consumidor e da capacidade
medida, portanto não é correto chamar a partição de “buffer de 30 dias” sem
taxa de amostragem e ensaio de retenção.

## S8-T8: escopo de proteção do dispositivo

O hardware de bancada protege somente o fluxo que foi implementado e medido no
checkout. Credenciais individuais por dispositivo existem no contrato do
backend S2-T8, com hash no servidor, rotação e revogação. Isso não significa que
a credencial gravada no firmware esteja protegida contra extração física.

Sem Flash Encryption, uma chave armazenada na flash do ESP32 pode ser extraída
por quem obtiver acesso físico compatível. Uma chave extraída pode permitir
falsificação da identidade daquele dispositivo até a revogação. Não há, neste
checkout, evidência de Flash Encryption, Secure Boot, TLS no MQTT ou assinatura
de payloads do firmware.

### Estados

- **Bancada / implementado no software:** firmware PlatformIO para o alvo
  `esp32dev`, credencial configurada por `FIELDNODE_DEVICE_ID`, protocolos e
  módulos host-side cobertos pelos testes existentes.
- **Não comprovado fisicamente:** resistência à extração de flash, alcance
  ESP-NOW, retenção prolongada, operação em máquina agrícola e recuperação de
  placa após falha de firmware.
- **Roadmap:** Flash Encryption, Secure Boot, TLS, validação em placa dedicada,
  ensaio de campo e proteção física contra adulteração.

### Plano ARCHITECT_NOW, ativação DEFER

Flash Encryption e Secure Boot devem ser planejados agora, mas só ativados em
placa dedicada depois de fechar o hardware de demonstração. A ativação pode
programar eFuses e ser irreversível. Nenhuma eFuse foi alterada nesta tarefa.

Antes de qualquer provisionamento definitivo, exigir: chip e revisão
identificados; documentação oficial; firmware mínimo de recuperação; chaves de
assinatura com backup; procedimento de provisionamento; boot válido e rejeição
de firmware inválido; teste de atualização e recuperação; compatibilidade de
armazenamento; substituição de placa; registro das eFuses; e aprovação explícita.
Sem recuperação confiável, a ativação permanece bloqueada.

OTA está em **DEFER**. Ela depende de firmware versionado, autenticação,
assinatura, rollback, recuperação de falhas e validação em hardware dedicado.
Atualização manual por cabo não é OTA.

## Desgaste

O cálculo obrigatório é:

```text
escritas_diárias = leituras_por_dia × 235 bytes
dias_por_ciclo = bytes_apagados_por_ciclo / escritas_diárias
vida_estimada = ciclos_de_apagamento_do_datasheet × dias_por_ciclo
```

Este checkout usa o alvo genérico `esp32dev`, mas não identifica o part number
da flash instalada. O valor de ciclos do datasheet, tamanho de bloco/setor,
taxa real de amostragem e distribuição do LittleFS ainda não foram medidos.
Logo, a estimativa numérica e a promessa de 30 dias estão **PENDENTES** até a
placa usada ser identificada e o ensaio ser registrado.

## S8-T5: rádio

`firmware/lib/espnow_link` valida o quadro compacto de 28 bytes e CRC-16.
`firmware/node` e `firmware/gateway` reservam as fronteiras de integração. O
canal ESP-NOW deve ser o mesmo canal Wi-Fi do gateway; isso é uma restrição de
coexistência, não uma medição de alcance.

PER, distância, obstáculos, reenvio por classe, callback de falha e ACK de
aplicação permanecem **NÃO VERIFICADOS** sem duas placas e logs físicos.
