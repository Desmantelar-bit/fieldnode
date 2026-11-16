# S8-T8 - Segurança do dispositivo e escopo de hardware

## Resultado

**REVISÃO DOCUMENTAL CONCLUÍDA.** Flash Encryption, Secure Boot e OTA não foram
ativados. Nenhuma eFuse foi alterada. O escopo foi separado entre implementação,
bancada e roadmap.

## Arquivos revisados

- `docs/HARDWARE.md`
- `docs/REPOSICIONAMENTO_ESCOPO_HARDWARE.md`
- `docs/BOM.md`
- `docs/CLAIMS_VS_CODE.md`
- `docs/SEGURANCA.md`
- `docs/evidence/s2/S2-T8_REPORT.md`
- `firmware/platformio.ini`
- `firmware/include/secrets.example.h`
- `firmware/README.md`

## Matriz de controles

| Controle | Estado real | Decisão |
|---|---|---|
| Credencial individual | Implementada no backend S2-T8, com hash, rotação e revogação | Manter; não alegar proteção física |
| Chave em flash | Pode ser extraída com acesso físico adequado sem proteção de flash | Risco explícito |
| Flash Encryption | Não implementada nem validada | `ARCHITECT_NOW`, ativação `DEFER` em placa dedicada |
| Secure Boot | Não implementado nem validado | `ARCHITECT_NOW`, ativação `DEFER` em placa dedicada |
| OTA segura | Não implementada | `DEFER` |
| eFuses | Nenhuma operação executada | Bloqueadas nesta tarefa |

## BOM

`docs/BOM.md` registra que não há comprovantes de compra no checkout. Não foram
inventados fornecedor, data ou custo.

## Riscos residuais e pendências

- chave do firmware continua exposta a extração física;
- MQTT de bancada permanece sem TLS conforme `docs/SEGURANCA.md`;
- não há validação física de rádio, sensor, CAN/J1939 ou campo;
- ativação futura exige placa dedicada, recuperação e aprovação explícita;
- proteção da branch e execução real do GitHub Actions dependem do GitHub e
  permanecem pendentes até observar uma execução real.

## Critério de consistência

`docs/CLAIMS_VS_CODE.md` deve distinguir credencial individual no backend de
proteção contra extração, e marcar Secure Boot, Flash Encryption, OTA segura e
campo como roadmap, DEFER ou não verificados conforme a evidência.
