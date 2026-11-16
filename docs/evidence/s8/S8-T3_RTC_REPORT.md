# S8-T3 · RTC DS3231

## Estado

- **IMPLEMENTADO:** módulo I2C DS3231, leitura de OSF, política `rtc`/`gateway`/`unsynced`, preservação de `boot_id` e `uptime_ms` no payload existente.
- **TESTADO EM HOST:** política de seleção em `firmware/test/native/test_s8.cpp`.
- **TESTADO EM BANCADA:** pendente, incluindo desligamento de 10 minutos e remoção de bateria.
- **MEDIDO:** nenhuma deriva física medida.
- **PENDENTE:** integração de uma mensagem MQTT autenticada que chame `sync_from_gateway()`.

Configuração prevista: SDA GPIO 21, SCL GPIO 22, 100 kHz, endereço DS3231
`0x68`. O MPU6050 também inicia em `0x68`; AD0 precisa ser alterado para `0x69`
ou o barramento deve ser separado. Isso é requisito elétrico.

OSF ativo sempre resulta em `unsynced`. A flag só é limpa depois de gravar,
reler e confirmar um horário plausível vindo do gateway. Nenhum timestamp de
compilação ou horário do notebook é inventado pelo firmware.

Precisão e deriva de datasheet não foram tratadas como medição do módulo físico.
O ensaio real continua necessário.
