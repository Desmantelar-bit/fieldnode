# Auditoria de Correção S0-T1 / S0-T2

Data: 2026-11-04
Commit observado: `cd6360ff330dab9c52c6f0f4e1959fe1bf154aeb` (`main`)
Status: alterações locais pendentes; não commitadas.

Este registro resume verificações executadas nesta auditoria. Não é uma transcrição integral do console nem substitui os logs históricos existentes.

## Ambiente

- `python --version`: `Python 3.10.0` no PATH.
- `py -0p`: Python 3.12 está instalado (`Python312`), além de 3.10, 3.13 e 3.14.
- `py -3.12 -m pip show Django pytest`: inicialmente não encontrados. Foi criado venv temporário e instaladas as dependências declaradas; log: [install_py312_2026-11-04.txt](install_py312_2026-11-04.txt).
- `node --version`: `v24.16.0`; `where.exe node` encontrou `C:\Program Files\nodejs\node.exe`.
- `where.exe nvm`, `fnm`, `volta`: nenhum gerenciador localizado. Node 20 não está disponível nesta sessão.
- `Get-Command gitleaks`: não encontrado. Gitleaks oficial não foi executado.

## Docker

- `Get-Service com.docker.service`: `Stopped` (StartType `Manual`).
- `docker info --format '{{.ServerVersion}}'`: falhou ao conectar a `//./pipe/dockerDesktopLinuxEngine`; daemon indisponível.
- `docs/evidence/s0/compose_up.txt` preserva a tentativa histórica, com código de saída 1. Compose, migrations no container e healthcheck em Compose não foram concluídos; tempo de inicialização não medido.
- A resposta HTTP 200 em `health.json` declara `environment: local_sqlite`, portanto não serve como evidência do Compose.

## Repositório e higiene

- `git ls-files | Select-String -Pattern '^(\.next|\.kiro)/'`: sem saída.
- Busca atual de `api_tcc/api/page.tsx` e `frontend-next/src/types/`: somente `api.ts` e `telemetry.ts` permanecem rastreados nessa pasta.
- Busca de nomes de arquivos rastreados por `sqlite`, `bak`, `env`, `backup` ou `secret`: sem correspondências. Isto verifica nomes, não o conteúdo de segredos.
- `git check-ignore -v poetry.lock Pipfile.lock frontend-next/package-lock.json`: a antiga regra global ignorava `poetry.lock` e `Pipfile.lock`; `package-lock.json` não era ignorado. A regra global foi removida de `.gitignore`.
- O working tree contém remoções, alteração de `.gitignore` e documentação não commitadas. Nenhum commit foi criado nesta auditoria.

## Testes, frontend e migrations

- Os logs históricos `tests_django.txt` (298 testes, 105.072s) e `tests_pytest.txt` (301 testes, warnings registrados) não identificam a fase before/after; a comparação de regressão não pode ser comprovada.
- No Python 3.12, Django passou 298 testes em 89.558s, exit code 0: [tests_django_after_py312_2026-11-04.txt](tests_django_after_py312_2026-11-04.txt).
- No Python 3.12, pytest passou 301 testes, com 27.050 warnings, em 97.19s, exit code 0: [tests_pytest_after_py312_2026-11-04.txt](tests_pytest_after_py312_2026-11-04.txt). Os avisos incluem incompatibilidade de versões em modelos pickle e NumPy; não foram corrigidos neste escopo.
- Também houve execuções em Python 3.10: Django 298/298 em 74.912s; pytest 301 aprovados, 83 warnings, em 80.24s. Os logs estão em `tests_django_after_2026-11-04.txt` e `tests_pytest_after_2026-11-04.txt`.
- `front_build.txt` registra `npm ci` com código 0, lint com código 1 (`eslint` não reconhecido), `npx tsc --noEmit` com código 1 (download de `tsc@2.0.4`) e build com código 1 (`Cannot find module 'typescript'` ao carregar `next.config.ts`). Débito formal: https://github.com/Desmantelar-bit/fieldnode/issues/2.
- Python 3.12 retornou `No changes detected` em `makemigrations --check --dry-run`; `showmigrations api_tcc` confirmou 0026 pendente no SQLite. Evidências: [check](migrations_check_py312_2026-11-04.txt) e [estado SQLite](migrations_applied_sqlite_py312_2026-11-04.txt). Não houve `migrate`; MySQL do Compose não foi verificado.
- A regra global `*.lock` foi removida; Node 20 e Docker continuam indisponíveis. O pytest histórico registrava 44 warnings; as execuções atuais registraram 83 no Python 3.10 e 27.050 no Python 3.12, diferenças que permanecem não investigadas.

## Segurança

- Gitleaks oficial não estava instalado. Não houve varredura Gitleaks e não se declara ausência de segredos.
- A busca de nomes de arquivos acima não encontrou correspondências, mas é insuficiente para detectar segredos embutidos em conteúdo.

## Veredito

- **S0-T1: parcialmente atendida.** As suítes e o check de migrations passaram no Python 3.12; Node 20, Compose e identificação de um before original permanecem pendentes.
- **S0-T2: parcialmente atendida.** O estado de arquivos/índice foi conferido e a regra global de lock removida; Gitleaks, prova de ausência de regressão e commit permanecem pendentes.