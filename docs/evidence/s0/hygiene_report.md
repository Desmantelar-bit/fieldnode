# RELATÓRIO PARCIAL DE HIGIENE E CONSOLIDAÇÃO DO REPOSITÓRIO (S0-T2)
## FieldNode — Eliminação Segura de Duplicações, Remoção de Artefatos e Auditoria de Segredos

> **Registro das alterações declaradas para S0-T2; tarefa ainda não encerrada.** A auditoria de correção confirmou parte do estado atual, mas não dispõe de evidência preservada para todas as afirmações históricas. Consulte [correction_2026-11-04.md](correction_2026-11-04.md).

---

## 1. Estado Inicial do Repositório

No início da Sprint 0 (commit `cd6360ff330dab9c52c6f0f4e1959fe1bf154aeb`):
- O repositório continha arquivos gerados por builds e ferramentas versionados no Git.
- Arquivos de protótipos antigos do frontend encontravam-se no diretório do backend Django.
- O diretório `frontend-next/src/types/` continha stubs de 0 bytes de componentes React e serviços.
- Existiam comandos de gerenciamento Django redundantes e com schemas legados descontinuados.
- O `.gitignore` permitia o versionamento acidental de ferramentas como Kombai e arquivos `.lock` de extensões.

---

## 2. Artefatos Removidos do Rastreamento Git

Os seguintes arquivos locais/gerados foram desindexados (`git rm -r --cached`):

| Caminho | Natureza do Arquivo | Status |
|---|---|---|
| `.next/trace` | Log de telemetria/trace gerado pelo compilador Next.js | DESINDEXADO |
| `.kiro/settings/.kirocrew-cli-settings.lock` | Lock file de runtime do assistente Kiro | DESINDEXADO |
| `.kiro/settings/cli.json` | Configuração local de ferramenta de agente | DESINDEXADO |

*Reverificação em 2026-11-04*: `git ls-files | Select-String -Pattern '^(\.next|\.kiro)/'` retornou vazio. O resultado e o limite da verificação estão em [correction_2026-11-04.md](correction_2026-11-04.md).

---

## 3. Arquivos Removidos do Repositório

Total líquido de arquivos deletados: **10 arquivos**.

1. `api_tcc/api/page.tsx`
2. `api_tcc/management/commands/criar_prescricoes_simples.py`
3. `api_tcc/management/commands/populate_db.py`
4. `frontend-next/src/types/FleetGrid.tsx`
5. `frontend-next/src/types/SkeletonGrid.tsx`
6. `frontend-next/src/types/page.tsx`
7. `frontend-next/src/types/telemetryService.ts`
8. `.kiro/settings/.kirocrew-cli-settings.lock` (desindexado)
9. `.kiro/settings/cli.json` (desindexado)
10. `.next/trace` (desindexado)

---

## 4. Duplicações Investigadas e Implementações Canônicas

### 4.1. Frontend: Componentes e Tipos (`src/types/`)

| Arquivo em `src/types/` | Tamanho | Implementação Canônica Escolhida | Justificativa |
|---|---|---|---|
| `FleetGrid.tsx` | 0 bytes | `frontend-next/src/components/FleetGrid.tsx` (92 linhas, 3.972 bytes) | O arquivo em `types/` era um stub vazio. A implementação real em `components/` é importada e consumida por `dashboard/page.tsx` e `maquinas/page.tsx`. Componentes visuais não pertencem a `types/`. |
| `SkeletonGrid.tsx` | 0 bytes | `frontend-next/src/components/SkeletonGrid.tsx` (28 linhas, 1.068 bytes) | O arquivo em `types/` era um stub vazio. A implementação canônica em `components/` é consumida por `dashboard/loading.tsx` e `dashboard/page.tsx`. |
| `page.tsx` | 0 bytes | Rotas do Next.js App Router (`src/app/**/page.tsx`) | Stub vazio sem nenhum consumidor no projeto. Nome ambíguo e fora da convenção. |
| `telemetryService.ts` | 0 bytes | `frontend-next/src/services/` | Stub vazio sem definições de tipos e sem consumidores. Serviços pertencem à camada `services/`. |

