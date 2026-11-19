#!/usr/bin/env bash
set -Eeuo pipefail

# Fixture-only acceptance test. It creates two disposable databases in the
# running Compose MySQL service and never uses the application database.
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
export FIELDNODE_BACKUP_DIR="${FIELDNODE_BACKUP_DIR:-./backups/test-run}"
export FIELDNODE_BACKUP_KEEP=10
KEY_FILE="${FIELDNODE_BACKUP_PASSPHRASE_FILE:-}"
[[ -r "$KEY_FILE" ]] || { echo "FIELDNODE_BACKUP_PASSPHRASE_FILE obrigatorio" >&2; exit 2; }
suffix="$(date -u +%Y%m%d%H%M%S)"
source_db="fieldnode_backup_fixture_${suffix}"
target_db="fieldnode_restore_fixture_${suffix}"
db_exec() {
  docker compose -f "$COMPOSE_FILE" exec -T db sh -c 'MYSQL_PWD="$DB_PASSWORD" mysql -u"$DB_USER" -e "$1"' sh "$1"
}
cleanup() {
  db_exec "DROP DATABASE IF EXISTS ${source_db}; DROP DATABASE IF EXISTS ${target_db};" >/dev/null 2>&1 || true
}
trap cleanup EXIT
db_exec "CREATE DATABASE ${source_db}; CREATE DATABASE ${target_db}; CREATE TABLE ${source_db}.fixture (id INT PRIMARY KEY, value VARCHAR(80) NOT NULL); INSERT INTO ${source_db}.fixture VALUES (1,'alpha'),(2,'beta'),(3,'gamma');"
export FIELDNODE_BACKUP_DATABASE="$source_db"
./scripts/backup.sh
artifact="$(find "$FIELDNODE_BACKUP_DIR" -maxdepth 1 -name 'fieldnode_*.sql.gz.enc' -type f -printf '%T@ %p\n' | sort -nr | awk 'NR==1 {print $2}')"
[[ -n "$artifact" ]] || { echo "artefato não encontrado" >&2; exit 3; }
export FIELDNODE_RESTORE_DATABASE="$target_db"
export FIELDNODE_RESTORE_CONFIRM="RESTORE_TEST_${target_db}"
./scripts/restore.sh "$artifact"
source_count="$(db_exec "SELECT COUNT(*) FROM ${source_db}.fixture;" | tail -n 1 | tr -d '\r')"
target_count="$(db_exec "SELECT COUNT(*) FROM ${target_db}.fixture;" | tail -n 1 | tr -d '\r')"
[[ "$source_count" == "$target_count" && "$target_count" == "3" ]] || { echo "count mismatch source=$source_count target=$target_count" >&2; exit 4; }
echo "restore_test=passed source_count=$source_count target_count=$target_count artifact=$artifact"
