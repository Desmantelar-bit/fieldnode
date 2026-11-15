# S4-T7 · Agenda interna de manutenção

## Implementado

- `GET /api/workorders/` com intervalo `de`/`ate`, paginação e filtros de máquina, responsável, status e prioridade.
- `PATCH /api/workorders/<id>/` para reagendar ou concluir uma WorkOrder autorizada.
- Histórico da OS preserva prazo/status anterior e novo; auditoria registra a operação.
- Conflito potencial do responsável no mesmo dia é retornado como aviso, sem bloqueio.
- Rota `/agenda` com navegação semanal/mensal e estados de carregamento, vazio e erro.
- A agenda usa as WorkOrders existentes; não foi criado modelo paralelo de compromissos.

## Verificação

- `manage.py check`: VERIFICADO.
- `npm run lint`: VERIFICADO.
- `npm run type-check`: VERIFICADO.
- E2E real de reagendamento e inspeção visual desktop/mobile: NÃO VERIFICADO nesta rodada.

## Limites

O conflito é deliberadamente por mesmo dia porque o modelo atual possui apenas `prazo`, sem início/fim/duração. Não há integração com RH, escala ou agenda externa.
