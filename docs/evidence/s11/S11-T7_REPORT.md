# S11-T7 - API V1 e contrato versionado

## Entrega

- `/api/v1/` foi adicionado reutilizando as rotas atuais e os mesmos serializers/regras, sem duplicar domínio.
- `/api/` continua como alias de compatibilidade e recebe `Deprecation: true` e `Link` para a V1. Não foi inventada uma data de `Sunset`.
- A geração OpenAPI existente do `drf-yasg` continua sendo a fonte do contrato; a rota `/swagger.json/` respondeu HTTP 200 em verificação local com host permitido.
- `OrganizationToken` foi adicionado com hash SHA-256, organização, escopos, expiração e revogação. O valor bruto só é retornado na emissão.
- O escopo aplicado nesta entrega é `passport:export`, usado efetivamente por `GET /api/v1/passport/export/`. O token não aceita organização arbitrária do request.
- Emissão e revogação ficam em `/api/v1/auth/organization-tokens/`, exigindo administrador da organização.

## Evidência executada

```text
venv\Scripts\python.exe manage.py check
System check identified no issues (0 silenced).

venv\Scripts\python.exe manage.py makemigrations --check --dry-run
No changes detected

venv\Scripts\python.exe manage.py migrate --noinput
Applying api_tcc.0060_organizationtoken... OK

venv\Scripts\python.exe manage.py test api_tcc.tests.test_s11_passport_v1 --verbosity 1
Ran 3 tests ... OK
```

## Pendências e limites

- A matriz completa de consumidores frontend/gateway e testes Schemathesis não foi criada nesta entrega; o teste de contrato implementado é HTTP de alias/V1 e o Passport.
- `manage.py check --deploy` ainda reporta seis avisos de configuração do ambiente atual (`DEBUG`, HTTPS/HSTS, cookies seguros e `SECRET_KEY`). A API não deve ser anunciada como pronta para produção por causa do prefixo V1.
- A API completa ainda contém rotas legadas e experimentais; elas foram expostas sob V1 por reutilização de rota, mas não há afirmação de que todas sejam contrato público final.
