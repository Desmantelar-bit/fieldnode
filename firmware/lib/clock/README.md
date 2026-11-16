# Relógio DS3231

O módulo usa o DS3231 em `0x68`, com SDA GPIO 21 e SCL GPIO 22, a 100 kHz.
Como o MPU6050 também usa `0x68` por padrão, o hardware precisa mudar AD0 do
MPU6050 para `0x69` ou colocar os dispositivos em barramentos distintos.

No boot, comunicação e status são verificados. OSF ativo, falha de I2C, data
implausível ou ausência de evidência persistida deixam a fonte em `unsynced`.
Uma sincronização por gateway grava, relê e só então limpa OSF. Precisão de
datasheet não é medição deste módulo.
