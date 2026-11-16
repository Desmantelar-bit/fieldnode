# S7-T5 - Codec compacto e plano de rádio

## IMPLEMENTADO

- `connectivity/codec_compact.py` implementa o quadro versão 1 de 28 bytes,
  little-endian, com `device_idx`, flags de classe/regime/tempo/GPS,
  quantização explícita e CRC-16/CCITT-FALSE.
- `device_idx` não é derivado de `device_id`; o decoder exige identidade
  fornecida ou registro do gateway.
- `unsynced` usa timestamp zero com estado explícito. GPS ausente usa flag.
- CRC é integridade acidental, não autenticação.

## DOCUMENTADO

`docs/PLANO_TESTE_RADIO.md` separa protocolo de software e validação física.
Não há firmware ou biblioteca de rádio no checkout que permita confirmar
limites universais de ESP-NOW/LoRa.

## PENDENTE / VALIDATE_NOW

Faltam hardware, versões de biblioteca, parâmetros de rádio e medições de
RSSI, PER, distância, obstrução e antena. Portanto este relatório não afirma
alcance nem funcionamento físico.

## Evidência

Comando executado: `venv\\Scripts\\python.exe -m unittest simulators.test_s7_t5_codec`

Resultado observado: `Ran 3 tests - OK`. Os testes executaram
10.000 round-trips determinísticos, corrupção de cada um dos 26 bytes
cobertos e rejeição de quadro truncado/extra, além de GPS ausente e resolução
de `device_idx`.
