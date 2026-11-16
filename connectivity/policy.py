from __future__ import annotations

from copy import deepcopy
from typing import Any

POLICY_VERSION = "1"
POLICY: dict[str, Any] = {
    "version": POLICY_VERSION,
    "classes": {
        "A": {"order": ["http", "mqtt", "lora", "sat_sim"], "ttl_s": None, "max_cost_day": 5.0},
        "B": {"order": ["http", "mqtt", "mule"], "ttl_s": 259200, "batch_s": 60},
        "C": {"order": ["http", "mule"], "ttl_s": 1209600, "batch_s": 900, "aggregate": True},
    },
}


def load_policy(value: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a copy so a test/configuration cannot mutate the global policy."""
    selected = value if value is not None else POLICY
    if not selected.get("version") or not isinstance(selected.get("classes"), dict):
        raise ValueError("política de conectividade inválida")
    return deepcopy(selected)
