# S8-T12 - CAN real em modo somente escuta

## Estado

**IMPLEMENTACAO DE SOFTWARE VERIFICADA; ACEITE FISICO PENDENTE.**

Foi adicionado `firmware/lib/can_listen` com TWAI nativo e as duas taxas
necessarias ao procedimento: 250 kbit/s para o ensaio J1939 e 500 kbit/s para
o ensaio OBD-II. A configuracao e sempre `TWAI_MODE_LISTEN_ONLY`; nao ha
funcao de envio no modulo.

## Evidencia disponivel

- teste nativo `test_can_listener_is_listen_only`: passou;
- parser J1939 existente cobre rotacao, temperatura do liquido, pressao de
  oleo e DM1 em quadros estendidos;
- compilacao nativa/teste host-side: 11/11 testes passaram.

## Ainda nao realizado

- veiculo real autorizado;
- confirmacao da taxa no conector e da pinagem;
- gravacao continua de 30 minutos;
- conferencia manual de tres parametros contra painel ou scanner;
- log bruto anonimizado, foto e verificacao eletrica de zero transmissao.

Portanto, S8-T12 nao esta aceito como leitura de equipamento real. O codigo
prepara a bancada; a evidencia fisica continua sendo uma atividade autorizada.
