# S2-T5 — Sessão do navegador sem token em `localStorage`

## Estado em 2026-11-13

Implementação reforçada, mas aceite ainda **não comprovado integralmente**: não há teste Playwright de integração do login/BFF nem captura DevTools nesta execução.

## Arquitetura observada e alterada

O fluxo existente já fazia login via rota catch-all do Next, guardava o token DRF em `fieldnode_session` com `HttpOnly`, e retornava ao navegador apenas dados de perfil. O serviço de autenticação guardava o perfil (não o token) em `localStorage`. O proxy, porém, aceitava mutações sem header CSRF, permitia mutação sem `Origin`, usava `SameSite=Strict` e repassava `X-API-Key` fornecido pelo browser.

Agora o BFF exige `X-FieldNode-CSRF: 1` e valida `Origin`, ou `Referer` quando Origin estiver ausente, em POST/PUT/PATCH/DELETE. Em produção, somente origens configuradas em `FIELDNODE_FRONTEND_URL` são aceitas. O proxy não encaminha Authorization nem X-API-Key fornecidos pelo navegador. A sessão usa `HttpOnly`, `SameSite=Lax`, `Path=/`, `Secure` em produção ou HTTPS e Max-Age limitado ao `expires_in` recebido do Django. Resposta de login nunca inclui o campo token no JSON. Se o Django estiver indisponível durante logout, o BFF apaga o cookie e retorna 503 informando que não confirmou a revogação no servidor.

O logout normal chama `POST /api/auth/logout/`; o Django remove o token DRF antes de o BFF remover o cookie. O frontend chama o BFF para login, sessão e logout e não lê o token. O SW sincroniza telemetria pelo same-origin `/api/telemetria/`, com `credentials: include` e header CSRF, preservando itens em falha de autenticação.

## Arquivos alterados

- `frontend-next/src/app/api/[...path]/route.ts`
- `api_tcc/api/views_auth.py` (registro agora retorna TTL real para o BFF)
- `api_tcc/api/views_decision_action.py` (404 para recurso de outra organização)
- `frontend-next/src/services/authService.ts`
- `frontend-next/src/services/telemetryService.ts`
- `frontend-next/src/services/operatorService.ts`
- `frontend-next/src/components/SessionGate.tsx`
- `frontend-next/src/components/LogoutButton.tsx` (não mascara falha HTTP de invalidação)
- `frontend-next/public/sw.js`
- `docs/SEGURANCA.md`

## Evidência e limites

- A busca no frontend mostra que `fn-auth-token` apenas é removido; o serviço persiste `fn-auth-user` (perfil), nunca lê ou grava o token. `localStorage` também guarda preferências visuais.
- Playwright com browser e DevTools: **NÃO VERIFICADO**. Não há configuração/fluxo E2E de autenticação presente para execução nesta tarefa.
- Teste de integração BFF para CSRF/origem: **NÃO VERIFICADO**.
- O código Django de logout apaga o `Token` do usuário; reutilização do token em chamada real pós-logout: **NÃO VERIFICADO**.
- `.venv/Scripts/python.exe -m pytest api_tcc/tests/test_auth.py api_tcc/tests/test_tenant_isolation.py -q`: **16 passed** on the latest combined run.
- O autenticador Django rejeita tokens após o TTL; renovação automática não foi adicionada.
- Não há captura DevTools. Portanto, o aceite integral S2-T5 permanece pendente, embora o código revisto não devolva token no JSON de sucesso do BFF.
