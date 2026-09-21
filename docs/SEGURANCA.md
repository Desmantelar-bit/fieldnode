# Segurança

Este documento registra o modelo de segurança atual do FieldNode. Ele descreve o estado do MVP, não uma promessa de segurança de produção.

## Autenticação

- A autenticação administrativa atual usa DRF `TokenAuthentication`.
- `POST`, `PUT`, `PATCH` e `DELETE` nos cadastros administrativos exigem usuário autenticado.
- `POST /api/telemetria/` e `POST /api/telemetria/lote/` continuam sendo endpoints máquina-a-máquina protegidos por `X-API-Key`, validada no backend.
- GETs públicos existem para demonstração, dashboard e consultas operacionais do MVP.
- O frontend usa `Authorization: Token <token>` para operações autenticadas e não deve receber `FIELDNODE_API_KEY`.

## Demo Mode

`DEMO_MODE=True` significa que leituras públicas anônimas de demonstração, quando existentes, são limitadas a máquinas marcadas explicitamente com `Machine.is_demo=True`.

`DEMO_MODE` não é autorização, não é autenticação e não é bypass de permissões.

`Machine.is_demo=True` significa apenas que a máquina foi criada para demonstração controlada. Não significa que dado real foi autorizado para publicação.

Com `DEMO_MODE=False`, o backend segue o contrato normal de segurança do MVP. A flag desativada não transforma `is_demo=True` em substituto de autenticação e não cria uma regra nova de exposição.

## Leituras Públicas

Quando o request é anônimo e `DEMO_MODE=True`, as leituras públicas ligadas a telemetria consultam somente registros associados a `Machine.is_demo=True`.

O caso mínimo validado é:

```text
GET /api/leituras/ultimas/
DEMO_MODE=True
Machine demo: is_demo=True -> aparece
Machine real: is_demo=False -> não aparece
```

O filtro é aplicado no backend antes da resposta ser serializada.

## CORS

A configuração atual usa `CORS_ALLOWED_ORIGINS` por variável de ambiente. O projeto não usa `CORS_ALLOW_ALL_ORIGINS=True` como regra permanente.

CORS restringe consumo pelo navegador, mas não substitui autenticação. Requests diretos fora do navegador ainda precisam ser protegidos por permissões, token ou API key conforme o endpoint.

## DÍVIDA / LIMITAÇÃO CONHECIDA

- O MVP ainda guarda token administrativo em `localStorage` no frontend.
- Não há MFA.
- Não há rotação automática de token.
- O token DRF padrão não possui expiração adequada para um piloto real.
- O isolamento multi-tenant ainda não deve ser tratado como completo para produção.
- Endpoints GET públicos existem no contrato atual do MVP e precisam ser revisados antes de piloto com dados reais.

Antes de qualquer piloto real, a autenticação deve evoluir para sessão com cookie `HttpOnly`, `Secure`, `SameSite`, expiração, rotação e proteção CSRF.

## Dívidas Técnicas Reveladas pela Validação Comercial (John Deere, Solinftec, Case IH)

As conversas de validação comercial de 2026-09-19 tornaram concretas as seguintes lacunas de segurança e integração para um piloto real:

**Upload pós-offline (Case IH):** a preocupação explícita foi com a segurança e confiabilidade do upload de dados acumulados após horas offline. O mecanismo atual de deduplicação UUID cobre a idempotência, mas não há autenticação mútua no canal de sincronização nem verificação de integridade do payload acumulado (hash end-to-end). Antes de piloto real, o canal de ressincronização precisa de autenticação e verificação de integridade.

**Integração com sistemas de BI proprietários (Case IH / Clealco):** usinas que consomem dados brutos via exportação CSV/XLSX para sistemas proprietários precisam de um canal autenticado de exportação. O endpoint atual de exportação é público (sem token). Para piloto real, exportação de dados operacionais deve exigir autenticação.

**Sensores externos sem CAN (John Deere e Case IH):** máquinas antigas sem barramento J1939 acessível dependem de sensores externos. O FieldNode atual não tem modelo de autenticação ou validação de origem para sensores externos além da `X-API-Key` global. Para frotas mistas em piloto real, cada dispositivo de borda deveria ter identidade própria.

**Dashboard local offline-first na cabine:** o Service Worker atual cobre fila de telemetria offline, mas não um dashboard operacional acessível sem internet. Isso não é uma vulnerabilidade de segurança, mas é uma lacuna funcional citada pelos três especialistas como requisito de piloto.

## Decisão Atual Sobre Token

Nesta fase, o FieldNode usa DRF `TokenAuthentication`. JWT, OAuth, SSO, refresh token e access token customizado ficam fora do escopo deste bloco.

A decisão é coerente com o estágio atual: equipe de TCC, protótipo controlado e eventual piloto pequeno. Para piloto real, essa decisão precisa ser reavaliada.
