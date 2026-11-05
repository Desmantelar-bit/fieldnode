# Contrato v1 de severidade

A fonte de verdade é `contracts/severity.v1.json`, consumida pelo backend e pelos artefatos gerados. Os valores são heurísticos de bancada (`source: bancada-2026`), não limites operacionais validados em máquinas reais.

| Métrica | Unidade | Atenção | Crítico | Faixa |
|---|---|---:|---:|---:|
| Temperatura | C | 75 | 85 | 0–150 |
| Vibração | indice_0_10 | 5 | 8 | 0–10 |
| RPM | rpm | depende do regime | depende do regime | 0–5000 |

## D-01

As fronteiras usam `>=`: exatamente 75/85 e 5/8 já entram na respectiva classe. RPM não recebe classificação fixa nesta versão, pois depende do regime.

## Severidade e transmissão

Severidade é o estado factual da métrica. Classe de transmissão é a prioridade: `A` para `CRITICO`, `B` para `ATENCAO`, evidência diferente de `boa` ou dado atrasado, e `C` nos demais casos. Evidência fraca nunca rebaixa um crítico: crítico permanece A.

## Vibração e firmware

`vibracao` é um índice adimensional de 0 a 10. Não é aceleração em `g`; não há conversão automática. Medidas físicas futuras devem usar campos separados. O hardware real permanece no contrato v0 até migração versionada; o simulador v1 não prova migração do firmware.
