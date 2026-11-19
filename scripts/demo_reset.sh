#!/usr/bin/env bash
set -Eeuo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
DEMO_USERNAME="${DEMO_USERNAME:-}"
if [[ -z "$DEMO_USERNAME" && -f .env ]]; then
  DEMO_USERNAME="$(sed -n 's/^DEMO_USERNAME[[:space:]]*=[[:space:]]*//p' .env | tail -n 1)"
fi
demo_mode="${DEMO_MODE:-}"
if [[ -z "$demo_mode" && -f .env ]]; then
  demo_mode="$(sed -n 's/^DEMO_MODE[[:space:]]*=[[:space:]]*//p' .env | tail -n 1)"
fi
[[ "$demo_mode" =~ ^(True|true|1)$ ]] || { echo "falha segura: DEMO_MODE=True é obrigatório" >&2; exit 2; }
[[ "$DEMO_USERNAME" =~ ^[A-Za-z0-9_.@+-]+$ ]] || { echo "DEMO_USERNAME válido é obrigatório" >&2; exit 2; }
docker compose -f "$COMPOSE_FILE" exec -T web python manage.py migrate --noinput
docker compose -f "$COMPOSE_FILE" exec -T web python manage.py popular_tudo --username "$DEMO_USERNAME"
docker compose -f "$COMPOSE_FILE" exec -T web python manage.py check
echo "demo-reset=OK (dados sintéticos idempotentes; nenhum volume foi removido)"
