#!/usr/bin/env bash
set -Eeuo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
BACKUP_DIR="${FIELDNODE_BACKUP_DIR:-./backups}"
KEEP="${FIELDNODE_BACKUP_KEEP:-7}"
PASSPHRASE_FILE="${FIELDNODE_BACKUP_PASSPHRASE_FILE:-}"
if [[ -z "$PASSPHRASE_FILE" || ! -r "$PASSPHRASE_FILE" ]]; then
  echo "FIELDNODE_BACKUP_PASSPHRASE_FILE deve apontar para um arquivo protegido" >&2
  exit 2
fi
if ! [[ "$KEEP" =~ ^[1-9][0-9]*$ ]]; then echo "FIELDNODE_BACKUP_KEEP invalido" >&2; exit 2; fi
mkdir -p "$BACKUP_DIR"
umask 077
run_id="$(date -u +%Y%m%dT%H%M%SZ)"
base="$BACKUP_DIR/fieldnode_${run_id}"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/fieldnode-backup.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "backup_id=$run_id started_at=$started"
SOURCE_DB="${FIELDNODE_BACKUP_DATABASE:-}"
docker compose -f "$COMPOSE_FILE" exec -T -e FIELDNODE_BACKUP_DATABASE="$SOURCE_DB" db sh -c 'MYSQL_PWD="$DB_PASSWORD" mysqldump --single-transaction --routines --triggers --events --hex-blob "${FIELDNODE_BACKUP_DATABASE:-$DB_NAME}"' > "$tmp/dump.sql"
test -s "$tmp/dump.sql"
gzip -c "$tmp/dump.sql" > "$tmp/dump.sql.gz"
dump_sha="$(sha256sum "$tmp/dump.sql.gz" | awk '{print $1}')"
openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -salt -in "$tmp/dump.sql.gz" -out "${base}.sql.gz.enc" -pass "file:${PASSPHRASE_FILE}"
test -s "${base}.sql.gz.enc"
encrypted_sha="$(sha256sum "${base}.sql.gz.enc" | awk '{print $1}')"
finished="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat > "${base}.manifest" <<EOF
backup_id=$run_id
started_at=$started
finished_at=$finished
mysql_source=compose:db
database_scope=${SOURCE_DB:-DB_NAME}
format=mysqldump|gzip|openssl-aes-256-cbc-pbkdf2
dump_gzip_sha256=$dump_sha
encrypted_sha256=$encrypted_sha
artifact=$(basename "${base}.sql.gz.enc")
validation=encrypted-artifact-written
EOF
echo "backup_id=$run_id artifact=${base}.sql.gz.enc encrypted_sha256=$encrypted_sha"
mapfile -t artifacts < <(find "$BACKUP_DIR" -maxdepth 1 -type f -name 'fieldnode_*.sql.gz.enc' -printf '%T@ %p\n' | sort -nr | awk '{print $2}')
if (( ${#artifacts[@]} > KEEP )); then
  for artifact in "${artifacts[@]:KEEP}"; do
    manifest="${artifact%.sql.gz.enc}.manifest"
    rm -f -- "$artifact" "$manifest"
    echo "retention_removed=$(basename "$artifact")"
  done
fi
