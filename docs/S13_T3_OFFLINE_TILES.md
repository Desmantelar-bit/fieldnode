# S13-T3 · decisão de tiles offline

## Estado

O FieldNode mantém cache local dos tiles que o operador realmente visualizou,
com atribuição visível ao OpenStreetMap. O Service Worker usa um cache separado
para a camada cartográfica e reaproveita os tiles quando o gateway cai.

## Decisão de licença

Não usar `tile.openstreetmap.org` para pré-carregar a bounding box da fazenda.
A política oficial do serviço proíbe download antecipado, prefetch em massa e
uso offline. A função de cálculo de tiles fica preparada para um provedor que
autorize explicitamente esse uso, mas não deve ser chamada contra o endpoint
OSM padrão.

Para atender ao requisito de área pré-carregada, a decisão pendente é contratar
um provedor com licença de offline/prefetch ou operar tiles próprios. Antes do
piloto, registrar o provedor, licença, atribuição, limites de zoom e política de
atualização.

Fonte verificada em 19/11/2026:
https://operations.osmfoundation.org/policies/tiles/
