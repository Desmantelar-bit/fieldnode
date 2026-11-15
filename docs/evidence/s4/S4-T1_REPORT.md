# S4-T1 · Relatório de consolidação

## Diagnóstico

Foram encontrados três caminhos: o serviço legado `services/prescricao.py`, o
pipeline `ia/pipeline.py` e as views de prescrição em conjunto com
`services/decisions.py`. O primeiro persistia `Prescricao`; os demais já tinham
contratos de `Decision`, com risco de divergência.

## Implementação

- `Decision` permanece como entidade ativa única.
- `0041_migrate_prescricao_to_decision` converte o histórico e remove o modelo.
- Rotas legadas delegam/consultam `Decision` e retornam `Deprecation: true`.
- Comandos de dados de teste foram ajustados para criar `Decision`.
- O serviço legado e o serializer do modelo antigo foram removidos.
- A arquitetura foi registrada em `docs/OPERATIONAL_DECISION_MEMORY.md`.

## Validação

VERIFICADO: `docker compose exec -T web python manage.py check`.

VERIFICADO: `python manage.py makemigrations --check --dry-run` sem mudanças.

VERIFICADO: dump lógico criado antes da auditoria final em
`docs/evidence/s4/fieldnode-s4-backup.sql` (1.520.680 bytes, 46 tabelas,
SHA-256 `2F21363E0128763A132BB468BF91413C8F99F9B50605DA65A69DA253EC8D76E3`).

VERIFICADO: migration `0041` aplicada no MySQL do Compose, sem apagar volume.

VERIFICADO: 6 registros legados foram convertidos para `Decision`; a inspeção
do schema retornou `legacy_tables=[]`, e os identificadores históricos ficaram
em `Decision.detalhes`.

VERIFICADO: 17 testes focados de Decision, compatibilidade e integração
passaram, incluindo o teste novo das rotas legadas.

VERIFICADO: `npm run type-check`, `npm run lint` e o build Next.js da imagem
frontend passaram.

REGISTRADO: a execução mais ampla de 38 testes também expôs três falhas de
contrato antigas de ingestão (`ok` versus `acked`, `duplicata ignorada` versus
`duplicate`, e autorização 403 versus 400). Elas não pertencem à consolidação
de prescrição e permanecem pendentes para a tarefa de contrato de ingestão.

## Pendências

É necessário atualizar os testes de contrato de ingestão e executar a suíte
completa após essa correção. A integração CI da S3-T11 permanece não verificada
porque não havia workflow específico no checkout.

Limitação de auditoria: o dump disponível foi criado após a aplicação da
`0041`; portanto, o critério estrito de backup capturado antes do `DROP TABLE`
não pode ser declarado verificado nesta execução. O dump atual é preservado
como ponto de restauração do estado consolidado.
