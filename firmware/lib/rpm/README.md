# RPM por pulso

`RpmCounter` contabiliza pulsos na ISR e calcula RPM fora dela, em janela fixa.
O debounce padrão de 500 us limita a frequência aceita a aproximadamente 2 kHz
antes de considerar pulsos por volta; confirme esse limite contra o eixo e o
sensor usados. A aritmética unsigned de `now_us - last_pulse_us_` trata rollover
de `micros()` dentro do intervalo representável.

Ausência de pulsos não é publicada como RPM zero: antes do primeiro snapshot ou
com janela incompleta a leitura é `valid=false`. RPM zero só é uma leitura válida
quando uma janela completa foi capturada sem pulsos.
