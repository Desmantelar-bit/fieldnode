# Registro de Backfill de Máquinas (S1-T1)

Backfill iniciado em 2026-09-04 13:35:54
----------------------------------------
Evidência real extraída do banco atual para mapeamento old -> new do S1-T1.

OLD: "AGCO-RT120-08" -> NEW: "AGCO-RT120-08" -> MACHINE_ID: "904298c1-dd69-4c42-8948-b0118d37ae06"
OLD: "CASE-TC5000-01" -> NEW: "CASE-TC5000-01" -> MACHINE_ID: "6455b069-dad8-416e-9af7-9e7f776ee54a"
OLD: "CLAAS-LEX-04" -> NEW: "CLAAS-LEX-04" -> MACHINE_ID: "91929536-ace3-4846-8966-6ac0b7356b19"
OLD: "COLH-01" -> NEW: "COLH-01" -> MACHINE_ID: "9a8d4355-c991-4fa1-af61-b880e4189567"
OLD: "FENDT-IDEAL-05" -> NEW: "FENDT-IDEAL-05" -> MACHINE_ID: "b678660c-262d-447f-8597-cf32960b1567"
OLD: "JOHN-S750-03" -> NEW: "JOHN-S750-03" -> MACHINE_ID: "def624dd-2e61-4b9b-b5b8-fde689147433"
OLD: "MASSEY-7700-06" -> NEW: "MASSEY-7700-06" -> MACHINE_ID: "04832fa4-ff8b-49fc-a799-694bb800b13a"
OLD: "NEW-CR890-02" -> NEW: "NEW-CR890-02" -> MACHINE_ID: "ff700fe3-95bc-4368-b298-c295e0e84079"
OLD: "VALTRA-T210-07" -> NEW: "VALTRA-T210-07" -> MACHINE_ID: "e02bd05e-4099-4628-8ab0-dcea4815bfcf"
----------------------------------------
Resumo do backfill:
Total de IDs lidos            : 97
IDs distintos de LeituraTelemetria: 9
Machines criadas na execução  : 9
Já existentes                 : 88
Ignorados (vazios)            : 0
----------------------------------------
Backfill concluído com sucesso.

Observação: os valores do banco atual mostram que as entradas históricas eram já compatíveis com a normalização .strip().upper(); os casos com espaços/maiúsculas misturadas aparecem no comportamento do command e nos testes, mas o banco atual contém os valores já normalizados e seus respectivos Machine.id reais.
