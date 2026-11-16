# Plano de teste de rádio LoRa/ESP-NOW

## Escopo

Este é um protocolo de medição para hardware real. O codec compacto foi
validado em software, mas isso não comprova que LoRa ou ESP-NOW funcionem no
campo, nem permite anunciar alcance, RSSI ou PER.

## Quadro usado

O quadro versão 1 tem 28 bytes, little-endian: `u8 versão`, `u8
classe_flags`, `u16 device_idx`, `u32 sequence`, `u32 event_time_unix_s`,
`i16 temperatura x100`, `u16 vibracao x100`, `u16 rpm`, `i32 latitude x1e5`,
`i32 longitude x1e5` e `u16 CRC`. A ausência de GPS é indicada por flag, não
por coordenada sentinela. `device_idx` é resolvido pelo registro do gateway.

`CRC-16/CCITT-FALSE` usa polinômio `0x1021`, inicial `0xffff`, sem reflexão e
`xorout=0`, cobrindo os primeiros 26 bytes; o CRC é serializado little-endian.
Ele detecta corrupção acidental, mas não autentica a origem. O quadro não
comporta HMAC completo: o gateway deve validar dispositivo registrado,
sequência e replay, e o próximo salto deve usar o contrato autenticado
existente. Spoofing local continua risco pendente.

## Limites a confirmar antes do ensaio

| Item | Registro obrigatório | Estado |
| --- | --- | --- |
| ESP-NOW | modelo ESP32, ESP-IDF/Arduino core e biblioteca | PENDENTE |
| LoRa | rádio, biblioteca, frequência, SF, BW, CR e região | PENDENTE |
| Payload útil | limite da versão/configuração e cabeçalhos | PENDENTE |
| Antena | modelo, ganho, orientação e altura | PENDENTE |
| Ambiente | coordenadas, obstáculos, alimentação e clima | PENDENTE |

Não há firmware nem biblioteca de rádio deste checkout para sustentar um
limite físico específico. Os 28 bytes são o tamanho do quadro do software.

## Protocolo

Para cada cenário, enviar uma sequência conhecida de `N` quadros, registrar
`device_idx`, sequência, timestamp de início/fim, RSSI quando disponível,
mensagens recebidas, inválidas, duplicadas e pendentes. Encerrar a janela
somente após o timeout definido antes do teste. Calcular:

`PER = mensagens perdidas / mensagens transmitidas`

Mensagens pendentes só entram como perdidas depois do timeout e do encerramento
documentado. Duplicatas e quadros com CRC inválido ficam separados da perda.

## Matriz de ensaio

| Cenário | Distância medida | Obstrução | Orientação | Taxa | Repetições | Resultado |
| --- | ---: | --- | --- | --- | ---: | --- |
| Linha de visada | preencher | nenhuma | preencher | preencher | preencher | PENDENTE |
| Obstrução parcial | preencher | preencher | preencher | preencher | preencher | PENDENTE |
| Obstrução significativa | preencher | preencher | preencher | preencher | preencher | PENDENTE |
| Reinício e recuperação | preencher | preencher | preencher | preencher | preencher | PENDENTE |
| Quadro de 28 bytes | preencher | preencher | preencher | preencher | preencher | PENDENTE |
| Payload próximo do limite | preencher | preencher | preencher | preencher | preencher | PENDENTE |

Repetir com orientações de antena diferentes e, se puder ser medido com
segurança, com interferência/congestionamento. Registrar latência somente se
o relógio e o método forem definidos. Respeitar a regulamentação local; não
alterar potência ou frequência para favorecer um resultado.

## Critérios

Definir antes da execução os limiares de sucesso, falha e inconclusivo para
cada rádio e cenário. Não extrapolar ESP-NOW para LoRa, nem um único ensaio
para alcance máximo. Qualquer afirmação sobre alcance, estabilidade, RSSI,
PER ou funcionamento real é **VALIDATE_NOW** até haver registro físico.
