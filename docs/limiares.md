# Limiares v1 de severidade

Os limiares de severidade são heurísticos de bancada (`bancada-2026`), não limites operacionais validados para máquinas reais. A fonte canônica é `contracts/severity.v1.json`; alterar esse JSON e regenerar os artefatos com `python scripts/gen_contracts.py`.

| Métrica | Unidade | Atenção | Crítico | Faixa de entrada |
|---|---|---:|---:|---:|
| Temperatura | °C | 75 | 85 | 0–150 |
| Vibração | índice adimensional `indice_0_10` | 5 | 8 | 0–10 |
| RPM | rpm | Dependente do regime | Dependente do regime | 0–5000 |

D-01: as fronteiras são inclusivas (`>=`); exatamente 75 °C ou índice 5 é `ATENCAO`, e exatamente 85 °C ou índice 8 é `CRITICO`. Valores fora da faixa são inválidos para classificação. RPM não tem limiar de severidade fixo porque depende do regime.

D-02: `vibracao` é o índice adimensional 0–10. A unidade `g` não é equivalente e payload que a declarar é rejeitado; não existe conversão automática tecnicamente validada. RMS, pico em `g` e curtose são medidas futuras distintas. A omissão de `vibracao_unit` em payload legado assume `indice_0_10` por compatibilidade, sem afirmar proveniência dos registros históricos.

Severidade não é prioridade de transmissão. `CRITICO` sempre recebe classe A, inclusive com evidência fraca ou atraso; `ATENCAO`, evidência diferente de `boa` ou atraso recebe B; demais casos recebem C.

Tendência de temperatura e outras regras determinísticas de janela são sinais separados destes limiares de severidade. Limites específicos por modelo poderão vir de `Machine/Modelo` (S5-T3, S11). O firmware continua usando contrato v0 até migração versionada; o contrato v1 não declara adoção pelo hardware.
