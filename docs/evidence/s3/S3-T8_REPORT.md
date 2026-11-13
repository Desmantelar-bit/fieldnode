# S3-T8 — painel “Quem está por trás do FieldNode”

## Integração e direção visual

O botão discreto foi integrado ao cabeçalho compartilhado do `AppShell`, sem deslocar o conteúdo das páginas. Ele abre um diálogo editorial responsivo com retratos retangulares, áreas de contribuição, descrições curtas e links profissionais. A composição usa tokens existentes e movimento breve, desativado com `prefers-reduced-motion`. O diálogo suporta Escape, contenção e restauração de foco.

## Fotografias e dados

Os arquivos existentes na raiz do repositório são JPEGs (não PNGs como descrito no briefing). Foram copiados sem edição para `frontend-next/public/team/` e associados pelo nome do arquivo:

| Integrante | Arquivo original | Arquivo público |
| --- | --- | --- |
| Vinícius Morales | `vinicius.jpg` | `frontend-next/public/team/vinicius.jpg` |
| Ana Furlaneto | `ana.jpg` | `frontend-next/public/team/ana.jpg` |
| Giovana D'Angelo | `giovana.jpg` | `frontend-next/public/team/giovana.jpg` |
| Paola Soares Machado | `paola.jpg` | `frontend-next/public/team/paola.jpg` |

Os nomes dos arquivos fornecem a associação adotada. Não foi feita edição nem geração de retratos. A associação visual pessoa/foto e a autorização individual de publicação não podem ser confirmadas somente pelo código; o pedido forneceu as imagens e solicitou expressamente o painel.

Os dados tipados estão centralizados em `frontend-next/src/data/team.ts`. Os quatro LinkedIns e os três GitHubs fornecidos foram usados literalmente. Giovana não recebe GitHub. Nenhum e-mail ou dado biográfico adicional é apresentado. As descrições são texto editorial sobre as contribuições no FieldNode, não citações pessoais.

## Evidências e verificação

O Playwright em `frontend-next/tests/playwright_map_test.js` verifica a presença dos quatro integrantes, a ausência do GitHub de Giovana, abertura/fechamento e captura em mobile e desktop. Capturas esperadas em `docs/evidence/s3/captures/`:

- `s3-t8-team-mobile.png`
- `s3-t8-team-mobile-bottom.png` (continuação rolada com Paola)
- `s3-t8-team-desktop.png`

**Verificado:** o mesmo teste Playwright confirmou os quatro nomes, links GitHub exatos para os três membros, ausência de GitHub para Giovana, atributos seguros nos links externos, abertura, Escape, foco contido e retorno do foco em viewport mobile e desktop. `img.decode()` confirmou o carregamento das quatro fotografias. As capturas listadas foram geradas pelo teste. `npm run lint` e `npm run type-check` passaram.

`npm run build` passou após a implementação. Não há e-mails autorizados fornecidos para publicação.
