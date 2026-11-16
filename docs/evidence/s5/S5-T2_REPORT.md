# S5-T2 · Harness de avaliação

## Status

IMPLEMENTADO; execução reproduzível verificada com `python -m ml.eval.run`. A disponibilidade literal do comando `make` depende da instalação local do GNU Make; nesta máquina ele não está instalado, portanto `make eval` ficou NÃO VERIFICADO como comando de shell, embora o alvo esteja presente no `Makefile`.

## Evidência

- Oito cenários estão em `ml/eval/scenarios.py`.
- `ml/eval/fixtures/benchmark_v1.json` fixa cenários, versão e 20 sementes.
- O treino usa uma série normal independente e não consulta os rótulos de avaliação.
- `ml/eval/metrics.py` calcula matriz de confusão, precisão, recall, F1, falsos positivos por hora e tempo até detecção.
- `docs/AVALIACAO_ANOMALIA.md` é gerado pelo harness e identifica os resultados como sintéticos, não de campo.

## Resultado

O relatório preserva falsos positivos, métricas indefinidas e limitações. Não houve ajuste do modelo com base no resultado do benchmark.
