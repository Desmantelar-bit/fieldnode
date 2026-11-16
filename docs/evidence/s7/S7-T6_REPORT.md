# S7-T6 - Canal de emergência SIMULADO

## IMPLEMENTADO

`connectivity/providers/sat_sim.py` implementa o `ConnectivityProvider` real
com o nome `sat_sim`, custo configurável, relógio injetável, orçamento diário,
deduplicação por `(device_id, sequence_number)` e relatório observável.
`ConnectivityManager` só permite o provider na ordem da classe A. B e C não o
selecionam. Quando o orçamento bloqueia uma mensagem, não há ACK válido e a
outbox permanece pendente.

## Evidência

Comando executado: `venv\\Scripts\\python.exe -m unittest simulators.test_s7_t6_sat_sim`

Resultado observado: `Ran 3 tests - OK`. O teste de integração
simulou duas mensagens A com custo 1 e orçamento 1: uma foi confirmada e uma
permaneceu pendente por orçamento. Também foram verificadas deduplicação por
`(device_id, sequence_number)` e exclusão de B/C da política.

## Limite explícito

**SIMULADO: os resultados demonstram somente a política e o comportamento do
software de simulação. Não comprovam hardware, cobertura, disponibilidade,
latência, custo comercial ou transmissão real por satélite.**
