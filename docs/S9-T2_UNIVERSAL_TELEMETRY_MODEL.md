# S9-T2 — Universal Telemetry Model v0.1

## O que foi entregue

O FieldNode agora separa o dado recebido do dado que pode ser consumido pelos
estágios canônicos:

```text
payload recebido
  -> RawTelemetry (preservado)
  -> FabricanteMapping (adaptador versionado)
  -> CanonicalTelemetry (se houver mapeamento ativo)
```

`RawTelemetry` guarda máquina, fabricante, nome bruto, valor, unidade,
protocolo simulado, momento de recebimento e o payload original. Um parâmetro
sem adaptador permanece persistido com `quality=unsupported_parameter` e não
gera um registro canônico.

`Machine.capabilities(manufacturer)` lista os parâmetros canônicos mapeados e
ativos para o fabricante informado. Se o fabricante não for informado, o
método tenta usar a marca do `Modelo` cadastrado.

## Adaptadores v0.1

A migration 0024 cadastra estes exemplos simulados:

| Fabricante do adaptador | Nome bruto | Nome canônico | Versão |
| --- | --- | --- | --- |
| `case_ih_v1` | `SPN_190` | `engine.rpm` | `v0.1` |
| `john_deere_v1` | `engine_speed` | `engine.rpm` | `v0.1` |

Também existem mapeamentos de compatibilidade para o payload legado do
simulador (`fieldnode_simulator_v1`).

## Limite metodológico

Esses identificadores são adaptadores e dados simulados. A entrega demonstra o
modelo de interoperabilidade e a convergência semântica, mas não comprova
leitura de CAN, J1939, ISOBUS ou qualquer protocolo físico de Case IH, John
Deere ou New Holland. Drivers, decodificação física e validação em hardware
real continuam fora deste bloco.

## Verificação

```text
python manage.py test api_tcc.tests.test_normalizacao api_tcc.tests.test_integration
```

Os testes verificam a convergência de dois nomes brutos para `engine.rpm` e a
retenção explícita de parâmetros ainda não suportados.
