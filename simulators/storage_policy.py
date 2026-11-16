"""Política de capacidade e retenção do outbox SQLite.

O módulo mede o arquivo persistente real, incluindo WAL/SHM quando presentes.
Os limites são relativos a ``max_bytes`` injetado pelo simulador ou ao limite
físico informado pelo operador. Não há promessa de preservação quando o
armazenamento reservado já foi consumido: nesse caso a gravação falha de forma
explícita.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path


class StorageFullError(RuntimeError):
    """A mensagem não pôde ser persistida sem violar a política."""


@dataclass(frozen=True)
class StoragePolicyConfig:
    max_bytes: int | None = None
    reserve_bytes: int = 0
    compress_threshold: float = 0.90
    aggregate_threshold: float = 0.95
    discard_threshold: float = 0.98
    ttl_seconds: dict[str, int | None] = field(
        default_factory=lambda: {"A": None, "B": 72 * 3600, "C": 14 * 24 * 3600}
    )

    def __post_init__(self) -> None:
        if self.max_bytes is not None and self.max_bytes <= 0:
            raise ValueError("max_bytes deve ser positivo")
        if self.reserve_bytes < 0:
            raise ValueError("reserve_bytes não pode ser negativo")
        if not 0 < self.compress_threshold < self.aggregate_threshold < self.discard_threshold <= 1:
            raise ValueError("limiares devem obedecer 0 < compressão < agregação < descarte <= 1")
        if set(self.ttl_seconds) - {"A", "B", "C"}:
            raise ValueError("ttl_seconds aceita apenas classes A, B e C")
        if any(value is not None and value < 0 for value in self.ttl_seconds.values()):
            raise ValueError("TTL deve ser não negativo ou None")


class StoragePolicy:
    def __init__(self, connection: sqlite3.Connection, db_path: Path,
                 config: StoragePolicyConfig) -> None:
        self.connection = connection
        self.db_path = Path(db_path)
        self.config = config

    def usage_bytes(self) -> int:
        """Retorna o espaço ocupado pelo banco e seus arquivos auxiliares."""
        paths = (self.db_path, Path(f"{self.db_path}-wal"), Path(f"{self.db_path}-shm"))
        return sum(path.stat().st_size for path in paths if path.exists())

    def occupancy(self) -> float | None:
        if self.config.max_bytes is None:
            return None
        return self.usage_bytes() / self.config.max_bytes

    def stage(self) -> str:
        occupancy = self.occupancy()
        if occupancy is None:
            return "UNLIMITED"
        if occupancy >= self.config.discard_threshold:
            return "DISCARD_C"
        if occupancy >= self.config.aggregate_threshold:
            return "AGGREGATE_C"
        if occupancy >= self.config.compress_threshold:
            return "COMPRESS_C"
        return "NORMAL"

    def can_admit(self, estimated_bytes: int, priority: str) -> bool:
        """Respeita a reserva: A/B não consomem o espaço protegido de reserva."""
        if estimated_bytes < 0:
            raise ValueError("estimated_bytes não pode ser negativo")
        if self.config.max_bytes is None:
            return True
        available = self.config.max_bytes - self.usage_bytes()
        protected = 0 if priority in {"A", "B"} else self.config.reserve_bytes
        return available - protected >= estimated_bytes

    def require_admission(self, estimated_bytes: int, priority: str) -> None:
        if not self.can_admit(estimated_bytes, priority):
            raise StorageFullError(
                f"armazenamento insuficiente para classe {priority}; "
                f"stage={self.stage()} usage={self.usage_bytes()} max={self.config.max_bytes}"
            )
