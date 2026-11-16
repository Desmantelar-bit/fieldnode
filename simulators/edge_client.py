#!/usr/bin/env python3
"""Gateway de bancada com outbox SQLite persistente.

Cada leitura é gravada antes de qualquer tentativa HTTP. Reenvios preservam
``message_id``, ``sequence_number`` e ``payload_hash``. O cliente é externo ao
Django e depende apenas da biblioteca padrão e de requests.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import logging
import os
import sqlite3
import threading
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from hmac import compare_digest
from pathlib import Path
from typing import Any

import requests

try:
    from simulators.storage_policy import StoragePolicy, StoragePolicyConfig, StorageFullError
except ModuleNotFoundError:  # execução direta: python simulators/edge_client.py
    from storage_policy import StoragePolicy, StoragePolicyConfig, StorageFullError
from api_tcc.sync_contract import validate_sync_envelope

LOGGER = logging.getLogger("fieldnode.edge_client")
STATUS_PENDING = "PENDENTE"
STATUS_SENDING = "ENVIANDO"
STATUS_SYNCED = "SINCRONIZADA"
STATUS_ERROR = "ERRO"
STATUS_BLOCKED = "BLOCKED"
PRIORITIES = ("A", "B", "C")
MAX_BATCH_UNCOMPRESSED_BYTES = 2 * 1024 * 1024
MAX_BATCH_COMPRESSED_BYTES = 512 * 1024


def canonical_json(payload: dict[str, Any]) -> str:
    # Deve permanecer compatível com api_tcc.services.telemetria._computar_payload_hash.
    return json.dumps(payload, sort_keys=True, default=str)


def payload_hash(payload: dict[str, Any]) -> str:
    canonical = dict(payload)
    if canonical.get("message_id"):
        canonical.pop("id", None)
    # ``via`` is mutable transport metadata. It must not change the identity
    # fingerprint when a mule appends another hop.
    canonical.pop("via", None)
    return hashlib.sha256(canonical_json(canonical).encode("utf-8")).hexdigest()


def compress_batch(payloads: list[dict[str, Any]]) -> tuple[bytes, str, dict[str, int]]:
    """Serializa deterministicamente e comprime um lote; hash e do corpo cru."""
    body = canonical_json({"messages": payloads}).encode("utf-8")
    if len(body) > MAX_BATCH_UNCOMPRESSED_BYTES:
        raise ValueError("lote excede o limite descomprimido")
    encoded = gzip.compress(body, mtime=0)
    if len(encoded) > MAX_BATCH_COMPRESSED_BYTES:
        raise ValueError("lote excede o limite comprimido")
    return encoded, hashlib.sha256(body).hexdigest(), {
        "original_bytes": sum(len(canonical_json(item).encode("utf-8")) for item in payloads),
        "serialized_bytes": len(body),
        "compressed_bytes": len(encoded),
        "message_count": len(payloads),
    }


def decompress_batch(encoded: bytes, expected_hash: str, *, max_bytes: int = MAX_BATCH_UNCOMPRESSED_BYTES) -> list[dict[str, Any]]:
    """Valida gzip e hash antes de devolver qualquer item do lote."""
    try:
        body = gzip.decompress(encoded)
    except (OSError, EOFError) as exc:
        raise ValueError("gzip inválido ou truncado") from exc
    if len(body) > max_bytes:
        raise ValueError("expansão gzip excede o limite")
    actual_hash = hashlib.sha256(body).hexdigest()
    if not compare_digest(actual_hash, expected_hash):
        raise ValueError("payload_hash divergente após descompressão")
    decoded = json.loads(body.decode("utf-8"))
    messages = decoded.get("messages") if isinstance(decoded, dict) else None
    if not isinstance(messages, list) or any(not isinstance(item, dict) for item in messages):
        raise ValueError("lote inválido")
    return messages


def classify_priority(payload: dict[str, Any]) -> str:
    """Classifica com os limiares v1 e preserva precedência crítica A."""
    from api_tcc.contracts import classify, classify_combined, transmission_class

    severity = classify_combined([
        classify("temperatura", float(payload["temperatura"])),
        classify("vibracao", float(payload["vibracao"])),
    ])
    return transmission_class(severity, payload.get("evidence_quality", "boa"), payload.get("atrasado", False))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class EdgeBuffer:
    def __init__(self, path: str | Path, device_id: str,
                 *, storage_config: StoragePolicyConfig | None = None) -> None:
        self.path = Path(path)
        self.device_id = device_id
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # The edge export server handles HTTP requests in worker threads.
        # Writes remain serialized by the edge process; allowing this single
        # connection to be read by request threads is required for the demo.
        self.connection = sqlite3.connect(self.path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA busy_timeout = 5000")
        self._create_schema()
        self.storage_policy = StoragePolicy(
            self.connection, self.path, storage_config or StoragePolicyConfig()
        )
        self._recover_in_flight()

    def close(self) -> None:
        self.connection.close()

    def _create_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS outbox (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,
                payload TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                priority_class TEXT NOT NULL CHECK (priority_class IN ('A', 'B', 'C')),
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_attempt_at TEXT,
                last_error TEXT,
                payload_encoding TEXT NOT NULL DEFAULT 'json',
                UNIQUE (device_id, message_id),
                UNIQUE (device_id, sequence_number)
            );
            CREATE INDEX IF NOT EXISTS idx_outbox_dispatch
                ON outbox (status, priority_class, sequence_number);
            CREATE TABLE IF NOT EXISTS edge_cursor (
                device_id TEXT PRIMARY KEY,
                last_acked_sequence INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS edge_acknowledgement (
                device_id TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,
                message_id TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                PRIMARY KEY (device_id, sequence_number),
                UNIQUE (device_id, message_id)
            );
            CREATE TABLE IF NOT EXISTS storage_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                priority_class TEXT NOT NULL,
                message_ids TEXT NOT NULL,
                bytes_affected INTEGER NOT NULL DEFAULT 0,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE (event_type, message_ids)
            );
            CREATE TABLE IF NOT EXISTS c_aggregates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bucket_start TEXT NOT NULL,
                source_device_id TEXT NOT NULL,
                sample_count INTEGER NOT NULL,
                valid_count INTEGER NOT NULL,
                missing_count INTEGER NOT NULL,
                values_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        columns = {row["name"] for row in self.connection.execute("PRAGMA table_info(outbox)")}
        if "payload_encoding" not in columns:
            self.connection.execute("ALTER TABLE outbox ADD COLUMN payload_encoding TEXT NOT NULL DEFAULT 'json'")
        aggregate_columns = {row["name"] for row in self.connection.execute("PRAGMA table_info(c_aggregates)")}
        for name, definition in {
            "bucket_end": "TEXT",
            "boot_id": "TEXT",
            "message_ids_json": "TEXT NOT NULL DEFAULT '[]'",
        }.items():
            if name not in aggregate_columns:
                self.connection.execute(f"ALTER TABLE c_aggregates ADD COLUMN {name} {definition}")
        self.connection.execute(
            "INSERT OR IGNORE INTO edge_cursor(device_id) VALUES (?)", (self.device_id,)
        )
        self.connection.commit()

    def _recover_in_flight(self) -> None:
        self.connection.execute(
            "UPDATE outbox SET status = ? WHERE device_id = ? AND status = ?",
            (STATUS_PENDING, self.device_id, STATUS_SENDING),
        )
        self.connection.commit()

    def next_sequence(self) -> int:
        row = self.connection.execute(
            "SELECT MAX(value) + 1 AS next_sequence FROM ("
            "SELECT last_acked_sequence AS value FROM edge_cursor WHERE device_id = ? "
            "UNION ALL SELECT sequence_number AS value FROM outbox WHERE device_id = ? "
            "UNION ALL SELECT sequence_number AS value FROM edge_acknowledgement WHERE device_id = ?) q",
            (self.device_id, self.device_id, self.device_id),
        ).fetchone()
        return int(row["next_sequence"])

    def enqueue(self, payload: dict[str, Any]) -> int:
        priority = classify_priority(payload)
        payload.setdefault("priority_class", priority)
        self._prepare_storage(priority, payload)
        envelope = dict(payload)
        envelope["payload_hash"] = payload_hash(payload)
        valid, reason = validate_sync_envelope(envelope)
        if not valid:
            raise ValueError(reason)
        encoded, encoding = self._encode_payload(payload, priority)
        with self.connection:
            cursor = self.connection.execute(
                """INSERT INTO outbox
                (device_id, message_id, sequence_number, payload, payload_hash,
                 priority_class, status, created_at, payload_encoding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (self.device_id, str(payload["message_id"]), int(payload["sequence_number"]),
                 encoded, payload_hash(payload),
                 priority, STATUS_PENDING, utc_now(), encoding),
            )
        return int(cursor.lastrowid)

    def _encode_payload(self, payload: dict[str, Any], priority: str) -> tuple[str, str]:
        raw = canonical_json(payload).encode("utf-8")
        if priority == "C" and self.storage_policy.stage() in {"COMPRESS_C", "AGGREGATE_C", "DISCARD_C"}:
            return base64.b64encode(gzip.compress(raw)).decode("ascii"), "gzip+base64"
        return raw.decode("utf-8"), "json"

    def _prepare_storage(self, priority: str, payload: dict[str, Any]) -> None:
        estimate = len(canonical_json(payload).encode("utf-8")) + 512
        stage = self.storage_policy.stage()
        if stage in {"AGGREGATE_C", "DISCARD_C"}:
            self._manage_c_storage(estimate)
        self.storage_policy.require_admission(estimate, priority)

    def _manage_c_storage(self, required_bytes: int) -> None:
        while not self.storage_policy.can_admit(required_bytes, "C"):
            row = self.connection.execute(
                "SELECT *, length(payload) AS size FROM outbox "
                "WHERE device_id = ? AND priority_class = 'C' AND status = ? "
                "ORDER BY sequence_number ASC LIMIT 1",
                (self.device_id, STATUS_PENDING),
            ).fetchone()
            if row is None:
                break
            if self.storage_policy.stage() == "AGGREGATE_C":
                self._aggregate_rows([row])
            else:
                self._discard_rows([row], "storage threshold 98%")

    def _aggregate_rows(self, rows: list[sqlite3.Row]) -> None:
        samples: list[dict[str, Any]] = []
        for row in rows:
            payload = self._decode_row(row)
            samples.append(payload)
        if not samples:
            return
        numeric = {}
        for key in ("temperatura", "vibracao", "rpm"):
            values = [float(item[key]) for item in samples if isinstance(item.get(key), (int, float))]
            if values:
                numeric[key] = {"mean": sum(values) / len(values), "min": min(values),
                                "max": max(values), "n": len(values)}
        ids = [str(row["message_id"]) for row in rows]
        times = [item.get("timestamp", item.get("event_time")) for item in samples
                 if item.get("timestamp", item.get("event_time"))]
        bucket_start = self._bucket_start(times[0] if times else None)
        bucket_end = self._bucket_end(bucket_start)
        boot_ids = {str(item.get("boot_id")) for item in samples if item.get("boot_id")}
        with self.connection:
            self.connection.execute(
                "INSERT INTO c_aggregates "
                "(bucket_start, bucket_end, source_device_id, boot_id, sample_count, valid_count, missing_count, values_json, message_ids_json, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (bucket_start, bucket_end, self.device_id, next(iter(boot_ids)) if len(boot_ids) == 1 else None,
                 len(samples), sum(item["n"] for item in numeric.values()) // max(len(numeric), 1), 0,
                 canonical_json(numeric), json.dumps(ids, sort_keys=True), utc_now()),
            )
            self.connection.executemany("DELETE FROM outbox WHERE id = ?", [(row["id"],) for row in rows])
            self._record_storage_event("aggregate", "C", ids, sum(int(row["size"]) for row in rows),
                                       "storage threshold 95%; aggregate preserves interval and statistics")
        self._compact_storage()

    @staticmethod
    def _bucket_start(value: str | None) -> str:
        if not value:
            return utc_now()[:16] + ":00"
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            parsed = parsed.replace(second=0, microsecond=0)
            parsed = parsed.replace(minute=parsed.minute - parsed.minute % 1)
            return parsed.isoformat()
        except ValueError:
            return utc_now()[:16] + ":00"

    @staticmethod
    def _bucket_end(value: str) -> str:
        parsed = datetime.fromisoformat(value)
        return (parsed + timedelta(seconds=60)).isoformat()

    def _discard_rows(self, rows: list[sqlite3.Row], reason: str) -> None:
        ids = [str(row["message_id"]) for row in rows]
        with self.connection:
            self.connection.executemany("DELETE FROM outbox WHERE id = ?", [(row["id"],) for row in rows])
            self._record_storage_event("discard", "C", ids, sum(int(row["size"]) for row in rows), reason)
        self._compact_storage()

    def _compact_storage(self) -> None:
        """Reclama espaço liberado sem apagar dados ainda pendentes."""
        self.connection.commit()
        self.connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        self.connection.execute("VACUUM")

    def _record_storage_event(self, event_type: str, priority: str, message_ids: list[str],
                              bytes_affected: int, reason: str) -> None:
        self.connection.execute(
            "INSERT OR IGNORE INTO storage_events "
            "(event_type, priority_class, message_ids, bytes_affected, reason, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (event_type, priority, json.dumps(message_ids, sort_keys=True), bytes_affected, reason, utc_now()),
        )

    def _decode_row(self, row: sqlite3.Row) -> dict[str, Any]:
        raw = str(row["payload"])
        if row["payload_encoding"] == "gzip+base64":
            return json.loads(gzip.decompress(base64.b64decode(raw)).decode("utf-8"))
        return json.loads(raw)

    def purge_expired(self, *, reference_time: datetime | None = None) -> dict[str, int]:
        """Expira apenas pendencias com referencia temporal confiavel.

        A classe A nunca e expirada automaticamente. Cada remocao deixa um
        registro compacto em ``storage_events``; payload completo nao vai para
        log nem para a auditoria.
        """
        reference_time = reference_time or datetime.now(timezone.utc)
        expired: dict[str, int] = {priority: 0 for priority in PRIORITIES}
        rows = self.connection.execute(
            "SELECT * FROM outbox WHERE device_id = ? AND status = ? AND priority_class IN ('B', 'C')",
            (self.device_id, STATUS_PENDING),
        ).fetchall()
        for row in rows:
            ttl = self.storage_policy.config.ttl_seconds.get(str(row["priority_class"]))
            if ttl is None:
                continue
            payload = self._decode_row(row)
            if payload.get("time_source", "unsynced") == "unsynced":
                continue
            raw_time = payload.get("event_time", payload.get("timestamp"))
            if not raw_time:
                continue
            try:
                event_time = datetime.fromisoformat(str(raw_time).replace("Z", "+00:00"))
                if event_time.tzinfo is None:
                    event_time = event_time.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if reference_time - event_time <= timedelta(seconds=ttl):
                continue
            with self.connection:
                self.connection.execute("DELETE FROM outbox WHERE id = ?", (row["id"],))
                self._record_storage_event(
                    "discard_ttl", str(row["priority_class"]), [str(row["message_id"])],
                    len(str(row["payload"]).encode("utf-8")),
                    f"TTL expirado; ttl_seconds={ttl}; event_time={event_time.isoformat()}",
                )
            expired[str(row["priority_class"])] += 1
        if sum(expired.values()):
            self._compact_storage()
        return expired

    def storage_status(self) -> dict[str, Any]:
        return {"bytes": self.storage_policy.usage_bytes(), "max_bytes": self.storage_policy.config.max_bytes,
                "occupancy": self.storage_policy.occupancy(), "stage": self.storage_policy.stage()}

    def pending(self) -> list[sqlite3.Row]:
        rows: list[sqlite3.Row] = []
        for priority in PRIORITIES:
            rows.extend(self.connection.execute(
                """SELECT * FROM outbox
                WHERE device_id = ? AND status = ? AND priority_class = ?
                ORDER BY sequence_number ASC""",
                (self.device_id, STATUS_PENDING, priority),
            ).fetchall())
        return rows

    def transfer_candidates(self) -> list[sqlite3.Row]:
        """Retorna cópias persistidas que podem ser levadas por um Data Mule."""
        return self.pending()

    def cursor(self) -> int:
        row = self.connection.execute(
            "SELECT last_acked_sequence FROM edge_cursor WHERE device_id = ?", (self.device_id,)
        ).fetchone()
        return int(row["last_acked_sequence"])

    def _advance_contiguous_cursor(self) -> int:
        current = self.cursor()
        while self.connection.execute("SELECT 1 FROM edge_acknowledgement WHERE device_id = ? AND sequence_number = ?",
                                      (self.device_id, current + 1)).fetchone():
            current += 1
        self.connection.execute(
            "UPDATE edge_cursor SET last_acked_sequence = ? WHERE device_id = ?",
            (current, self.device_id),
        )
        return current

    def mark_sending(self, row_id: int) -> None:
        self.connection.execute(
            "UPDATE outbox SET status = ?, attempts = attempts + 1, last_attempt_at = ? WHERE id = ?",
            (STATUS_SENDING, utc_now(), row_id),
        )
        self.connection.commit()

    def mark_synced(self, row_id: int) -> int:
        with self.connection:
            row = self.connection.execute("SELECT * FROM outbox WHERE id = ?", (row_id,)).fetchone()
            if row is None:
                return self.cursor()
            self.connection.execute(
                "INSERT OR REPLACE INTO edge_acknowledgement(device_id, sequence_number, message_id, payload_hash) VALUES (?, ?, ?, ?)",
                (row["device_id"], row["sequence_number"], row["message_id"], row["payload_hash"]),
            )
            self.connection.execute("DELETE FROM outbox WHERE id = ?", (row_id,))
            return self._advance_contiguous_cursor()

    def apply_backend_ack(self, ack: dict[str, Any]) -> bool:
        """Apply a propagated backend ACK, keeping the same validation as HTTP."""
        if (ack.get("device_id") != self.device_id or ack.get("status") not in {"acked", "duplicate"}):
            return False
        row = self.connection.execute(
            "SELECT id, message_id, sequence_number, payload_hash FROM outbox "
            "WHERE device_id = ? AND message_id = ?",
            (self.device_id, ack.get("message_id")),
        ).fetchone()
        if row is None or ack.get("sequence_number") != row["sequence_number"] or ack.get("payload_hash") != row["payload_hash"]:
            return False
        self.mark_synced(int(row["id"]))
        return True

    def mark_error(self, row_id: int, reason: str) -> None:
        self.connection.execute(
            "UPDATE outbox SET status = ?, last_error = ? WHERE id = ?",
            (STATUS_ERROR, reason[:1000], row_id),
        )
        self.connection.commit()

    def mark_blocked(self, row_id: int, reason: str) -> None:
        self.connection.execute(
            "UPDATE outbox SET status = ?, last_error = ? WHERE id = ?",
            (STATUS_BLOCKED, reason[:1000], row_id),
        )
        self.connection.commit()

    def mark_retryable(self, row_id: int, reason: str) -> None:
        self.connection.execute(
            "UPDATE outbox SET status = ?, last_error = ? WHERE id = ?",
            (STATUS_PENDING, reason[:1000], row_id),
        )
        self.connection.commit()

    def counts(self) -> dict[str, int]:
        rows = self.connection.execute(
            "SELECT status, COUNT(*) AS count FROM outbox WHERE device_id = ? GROUP BY status",
            (self.device_id,),
        ).fetchall()
        return {str(row["status"]): int(row["count"]) for row in rows}


