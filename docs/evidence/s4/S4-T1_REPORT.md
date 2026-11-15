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

VERIFICADO: migration `0041` aplicada no MySQL do Compose, sem apagar volume.

EXECUTADO COM FALHAS DE CONTRATO FORA DO ESCOPO: 38 testes focados de Decision
e integração; três falharam nos contratos antigos de ingestão (`ok` versus
`acked`, `duplicata ignorada` versus `duplicate`, e autorização 403 versus 400).

## Pendências

É necessário atualizar os testes de contrato de ingestão e executar a suíte
completa após essa correção. A validação visual Playwright da S3-T11 depende de
instalar as dependências npm no host; a instalação ficou bloqueada no registry
durante esta execução.
