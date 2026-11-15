# S4-T6 · Feedback de limiar com trilha

## Implementado

- `ThresholdOverride` por máquina e métrica, com justificativa, autor e expiração.
- Criação somente para Decision rejeitada com `motivo_rejeicao=FALSO_ALARME` e usuário com permissão de escrita na organização.
- Limiar efetivo consulta apenas override vigente e limita `critico` ao teto do contrato `severity.v1`.
- Eventos de temperatura passam pelo limiar efetivo; após expiração, voltam ao contrato.
- Criação do override gera `AuditLog` em transação.

## Verificação

- `manage.py check`: VERIFICADO.
- `manage.py test api_tcc.tests.test_decisions`: VERIFICADO.
- Testes específicos S4-T6/S4-T7: adicionados em `api_tcc/tests/test_s4_t6_t7.py`; execução completa ainda pendente nesta rodada.

## Limites

Os valores do contrato continuam sendo heurísticos de bancada. O override não transforma o sinal em predição de falha nem substitui validação operacional externa.
