# S2-T6 — Matriz de isolamento entre organizações

## Estado em 2026-11-13

Cobertura iniciada; **tarefa não concluída**. O inventário e as regressões abaixo não equivalem a prova de isolamento de cada operação.

## Implementado

Criado `api_tcc/tests/test_tenant_isolation.py` com classificação explícita de **63 nomes de rota e 119 combinações únicas rota/método** declaradas em `api_tcc/urls.py` (204 registros considerando padrões normais e variantes de formato DRF), incluindo operações dos routers e descoberta recursiva. A verificação falha se um nome, método ou quantidade de padrões mudar sem atualização explícita. Um teste sintético comprova que uma operação sem entrada é detectada. Testes com duas organizações verificam listagem de eventos e operários, detalhe de evento/decisão e escrita de decisão.

## Verificação executada

Comando: `.venv/Scripts/python.exe -m pytest api_tcc/tests/test_tenant_isolation.py -q`

Resultado mais recente: **8 passed** para `test_tenant_isolation.py`.

Vazamento de existência encontrado: `PATCH /decisions/<id>/` retornava 403 para recurso de outra organização, enquanto recurso inexistente retornava 404. A view agora responde 404 antes de checar o papel de escrita; um membro sem papel suficiente dentro da própria organização continua recebendo 403. O teste confirma que a decisão A permanece pendente após a tentativa de B.

Também foi encontrada leitura anônima de catálogos globais em `DEMO_MODE`, sem marca `is_demo`; ela foi bloqueada para os ViewSets genéricos. O endpoint de operários agora lista apenas operadores vinculados às máquinas autorizadas do usuário (staff mantém acesso administrativo). Há teste para impedir que `Operario` sem vínculo apareça ao usuário B.

O teste descobre operações GET/POST/PUT/PATCH/DELETE de cada callback e compara o par nome/método com a matriz. O teste ainda não foi executado com uma rota artificialmente adicionada; a falha por adição decorre da comparação explícita de conjuntos.

## Cobertura pendente

- Exercitar acesso cruzado em todas as operações, incluindo os 14 ViewSets de catálogo e rotas de telemetria, relatórios, exportação, mapa, DLQ, prescrições e status.
- Verificar efeitos de escrita, paginação, filtros, contagens e exportações.
- Executar cenários com `DEMO_MODE=True/False`, `is_demo=True/False` e usuário sem Membership.
- Validar comportamento de cada operação individualmente; a classificação atual identifica explicitamente o método e a categoria, mas os cenários de acesso não executam todas as entradas.
- A prova sintética confirma a detecção da operação sem classificação; ainda falta executar e guardar a saída do runner após inserir temporariamente rota real não classificada.

Exceções públicas classificadas em `ROTAS_PUBLICAS`: login/registro (credencial e cadastro), `api-root` (links), `api-health` (healthcheck) e leituras em `DEMO_MODE` listadas com justificativa no teste. Catálogos globais sem marca demo não são anônimos; operários têm filtro de organização. Leituras de demonstração dependem de `is_demo=True`; cenários completos desse filtro permanecem pendentes. Não foram encontrados vazamentos nos comportamentos cruzados exercitados, mas as rotas não testadas permanecem inconclusivas. S2-T6 não está concluída.
