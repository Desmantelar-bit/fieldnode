"""Validação leve do envelope Sync Protocol v1 sem dependência externa.

O JSON Schema em ``contracts/sync.v1.json`` é a fonte compartilhada para
clientes e firmware. Esta função cobre as invariantes que o runtime precisa
enforçar mesmo quando ``jsonschema`` não está instalado no edge.
"""

from __future__ import annotations

import re
from typing import Any

HASH_RE = re.compile(r"^[a-fA-F0-9]{64}$")
PRIORITIES = {"A", "B", "C"}


def validate_sync_envelope(payload: dict[str, Any]) -> tuple[bool, str]:
    required = ("device_id", "message_id", "sequence_number", "payload_hash", "schema_version")
    missing = [field for field in required if field not in payload]
    if missing:
        return False, f"campos ausentes no envelope Sync v1: {', '.join(missing)}"
    if not isinstance(payload["device_id"], str) or not payload["device_id"].strip():
        return False, "device_id deve ser texto não vazio"
    if not isinstance(payload["message_id"], str) or not payload["message_id"].strip():
        return False, "message_id deve ser texto não vazio"
    if isinstance(payload["sequence_number"], bool) or not isinstance(payload["sequence_number"], int) or payload["sequence_number"] < 1:
        return False, "sequence_number deve ser inteiro positivo"
    if not isinstance(payload["schema_version"], str) or not payload["schema_version"].strip():
        return False, "schema_version deve ser texto não vazio"
    if not isinstance(payload["payload_hash"], str) or not HASH_RE.fullmatch(payload["payload_hash"]):
        return False, "payload_hash deve ser SHA-256 hexadecimal"
    priority = payload.get("priority_class", payload.get("priority"))
    if priority not in PRIORITIES:
        return False, "priority_class deve ser A, B ou C"
    encoding = payload.get("encoding", "json")
    if encoding not in {"json", "gzip+base64"}:
        return False, "encoding Sync v1 inválido"
    return True, ""