**Resultado**: O diretório `frontend-next/src/types/` contém **exclusivamente** os arquivos `.ts` de tipos canônicos:
- `frontend-next/src/types/api.ts`
- `frontend-next/src/types/telemetry.ts`

### 4.2. Backend: Arquivo Indevido `api_tcc/api/page.tsx`

- **Investigação**: Arquivo TypeScript/React de 1.939 bytes localizado no diretório backend `api_tcc/api/`. Implementava uma interface simplificada para download de relatórios CSV.
- **Implementação canônica**: `frontend-next/src/app/relatorios/page.tsx` (10.921 bytes), tela de relatórios completa e integrada à navegação e design system do frontend.
- **Consumidores de `api_tcc/api/page.tsx`**: ZERO (pesquisa regex global em todo o repositório confirmou ausência de referências).
- **Ação**: Removido integralmente.

---

## 5. Consolidação dos Comandos Django

Foram investigados os 3 grupos de comandos apontados pelo roadmap:

### Grupo 1: `criar_prescricoes_simples` vs `criar_prescricoes_teste`
- **Análise**:
  - `criar_prescricoes_simples.py` (38 linhas): Assumia que uma `Colheitadeira` já existia no banco e apenas criava duas prescrições mockadas (`p1` e `p2`). Zero referências no repositório.
  - `criar_prescricoes_teste.py` (62 linhas): Cria todas as dependências necessárias (`UnidadedeMedida`, `Marca`, `Modelo`, `Operario`, `Colheitadeira COLH-01`) e gera as prescrições de teste de forma determinística. Documentado em `scripts/README.md`.
- **Decisão**: **Situação A (Duplicação comprovada sem consumidores)**. `criar_prescricoes_simples.py` foi removido. `criar_prescricoes_teste.py` mantido como canônico.

### Grupo 2: `populate_db` vs `popular_tudo`
- **Análise**:
  - `populate_db.py` (130 linhas): Código legado das sprints 1-3. Utilizava atributos depreciados em PascalCase (`Nome`, `Porcentagem`, `TempodeServico`, `Nobanco`) e não instanciava os modelos `Organization` e `Machine` introduzidos no contrato multi-tenant da arquitetura atual. Zero referências no repositório.
  - `popular_tudo.py` (175 linhas): Implementação canônica atualizada que popula `Organization`, `Membership`, `Machine` com `is_demo=True`, coordenadas GPS reais em Goiás/DF e histórico de telemetria. Referenciado em `README.md`, `docker-compose.yml` e `scripts/seed_data.py`.
- **Decisão**: **Situação A (Duplicação obsoleta sem consumidores)**. `populate_db.py` foi removido. `popular_tudo.py` mantido como canônico.

### Grupo 3: `treinar_isolation_forest` vs `treinar_modelo_anomalia`
- **Análise**:
  - `treinar_isolation_forest.py` (32 linhas): Treina o modelo base não supervisionado de Isolation Forest com dados normais sintéticos de bancada gerados de forma reproduzível via NumPy (`seed 42`), persistindo em `MODELO_PATH` (`isolation_forest.joblib`). Documentado no `README.md`.
  - `treinar_modelo_anomalia.py` (39 linhas): Treina modelos supervisionados/específicos por máquina a partir de leituras reais do banco (`LeituraTelemetria`), persistindo no registro de modelos por máquina (`registry.get_model_path`). Consumido pela suíte de testes em `api_tcc/tests/test_anomaly_persistence.py`.
- **Decisão**: **Situação C (Implementações e finalidades distintas)**. Ambos foram **preservados** e sua diferenciação foi documentada.

---

## 6. Auditoria de Segredos e Dados Sensíveis

- **Gitleaks oficial**: não instalado no ambiente em 2026-11-04; nenhuma execução Gitleaks foi feita. Portanto, não há resultado que permita declarar “sem achados”.
- **Verificação substituta limitada**: a busca atual de nomes de arquivos rastreados por extensões `.sqlite`, `.sqlite3`, `.bak`, `.env` e termos `backup`/`secret` não retornou correspondências. Isso não examina o conteúdo dos arquivos e não substitui um scanner de segredos.
- As afirmações anteriores sobre busca de padrões de credenciais e ausência de segredos não têm saída bruta preservada e ficam **não verificadas** até uma varredura adequada.

