# Consolidação final do FieldNode

Data: 15/10/2026

## Resultado verificado

- Repositório final: raiz `C:\Users\Usuario\fieldnode`, branch `main`.
- Backend preservado em `api_tcc/`, `setup/` e `manage.py`.
- Frontend oficial consolidado em `frontend-next/`, a partir do clone Git
  independente `Front Full Node`.
- O clone ainda está presente localmente durante esta auditoria para permitir
  revisão final e preservação do histórico; sua remoção ocorre somente após o
  bundle de segurança e o commit desta consolidação.

## Auditoria dos dois projetos

O clone tinha histórico próprio, remoto `https://github.com/acfurlaneto/frontfieldnode`
e HEAD `bce3d91`. A branch `main` estava limpa. A raiz tinha HEAD `3692aab`,
com a consolidação anterior já commitada, mas o clone foi disponibilizado como
diretório não rastreado e não podia ser tratado como já incorporado.

Foram comparados os arquivos rastreados de frontend e backend. O frontend do
clone foi adotado como fonte visual e funcional prioritária. O backend do clone
era uma revisão anterior e não continha as migrations, eventos, decisões,
DLQ, normalização e serviços presentes na raiz; por isso o backend da raiz foi
preservado. A alteração útil recuperada do clone foi o fluxo de cadastro,
junto às telas e serviços de autenticação correspondentes.

## Cadastro e autenticação

- `POST /api/auth/register/`: público, valida senha com os validadores Django,
  usa `create_user`, cria token DRF e nunca aceita campos administrativos.
- `POST /api/auth/login/`: contrato anterior preservado, incluindo renovação de
  token expirado.
- `POST /api/auth/logout/`: exige token e revoga a sessão no backend.
- `GET /api/auth/me/`: exige token e retorna somente o perfil básico.
- Usuários criados no cadastro são verificados como não `staff` e não
  `superuser` no teste automatizado.

## Testes executados

| Verificação | Resultado | Evidência |
|---|---|---|
| `manage.py check` | PASSOU | nenhum problema reportado |
| `manage.py makemigrations --check --dry-run` | PASSOU | `No changes detected` |
| `manage.py test api_tcc.tests.test_auth` | PASSOU | 7 testes |
| `manage.py test api_tcc` | PASSOU | 287 testes, 121,419 s |
| `npm run lint` | PASSOU | ESLint sem erro |
| `npm run build` | BLOQUEADO | compilou, tipou e gerou 12 páginas, mas travou em `Collecting build traces` com `.next/trace` em uso por outro processo |
| `git diff --check` | PASSOU | sem erro de whitespace |

Os testes Django emitiram avisos já conhecidos de versão do scikit-learn,
fallback do Gemini e locks do SQLite em testes concorrentes; ainda assim a
suíte terminou com 287/287 aprovados. Isso não prova validação física,
comercial, hardware ou execução live do Gemini.

## Git e preservação

- Branch ativa: `main`.
- Branch de backup existente: `safety/pre-consolidation-20261015`.
- Branch `feature/merge-front-novo` aponta para o mesmo histórico recente da
  consolidação anterior; não foi criado merge artificial.
- O histórico do clone independente foi preservado em bundle fora da árvore
  antes da remoção do diretório.
- Não houve force push nem reescrita do remoto.

## Pendências reais

- O build precisa ser repetido sem o processo que mantém `.next/trace` aberto.
- Fluxos completos no navegador e validação HTTP integrada ainda não foram
  executados nesta rodada.
- A integração do clone prova consolidação de código e contratos, não prova
  sensor físico, ESP32, ESP-NOW, campo, autonomia, retenção física ou compra.
- Segredos históricos continuam exigindo rotação ou revogação pelos donos dos
  serviços; apagar um arquivo atual não reescreve o passado.
