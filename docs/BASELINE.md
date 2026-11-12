# BASELINE TÉCNICO REPRODUZÍVEL — FIELDNODE
## Auditoria do Estado Atual e Evidências Verificáveis (S0-T1)

> **Registro histórico das execuções de S0-T1.**
> A auditoria de 2026-11-04 mantém S0-T1/S0-T2 parcialmente comprovadas.
> Consulte `docs/evidence/s0/correction_2026-11-04.md` para o estado atual.

## Status S0

- **Docker:** bloqueado em 2026-11-04 (`com.docker.service` parado); a tentativa de `docker compose up --build -d` não subiu os serviços.
- **Gitleaks:** ferramenta ausente no host; varredura formal não realizada.
- **Node:** ambiente real v24.16.0; referência do roadmap Node 20.
- **S0-T1/S0-T2:** parcialmente atendidas, com ressalvas documentadas neste baseline.

---

## 1. Identificação do Projeto

- **Nome**: FieldNode — Telemetria e Inteligência Operacional para Máquinas Agrícolas
- **Tipo**: AgTech / Industrial Intelligence (SaaS B2B)
- **Repositório**: `c:\Users\Usuario\fieldnode`

---

## 2. Data e Horário da Auditoria

- **Data/Hora**: 2026-11-04 17:02:40 -03:00 (Início) até 2026-11-04 17:25:00 -03:00 (Conclusão)
- **Fuso horário**: America/Sao_Paulo (UTC-03:00)
- **Evidência**: [commit.txt](evidence/s0/commit.txt) e [environment.txt](evidence/s0/environment.txt)

---

## 3. Commit e Branch Analisados

- **Commit**: `cd6360ff330dab9c52c6f0f4e1959fe1bf154aeb`
- **Branch**: `main`
- **Evidência**: [commit.txt](evidence/s0/commit.txt)

---

## 4. Ambiente Utilizado

- **Sistema Operacional**: Windows 10 Pro / Windows 11 (`Microsoft Windows 10.0.26100.0`)
- **Shell**: PowerShell (Windows)
- **Arquitetura**: x86_64 / amd64
- **Ambiente Virtual Python**: `venv/` (Python 3.10.0, Django 5.2, pytest 8.0.0)
- **Evidência**: [environment.txt](evidence/s0/environment.txt)

---

## 5. Versões das Ferramentas

| Ferramenta | Versão Registrada | Evidência |
|---|---|---|
| Python | 3.10.0 | [environment.txt](evidence/s0/environment.txt) |
| pip | 25.2 | [environment.txt](evidence/s0/environment.txt) |
| Node.js | v24.16.0 | [environment.txt](evidence/s0/environment.txt) |
| npm | 11.13.0 | [environment.txt](evidence/s0/environment.txt) |
| Docker CLI | 29.4.3 (build 055a478) | [environment.txt](evidence/s0/environment.txt) |
| Docker Compose | v5.1.3 | [environment.txt](evidence/s0/environment.txt) |
| Django | 5.2 | [tests_django.txt](evidence/s0/tests_django.txt) |
| pytest | 8.0.0 | [tests_pytest.txt](evidence/s0/tests_pytest.txt) |

---

## 6. Estado Inicial do Git

- **Status inicial**: `clean` (nenhuma alteração pendente antes do início da auditoria)
- **Arquivos rastreados com irregularidades identificadas na S0-T1**:
  - `.next/trace` (artefato de build rastreado no Git)
  - `.kiro/settings/.kirocrew-cli-settings.lock` e `.kiro/settings/cli.json` (arquivos de IDE rastreados)
  - `api_tcc/api/page.tsx` (componente React colocado indevidamente dentro do backend Django)
  - `frontend-next/src/types/FleetGrid.tsx` (0 bytes, stub vazio)
  - `frontend-next/src/types/SkeletonGrid.tsx` (0 bytes, stub vazio)
  - `frontend-next/src/types/page.tsx` (0 bytes, stub vazio)
  - `frontend-next/src/types/telemetryService.ts` (0 bytes, stub vazio)
