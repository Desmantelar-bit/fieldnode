from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, TypedDict


Envelope = Mapping[str, Any]


class Ack(TypedDict, total=False):
    message_id: str
    device_id: str
    sequence_number: int
    payload_hash: str
    status: str
    error: str
    attempted: bool
    charged: bool


class ConnectivityProvider(Protocol):
    name: str

    def available(self) -> bool: ...

    def max_payload_bytes(self) -> int: ...

    def cost_per_msg(self) -> float | None: ...

    def send(self, batch: list[Envelope]) -> list[Ack]: ...
