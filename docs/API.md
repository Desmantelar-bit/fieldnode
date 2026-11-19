# API V1

O contrato versionado está disponível em `/api/v1/`. Nesta primeira entrega, a V1 reutiliza as rotas já consumidas pelo frontend e pelo gateway, preservando os serializers e as regras de isolamento existentes. A rota `/api/` permanece como alias durante o ciclo de migração e responde com `Deprecation: true` e `Link: </api/v1/>; rel="successor-version"`.

## Passport

`GET /api/v1/passport/export/` exporta um ZIP por organização. Usuários precisam de membership `admin` ou `member` e informam `organization_id` apenas como seleção de uma organização que já possuem. Tokens de integração usam `Authorization: Bearer ...` e exigem o escopo `passport:export`; a organização vem do token, nunca do request.

O token é emitido uma única vez por `POST /api/v1/auth/organization-tokens/` por um administrador. O valor bruto não é persistido. Revogação usa `DELETE` com o identificador do token.

O Passport v0.1 contém `manifest.json`, `telemetry.csv`, `events.json`, `decisions.json`, `work_orders.json`, `provenance.json` e `FORMAT.md`. Os arquivos possuem SHA-256. A assinatura HMAC-SHA256 depende de `FIELDNODE_PASSPORT_SIGNING_KEY`; sem essa configuração o pacote é identificável como não assinado e não deve ser importado como confiável.

## Depreciação

Não há data de Sunset inventada nesta entrega. A remoção do alias depende de inventário de consumidores e decisão explícita de ciclo. O header identifica a migração sem transformar uma hipótese comercial em calendário.