- **Evidência**: [commit.txt](evidence/s0/commit.txt)

---

## 7. Resultado dos Testes Django

- **Comando**: `python manage.py test api_tcc simulators -v 2`
- **Classificação**: **PASSOU**
- **Testes encontrados / executados**: 298
- **Aprovados**: 298
- **Falhas**: 0
- **Erros**: 0
- **Ignorados / Skipped**: 0
- **Duração**: 105.072s
- **Banco utilizado**: SQLite in-memory (`file:memorydb_default?mode=memory&cache=shared`)
- **Código de saída**: 0
- **Evidência**: [tests_django.txt](evidence/s0/tests_django.txt)

---

## 8. Resultado dos Testes Pytest

- **Comando**: `pytest -q` (executado via `python -m pytest -q`)
- **Classificação**: **PASSOU**
- **Coletados**: 301
- **Aprovados**: 301 (100%)
- **Falhas**: 0
- **Ignorados / Skipped**: 0
- **Warnings**: 44 (avisos de descompatibilidade sklearn 1.8 vs 1.4.2 em unpickle de modelos e CacheKeyWarning de chave com espaços)
- **Código de saída**: 0
- **Evidência**: [tests_pytest.txt](evidence/s0/tests_pytest.txt)

---

## 9. Quantidade de Testes Encontrados versus Executados

### A verdade sobre a divergência: 292 vs 298 vs 301

| Métrica | Valor Comprovado | Explicação Técnica |
|---|---|---|
| Declarações `def test_` no código | **301** | Busca regex em `api_tcc/tests/*.py` (292) e `simulators/*.py` (9: 6 em `test_edge_client.py` + 3 em `test_transbordo_mule_client.py`). |
| Testes executados pelo Django test runner | **298** | O Django utiliza o `unittest.defaultTestLoader`. Ele apenas descobre classes derivadas de `unittest.TestCase`. O arquivo `simulators/test_transbordo_mule_client.py` possui 3 funções de teste que utilizam `@pytest.fixture` puro (sem classe `TestCase`), sendo ignorado pelo runner padrão do Django (301 - 3 = 298). |
| Testes coletados e executados pelo Pytest | **301** | O Pytest descobre tanto testes `unittest.TestCase` quanto funções puras com fixtures. Executa os 298 testes do Django + os 3 testes do simulador transbordo (total: 301). |
| Menção original a "292 testes" | **292** | Corresponde exatamente à contagem de testes contidos apenas no diretório `api_tcc/tests/`, desconsiderando o módulo `simulators/` (292 + 6 + 3 = 301). |
| Classes de teste | **71** | Classes que herdam de `TestCase` em `api_tcc/tests/` e `simulators/`. |
| Arquivos de teste | **28** | 26 em `api_tcc/tests/` (excluindo `__init__.py`) + 2 em `simulators/`. |
| Testes parametrizados | **0** | Nenhuma utilização de `@pytest.mark.parametrize` ou `@parameterized`. |

- **Evidência**: [tests_django.txt](evidence/s0/tests_django.txt) e [tests_pytest.txt](evidence/s0/tests_pytest.txt)

---

## 10. Auditoria de Migrations

- **Comando**: `python manage.py makemigrations --check --dry-run`
- **Classificação**: **PASSOU** (Nenhuma alteração de modelo pendente de migration)
- **Total de arquivos de migration**: 27 (26 migrations de schema de `0001_initial.py` até `0026_rename_tempumi_ambiente.py` + `__init__.py`)
- **Migrations aplicadas no SQLite local (`db.sqlite3`)**: 25 (0001 até 0025 aplicadas; `0026_rename_tempumi_ambiente` pendente de aplicação no banco local)
- **Evidência**: [migrations_check.txt](evidence/s0/migrations_check.txt)

---

## 11. Arquivos Python Acima de 300 Linhas

Critério de exclusão: `.venv/`, `venv/`, `*/migrations/*`, `__pycache__`, `.pytest_cache/`.
Total de arquivos Python analisados: **100 arquivos** (13.948 linhas no total).

