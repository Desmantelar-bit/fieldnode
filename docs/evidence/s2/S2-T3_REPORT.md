# S2-T3 · Swagger e documentação fora de dev

## Arquivos alterados

- `setup/settings.py`
- `setup/urls.py`
- `api_tcc/tests/test_documentacao_urls.py`

## Regra final

`SWAGGER_ENABLED` usa `DEBUG` como padrão e é interpretada como booleano pela configuração `python-decouple`. O acesso anônimo é permitido somente quando `DEBUG=True` e `SWAGGER_ENABLED=True`. Em qualquer outra combinação, o `schema_view` exige `IsAdminUser`; portanto, definir a flag como verdadeira fora de `DEBUG` não torna a documentação pública. Com a flag falsa, as rotas continuam disponíveis para usuários staff, conforme a semântica do roadmap.

## Rotas e raiz

A política central protege `/swagger/`, `/swagger.json/` e `/redoc/`. Não foram encontradas outras rotas de schema/documentação no `setup/urls.py` ou em `api_tcc/urls.py`.

`/` redireciona para `FIELDNODE_FRONTEND_URL`. A variável já existia no `.env.example` e no Docker Compose. Sem valor, o fallback é `http://localhost:3000` em desenvolvimento e `/api/health/` fora de `DEBUG`, evitando configurar um host local fixo para produção.

## Verificação

- `USE_SQLITE=True .venv/Scripts/python.exe -m pytest api_tcc/tests/test_documentacao_urls.py -q`: passou dentro da suíte focada, cobrindo documentação pública em dev, anônimo/usuário comum/staff fora de dev, flag desligada e destino da raiz.
- A suíte focada combinada com S2-T4: **15 passed**.
- `python manage.py check`: sem problemas.

