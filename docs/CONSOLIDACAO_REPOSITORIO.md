# Registro de consolidação do repositório

Data da execução: 15/10/2026.

## Decisão de fontes

- O backend canônico permanece na raiz, em `api_tcc/`, `setup/`, `manage.py`
  e nos scripts de operação.
- O frontend canônico é `frontend-next/`.
- `frontfieldnode/` era um gitlink para um repositório Git aninhado, com uma
  revisão anterior do backend e do frontend. A auditoria
  `AUDITORIA_FINAL_LEVIATA.md` já havia identificado que copiá-lo por cima
  causaria regressões de contrato e segurança.
- O conteúdo histórico foi movido para
  `C:\Users\Usuario\fieldnode-archive-20261015\frontfieldnode`, fora da árvore
  versionada. A referência Git do gitlink foi preservada pela branch
  `safety/pre-consolidation-20261015`.

## Branch de integração

`feature/merge-front-novo` foi a única candidata não incorporada à `main` local
e continha três commits posteriores à `main`: a documentação do contrato, a
expansão dos endpoints e as melhorias finais do frontend. Os branches remotos
de agentes apontavam para commits ancestrais ou linhas já representadas no
histórico principal. A integração final será um fast-forward dessa branch para
`main`, sem criar merge artificial.

## O que foi preservado

- Backend Django, migrations, modelos, autenticação, ingestão, pipeline de
  análise, endpoints, scripts e testes.
- Shell, identidade visual, páginas, componentes, gráficos, mapa, estados da
  interface, Service Worker, autenticação do frontend e documentação de
  contrato em `frontend-next/`.
- Histórico do repositório e uma referência local de recuperação antes da
  remoção do gitlink.

## O que foi removido

Somente o gitlink `frontfieldnode` foi removido da árvore principal. Não foram
apagadas migrations, banco, uploads, dependências ou código do frontend
canônico. A cópia física foi arquivada fora do workspace para permitir
recuperação durante a validação.

## Referências e contrato

As referências operacionais apontam para `frontend-next/`. A menção histórica à
cópia antiga foi ajustada no contrato frontend-backend e permanece registrada
apenas como contexto de auditoria, não como dependência de execução.

## Verificações pré-consolidação

- `python manage.py check`: PASSOU.
- `python manage.py test api_tcc`: PASSOU, 285 testes.
- `python manage.py makemigrations --check --dry-run`: PASSOU, nenhuma
  migration pendente.
- `npm run lint` em `frontend-next`: PASSOU.
- `NODE_OPTIONS=--use-system-ca npm run build` em `frontend-next`: PASSOU.
- `docker version` e `docker compose ps`: PASSOU; serviços ativos e healthchecks
  saudáveis.
- `python -m pytest`: FALHOU na coleta por incluir a cópia Git aninhada, além
  de não configurar `DJANGO_SETTINGS_MODULE` para o runner genérico. Esse
  resultado motivou a retirada do gitlink; a suíte oficial Django passou após
  a consolidação.
- A primeira tentativa de `npm run build` foi bloqueada pelo certificado das
  fontes Google; a repetição com `NODE_OPTIONS=--use-system-ca` passou.
