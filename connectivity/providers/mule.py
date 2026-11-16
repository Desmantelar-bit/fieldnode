from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Callable


class MuleProvider:
    """Logical adapter; network transport remains outside S7-T1."""
    name = "mule"

    def __init__(self, sender: Callable[[list[Mapping[str, Any]]], list[dict[str, Any]]], *, available: bool = True,
                 max_bytes: int = 512 * 1024) -> None:
        self._sender, self._available, self._max_bytes = sender, available, max_bytes

    def available(self) -> bool:
        return self._available

    def max_payload_bytes(self) -> int:
        return self._max_bytes

    def cost_per_msg(self) -> float:
        return 0.0

    def send(self, batch: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return self._sender(batch)