class EdgeClient:
    def __init__(self, buffer: EdgeBuffer, api_url: str, device_key: str, *, timeout: float = 10.0,
                 max_attempts: int | None = 5, backoff_base: float = 2.0, backoff_max: float = 60.0,
                 session: Any | None = None,
                 sleep: Callable[[float], None] = time.sleep,
                 connectivity_manager: Any | None = None) -> None:
        self.buffer = buffer
        self.api_url = api_url.rstrip("/") + "/"
        self.device_key = device_key
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.session = session or requests.Session()
        self.sleep = sleep
        self.connectivity_manager = connectivity_manager

    def synchronize(self, *, stop_on_retryable_failure: bool = False) -> int:
        if self.connectivity_manager is not None:
            return int(self.connectivity_manager.tick().get("acked", 0))
        synced = 0
        for row in self.buffer.pending():
            if self.max_attempts is not None and int(row["attempts"]) >= self.max_attempts:
                self.buffer.mark_error(int(row["id"]), "MAX_ATTEMPTS atingido")
                continue
            if self._send(row):
                synced += 1
            elif stop_on_retryable_failure:
                status = self.buffer.connection.execute(
                    "SELECT status FROM outbox WHERE id = ?", (int(row["id"]),)
                ).fetchone()
                if status and status["status"] == STATUS_PENDING:
                    break
        return synced

    def _send(self, row: sqlite3.Row) -> bool:
        row_id = int(row["id"])
        self.buffer.mark_sending(row_id)
        payload = self.buffer._decode_row(row)
        try:
            response = self.session.post(
                self.api_url, json=payload,
                headers={"X-Device-Id": self.buffer.device_id, "X-Device-Key": self.device_key,
                         "Content-Type": "application/json"},
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            return self._retryable_failure(row, f"{type(exc).__name__}: {exc}")
        if response.status_code in (401, 403):
            self.buffer.mark_error(row_id, f"authentication failure HTTP {response.status_code}")
            return False
        if response.status_code == 429 or response.status_code >= 500:
            return self._retryable_failure(row, f"HTTP {response.status_code}")
        if response.status_code < 200 or (response.status_code >= 300 and response.status_code != 409):
            self.buffer.mark_error(row_id, f"permanent HTTP {response.status_code}")
            return False
        try:
            body = response.json()
        except (ValueError, json.JSONDecodeError) as exc:
            self.buffer.mark_error(row_id, f"ACK JSON inválido: {exc}")
            return False
        if body.get("message_id") != row["message_id"]:
            self.buffer.mark_error(row_id, "message_id divergente no ACK")
            return False
        if body.get("device_id") != row["device_id"]:
            self.buffer.mark_error(row_id, "device_id divergente no ACK")
            return False
        ack_status = body.get("status")
        if ack_status == "conflict":
            self.buffer.mark_blocked(row_id, "conflito de identidade/hash registrado no servidor")
            return False
        if ack_status == "rejected":
            self.buffer.mark_error(row_id, str(body.get("reason", "mensagem rejeitada pelo servidor")))
            return False
        if ack_status not in {"acked", "duplicate"}:
            self.buffer.mark_retryable(row_id, "ACK ausente ou status desconhecido")
            return False
        if body.get("sequence_number") != row["sequence_number"]:
            self.buffer.mark_error(row_id, "sequence_number divergente no ACK")
            return False
        if body.get("payload_hash") != row["payload_hash"]:
            self.buffer.mark_error(row_id, "payload_hash divergente no ACK")
            return False
        cursor = self.buffer.mark_synced(row_id)
        LOGGER.info("ACK device=%s seq=%s cursor_contiguo=%d", row["device_id"], row["sequence_number"], cursor)
        return True

    def _retryable_failure(self, row: sqlite3.Row, reason: str) -> bool:
        attempt_number = int(row["attempts"])
        row_id = int(row["id"])
        if self.max_attempts is not None and attempt_number >= self.max_attempts:
            self.buffer.mark_error(row_id, f"{reason}; MAX_ATTEMPTS atingido")
            return False
        self.buffer.mark_retryable(row_id, reason)
        delay = min(self.backoff_max, self.backoff_base * (2 ** max(attempt_number - 1, 0)))
        if delay > 0:
            self.sleep(delay)
        return False


def generate_payload(device_id: str, sequence_number: int, index: int, *, source: str = "simulador",
                     time_source: str = "gateway", boot_id: str | None = None) -> dict[str, Any]:
    if index % 10 == 0:
        temperature, vibration = 115.0, 2.0
    elif index % 3 == 0:
        temperature, vibration = 80.0, 1.0
    else:
        temperature, vibration = 70.0, 0.5
    payload = {
        "id": str(uuid.uuid4()), "device_id": device_id, "message_id": str(uuid.uuid4()),
        "sequence_number": sequence_number, "maquina_id": device_id,
        "boot_id": boot_id or str(uuid.uuid4()), "uptime_ms": index * 1000,
        "time_source": time_source,
        "temperatura": temperature, "vibracao": vibration, "vibracao_unit": "indice_0_10", "rpm": 1800,
        "source": source, "transport": "http", "schema_version": "1.1",
    }
    if time_source != "unsynced":
        payload["timestamp"] = utc_now()
    return payload


class OfflineSimulator:
    """Simula um ESP32 offline: coleta dados com boot_id e uptime monotônico."""

    def __init__(
        self,
        device_id: str,
        *,
        uptime_start_ms: int = 0,
        time_source: str = "unsynced",
    ) -> None:
        self.device_id = device_id
        self.boot_id: str = str(uuid.uuid4())
        self._uptime_ms: int = uptime_start_ms
        self.time_source: str = time_source

    def reboot(self) -> None:
        self.boot_id = str(uuid.uuid4())
        self._uptime_ms = 0

    def tick(self, ms: int = 5000) -> None:
        self._uptime_ms += ms

    def sync_ntp(self) -> None:
        self.time_source = "ntp"

    def sync_gateway(self) -> None:
        self.time_source = "gateway"

    def go_offline(self) -> None:
        self.time_source = "unsynced"

    @property
    def uptime_ms(self) -> int:
        return self._uptime_ms

    def generate_reading(
        self,
        sequence_number: int,
        *,
        temperatura: float = 72.0,
        vibracao: float = 0.35,
        rpm: int = 1800,
        source: str = "simulador",
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "device_id": self.device_id,
            "maquina_id": self.device_id,
            "message_id": str(uuid.uuid4()),
            "sequence_number": sequence_number,
            "boot_id": self.boot_id,
            "uptime_ms": self._uptime_ms,
            "time_source": self.time_source,
            "temperatura": temperatura,
            "vibracao": vibracao,
            "vibracao_unit": "indice_0_10",
            "rpm": rpm,
            "source": source,
            "transport": "http",
            "schema_version": "1.1",
        }
        if self.time_source != "unsynced":
            payload["timestamp"] = utc_now()
        return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device-id", default=os.getenv("DEVICE_ID", "edge-bench-01"))
    parser.add_argument("--count", type=int, default=0)
    parser.add_argument("--time-source", choices=("rtc", "gateway", "ntp", "unsynced"), default="gateway")
    parser.add_argument("--interval", type=float, default=0.0)
    parser.add_argument("--api-url", default=os.getenv("FIELDNODE_API_URL", "http://127.0.0.1:8000/api") + "/telemetria/")
    parser.add_argument("--device-key", default=os.getenv("FIELDNODE_DEVICE_KEY", ""))
    parser.add_argument("--buffer-path", default="simulators/edge_buffer.db")
    parser.add_argument("--offline", action="store_true", help="gera e persiste sem sincronizar nesta execução")
    parser.add_argument("--sync-only", action="store_true")
    parser.add_argument("--watch", action="store_true", help="gera continuamente e sincroniza com retry durável")
    parser.add_argument("--timeout", type=float, default=float(os.getenv("EDGE_HTTP_TIMEOUT", "10")))
    parser.add_argument("--max-attempts", type=int, default=int(os.getenv("EDGE_MAX_ATTEMPTS", "5")))
    parser.add_argument("--backoff-base", type=float, default=float(os.getenv("EDGE_BACKOFF_BASE", "2")))
    parser.add_argument("--backoff-max", type=float, default=float(os.getenv("EDGE_BACKOFF_MAX", "60")))
    return parser


def build_connectivity_manager(buffer: EdgeBuffer, api_url: str, device_id: str, device_key: str,
                               *, timeout: float, max_attempts: int | None = 5,
                               session: Any | None = None) -> Any:
    """Build the transport layer without exposing provider choices to the loop."""
    try:
        from connectivity.manager import ConnectivityManager
        from connectivity.providers.http import HttpProvider
    except ModuleNotFoundError:  # direct execution from simulators/
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from connectivity.manager import ConnectivityManager
        from connectivity.providers.http import HttpProvider
    return ConnectivityManager(
        buffer,
        [HttpProvider(api_url, device_id, device_key, timeout=timeout, session=session)],
        max_attempts=max_attempts,
    )


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = build_parser().parse_args()
    if args.count < 0 or args.max_attempts < 1:
        raise SystemExit("--count e --max-attempts devem ser válidos")
    if args.watch and (args.interval <= 0 or args.offline or args.sync_only):
        raise SystemExit("--watch exige --interval positivo e não combina com --offline/--sync-only")
    if args.watch and not args.device_key:
        raise SystemExit("FIELDNODE_DEVICE_KEY/--device-key é obrigatório para sincronizar")
    boot_id = str(uuid.uuid4())
    buffer = EdgeBuffer(args.buffer_path, args.device_id)
    try:
        if args.watch:
            client = EdgeClient(
                buffer,
                args.api_url,
                args.device_key,
                timeout=args.timeout,
                max_attempts=None,
                backoff_base=args.backoff_base,
                backoff_max=args.backoff_max,
                connectivity_manager=build_connectivity_manager(
                    buffer, args.api_url, args.device_id, args.device_key, timeout=args.timeout, max_attempts=None
                ),
            )
            index = 0
            LOGGER.info(
                "gateway contínuo ativo device=%s intervalo=%.1fs outbox=%s (Ctrl+C para parar)",
                args.device_id,
                args.interval,
                args.buffer_path,
            )
            sync_worker: threading.Thread | None = None
            try:
                while True:
                    payload = generate_payload(args.device_id, buffer.next_sequence(), index,
                                               time_source=args.time_source, boot_id=boot_id)
                    buffer.enqueue(payload)
                    LOGGER.info(
                        "leitura persistida device=%s seq=%s pendentes=%s",
                        args.device_id,
                        payload["sequence_number"],
                        buffer.counts().get(STATUS_PENDING, 0),
                    )
                    if sync_worker is None or not sync_worker.is_alive():
                        def synchronize_pending() -> None:
                            sync_buffer = EdgeBuffer(args.buffer_path, args.device_id)
                            try:
                                EdgeClient(
                                    sync_buffer,
                                    args.api_url,
                                    args.device_key,
                                    timeout=args.timeout,
                                    max_attempts=None,
                                    backoff_base=args.backoff_base,
                                    backoff_max=args.backoff_max,
                                    connectivity_manager=build_connectivity_manager(
                                        sync_buffer, args.api_url, args.device_id, args.device_key,
                                        timeout=args.timeout, max_attempts=None
                                    ),
                                ).synchronize(stop_on_retryable_failure=True)
                            finally:
                                sync_buffer.close()

                        sync_worker = threading.Thread(
                            target=synchronize_pending,
                            name="fieldnode-outbox-sync",
                            daemon=True,
                        )
                        sync_worker.start()
                    index += 1
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                LOGGER.info("gateway contínuo encerrado pelo operador")
                LOGGER.info(
                    "outbox device=%s cursor_contiguo=%d counts=%s",
                    args.device_id,
                    buffer.cursor(),
                    buffer.counts(),
                )
                return 0
        if not args.sync_only:
            for index in range(args.count):
                buffer.enqueue(generate_payload(args.device_id, buffer.next_sequence(), index,
                                                 time_source=args.time_source, boot_id=boot_id))
                if args.interval > 0:
                    time.sleep(args.interval)
        if not args.offline:
            if not args.device_key:
                raise SystemExit("FIELDNODE_DEVICE_KEY/--device-key é obrigatório para sincronizar")
            EdgeClient(buffer, args.api_url, args.device_key, timeout=args.timeout,
                       max_attempts=args.max_attempts, backoff_base=args.backoff_base,
                       backoff_max=args.backoff_max,
                       connectivity_manager=build_connectivity_manager(
                           buffer, args.api_url, args.device_id, args.device_key,
                           timeout=args.timeout, max_attempts=args.max_attempts
                       )).synchronize()
        LOGGER.info("outbox device=%s cursor_contiguo=%d counts=%s", args.device_id, buffer.cursor(), buffer.counts())
    finally:
        buffer.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
