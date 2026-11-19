#!/usr/bin/env bash
set -Eeuo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
BACKUP="${1:-}"
PASSPHRASE_FILE="${FIELDNODE_BACKUP_PASSPHRASE_FILE:-}"
if [[ -z "$BACKUP" || ! -r "$BACKUP" ]]; then echo "backup legivel obrigatorio" >&2; exit 2; fi
if [[ -z "$PASSPHRASE_FILE" || ! -r "$PASSPHRASE_FILE" ]]; then echo "FIELDNODE_BACKUP_PASSPHRASE_FILE obrigatorio" >&2; exit 2; fi
manifest="${BACKUP%.sql.gz.enc}.manifest"
[[ -r "$manifest" ]] || { echo "manifesto ausente: $manifest" >&2; exit 2; }
expected="$(awk -F= '$1=="encrypted_sha256" {print $2}' "$manifest")"
actual="$(sha256sum "$BACKUP" | awk '{print $1}')"
[[ -n "$expected" && "$expected" == "$actual" ]] || { echo "hash do artefato diverge" >&2; exit 3; }
TARGET_DB="${FIELDNODE_RESTORE_DATABASE:-}"
[[ -n "$TARGET_DB" && "$TARGET_DB" =~ ^[A-Za-z0-9_]+$ ]] || { echo "FIELDNODE_RESTORE_DATABASE explicito e obrigatorio" >&2; exit 2; }
[[ "${FIELDNODE_RESTORE_CONFIRM:-}" == "RESTORE_TEST_${TARGET_DB}" ]] || { echo "confirmacao ausente para banco de teste" >&2; exit 2; }
tmp="$(mktemp -d "${TMPDIR:-/tmp}/fieldnode-restore.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
umask 077
echo "restore_started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ) target_database=$TARGET_DB"
openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 -in "$BACKUP" -out "$tmp/dump.sql.gz" -pass "file:${PASSPHRASE_FILE}"
gzip -t "$tmp/dump.sql.gz"
gzip -dc "$tmp/dump.sql.gz" | docker compose -f "$COMPOSE_FILE" exec -T -e FIELDNODE_RESTORE_DATABASE="$TARGET_DB" db sh -c 'MYSQL_PWD="$DB_PASSWORD" mysql --database="$FIELDNODE_RESTORE_DATABASE"'
echo "restore_finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ) result=completed target_database=$TARGET_DB"
