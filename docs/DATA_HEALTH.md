# Data Health e Trust Score

## O que e

`trust_score` e um score heuristico de confianca por leitura de telemetria.
Ele vai de `0.0` a `1.0` e e calculado no momento da ingestao, depois da
validacao binaria do payload.

A pergunta que ele responde e:

```text
quanto o FieldNode deve confiar nesta leitura aceita?
```

## O que nao e

O Trust Score nao e:

- diagnostico fisico do sensor;
- diagnostico da maquina;
- probabilidade estatistica;
- resultado de machine learning;
- motivo para rejeitar leitura neste bloco.

Uma leitura com score baixo continua podendo ser armazenada. O score indica
suspeita sobre a qualidade do dado, nao uma certeza de falha.

## Sinais usados

| Sinal | Condicao | Efeito |
| --- | --- | --- |
| Gap temporal | Intervalo acima de 5 minutos em relacao a leitura anterior da mesma `Machine`, com penalidade progressiva ate 2 horas | Reduz o score |
| Ordem temporal | `timestamp` da leitura atual menor que o da leitura anterior | Reduz o score |
| Repeticao | Mesmo sensor repetido por 3 ou mais leituras consecutivas, com impacto maior em 5 repeticoes | Reduz o score |
| Range fisico | Valor dentro do range aceito, mas nos 5% mais proximos do limite inferior ou superior | Reduz levemente o score |
| Continuidade | Todos os sensores comparaveis mudam ate 5% do range em relacao a leitura anterior | Aplica bonus pequeno |
| Salto abrupto | Algum sensor muda 35% ou mais do range em relacao a leitura anterior | Reduz o score |

## Pesos iniciais

| Constante | Valor |
| --- | --- |
| `EXPECTED_GAP_SECONDS` | `300` |
| `MAX_GAP_SECONDS` | `7200` |
| `GAP_PENALTY_MAX` | `0.25` |
| `OUT_OF_ORDER_PENALTY` | `0.30` |
| `STUCK_SENSOR_MIN_REPETITIONS` | `3` |
| `STUCK_SENSOR_STRONG_REPETITIONS` | `5` |
| `STUCK_SENSOR_PENALTY_PER_FIELD` | `0.12` |
| `STUCK_SENSOR_PENALTY_MAX` | `0.42` |
| `RANGE_PROXIMITY_RATIO` | `0.05` |
| `RANGE_PROXIMITY_PENALTY_PER_FIELD` | `0.04` |
| `RANGE_PROXIMITY_PENALTY_MAX` | `0.12` |
| `SMOOTH_CHANGE_RATIO` | `0.05` |
| `ABRUPT_CHANGE_RATIO` | `0.35` |
| `CONTINUITY_BONUS` | `0.04` |
| `ABRUPT_CHANGE_PENALTY` | `0.08` |

## Limites fisicos

Os ranges usados pelo Trust Score sao os mesmos usados por `validar_payload()`,
centralizados em `api_tcc/services/sensor_limits.py`:

| Sensor | Minimo | Maximo |
| --- | --- | --- |
| `temperatura` | `0.0` | `150.0` |
| `vibracao` | `0.0` | `10.0` |
| `rpm` | `0` | `5000` |

## Historico

`calcular_trust_score(leitura, historico_recente)` recebe historico ja filtrado
pela mesma `Machine`, ordenado do mais recente para o mais antigo.

A funcao pura nao executa query. A ingestao busca no maximo as ultimas 5
leituras da mesma `Machine` antes de chamar a heuristica.

## Limitacoes

Estes pesos sao uma heuristica inicial calibravel. Eles nao foram calibrados
estatisticamente e nao devem ser apresentados como probabilidade. Backfill de
leituras historicas nao faz parte deste bloco; por isso `trust_score = null`
indica leitura antiga ainda nao pontuada.
