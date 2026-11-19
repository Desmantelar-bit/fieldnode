# Deploy e gateway do FieldNode

Este documento separa demonstração local de produção. `gateway-up` sobe o
Compose local e valida o ambiente. Não faz `down -v`, não recria volumes e não
executa seed automaticamente.

## Gateway local

Pré-requisitos: Docker Desktop com Compose v2, Git, `curl` e `make` (ou execução
manual equivalente no Windows). Em uma cópia limpa:

```powershell
Copy-Item .env.example .env
# edite .env: SECRET_KEY, DB_PASSWORD, DB_ROOT_PASSWORD, MQTT_USERNAME e MQTT_PASSWORD
make gateway-up
```

O fluxo executa `docker compose up -d --build`, migrations e
`scripts/preflight.sh`. O preflight verifica containers em execução, healthcheck,
backend, readiness, migrations, autenticação real do broker, frontend e exibe o
relógio local/UTC. Ele não imprime credenciais.

Se `make` não estiver disponível, execute os mesmos passos com:

```powershell
docker compose up -d --build
docker compose exec -T web python manage.py migrate --noinput
# em Git Bash/WSL:
bash scripts/preflight.sh
```

Endereços locais: dashboard `http://127.0.0.1:3000`, API
`http://127.0.0.1:8000/api/health/`, MySQL somente para diagnóstico local em
`127.0.0.1:3307`. O broker fica em `127.0.0.1:${MQTT_HOST_PORT}`. Não exponha
MySQL ou MQTT na internet.

### Hotspot

O repositório não cria hotspot de forma portátil. No Windows, configure o
Mobile Hotspot do sistema e use a rede local existente; o gateway continua
válido sem hotspot. Composição iniciada não é evidência de rádio ou hotspot.

## Produção/nuvem

O provedor e destino de D-26 não estão definidos neste checkout. Por isso,
`make cloud-up` recusa a execução e não finge ser um deploy. Não publique o
Compose local como substituto de uma arquitetura de produção.

Antes de qualquer exposição pública, confirme no destino real: `DEBUG=False`,
`SECRET_KEY` por secret manager, `ALLOWED_HOSTS` exato, CORS/CSRF exatos,
proxy HTTPS real, `SECURE_SSL=True` somente atrás desse proxy, cookies seguros,
backup/restore, logs sem segredos, migrations coordenadas e `collectstatic`.
O banco e o broker devem permanecer em rede privada. O ambiente de produção
não usa usuário demo, seed ou credencial padrão.

## Parada, persistência e recuperação

`docker compose stop` preserva volumes. `docker compose down` preserva os
volumes nomeados; não use `down -v` no fluxo normal. Consulte
[`BACKUP_RESTORE.md`](BACKUP_RESTORE.md) antes de atualizar ou restaurar dados.

Diagnóstico rápido:

```powershell
docker compose ps
docker compose logs --tail=100 web
docker compose logs --tail=100 worker
docker compose exec web python manage.py showmigrations --plan
```

## Critério de tempo

O alvo de menos de dez minutos é **não verificado** neste checkout: exige
execução cronometrada em máquina limpa, incluindo clone, imagens, configuração,
build, migrations, preflight e abertura do dashboard. Uma máquina já aquecida
ou com volumes existentes não prova esse critério.
