# Consolidação final do FieldNode

Data: 15/10/2026

## A. Resultado

- Backend: raiz do repositório, principalmente `api_tcc/`, `setup/` e
  `manage.py`.
- Frontend: `frontend-next/`.
- Branch de trabalho consolidada: `feature/merge-front-novo`.
- Branch final: `main`, atualizada por fast-forward após este commit.
- `frontfieldnode/`: removido da árvore principal. Era um gitlink aninhado, não
  uma segunda fonte canônica. A cópia foi preservada fora do workspace em
  `C:\Users\Usuario\fieldnode-archive-20261015\frontfieldnode`.

O resultado mantém uma única raiz Git e nenhuma dependência operacional do
checkout antigo do frontend.

## B. Decisões de consolidação

O backend da raiz foi preservado. O frontend integrado já existente em
`frontend-next/` foi mantido porque contém as correções mais recentes de
contrato, autenticação, estados da interface e segurança. A revisão histórica
aninhada não foi copiada por cima.

Foi criada a referência recuperável
`safety/pre-consolidation-20261015` antes da remoção estrutural. Nenhuma
migration, configuração local, banco ou segredo foi incluído na consolidação.

## C. Integração técnica

O contrato documentado usa `FIELDNODE_SERVER_API_URL` para o proxy server-side
do Next. A chave `FIELDNODE_API_KEY` permanece restrita ao backend e aos
clientes de ingestão; não foi reintroduzida no bundle do browser. As rotas
principais e o endpoint de prescrição por máquina permanecem no frontend e no
backend canônicos, conforme `CONTRATO_FRONT_BACK.md` e
`docs/CONTRATO_FRONT_BACK_FRONTEND.md`.

## D. Testes e verificações

| Verificação | Comando | Resultado | Observação |
|---|---|---|---|
| Django check | `venv\Scripts\python.exe manage.py check` | PASSOU | Nenhum problema reportado. |
| Django suite | `venv\Scripts\python.exe manage.py test api_tcc --verbosity=1` | PASSOU | 285 testes; banco de teste criado e destruído pelo runner. |
| Migrations | `venv\Scripts\python.exe manage.py makemigrations --check --dry-run` | PASSOU | Nenhuma migration pendente. |
| Lint frontend | `npm run lint` em `frontend-next` | PASSOU | ESLint concluiu sem saída de erro. |
| Build frontend | `NODE_OPTIONS=--use-system-ca npm run build` | PASSOU | Next compilou, tipou e gerou as 14 páginas. |
| Docker | `docker version; docker compose ps` | PASSOU | `db`, `mosquitto`, `web` saudáveis; `worker` ativo. |
| Pytest genérico | `venv\Scripts\python.exe -m pytest` | FALHOU | Antes da remoção, coletava o gitlink aninhado e falhava também por configuração Django ausente. |
| Fluxos HTTP completos | — | NÃO VERIFICADO | Ainda exige executar login, telemetria, prescrição, mapa e relatórios contra ambiente de teste. |

## E. Git

- Candidata de backup/integracão: `feature/merge-front-novo`.
- Estratégia: preservar a branch, remover o gitlink em commit separado e fazer
  fast-forward para `main`; não criar merge vazio.
- Referência de recuperação: `safety/pre-consolidation-20261015`.
- Commit da consolidação: este commit, identificado pelo histórico Git da
  branch `feature/merge-front-novo`.
- Commit final da `main`: o mesmo commit após o fast-forward, verificado no
  estado final do repositório.
- Remoto: não publicado nesta etapa.

## F. Pendências reais

- Validar os fluxos frontend-backend por HTTP com dados não produtivos.
- A outbox web continua sem autorização server-side para enviar a chave de
  ingestão, conforme já documentado; isso é uma limitação de contrato, não um
  motivo para expor segredo no browser.
