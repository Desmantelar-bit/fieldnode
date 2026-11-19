#!/usr/bin/env bash
set -Eeuo pipefail

OUT_DIR="${FIELDNODE_IMAGE_DIR:-./release-artifacts/docker-images}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
mkdir -p "$OUT_DIR"
command -v docker >/dev/null 2>&1 || { echo "Docker não encontrado" >&2; exit 2; }
docker info >/dev/null 2>&1 || { echo "Docker não está disponível" >&2; exit 2; }

mapfile -t images < <(docker compose -f "$COMPOSE_FILE" images | awk 'NR > 1 && $2 != "" && $3 != "" {print $2 ":" $3}' | awk 'NF && !seen[$0]++')
(( ${#images[@]} > 0 )) || { echo "nenhuma imagem Compose encontrada" >&2; exit 3; }
manifest="$OUT_DIR/manifest.txt"
{
  echo "created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "compose_file=$COMPOSE_FILE"
  for image in "${images[@]}"; do
    safe="${image//\//_}"; safe="${safe//:/_}"
    archive="$OUT_DIR/${safe}.tar"
    docker image inspect "$image" >/dev/null
    docker save --output "$archive" "$image"
    sha256sum "$archive"
    echo "image=$image archive=$(basename "$archive")"
  done
} | tee "$manifest"
echo "exportação concluída: $OUT_DIR"
