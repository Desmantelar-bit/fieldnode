# GPS UART

O módulo consome NMEA de forma incremental com TinyGPSPlus. Latitude,
longitude e velocidade só são utilizáveis quando há fix, HDOP no limite e dados
recentes. Sem fix, o payload deve omitir os campos, nunca preencher velocidade
com zero nem reutilizar silenciosamente uma coordenada antiga.

Os pinos e o baud são configuração de bancada em `firmware/include/config.h`;
devem ser confirmados contra o módulo físico antes de alegar validação.
