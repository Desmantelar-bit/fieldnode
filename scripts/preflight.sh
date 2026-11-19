#!/usr/bin/env bash
set -u
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
API_URL="${FIELDNODE_PREFLIGHT_API_URL:-http://127.0.0.1:8000/api}"
FRONTEND_URL="${FIELDNODE_PREFLIGHT_FRONTEND_URL:-http://127.0.0.1:3000}"
LOCAL_URL="${FIELDNODE_PREFLIGHT_LOCAL_URL:-$FRONTEND_URL}"
LOCAL_HOSTNAME="${FIELDNODE_PREFLIGHT_LOCAL_HOSTNAME:-}"
UPLINK_URL="${FIELDNODE_PREFLIGHT_UPLINK_URL:-}"
failures=0
ok() { printf '[OK]   %s\n' "$1"; }
warn() { printf '[WARN] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }
if ! command -v docker >/dev/null 2>&1; then fail 'Docker não encontrado no PATH.'; exit 1; fi
if ! docker info >/dev/null 2>&1; then fail 'Docker não está disponível; inicie o Docker Desktop.'; exit 1; fi
if docker compose -f "$COMPOSE_FILE" config >/dev/null 2>&1; then ok 'configuração do Compose válida'; else fail 'configuração do Compose inválida'; fi
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
demo_mode="${DEMO_MODE:-}"
if [ -z "$demo_mode" ] && [ -f .env ]; then
  demo_mode="$(sed -n 's/^DEMO_MODE[[:space:]]*=[[:space:]]*//p' .env | tail -n 1)"
fi
if [ "$demo_mode" = "True" ] || [ "$demo_mode" = "true" ] || [ "$demo_mode" = "1" ]; then
  ok 'DEMO_MODE habilitado explicitamente'
else
  warn 'DEMO_MODE não está habilitado no processo do preflight; confirme o contexto antes da banca'
fi
if [ "$LOCAL_URL" != "$FRONTEND_URL" ]; then
  if curl --fail --silent --show-error --max-time 5 "$LOCAL_URL/" >/dev/null; then ok "acesso local responde em $LOCAL_URL"; else fail "acesso local não respondeu em $LOCAL_URL"; fi
fi
if [ -n "$LOCAL_HOSTNAME" ]; then
  if command -v getent >/dev/null 2>&1 && getent hosts "$LOCAL_HOSTNAME" >/dev/null 2>&1; then
    ok "hostname local resolve: $LOCAL_HOSTNAME"
  elif command -v nslookup >/dev/null 2>&1 && nslookup "$LOCAL_HOSTNAME" >/dev/null 2>&1; then
    ok "hostname local resolve: $LOCAL_HOSTNAME"
  else
    fail "hostname local não resolve: $LOCAL_HOSTNAME"
  fi
else
  warn 'hostname local não configurado; fieldnode.local e HTTPS local permanecem não verificados'
fi
case "$LOCAL_URL" in
  https://*) if curl --fail --silent --show-error --max-time 5 "$LOCAL_URL/" >/dev/null; then ok 'HTTPS local respondeu'; else fail 'HTTPS local não respondeu'; fi ;;
  http://*) warn 'acesso local está em HTTP; isto não comprova HTTPS local' ;;
  *) fail "URL local inválida: $LOCAL_URL" ;;
esac
if [ -n "$UPLINK_URL" ]; then
  if curl --fail --silent --show-error --max-time 5 "$UPLINK_URL" >/dev/null; then ok 'destino de uplink respondeu'; else warn 'destino de uplink não respondeu; continuidade local ainda pode ser demonstrada'; fi
else
  warn 'destino de uplink não configurado; sincronização cloud não será declarada'
fi
RELEASE_DIR="${FIELDNODE_RELEASE_DIR:-./release-artifacts}"
VIDEO_PATH="${FIELDNODE_FALLBACK_VIDEO:-}"
if [ -z "$VIDEO_PATH" ] && [ -d "./media" ]; then
  VIDEO_PATH="$(find ./media -maxdepth 2 -type f \( -iname '*.mp4' -o -iname '*.webm' -o -iname '*.mkv' \) -print -quit 2>/dev/null || true)"
fi
if [ -n "$VIDEO_PATH" ] && [ -s "$VIDEO_PATH" ]; then ok "vídeo de fallback encontrado: $VIDEO_PATH"; else warn 'vídeo de fallback não encontrado; gate de contingência permanece pendente'; fi
if [ -s "$RELEASE_DIR/docker-images/manifest.txt" ]; then ok 'manifesto de imagens Docker encontrado'; else warn 'imagens Docker exportadas não encontradas; execute make save-demo-images'; fi
if find . -maxdepth 2 -type f -name 'fieldnode_*.manifest' -print -quit 2>/dev/null | grep -q .; then ok 'manifesto de backup encontrado'; else warn 'backup de demonstração não encontrado; gate de restauração permanece pendente'; fi
if command -v df >/dev/null 2>&1; then
  free_kb="$(df -Pk . | awk 'NR==2 {print $4}')"
  if [ -n "$free_kb" ] && [ "$free_kb" -gt 1048576 ] 2>/dev/null; then ok "espaço livre no volume de trabalho: ${free_kb} KiB"; else warn 'espaço livre no volume de trabalho está baixo ou não foi medido'; fi
else
  warn 'df não disponível; espaço em disco não verificado'
fi
if date -u >/dev/null 2>&1; then ok "relógio local: $(date '+%Y-%m-%d %H:%M:%S %Z') | UTC: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"; else warn 'não foi possível consultar o relógio local'; fi
if [ "$failures" -gt 0 ]; then printf 'preflight=FAIL failures=%s\n' "$failures"; exit 1; fi
printf 'preflight=OK\n'
