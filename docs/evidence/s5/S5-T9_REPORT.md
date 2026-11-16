# S5-T9 · Evidência técnica

Implementado: LabeledWindow, regra versionada decision-outcome-v1, materialização idempotente e comando exportar_dataset_rotulado.

O CSV de exemplo é sintético. Ele demonstra o cabeçalho e o formato, não a existência de 200 decisões reais. Rótulos inconclusivos não entram como positivo ou negativo.

Validação executada:

- manage.py check · VERIFICADO
- migration 0046 aplicada · VERIFICADO
- testes Django test_s5_t9_t10 · 4/4 aprovados

A suíte completa do worktree não foi verde: 434 testes, com 4 falhas e 2 erros preexistentes ou fora deste recorte. Entre eles estão a dependência pytest ausente para ml/eval, falhas de rotas/matriz, persistência/anomalia e locks concorrentes do SQLite. Esses resultados não foram atribuídos a S5-T9 sem evidência.

Pendências reais: coleta de desfechos reais, revisão humana das regras, distribuição mínima por classe e avaliação temporal antes de qualquer treinamento supervisionado.
