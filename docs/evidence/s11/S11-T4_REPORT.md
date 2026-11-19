# S11-T4/T5 - SDK de adaptadores e conformidade

## Resultado

IMPLEMENTADO EM TESTE CONTROLADO. Não representa integração real com OEM,
AEMP ou máquina física.

## Arquitetura

- `api_tcc/adapters/base.py`: contrato `Adapter`, registry, `validar_param` e resolução controlada.
- `api_tcc/adapters/examples.py`: dois formatos autorais demonstrativos.
- `api_tcc/services/j1939.py`: fonte J1939 usada na convergência.
- `api_tcc/tests/test_adapters.py`: registry, conflito, desconhecido, validação e extensibilidade.
- `api_tcc/tests/test_umm_conformidade.py`: três caminhos até `CanonicalTelemetry`.

O teste de extensibilidade registra um adaptador novo em menos de 50 linhas e
não altera `normalizacao.py`.

## Formatos

`demo_metrics_v1` usa `metrics.{rpm,coolant_temp}`. `demo_readings_v1` usa uma
lista com nomes `engine_speed` e `coolant_temperature`. Ambos são autorais e
explicitamente não são APIs oficiais de fabricantes.

## Conformidade

| Parâmetro | J1939 | Demo A | Demo B | Unidade | Tolerância |
| --- | --- | --- | --- | --- | --- |
| `engine.rpm` | PGN 61444 / SPN 190 | `metrics.rpm` | `readings.engine_speed` | rpm | 0,001 |
| `engine.coolant_temp` | PGN 65262 / SPN 110 | `metrics.coolant_temp` | `readings.coolant_temperature` | C | 0,001 |

Os valores controlados foram 2000 rpm e 80 C. J1939 foi marcado como
`medido`; os formatos demonstrativos como `simulado`. A convergência é de
representação canônica, não de origem física.

## AEMP

`ARCHITECT_NOW`. A documentação pública consultada descreve ISO 15143-3/AEMP,
mas o acesso operacional depende de provedor, registro, credenciais e, em
alguns casos, assinatura. Não foi criado adaptador AEMP nem endpoint fictício.

## Verificação

Comando:

```text
.\venv\Scripts\python.exe manage.py test api_tcc.tests.test_adapters api_tcc.tests.test_umm_conformidade api_tcc.tests.test_j1939 api_tcc.tests.test_proveniencia api_tcc.tests.test_normalizacao --verbosity 1
```

Resultado observado em 19/11/2026: **23 testes passaram**.

Limitação: a revisão de fontes J1939 e a validação física permanecem fora do
escopo desta evidência. A suíte completa do repositório mantém pendências
ambientais e uma falha de matriz de rotas já registrada separadamente.
