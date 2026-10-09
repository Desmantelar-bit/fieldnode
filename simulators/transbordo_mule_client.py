#!/usr/bin/env python3
"""PoC de transporte offline-first entre uma colhedora e a sede.

O encontro entre os simuladores é uma chamada Python. Isso prova o fluxo de
software, não rádio, proximidade física ou comunicação entre ESP32.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sqlite3
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import requests

try:
    from .edge_client import PRIORITIES, STATUS_PENDING, STATUS_SENDING, EdgeBuffer, canonical_json, utc_now
except ImportError:  # execução direta: python simulators/transbordo_mule_client.py
    from edge_client import PRIORITIES, STATUS_PENDING, STATUS_SENDING, EdgeBuffer, canonical_json, utc_now

LOGGER = logging.getLogger("fieldnode.transbordo_mule")
STATUS_SYNCED = "SINCRONIZADA"
STATUS_CONFLICT = "CONFLITO"


def _hash_payload(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


class MuleBuffer:
    """Buffer SQLite independente da outbox da colhedora."""

    def __init__(self, path: str | Path, transport_id: str = "transbordo-bench-01") -> None:
        self.path = Path(path)
        self.transport_id = transport_id
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA busy_timeout = 5000")
        self._create_schema()
        self._recover_in_flight()

    def close(self) -> None:
        self.connection.close()

    def _create_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS mule_buffer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,
                payload TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                priority_class TEXT NOT NULL CHECK (priority_class IN ('A', 'B', 'C')),
                transport_id TEXT NOT NULL,
                collection_status TEXT NOT NULL DEFAULT 'COLETADA',
                sync_status TEXT NOT NULL,
                collected_at TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_attempt_at TEXT,
                last_error TEXT,
                UNIQUE (device_id, message_id)
            );
            CREATE INDEX IF NOT EXISTS idx_mule_dispatch
                ON mule_buffer (sync_status, priority_class, sequence_number);
            CREATE TABLE IF NOT EXISTS mule_cursor (
                device_id TEXT PRIMARY KEY,
                last_acked_sequence INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        columns = {row[1] for row in self.connection.execute("PRAGMA table_info(mule_buffer)")}
        if "transport_id" not in columns:
            self.connection.execute(
                "ALTER TABLE mule_buffer ADD COLUMN transport_id TEXT NOT NULL DEFAULT 'unknown-transport'"
            )
        self.connection.commit()

    def _recover_in_flight(self) -> None:
        self.connection.execute(
            "UPDATE mule_buffer SET sync_status = ? WHERE sync_status = ?",
            (STATUS_PENDING, STATUS_SENDING),
        )
        self.connection.commit()

    def collect(self, rows: list[sqlite3.Row]) -> tuple[int, int]:
        """Persiste cópias idempotentes e falha explicitamente em conflito."""
        collected = 0
        already_known = 0
        for row in rows:
            payload = json.loads(str(row["payload"]))
            expected_hash = str(row["payload_hash"])
            if _hash_payload(payload) != expected_hash:
                raise ValueError(f"payload_hash inválido para {row['message_id']}")
            if str(payload.get("device_id")) != str(row["device_id"]):
                raise ValueError(f"device_id divergente para {row['message_id']}")
            if str(payload.get("message_id")) != str(row["message_id"]):
                raise ValueError(f"message_id divergente para {row['message_id']}")
            existing = self.connection.execute(
                "SELECT payload_hash FROM mule_buffer WHERE device_id = ? AND message_id = ?",
                (row["device_id"], row["message_id"]),
            ).fetchone()
            if existing:
                if str(existing["payload_hash"]) != expected_hash:
                    self.connection.execute(
                        "UPDATE mule_buffer SET collection_status = ?, last_error = ? "
                        "WHERE device_id = ? AND message_id = ?",
                        (STATUS_CONFLICT, "hash conflitante; cópia existente preservada",
                         row["device_id"], row["message_id"]),
                    )
                    self.connection.commit()
                    raise ValueError(f"hash conflitante para {row['message_id']}")
                already_known += 1
                continue
            self.connection.execute(
                """INSERT INTO mule_buffer
                (device_id, message_id, sequence_number, payload, payload_hash,
                 priority_class, transport_id, collection_status, sync_status, collected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'COLETADA', ?, ?)""",
                (row["device_id"], row["message_id"], row["sequence_number"],
                 row["payload"], expected_hash, row["priority_class"],
                 self.transport_id, STATUS_PENDING, utc_now()),
            )
            collected += 1
        self.connection.commit()
        return collected, already_known

    def pending(self) -> list[sqlite3.Row]:
        rows: list[sqlite3.Row] = []
        for priority in PRIORITIES:
            rows.extend(self.connection.execute(
                """SELECT * FROM mule_buffer
                WHERE sync_status = ? AND collection_status = 'COLETADA'
                  AND priority_class = ? ORDER BY sequence_number ASC""",
                (STATUS_PENDING, priority),
            ).fetchall())
        return rows

    def mark_sending(self, row_id: int) -> None:
        self.connection.execute(
            "UPDATE mule_buffer SET sync_status = ?, attempts = attempts + 1, last_attempt_at = ? WHERE id = ?",
            (STATUS_SENDING, utc_now(), row_id),
        )
        self.connection.commit()

    def mark_retryable(self, row_id: int, reason: str) -> None:
        self.connection.execute(
            "UPDATE mule_buffer SET sync_status = ?, last_error = ? WHERE id = ?",
            (STATUS_PENDING, reason[:1000], row_id),
        )
        self.connection.commit()

    def mark_error(self, row_id: int, reason: str) -> None:
        self.connection.execute(
            "UPDATE mule_buffer SET sync_status = 'ERRO', last_error = ? WHERE id = ?",
            (reason[:1000], row_id),
        )
        self.connection.commit()

    def mark_synced(self, row: sqlite3.Row) -> int:
        with self.connection:
            self.connection.execute(
                "UPDATE mule_buffer SET sync_status = ?, last_error = NULL WHERE id = ?",
                (STATUS_SYNCED, row["id"]),
            )
            cursor = self.connection.execute(
                "SELECT last_acked_sequence FROM mule_cursor WHERE device_id = ?",
                (row["device_id"],),
            ).fetchone()
            current = int(cursor["last_acked_sequence"]) if cursor else 0
            while self.connection.execute(
                """SELECT 1 FROM mule_buffer WHERE device_id = ? AND sequence_number = ?
                   AND sync_status = ?""",
                (row["device_id"], current + 1, STATUS_SYNCED),
            ).fetchone():
                current += 1
            self.connection.execute(
                """INSERT INTO mule_cursor(device_id, last_acked_sequence) VALUES (?, ?)
                ON CONFLICT(device_id) DO UPDATE SET last_acked_sequence = excluded.last_acked_sequence""",
                (row["device_id"], current),
            )
            return current

    def counts(self) -> dict[str, int]:
        rows = self.connection.execute(
            "SELECT sync_status, COUNT(*) AS count FROM mule_buffer GROUP BY sync_status"
        ).fetchall()
        return {str(row["sync_status"]): int(row["count"]) for row in rows}


class MuleClient:
    def __init__(self, buffer: MuleBuffer, api_url: str, api_key: str, *, timeout: float = 10.0,
                 max_attempts: int = 5, backoff_base: float = 2.0, backoff_max: float = 60.0,
                 session: Any | None = None, sleep: Callable[[float], None] = time.sleep) -> None:
        self.buffer = buffer
        self.api_url = api_url.rstrip("/") + "/"
        self.api_key = api_key
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.session = session or requests.Session()
        self.sleep = sleep

    def synchronize(self) -> int:
        synced = 0
        for row in self.buffer.pending():
            if int(row["attempts"]) >= self.max_attempts:
                self.buffer.mark_error(int(row["id"]), "MAX_ATTEMPTS atingido")
                continue
            if self._send(row):
                synced += 1
        return synced

    def _send(self, row: sqlite3.Row) -> bool:
        row_id = int(row["id"])
        self.buffer.mark_sending(row_id)
        try:
            response = self.session.post(
                self.api_url, json=json.loads(str(row["payload"])),
                headers={"X-API-Key": self.api_key, "Content-Type": "application/json"},
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            return self._retry(row, f"{type(exc).__name__}: {exc}")
        if response.status_code == 429 or response.status_code >= 500:
            return self._retry(row, f"HTTP {response.status_code}")
        if response.status_code in (401, 403):
            self.buffer.mark_error(row_id, f"authentication failure HTTP {response.status_code}")
            return False
        if response.status_code < 200 or response.status_code >= 300:
            self.buffer.mark_error(row_id, f"permanent HTTP {response.status_code}")
            return False
        try:
            body = response.json()
        except (ValueError, json.JSONDecodeError) as exc:
            self.buffer.mark_error(row_id, f"ACK JSON inválido: {exc}")
            return False
        if body.get("payload_hash") != row["payload_hash"] or body.get("message_id") != row["message_id"]:
            self.buffer.mark_error(row_id, "ACK não corresponde à mensagem enviada")
            return False
        cursor = self.buffer.mark_synced(row)
        LOGGER.info("ACK device=%s seq=%s cursor_contiguo=%d", row["device_id"], row["sequence_number"], cursor)
        return True

    def _retry(self, row: sqlite3.Row, reason: str) -> bool:
        attempt = int(row["attempts"])
        if attempt >= self.max_attempts:
            self.buffer.mark_error(int(row["id"]), f"{reason}; MAX_ATTEMPTS atingido")
            return False
        self.buffer.mark_retryable(int(row["id"]), reason)
        delay = min(self.backoff_max, self.backoff_base * (2 ** max(attempt - 1, 0)))
        if delay > 0:
            self.sleep(delay)
        return False


def collect_from_harvester(harvester: EdgeBuffer, mule: MuleBuffer) -> tuple[int, int]:
    """Simula o encontro lógico sem expor a conexão SQLite da colhedora."""
    return mule.collect(harvester.transfer_candidates())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device-id", default=os.getenv("DEVICE_ID", "colhedora-bench-01"))
    parser.add_argument("--count", type=int, default=0)
    parser.add_argument("--edge-buffer-path", default="simulators/edge_buffer.db")
    parser.add_argument("--mule-buffer-path", default="simulators/transbordo_mule_buffer.db")
    parser.add_argument("--transport-id", default=os.getenv("TRANSPORT_ID", "transbordo-bench-01"))
    parser.add_argument("--api-url", default=os.getenv("FIELDNODE_API_URL", "http://127.0.0.1:8000/api") + "/telemetria/")
    parser.add_argument("--api-key", default=os.getenv("FIELDNODE_API_KEY", ""))
    parser.add_argument("--offline", action="store_true", help="coleta sem conectar ao backend")
    parser.add_argument("--repeat-encounter", action="store_true")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--max-attempts", type=int, default=5)
    return parser


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = build_parser().parse_args()
    if args.count < 0 or args.max_attempts < 1:
        raise SystemExit("--count e --max-attempts devem ser válidos")
    harvester = EdgeBuffer(args.edge_buffer_path, args.device_id)
    mule = MuleBuffer(args.mule_buffer_path, args.transport_id)
    try:
        if args.count:
            try:
                from .edge_client import generate_payload
            except ImportError:
                from edge_client import generate_payload
            for index in range(args.count):
                harvester.enqueue(generate_payload(args.device_id, harvester.next_sequence(), index, source="data_mule"))
            LOGGER.info("[COLHEDORA] %d leituras persistidas localmente", args.count)
            LOGGER.info("[COLHEDORA] sincronização direta desativada para o cenário")
        collected, known = collect_from_harvester(harvester, mule)
        LOGGER.info("[DATA MULE] %d leituras coletadas; %d já conhecidas", collected, known)
        if args.repeat_encounter:
            collected, _ = collect_from_harvester(harvester, mule)
            LOGGER.info("[DATA MULE] encontro repetido: %d novas mensagens", collected)
        if not args.offline:
            if not args.api_key:
                raise SystemExit("FIELDNODE_API_KEY/--api-key é obrigatório para sincronizar")
            synced = MuleClient(mule, args.api_url, args.api_key, timeout=args.timeout,
                                max_attempts=args.max_attempts).synchronize()
            LOGGER.info("[DATA MULE] %d leituras confirmadas pelo backend", synced)
        LOGGER.info("[DATA MULE] buffer=%s counts=%s", mule.path, mule.counts())
    finally:
        mule.close()
        harvester.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
