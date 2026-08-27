# Resultados do teste de carga

Data de execução: 27/08/2026

Endpoint medido: `POST /api/telemetria/`

## Execução inicial, inválida para medir ingestão

A primeira execução usou um cliente sem o cabeçalho obrigatório `X-API-Key`.
Por isso, ela não mediu a capacidade de inserir telemetria: o endpoint rejeitou
as requisições antes de chegar à persistência.

Saída bruta preservada:

```text
--- 1 máquinas, 20 leituras cada ---
total de requests: 20
taxa de sucesso (201/200): 0/20
latência p50: 0.107s
latência p95: 1.102s

--- 5 máquinas, 20 leituras cada ---
total de requests: 100
taxa de sucesso (201/200): 0/100
latência p50: 0.109s
latência p95: 0.146s

--- 10 máquinas, 20 leituras cada ---
total de requests: 200
taxa de sucesso (201/200): 0/200
latência p50: 0.115s
latência p95: 0.156s

--- 20 máquinas, 20 leituras cada ---
total de requests: 400
taxa de sucesso (201/200): 0/400
latência p50: 0.145s
latência p95: 0.232s
```

O script daquela execução não imprimia a distribuição de status. O diagnóstico
manual, com o mesmo payload, confirmou o contrato:

```text
sem X-API-Key: 401
resposta: {"status":"erro","detalhes":"API key inválida ou ausente"}

com X-API-Key: 201
resposta: {"status":"ok", ...}
```

Conclusão: o resultado inicial de 0/400 foi causado por um erro no cliente de
teste, não por rejeição do payload nem incapacidade de ingestão da API.

## Correção aplicada ao simulador

O payload já era compatível com o contrato atual: UUID, `maquina_id`,
temperatura, vibração, RPM e timestamp ISO 8601 estão dentro das regras de
validação. A única correção foi incluir `X-API-Key`, lida de
`FIELDNODE_API_KEY` via ambiente. O script também passou a imprimir a
distribuição de status HTTP.

O cabeçalho não é registrado no relatório nem no terminal.

Além disso, o docstring foi corrigido: UUIDs exclusivos exercitam a ingestão
concorrente, mas não testam deduplicação. Esse comportamento exige uma bateria
separada que reenvie o mesmo UUID em paralelo.

## Execução corrigida, carga com autenticação válida

Comando executado por cenário:

```powershell
.\.venv\Scripts\python.exe -c "from scripts.teste_carga import rodar_teste; rodar_teste(<maquinas>, 20)"
```

Saída bruta:

```text
--- 1 máquinas, 20 leituras cada ---
total de requests: 20
taxa de sucesso (201/200): 20/20
distribuição de status HTTP: {201: 20}
latência p50: 1.494s
latência p95: 1.746s

--- 5 máquinas, 20 leituras cada ---
total de requests: 100
taxa de sucesso (201/200): 100/100
distribuição de status HTTP: {201: 100}
latência p50: 1.798s
latência p95: 2.766s

--- 10 máquinas, 20 leituras cada ---
total de requests: 200
taxa de sucesso (201/200): 200/200
distribuição de status HTTP: {201: 200}
latência p50: 1.813s
latência p95: 2.070s

--- 20 máquinas, 20 leituras cada ---
total de requests: 400
taxa de sucesso (201/200): 400/400
distribuição de status HTTP: {201: 400}
latência p50: 2.044s
latência p95: 2.752s
```

## Conclusão

| Cenário | Requests | Sucessos | Status HTTP | p50 | p95 |
| --- | ---: | ---: | --- | ---: | ---: |
| 1 máquina | 20 | 20/20 | 201: 20 | 1.494s | 1.746s |
| 5 máquinas | 100 | 100/100 | 201: 100 | 1.798s | 2.766s |
| 10 máquinas | 200 | 200/200 | 201: 200 | 1.813s | 2.070s |
| 20 máquinas | 400 | 400/400 | 201: 400 | 2.044s | 2.752s |

- A taxa de sucesso de inserção foi 100% nos quatro cenários corrigidos.
- Não houve respostas 429, portanto o rate limiter não bloqueou nenhuma
  requisição nesta execução.
- **Limitação validada:** no cenário crítico de 20 máquinas, o p95 foi
  **2.752s**, acima do limite de 1 segundo. A API aceitou todas as inserções,
  mas a latência observada não atende a esse critério.
- Não há evidência de deduplicação nesta medição, por escolha deliberada de
  UUID único por leitura.
