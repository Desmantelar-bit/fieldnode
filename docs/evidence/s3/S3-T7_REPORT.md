# S3-T7 — mapa mobile

## Diagnóstico e decisão de arquitetura

- `/mapa` renderiza `MapaFrota`, que delega a superfície ao `MapClient` com `fullBleed`.
- O dashboard renderiza `FleetMap`, outro wrapper de apresentação para o mesmo `MapClient`, sem full bleed. Os dois wrappers têm consumidores distintos e a configuração de apresentação difere; não são três implementações cartográficas concorrentes.
- `MapClient` é o único componente que cria Leaflet, carrega posições, normaliza payloads, desenha marcadores e mantém a seleção. Não foi removida lógica dos wrappers usados por suas páginas.
- `MapClient` também é o único lugar com lógica de apresentação; filtros e seleção permanecem no componente cartográfico.

## Experiência implementada

- Em viewport mobile, selecionar marcador abre uma bottom sheet com status e telemetria presentes no contrato de posição: temperatura, RPM e horário da última posição. O botão “Ver máquina” usa a rota existente `/detalhes?id=...`.
- A sheet tem botão de fechar, Escape, gesto vertical para baixo, foco contido e retorno do foco ao marcador. A altura é limitada a 39dvh para preservar pelo menos 55% da área do mapa mesmo considerando o cabeçalho da aplicação.
- A gaveta de busca tem fechamento por botão, backdrop e Escape. A busca já existente foi movida para essa gaveta no mobile, continua sendo aplicada enquanto se digita e persiste no parâmetro `q` da URL.
- O mapa permanece visível e arrastável; o zoom por roda fica desativado em telas touch para evitar rolagem involuntária.

## Limites de contrato

O relatório de S3-T6 (`S3-T6_REPORT.md`) registra que filtros/classificação compartilhados ainda não foram implementados e que a API de posições não fornece Trust Score, qualidade/observabilidade, severidade ou decisão associada. Por isso, esta entrega não cria filtros paralelos de status/severidade nem mostra valores derivados. A gaveta oferece busca textual, com estado local à rota do mapa persistido por `q`; a sincronização cruzada dashboard/máquinas segue pendente do contrato compartilhado de S3-T6.

## Evidências e verificação

O teste Playwright em `frontend-next/tests/playwright_map_test.js` cobre viewport 390×844, seleção, altura/área visível, fechamento por botão/Escape/gesto, persistência da busca, painel de equipe em mobile/desktop e erros de navegador. Capturas esperadas em `docs/evidence/s3/captures/`:

- `s3-t7-map-mobile.png`
- `s3-t7-bottom-sheet.png`
- `s3-t7-filter-drawer.png`
- `s3-t7-filter-preserved.png`

**Verificado:** `node tests/playwright_map_test.js` aprovado em viewport 390×844, incluindo medição geométrica da sheet/área de mapa, clique e Enter no marcador, botão, Escape, gesto, contenção e retorno do foco, gaveta, persistência de `q` ao fechar/reabrir e recarregar, além da limpeza de `q`. As capturas listadas foram geradas pelo teste. `npm run lint`, `npm run type-check` e `npm run build` passaram.

O teste intercepta a API com um fixture controlado; na sheet ele aparece como `Colheitadeira demonstrativa`. As capturas são evidência de interação/layout, não telemetria de operação real.

A relação de uma decisão a uma posição não existe no contrato consumido pelo mapa; a sheet não inventa a ação “Ver decisão”.
