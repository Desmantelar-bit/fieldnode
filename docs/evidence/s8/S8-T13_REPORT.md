# S8-T13 - EWMA/CUSUM, alarme local e prescricao curta

## Estado

**SOFTWARE DE BANCADA VERIFICADO; DEMONSTRACAO FISICA PENDENTE.**

`firmware/lib/spc` implementa baseline adaptativo, CUSUM bilateral e
congelamento do baseline durante alarme. O residuo e limitado para que um pico
isolado nao seja tratado automaticamente como deslocamento sustentado. Os
parametros continuam calibraveis e nao sao limites validados de maquina.

`firmware/lib/local_alarm` expoe o estado do alarme e um callback para LED,
buzzer ou OLED. `firmware/include/prescricao_curta.h` mantem a tabela fixa de
prescricao, incluindo `P03`.

O ciclo principal agora atualiza o SPC da temperatura e dispara `P03` pelo
callback local; a tentativa de Wi-Fi expira em 10 segundos para nao bloquear
essa parte local quando o gateway estiver indisponivel. O pino do buzzer ainda
precisa ser confirmado na placa efetivamente usada.

## Verificacao executada

O teste nativo cobre as quatro series pedidas:

1. degrau sustentado dispara CUSUM;
2. pico isolado nao dispara;
3. deriva lenta dentro da tolerancia nao dispara;
4. baseline permanece congelado depois do alarme.

Resultado: **11/11 testes nativos passaram**.

## Nao alegado

Ainda nao houve aquecimento fisico de sonda, video, OLED/buzzer conectado,
nem demonstracao com gateway desligado. Esses itens permanecem necessarios
para o aceite completo de OFFLINE-100.
