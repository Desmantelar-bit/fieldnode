# S3-T9 · Busca global, tooltips, contraste e redundância

## Escopo auditado

As seis páginas principais são `/dashboard`, `/colheitadeiras`, `/decisoes`, `/mapa`, `/operarios` e `/relatorios`. O chrome compartilhado foi alterado em `AppShell`, incluindo a busca global.

## Evidência de implementação

- Busca `Ctrl+K`/`Cmd+K` em `GlobalSearch.tsx`, com debounce de 220 ms, cancelamento por `AbortController`, navegação por setas/Enter/Escape e estados de vazio, erro e carregamento.
- Endpoint restrito a máquinas acessíveis, operadores vinculados a máquinas acessíveis e decisões dessas máquinas: `GET /api/search/?q=`.
- Tooltips de métrica foram adicionados como conteúdo acessível por foco, sem esconder a informação essencial.
- Tokens de status no tema claro foram escurecidos para preservar contraste de texto; a identidade visual lima permanece como acento e preenchimento.
- A fila operacional continua em `AttentionStrip`/Central de decisões; o resumo da frota continua separado no dashboard. Não foi removida ação contextual legítima sem evidência de duplicação.

## Verificação

`npm run type-check` foi executado com saída 0 e `npm run build` compilou, gerou as 15 páginas estáticas e deixou `.next/BUILD_ID`. `@axe-core/playwright` e `npm run test:axe-s3` foram adicionados, mas a auditoria das seis rotas permanece **NÃO VERIFICADA** nesta execução porque exige servidor frontend ativo e `FIELDNODE_AUTH_TOKEN` real. O relatório técnico do axe será salvo nesta pasta quando essa execução for concluída.

## Pendências

- A página de decisões ainda precisa consumir o parâmetro `decision` da URL para abrir automaticamente um item vindo da busca.
- Não há fixtures de sessão/seed suficientes no repositório para afirmar o resultado visual de todas as seis páginas sem subir a aplicação.
