"""Hybrid logical clock and deterministic identities for replicated facts."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone

from django.conf import settings


FIELDNODE_NAMESPACE = uuid.UUID("6f1d2b1e-0000-4000-8000-00000000f1e1")
EVENT_WINDOW_MINUTES = 15


@dataclass
class HLC:
    node: str
    l: int = 0
    c: int = 0

    def now(self) -> tuple[int, int, str]:
        physical = int(time.time() * 1000)
        if physical > self.l:
            self.l, self.c = physical, 0
        else:
            self.c += 1
        return self.l, self.c, self.node

    def update(self, remote: tuple[int, int, str]) -> tuple[int, int, str]:
        remote_l, remote_c, _ = remote
        physical = int(time.time() * 1000)
        old_l = self.l
        self.l = max(old_l, remote_l, physical)
        if self.l == old_l and self.l == remote_l:
            self.c = max(self.c, remote_c) + 1
        elif self.l == old_l:
            self.c += 1
        elif self.l == remote_l:
            self.c = remote_c + 1
        else:
            self.c = 0
        return self.l, self.c, self.node


_CLOCK = HLC(getattr(settings, "NODE_ID", "") or "cloud")


def clock() -> HLC:
    return _CLOCK


def window_start(value: datetime, minutes: int = EVENT_WINDOW_MINUTES) -> datetime:
    """Round a factual timestamp using the versioned FieldNode window contract."""
    value = value.astimezone(dt_timezone.utc)
    minute = value.minute - (value.minute % minutes)
    return value.replace(minute=minute, second=0, microsecond=0)


def event_id(machine_id: object, regra: str, inicio_janela: datetime) -> uuid.UUID:
    return uuid.uuid5(
        FIELDNODE_NAMESPACE,
        f"{machine_id}|{regra}|{window_start(inicio_janela):%Y%m%dT%H%M}",
    )


def decision_id(event: object, regra: str) -> uuid.UUID:
    return uuid.uuid5(FIELDNODE_NAMESPACE, f"decision|{event}|{regra}")
