# S8-T2 · Features de vibração

## Estado

- **IMPLEMENTADO:** cálculo host de RMS, pico e curtose de Pearson; aquisição MPU6050 em janela de 128 amostras; payload opcional por eixo.
- **TESTADO EM HOST:** senoide e ruído gaussiano com seed fixa, em `firmware/test/native/test_s8.cpp`.
- **TESTADO EM BANCADA:** pendente, pois não há evidência de acelerômetro físico conectado nesta execução.
- **VALIDADO EM MÁQUINA:** pendente.
- **ROADMAP:** energia por faixa/FFT e calibração contra vibração de máquina real.

O MPU6050 foi escolhido por ser compatível com I2C nativo e não exigir nova
biblioteca PlatformIO nesta etapa. Configuração: ±2 g, 100 Hz nominal, DLPF
~44 Hz e janela de 128 amostras. A taxa física efetiva ainda precisa ser medida.

A média de cada janela é removida antes das estatísticas. A curtose é Pearson,
sem subtrair 3: senoide ideal tende a 1,5 e normal ideal a 3. Montagem,
orientação X/Y/Z e fixação influenciam diretamente o resultado.

`vibracao` continua sendo o índice legado 0–10. As features novas são campos
opcionais `vibracao_rms_g`, `vibracao_pico_g` e `vibracao_curtose`, cada um com
`x`, `y` e `z`, acompanhados de `vibracao_unit="g"`. Payloads antigos continuam
válidos; ausência das features não significa vibração zero.