---

## 7. Alterações no `.gitignore`

Foram adicionadas regras ao `.gitignore` para blindar o índice contra futuros acidentes:
```gitignore
# IDE e Tooling Caches
.vscode/
.idea/
.kilo/
.kiro/
.kombai/
.nanocoder/
```
- A regra global `*.lock` foi removida em 2026-11-04: `git check-ignore -v poetry.lock Pipfile.lock frontend-next/package-lock.json` confirmou que ela ignorava `poetry.lock` e `Pipfile.lock`. Os diretórios de ferramentas (`.kiro/`, `.kombai/` etc.) continuam ignorados por regras específicas.

---

## 8. Testes: Evidência Histórica e Limite da Comparação

| Evidência | Resultado | Limite |
|---|---|---|
| Evidência disponível | Resultado registrado | Limite |
|---|---|---|
| `tests_django.txt` | 298 testes aprovados, 0 falhas, 105.072s | Um arquivo; fase before/after não identificável |
| `tests_pytest.txt` | 301 testes aprovados; 44 warnings | Um arquivo; fase before/after não identificável |
| `tests_django_after_2026-11-04.txt` | 298 testes aprovados, 74.912s, exit code 0 | Execução pós-higiene no Python 3.10, fora da referência Python 3.12 |
| `tests_pytest_after_2026-11-04.txt` | 301 testes aprovados, 83 warnings, 80.24s, exit code 0 | Executado com `--ignore=docs/evidence/s0`; diferença de warnings ante histórico não investigada |
| `tests_django_after_py312_2026-11-04.txt` | 298 testes aprovados, 89.558s, exit code 0 | Execução pós-higiene no Python 3.12 |
| `tests_pytest_after_py312_2026-11-04.txt` | 301 testes aprovados, 27.050 warnings, 97.19s, exit code 0 | Execução no Python 3.12; warnings elevados permanecem sem triagem |
| `migrations_check.txt` | Nenhuma alteração de modelo pendente | Não comprova migrations aplicadas no SQLite ou MySQL |
| `front_build.txt` | lint, `npx tsc` e build falharam | Estado do comando documentado; issue #2 aberta |
| Artefatos rastreados | Consulta atual não encontrou `.next/` ou `.kiro/` | As remoções continuam não commitadas |
| `src/types/` | Quatro stubs ausentes do índice | Sem diff/grep histórico preservado para provar a comparação |
| Comandos de management | Dois arquivos constam como removidos | Relatório histórico documenta decisão; alteração não commitada |

**Conclusão**: as suítes passaram após a higiene no Python 3.12 e também foram executadas em Python 3.10. Os registros históricos não permitem provar a fase before; portanto, não declarar “zero regressões” comparativas. O pytest sem exclusão coletou um `.txt` de evidência como doctest e falhou por UnicodeDecodeError; com a pasta de evidência excluída, as suítes passaram.

---

## 9. Validação da Árvore Versionada

Estado de trabalho em 2026-11-04: as remoções e os documentos seguem como alterações pendentes, sem commit. `git diff --check` foi executado antes da atualização deste relatório; o resultado pós-atualização deve ser conferido no fechamento. Não há evidência suficiente para afirmar que todos os consumidores externos foram verificados ou que regressões estão ausentes.

---

## 10. Pendências e Próximas Ações

1. **Frontend**: tratar a falha registrada na [Issue #2](https://github.com/Desmantelar-bit/fieldnode/issues/2), fora do escopo de S0-T1/S0-T2.
2. **Migrations**: decidir/aplicar `0026_rename_tempumi_ambiente` ao SQLite local em etapa autorizada; MySQL permanece não verificado.
3. **Docker Engine**: validar em host com daemon disponível; neste ambiente, serviço parado e execução bloqueada.
4. **Gitleaks**: executar o binário oficial em ambiente disponível e preservar versão, comando, stdout/stderr e exit code.
5. **Testes**: obter registros separados de before/after apenas se evidência original existir; resultados históricos não podem ser reconstruídos.
