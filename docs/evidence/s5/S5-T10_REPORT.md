# S5-T10 · Metadados e manutenção por máquina

Implementado:

- MachineSpec: modelo textual, ano validado, horas acumuladas, limites JSON experimentais e origem.
- MaintenanceRecord: histórico vinculado à máquina, registro_id para idempotência, peças estruturadas em JSON e observação.
- importar_manutencao: CSV UTF-8 separado por ;, relatório por linha, rejeições explícitas e --dry-run.
- contexto de máquina no detalhe de decisão, incluindo horas desde a última manutenção somente quando calculável.

    python manage.py importar_manutencao docs/evidence/s5/S5-T10_IMPORT_EXEMPLO.csv --dry-run

Limites em MachineSpec.limites_json são aplicados somente após serem limitados à faixa segura do contrato central severity.v1; valores ausentes usam o contrato central. Overrides temporários existentes continuam com precedência e também são limitados.

Não foram inventados intervalos de manutenção, diagnóstico, previsão ou vida útil. Observações e peças são dados potencialmente sensíveis e não entram em logs detalhados. A retenção ainda depende da política S10-T6; esta tarefa não exclui histórico.

Validação executada:

- manage.py check · VERIFICADO
- migration 0046 aplicada · VERIFICADO
- importação com linha inválida e reexecução idempotente · coberta por teste Django
- captura visual · NÃO GERADA neste ambiente; inspeção visual em navegador permanece pendente.
