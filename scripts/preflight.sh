#!/usr/bin/env bash
set -u
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
API_URL="${FIELDNODE_PREFLIGHT_API_URL:-http://127.0.0.1:8000/api}"
FRONTEND_URL="${FIELDNODE_PREFLIGHT_FRONTEND_URL:-http://127.0.0.1:3000}"
failures=0
ok() { printf '[OK]   %s\n' "$1"; }
warn() { printf '[WARN] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }
if ! command -v docker >/dev/null 2>&1; then fail 'Docker não encontrado no PATH.'; exit 1; fi
if ! docker info >/dev/null 2>&1; then fail 'Docker não está disponível; inicie o Docker Desktop.'; exit 1; fi
for service in db mosquitto web worker frontend; do
  if docker compose -f "$COMPOSE_FILE" ps -a --status running --services 2>/dev/null | grep -Fxq "$service"; then
    ok "container $service em execução"
  else
    fail "container $service ausente ou parado"
  fi
done
if docker compose -f "$COMPOSE_FILE" ps --format json 2>/dev/null | grep -q '"Health":"unhealthy"'; then fail 'há container unhealthy.'; else ok 'nenhum container unhealthy reportado'; fi
if curl --fail --silent --show-error --max-time 5 "$API_URL/health/" >/dev/null; then ok 'backend responde em /api/health/'; else fail 'backend não respondeu em /api/health/'; fi
if curl --fail --silent --show-error --max-time 5 "$API_URL/health/ready" >/dev/null; then ok 'backend pronto em /api/health/ready'; else fail 'backend não está pronto em /api/health/ready'; fi
if docker compose -f "$COMPOSE_FILE" exec -T web python manage.py showmigrations --plan 2>/dev/null | grep -q '\[ \]'; then fail 'há migrations pendentes.'; else ok 'migrations aplicadas'; fi
if docker compose -f "$COMPOSE_FILE" exec -T mosquitto sh -c 'mosquitto_pub -h 127.0.0.1 -p 1883 -u "$MQTT_USERNAME" -P "$MQTT_PASSWORD" -t fieldnode/preflight -n -q 0' >/dev/null 2>&1; then ok 'broker MQTT aceitou a credencial configurada'; else fail 'broker MQTT não aceitou a credencial configurada'; fi
if curl --fail --silent --show-error --max-time 5 "$FRONTEND_URL/" >/dev/null; then ok 'frontend responde na rota inicial'; else fail 'frontend não respondeu na rota inicial'; fi
if date -u >/dev/null 2>&1; then ok "relógio local: $(date '+%Y-%m-%d %H:%M:%S %Z') | UTC: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"; else warn 'não foi possível consultar o relógio local'; fi
if [ "$failures" -gt 0 ]; then printf 'preflight=FAIL failures=%s\n' "$failures"; exit 1; fi
printf 'preflight=OK\n'