### 13 Arquivos com mais de 300 linhas identificados:

| Rank | Caminho | Linhas | Classificação de Risco |
|---|---|---|---|
| 1 | `api_tcc/api/views_ingestao.py` | **749** | Crítico (God View — lógica de ingestão, validação e deduplicação misturada) |
| 2 | `api_tcc/models.py` | **731** | Alto (Monólito de modelos sem divisão por domínio) |
| 3 | `scripts/seed_data.py` | **676** | Moderado (Script de seed com dados sintéticos volumosos) |
| 4 | `api_tcc/tests/test_correlation.py` | **465** | Baixo (Suíte extensiva de testes de correlation ID) |
| 5 | `api_tcc/services/telemetria.py` | **440** | Alto (Lógica central de telemetria) |
| 6 | `api_tcc/api/serializers.py` | **406** | Moderado (Serializers agrupados em um único arquivo) |
| 7 | `api_tcc/tests/test_json_logging.py` | **385** | Baixo (Suíte de testes de logging estruturado) |
| 8 | `api_tcc/tests/test_integration.py` | **377** | Baixo (Testes de integração end-to-end) |
| 9 | `simulators/teste_resiliencia.py` | **373** | Baixo (Script de teste de estresse de simulador) |
| 10 | `api_tcc/tests/test_identity_contract.py` | **366** | Baixo (Testes do contrato de identidade) |
| 11 | `simulators/edge_client.py` | **361** | Moderado (Cliente edge com buffer SQLite local e sync) |
| 12 | `api_tcc/tests/test_data_health.py` | **340** | Baixo (Testes de integridade de telemetria) |
| 13 | `api_tcc/tests/test_decisions.py` | **309** | Baixo (Testes do motor de decisões agentivas) |

- **Evidência**: [linhas_py.txt](evidence/s0/linhas_py.txt)

---

## 12. Resultado do Lint (Frontend)

- **Comando**: `npm run lint` em `frontend-next/`
- **Classificação**: **FALHOU** (Código de saída: 1)
- **Diagnóstico**: `eslint` não foi localizado no PATH após `npm ci`. O script invocou `eslint src`, mas o binário local em `node_modules/.bin` não pôde ser executado diretamente pelo shell Windows sem prefixo `npx` ou porque devDependencies não foram provisionadas corretamente pelo `npm ci` no ambiente Windows.
- **Evidência**: [front_build.txt](evidence/s0/front_build.txt)

---

## 13. Resultado do TypeScript (Frontend)

- **Comando**: `npx tsc --noEmit` em `frontend-next/`
- **Classificação**: **FALHOU** (Código de saída: 1)
- **Diagnóstico**: `tsc` não foi encontrado localmente e `npx` tentou baixar o pacote legado descontinuado `tsc@2.0.4`. O comando correto do projeto no `package.json` é `npm run type-check` (que invoca `tsc --noEmit` via script npm).
- **Evidência**: [front_build.txt](evidence/s0/front_build.txt)

---

## 14. Resultado do Build (Frontend)

