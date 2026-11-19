"""Creation of auditable, causally ordered domain changes."""

import hashlib
import json

from api_tcc.models import DomainChange
from api_tcc.services.hlc import clock


def canonical_hash(payload: object) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(raw).hexdigest()


def record_domain_change(*, entity: str, entity_id: object, op: str, payload: dict) -> DomainChange:
    hlc_l, hlc_c, node_id = clock().now()
    return DomainChange.objects.create(
        node_id=node_id,
        hlc_l=hlc_l,
        hlc_c=hlc_c,
        entity=entity,
        entity_id=str(entity_id),
        op=op,
        payload_hash=canonical_hash(payload),
        payload=payload,
    )
