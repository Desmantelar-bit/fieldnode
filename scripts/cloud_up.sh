#!/usr/bin/env bash
set -u
if [ -z "${FIELDNODE_CLOUD_PROVIDER:-}" ] || [ -z "${FIELDNODE_CLOUD_TARGET:-}" ]; then
  echo 'cloud-up bloqueado: D-26/provedor e destino de nuvem ainda não estão definidos.' >&2
  exit 2
fi
echo 'cloud-up ainda não possui um adaptador implementado para o provedor definido.' >&2
exit 3