- **Comando**: `npm run build` (`next build`) em `frontend-next/`
- **Classificação**: **FALHOU** (Código de saída: 1)
- **Diagnóstico**: O Next.js 15 utiliza `next.config.ts`, que exige que o TypeScript esteja acessível em runtime para transpilar o arquivo de configuração. O Next disparou uma instalação automática em runtime (`Installing devDependencies (npm): - typescript@5.8.2`), mas falhou com `Error: Cannot find module 'typescript' Require stack: .../transpile-config.js`.
- **Evidência**: [front_build.txt](evidence/s0/front_build.txt)
- **Débito formal**: [Issue #2](https://github.com/Desmantelar-bit/fieldnode/issues/2). Não corrigir dependências durante S0-T1/S0-T2.

---

## 15. Resultado do Docker Compose

- **Comando**: `docker compose up --build -d`
- **Classificação**: **NÃO EXECUTADO (LIMITAÇÃO DO AMBIENTE)**
- **Diagnóstico**: O serviço Windows `Docker Desktop Service` (`com.docker.service`) encontrava-se no estado `Stopped`. A tentativa de inicialização programática do serviço falhou por exigir elevação administrativa do Windows (`System.ServiceProcess.ServiceCommandException`). Embora os binários `docker` e `docker compose` estejam instalados e funcionais, a comunicação com o socket/pipe de runtime (`//./pipe/dockerDesktopLinuxEngine`) foi impedida pela ausência do daemon ativo.
- **Evidência**: [compose_up.txt](evidence/s0/compose_up.txt) e [compose_services.txt](evidence/s0/compose_services.txt)
- **Bloqueio ambiental (2026-11-04)**: `com.docker.service` estava parado; o daemon não respondeu. O experimento de `docker compose up --build -d` não foi executado com sucesso, não há tempo de setup e migrations/healthcheck do Compose permanecem pendentes.

---

## 16. Resultado do Migrate

- **Ambiente SQLite Local**: 25 migrations aplicadas, 1 pendente (`0026_rename_tempumi_ambiente`). Nenhuma quebra de integridade.
- **Ambiente Docker Compose / MySQL**: **NÃO EXECUTADO** devido à indisponibilidade do daemon Docker no host.
- **Evidência**: [migrations_check.txt](evidence/s0/migrations_check.txt)

---

## 17. Resultado do Healthcheck da API

- **Endpoint**: `http://localhost:8000/api/health/`
- **Classificação**: **PASSOU**
- **Status HTTP**: `200 OK`
- **Duração da resposta**: `2941.5 ms`
- **Payload retornado**:
  ```json
  {
    "status": "ok",
    "database": "ok",
    "mqtt_last_seen_seconds": 2009968,
    "version": "1.0"
  }
  ```
- **Correlation ID injetado**: `ddebf302-bd85-4ef9-a558-951be222c7ec`
- **Evidência**: [health.json](evidence/s0/health.json)
- **Limite**: esta resposta foi obtida em `local_sqlite`; não comprova o healthcheck dentro do Docker Compose.

---

## 18. Comparação SQLite versus MySQL

| Critério | SQLite Local (Ambiente de Testes) | MySQL 8 (Ambiente Docker Compose) |
|---|---|---|
| Motor de Banco | SQLite 3 (`db.sqlite3` / in-memory `:memory:`) | MySQL 8.0-debian (InnoDB) |
| Concorrência | Bloqueio em nível de banco/tabela no SQLite; concorrência real simulada | Row-level locking no InnoDB com transações ACID completas |
| Migrations | 25 aplicadas no `db.sqlite3`, 1 pendente (`0026`) | Planejado para aplicar todas as 26 migrations via entrypoint |
| Tipagem e Constraints | Tipagem dinâmica, validação parcial de constraints | Enforce estrito de foreign keys, charset utf8mb4 |
| Suíte de Testes | 298 testes passando no Django; 301 no Pytest | Não medido diretamente no container (Compose bloqueado) |

---

## 19. Cobertura de Testes

- **Classificação**: **NÃO MEDIDO**
- **Justificativa**: A suíte de testes original não inclui geração de relatório de cobertura configurada por padrão no `pytest.ini` (`pytest-cov` não invocado na S0-T1 para manter a estrita fidelidade aos comandos padronizados). Será aferida em tarefas posteriores com `coverage run` / `pytest --cov`.

## 20. Auditoria de Correção (2026-11-04)

- **S0-T1: parcial.** Logs históricos não identificam fase before/after.
   O resultado pós-higiene está nos logs listados abaixo.
- **Python 3.12 pós-higiene:** Django passou 298 testes em 89.558s.
   Pytest passou 301 em 97.19s, com 27.050 warnings. Ambos terminaram com
   exit code 0. Logs: [Django](evidence/s0/tests_django_after_py312_2026-11-04.txt)
   e [pytest](evidence/s0/tests_pytest_after_py312_2026-11-04.txt).
- **Python 3.10 adicional:** Django passou 298 testes em 74.912s.
   Pytest passou 301 em 80.24s, com 83 warnings. Logs: [Django](evidence/s0/tests_django_after_2026-11-04.txt)
   e [pytest](evidence/s0/tests_pytest_after_2026-11-04.txt).
- Os logs históricos não identificam com segurança a fase before/after.
- **Coleta pytest:** sem exclusões, pytest tentou ler o log Django como doctest
   e falhou por codificação UTF-16. A suíte passou excluindo `docs/evidence/s0`.
- **Ambiente:** dependências foram instaladas em venv temporário Python 3.12.
   Node 20 não está disponível. O baseline histórico usou Python 3.10 e Node 24.
- **Docker:** `com.docker.service` parado. O HTTP 200 da seção 17 é local,
   com SQLite; não comprova o Compose.
- **Frontend:** lint, TypeScript e build falharam. Débito: [Issue #2](https://github.com/Desmantelar-bit/fieldnode/issues/2).
- **Migrations:** Python 3.12 retornou `No changes detected`; `showmigrations`
   confirmou 0026 pendente no SQLite. MySQL não verificado; nenhuma migration
   foi aplicada nesta auditoria. Evidências: [check](evidence/s0/migrations_check_py312_2026-11-04.txt)
   e [estado SQLite](evidence/s0/migrations_applied_sqlite_py312_2026-11-04.txt).
- **Segredos:** Gitleaks oficial não instalado; varredura não executada.
   A busca por nomes de arquivos não prova ausência de segredos no conteúdo.
- **Higiene:** `.next/`, `.kiro/`, `api_tcc/api/page.tsx` e os quatro stubs
   não aparecem no índice. As alterações seguem pendentes e não commitadas.
- Registro detalhado: [correction_2026-11-04.md](evidence/s0/correction_2026-11-04.md).

---

## 21. Problemas Encontrados (Fotografia Real)

1. **Build e Tooling do Frontend Quebrado**:
   - `npm run lint` falha procurando binário global do `eslint`.
   - `npm run build` falha por ausência do módulo `typescript` em runtime no Next 15 para carregar `next.config.ts`.
   - 13 vulnerabilidades relatadas pelo npm (1 crítica, 6 high).
2. **Artefatos Rastreados Indevidamente**:
   - `.next/trace` versionado no Git.
   - `.kiro/settings/.kirocrew-cli-settings.lock` e `.kiro/settings/cli.json` versionados.
   - `api_tcc/api/page.tsx` presente no diretório da API Django.
   - 4 stubs de 0 bytes em `frontend-next/src/types/` (`FleetGrid.tsx`, `SkeletonGrid.tsx`, `page.tsx`, `telemetryService.ts`).
3. **Inconsistência de Migrations no Banco Local**:
   - A migration `0026_rename_tempumi_ambiente` existe no repositório, mas não foi aplicada ao `db.sqlite3` local.
4. **Acoplamento e Complexidade de Arquivos (Tamanho Excessivo)**:
   - 13 arquivos com mais de 300 linhas, destacando-se `views_ingestao.py` (749 linhas) e `models.py` (731 linhas).
5. **Warnings de Versão do Scikit-Learn no Backend**:
   - Histórico: 44 warnings. Pós-higiene: 83 no Python 3.10 e 27.050 no Python 3.12. Diferenças e avisos de compatibilidade não foram investigados.
6. **Daemon Docker Indisponível**:
   - O serviço do Docker Desktop está parado e requer elevação administrativa do Windows para permitir subir a stack completa via Compose.

---

## 22. Limitações da Auditoria

1. Docker Compose e MySQL 8 não foram validados: `com.docker.service` estava parado e o daemon indisponível.
2. O frontend não produziu build: falhou ao carregar `next.config.ts` por `Cannot find module 'typescript'`; débito registrado na [Issue #2](https://github.com/Desmantelar-bit/fieldnode/issues/2).
3. Python 3.12 foi validado em venv temporário com as dependências do projeto. Node 20 não está disponível nesta sessão; o frontend não foi reexecutado no runtime de referência.
4. Gitleaks oficial não está instalado; a varredura de segredos permanece não executada.

---

## 23. Pendências para as Próximas Tarefas

- **S0-T1/S0-T2**: Fechamento pendente da evidência de referência, da execução do Compose, da varredura Gitleaks e da identificação do log before original. A higiene observável foi aplicada, mas está sem commit.
- **Frontend**: débito documentado na [Issue #2](https://github.com/Desmantelar-bit/fieldnode); correção permanece fora desta auditoria.
- **Migration 0026**: pendente no SQLite local; decidir/aplicar em etapa autorizada. MySQL não verificado.
- **Warnings pytest**: a execução histórica registrou 44 e a pós-higiene 83; diferença não investigada.

---

## 24. Índice dos Arquivos de Evidência

| Arquivo de Evidência | Finalidade | Status / limite |
|---|---|---|
| [commit.txt](evidence/s0/commit.txt) | Commit HEAD, branch e status inicial | Histórico do commit; não representa o status atual |
| [environment.txt](evidence/s0/environment.txt) | Versões históricas de SO, runtimes e ferramentas | Python 3.10/Node 24; fora da referência |
| [tests_django.txt](evidence/s0/tests_django.txt) | Saída histórica Django | Arquivo presente; fase before/after não identificada |
| [tests_pytest.txt](evidence/s0/tests_pytest.txt) | Saída histórica pytest | Arquivo presente; fase before/after não identificada |
| [tests_django_after_py312_2026-11-04.txt](evidence/s0/tests_django_after_py312_2026-11-04.txt) | Suíte Django pós-higiene | 298 testes, 89.558s, exit 0; Python 3.12 |
| [tests_pytest_after_py312_2026-11-04.txt](evidence/s0/tests_pytest_after_py312_2026-11-04.txt) | Suíte pytest pós-higiene | 301 passaram, 27.050 warnings, 97.19s, exit 0; Python 3.12 |
| [tests_django_after_2026-11-04.txt](evidence/s0/tests_django_after_2026-11-04.txt) | Execução adicional Django | 298 testes, 74.912s, exit 0; Python 3.10 |
| [tests_pytest_after_2026-11-04.txt](evidence/s0/tests_pytest_after_2026-11-04.txt) | Execução adicional pytest | 301 passaram, 83 warnings, 80.24s, exit 0; Python 3.10 |
| [install_py312_2026-11-04.txt](evidence/s0/install_py312_2026-11-04.txt) | Instalação de dependências em venv temporário | Sucesso; fora do repositório |
| [migrations_check_py312_2026-11-04.txt](evidence/s0/migrations_check_py312_2026-11-04.txt) | Check de migrations no Python 3.12 | `No changes detected`; exit 0 |
| [migrations_applied_sqlite_py312_2026-11-04.txt](evidence/s0/migrations_applied_sqlite_py312_2026-11-04.txt) | Estado aplicado no SQLite local | 0001-0025 aplicadas; 0026 pendente |
| [migrations_check.txt](evidence/s0/migrations_check.txt) | `makemigrations --check --dry-run` | Sem drift detectado; não comprova migrations aplicadas |
| [linhas_py.txt](evidence/s0/linhas_py.txt) | Contagem histórica de linhas Python | Arquivo presente; números não recontados nesta auditoria |
| [front_build.txt](evidence/s0/front_build.txt) | npm ci, lint, tsc e build | Comandos registrados; lint/tsc/build falharam |
| [compose_up.txt](evidence/s0/compose_up.txt) | Tentativa de subida do Compose | Falhou; daemon indisponível |
| [compose_services.txt](evidence/s0/compose_services.txt) | `docker compose ps` | Falhou; daemon indisponível |
| [health.json](evidence/s0/health.json) | Resposta de `/api/health/` | HTTP 200 em `local_sqlite`; não é healthcheck do Compose |
| [hygiene_report.md](evidence/s0/hygiene_report.md) | Decisões declaradas de S0-T2 e ressalvas | Parcial; alterações ainda não commitadas |
| [correction_2026-11-04.md](evidence/s0/correction_2026-11-04.md) | Auditoria das lacunas e resultados atuais | Resumo verificável; Gitleaks/Compose pendentes |
