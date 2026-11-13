# S3-T1 — relatório de implementação e evidências

**Status: parcial.** A remoção do fallback e a proveniência controlada pelo backend foram implementadas. Faltam capturas visuais da aplicação em execução e validação de todos os estados pela interface real; por isso, a definição de conclusão da tarefa não está atendida.

## Diagnóstico inicial

- `DashboardMachineData.tsx` importava três séries estáticas de `src/data/mockData.ts` e usava essas séries quando não havia leituras. Os cards calculavam média e status a partir delas.
- `mockData.ts` também continha séries e resumos demonstrativos. A busca não encontrou outros consumidores no frontend.
- A telemetria não possuía campo `data_origin`. A evidência S1-T5 registra proveniência temporal, mas não classifica a origem da leitura.
- `docs/CLAIMS_VS_CODE.md` não existe neste checkout; não foi possível confrontar a entrega com essa matriz.
- O contrato não fornece intervalo esperado de transmissão por máquina. A saúde agregada tampouco fornece essa frequência.

## Mocks e fallbacks encontrados/removidos

- `mockRpmSeries`, `mockTemperaturaSeries`, `mockVibracaoSeries` e o mapa `DEMO_SERIES`: removidos do dashboard.
- `frontend-next/src/data/mockData.ts`: removido após confirmar ausência de outros imports.
- Vazio de API agora aparece como “Sem histórico suficiente”; falha inicial aparece como erro/offline; nenhum valor artificial é calculado para preencher cards ou gráficos.
- Uma falha de atualização com leituras anteriores preserva o último resultado e mostra um aviso. A tela explicita que não há intervalo esperado para calcular automaticamente sua idade.

## `data_origin`

- Campo persistido em `LeituraTelemetria.data_origin` com `medido`, `simulado`, `calculado` ou `estimado`, exposto somente para leitura pelo serializer e incluído nos endpoints de leituras consumidos pelo dashboard.
- Migration incremental `0039_leituratelemetria_data_origin.py`; migrations anteriores não foram alteradas.
- Novos registros sem evidência continuam com `NULL`. Registros históricos não foram retroativamente classificados.
- Leitura só recebe `medido` quando a view de ingestão passa ao serviço a identidade confirmada pela credencial HTTP individual e ela corresponde ao dispositivo. MQTT e ingestões sem prova física permanecem sem classificação.
- Fontes de simulação identificadas pelo backend e comandos/seeds locais marcam registros como `simulado`. O frontend não envia nem sobrescreve `data_origin`.
- Scripts locais `popular_tudo`, `populate_db` e `scripts/seed_data.py` foram atualizados para persistir `simulado`.

## Estados e apresentação

`DataStateBoundary` implementa os sete casos: `loading`, `ok`, `sem_historico`, `desatualizado`, `offline`, `erro` e `invalido`. `SimulatedBadge` apresenta o texto inequívoco `SIMULADO`. A tela resume a quantidade de leituras por origem, incluindo “não verificado”, quando o período contém origens diferentes.

O dashboard detecta ausência de dados e erros separadamente; payload inválido não é renderizado. Sem uma frequência de envio confiável, a interface não calcula desatualização por `3 × intervalo`; o estado e o componente existem, mas a classificação automática não foi ligada a uma frequência inventada.

## Arquivos

- Criados: `DataStateBoundary.tsx`, `SimulatedBadge.tsx`, migration `0039`, teste `test_data_origin.py`.
- Alterados: modelo, serializer, ingestão, listagem de últimas leituras, serviço de telemetria, dashboard e schemas de telemetria; comandos de seed e `scripts/seed_data.py`.
- Removido: `frontend-next/src/data/mockData.ts`.

## Verificações executadas

- `npm run test:s3-ui`: 1 teste aprovado; cobre renderização dos sete estados e selo.
- `python manage.py test api_tcc.tests.test_data_origin api_tcc.tests.test_telemetria --verbosity 0`: 30 testes aprovados.
- `python manage.py makemigrations --check --dry-run`: sem alterações pendentes.
- `npm run type-check`: aprovado.
- `npm run lint`: aprovado sem erros ou warnings.
- `npm run build`: aprovado.
- Busca de `mockData`, nomes dos mocks removidos e `DEMO_SERIES` em `frontend-next/src`: sem resultados.
- `git diff --check`: aprovado (Git informou apenas conversão LF/CRLF de `schemas/events.ts`).

## Evidências visuais e limitações

Não foram produzidas capturas de tela. O teste de componente renderiza os estados, mas não substitui a evidência solicitada de uma aplicação real em execução. Também não foi possível validar a classificação temporal automática nem verificar visualmente comportamento responsivo/acessível nos sete estados.

## Fora do escopo

Nenhuma faixa “Atenção agora”, TrustBadge, central de decisões, mudanças de limiares, lógica de Trust Score ou firmware foi implementada. A tarefa permanece **parcial**, não concluída.
