"""Message signing helpers for the store-and-forward protocol.

The mule is deliberately not a signer.  It may add transport-only ``via``
metadata, but it cannot change the origin fields covered by the signature.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


SIGNATURE_ALGORITHM = "HMAC-SHA256"
TRANSPORT_ONLY_FIELDS = {"via"}
SIGNATURE_FIELDS = {"signature", "signature_alg"}


def _canonical_signed_body(payload: dict[str, Any]) -> bytes:
    body = {
        key: value
        for key, value in payload.items()
        if key not in SIGNATURE_FIELDS | TRANSPORT_ONLY_FIELDS
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def sign_payload(payload: dict[str, Any], secret: str) -> dict[str, Any]:
    if not secret:
        raise ValueError("segredo de assinatura ausente")
    signed = dict(payload)
    signed["signature_alg"] = SIGNATURE_ALGORITHM
    signed["signature"] = hmac.new(
        secret.encode("utf-8"), _canonical_signed_body(signed), hashlib.sha256
    ).hexdigest()
    return signed


def verify_payload(payload: dict[str, Any], secret: str) -> bool:
    if not secret or payload.get("signature_alg") != SIGNATURE_ALGORITHM:
        return False
    supplied = str(payload.get("signature") or "")
    expected = hmac.new(
        secret.encode("utf-8"), _canonical_signed_body(payload), hashlib.sha256
    ).hexdigest()
    return bool(supplied) and hmac.compare_digest(supplied, expected)
