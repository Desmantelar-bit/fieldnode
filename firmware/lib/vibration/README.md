# Vibração por acelerômetro

O módulo usa MPU6050 em I2C, faixa de ±2 g, taxa nominal de 100 Hz e janela de
128 amostras. A leitura é convertida de counts para g, a média da janela é
removida e são calculados RMS, pico absoluto e curtose de Pearson por eixo.

O sensor deve ser fixado rigidamente na superfície observada. X/Y/Z precisam ser
registrados porque orientação, folga e material de montagem alteram o sinal.
Protoboard e sensor solto servem para testar a lógica, não para representar a
vibração de uma colheitadeira.

A remoção da média elimina a componente DC da janela e também pode remover
conteúdo real de frequência muito baixa. Energia por faixa/FFT permanece fora
desta etapa.
