#!/usr/bin/env python3
"""Gateway de bancada com outbox SQLite persistente.

Cada leitura é gravada antes de qualquer tentativa HTTP. Reenvios preservam
``message_id``, ``sequence_number`` e ``payload_hash``. O cliente é externo ao
Django e depende apenas da biblioteca padrão e de requests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sqlite3
import threading
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from api_tcc.contracts import classify, transmission_class

LOGGER = logging.getLogger("fieldnode.edge_client")
STATUS_PENDING = "PENDENTE"
STATUS_SENDING = "ENVIANDO"
STATUS_SYNCED = "SINCRONIZADA"
STATUS_ERROR = "ERRO"
STATUS_BLOCKED = "BLOQUEADA"  # conflict de hash: requer investigação manual
PRIORITIES = ("A", "B", "C")


def canonical_json(payload: dict[str, Any]) -> str:
    # Deve permanecer compatível com api_tcc.services.telemetria._computar_payload_hash.
    return json.dumps(payload, sort_keys=True, default=str)


def payload_hash(payload: dict[str, Any]) -> str:
    logical_payload = {key: value for key, value in payload.items() if key != "id"}
    return hashlib.sha256(canonical_json(logical_payload).encode("utf-8")).hexdigest()


def classify_priority(payload: dict[str, Any]) -> str:
    """Prioridade derivada do contrato v1; hardware real continua em v0."""
    severities = {
        "NORMAL": 0,
        "ATENCAO": 1,
        "CRITICO": 2,
    }
    severidade = max(
        classify("temperatura", float(payload["temperatura"])),
        classify("vibracao", float(payload["vibracao"])),
        key=severities.__getitem__,
    )
    return transmission_class(
        severidade,
        payload.get("evidence_quality", "boa"),
        payload.get("atrasado", False),
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class EdgeBuffer:
    def __init__(self, path: str | Path, device_id: str) -> None:
        self.path = Path(path)
        self.device_id = device_id
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
                UNIQUE (device_id, message_id),
                UNIQUE (device_id, sequence_number)
            );
            CREATE INDEX IF NOT EXISTS idx_outbox_dispatch
                ON outbox (status, priority_class, sequence_number);
            CREATE TABLE IF NOT EXISTS edge_cursor (
                device_id TEXT PRIMARY KEY,
                last_acked_sequence INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        self.connection.execute(
            "INSERT OR IGNORE INTO edge_cursor(device_id) VALUES (?)", (self.device_id,)
        )
        self.connection.commit()

    def _recover_in_flight(self) -> None:
        """Restaura mensagens que estavam ENVIANDO para PENDENTE após reinicialização."""
        self.connection.execute(
            "UPDATE outbox SET status = ? WHERE device_id = ? AND status = ?",
            (STATUS_PENDING, self.device_id, STATUS_SENDING),
        )
        self.connection.commit()

    def mark_blocked(self, row_id: int, reason: str) -> None:
        """Bloqueia item com status conflict: requer investigação manual.

        Um item BLOQUEADA não é retryable automaticamente, não avança o cursor
        contíguo e não pode ser removido da outbox sem intervenção explícita.
        O payload original é preservado para auditoria.
        """
        self.connection.execute(
            "UPDATE outbox SET status = ?, last_error = ? WHERE id = ?",
            (STATUS_BLOCKED, reason[:1000], row_id),
        )
        self.connection.commit()

    def next_sequence(self) -> int:
        row = self.connection.execute(
            "SELECT COALESCE(MAX(sequence_number), 0) + 1 AS next_sequence "
            "FROM outbox WHERE device_id = ?", (self.device_id,)
        ).fetchone()
        return int(row["next_sequence"])

    def enqueue(self, payload: dict[str, Any]) -> int:
        encoded = canonical_json(payload)
        with self.connection:
            cursor = self.connection.execute(
                """INSERT INTO outbox
                (device_id, message_id, sequence_number, payload, payload_hash,
                 priority_class, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    self.device_id,
                    str(payload["message_id"]),
                    int(payload["sequence_number"]),
                    encoded,
                    payload_hash(payload),
                    classify_priority(payload),
                    STATUS_PENDING,
                    utc_now(),
                ),
            )
        return int(cursor.lastrowid)

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
        while self.connection.execute(
            "SELECT 1 FROM outbox WHERE device_id = ? AND sequence_number = ? AND status = ?",
            (self.device_id, current + 1, STATUS_SYNCED),
        ).fetchone():
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
            self.connection.execute(
                "UPDATE outbox SET status = ?, last_error = NULL WHERE id = ?",
                (STATUS_SYNCED, row_id),
            )
            return self._advance_contiguous_cursor()

    def mark_error(self, row_id: int, reason: str) -> None:
        self.connection.execute(
            "UPDATE outbox SET status = ?, last_error = ? WHERE id = ?",
            (STATUS_ERROR, reason[:1000], row_id),
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
    def __init__(self, buffer: EdgeBuffer, api_url: str, api_key: str, *, timeout: float = 10.0,
                 max_attempts: int | None = 5, backoff_base: float = 2.0, backoff_max: float = 60.0,
                 session: Any | None = None,
                 sleep: Callable[[float], None] = time.sleep) -> None:
        self.buffer = buffer
        self.api_url = api_url.rstrip("/") + "/"
        self.api_key = api_key
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.session = session or requests.Session()
        self.sleep = sleep

    def synchronize(self, *, stop_on_retryable_failure: bool = False) -> int:
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
        payload = json.loads(str(row["payload"]))
        try:
            response = self.session.post(
                self.api_url, json=payload,
                headers={"X-API-Key": self.api_key, "Content-Type": "application/json"},
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            return self._retryable_failure(row, f"{type(exc).__name__}: {exc}")
        if response.status_code in (401, 403):
            self.buffer.mark_error(row_id, f"authentication failure HTTP {response.status_code}")
            return False
        if response.status_code == 429 or response.status_code >= 500:
            return self._retryable_failure(row, f"HTTP {response.status_code}")
        # HTTP 409 = conflict: mesmo (device_id, message_id) com hash diferente
        if response.status_code == 409:
            try:
                body_409 = response.json()
                ack_409 = body_409.get("ack", {})
            except (ValueError, json.JSONDecodeError):
                ack_409 = {}
            reason = (
                f"conflict HTTP 409: mesmo message_id com payload diferente "
                f"(hash_enviado={payload_hash(payload)[:16]}...)"
            )
            self.buffer.mark_blocked(row_id, reason)
            LOGGER.warning(
                "Conflito de hash (HTTP 409): device=%s msg=%s — item bloqueado para investigação",
                row["device_id"],
                row["message_id"],
            )
            return False
        if response.status_code < 200 or response.status_code >= 300:
            self.buffer.mark_error(row_id, f"permanent HTTP {response.status_code}")
            return False
        try:
            body = response.json()
        except (ValueError, json.JSONDecodeError) as exc:
            self.buffer.mark_error(row_id, f"ACK JSON inválido: {exc}")
            return False
        ack = body.get("ack")
        if not isinstance(ack, dict) or ack.get("status") not in {"acked", "duplicate"}:
            # Verificar se é um conflito de hash explícito do servidor
            if isinstance(ack, dict) and ack.get("status") == "conflict":
                reason = (
                    f"conflict: mesmo message_id com payload diferente no servidor "
                    f"(hash_enviado={payload_hash(payload)[:16]}...)"
                )
                self.buffer.mark_blocked(row_id, reason)
                LOGGER.warning(
                    "Conflito de hash: device=%s msg=%s — item bloqueado para investigação",
                    row["device_id"],
                    row["message_id"],
                )
                return False
            self.buffer.mark_error(row_id, "ACK ausente ou status inválido")
            return False
        if ack.get("payload_hash") != payload_hash(payload):
            self.buffer.mark_error(row_id, "payload_hash divergente no ACK")
            return False
        if ack.get("message_id") != row["message_id"]:
            self.buffer.mark_error(row_id, "message_id divergente no ACK")
            return False
        if ack.get("device_id") != row["device_id"]:
            self.buffer.mark_error(row_id, "device_id divergente no ACK")
            return False
        if ack.get("sequence_number") != int(row["sequence_number"]):
            self.buffer.mark_error(row_id, "sequence_number divergente no ACK")
            return False
        if not isinstance(ack.get("last_acked_sequence"), int) or ack[
            "last_acked_sequence"
        ] < int(row["sequence_number"]):
            self.buffer.mark_error(row_id, "cursor inválido no ACK")
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


def generate_payload(
    device_id: str,
    sequence_number: int,
    index: int,
    *,
    source: str = "simulador",
    boot_id: str | None = None,
    uptime_ms: int | None = None,
    time_source: str = "ntp",
) -> dict[str, Any]:
    """Gera um payload de telemetria com proveniência temporal explícita.

    boot_id + uptime_ms permitem reconstrução temporal offline.
    time_source declara a origem da referência de tempo.
    """
    if index % 10 == 0:
        temperature, vibration = 86.0, 2.0
    elif index % 3 == 0:
        temperature, vibration = 80.0, 1.0
    else:
        temperature, vibration = 70.0, 0.5

    payload: dict[str, Any] = {
        "id": str(uuid.uuid4()),
        "device_id": device_id,
        "message_id": str(uuid.uuid4()),
        "sequence_number": sequence_number,
        "maquina_id": device_id,
        "timestamp": utc_now(),
        "temperatura": temperature,
        "vibracao": vibration,
        "vibracao_unit": "indice_0_10",
        "rpm": 1800,
        "source": source,
        "transport": "http",
        "schema_version": "1.1",
        "time_source": time_source,
    }
    if boot_id is not None and uptime_ms is not None:
        payload["boot_id"] = boot_id
        payload["uptime_ms"] = uptime_ms
    return payload


class OfflineSimulator:
    """Simula um ESP32 offline: coleta dados com boot_id e uptime monotônico.

    Permite:
    - Inicialização com novo boot_id por reinicialização simulada.
    - Contagem monotônica de uptime (independente do relógio civil).
    - Operação com time_source=unsynced durante período offline.
    - Sincronização posterior (NTP/gateway) que estabelece âncora temporal.
    - Envio de lotes atrasados e fora de ordem.
    """

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
        self._readings: list[dict[str, Any]] = []

    def reboot(self) -> None:
        """Simula reinicialização: gera novo boot_id e zera uptime."""
        self.boot_id = str(uuid.uuid4())
        self._uptime_ms = 0
        self._readings = []

    def tick(self, ms: int = 5000) -> None:
        """Avança o contador monotônico de uptime."""
        self._uptime_ms += ms

    def sync_ntp(self) -> None:
        """Simula sincronização NTP: muda time_source para ntp."""
        self.time_source = "ntp"

    def sync_gateway(self) -> None:
        """Simula referência fornecida pelo gateway."""
        self.time_source = "gateway"

    def go_offline(self) -> None:
        """Volta ao estado não sincronizado."""
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
        """Gera uma leitura com os campos temporais do contrato v1."""
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
        # Leitura unsynced: omite timestamp para forçar ingestão via âncora+uptime.
        # Leitura com referência: inclui timestamp para ancorar a reconstrução.
        if self.time_source != "unsynced":
            payload["timestamp"] = utc_now()
        return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device-id", default=os.getenv("DEVICE_ID", "edge-bench-01"))
    parser.add_argument("--count", type=int, default=0)
    parser.add_argument("--interval", type=float, default=0.0)
    parser.add_argument("--api-url", default=os.getenv("FIELDNODE_API_URL", "http://127.0.0.1:8000/api") + "/telemetria/")
    parser.add_argument("--api-key", default=os.getenv("FIELDNODE_API_KEY", ""))
    parser.add_argument("--buffer-path", default="simulators/edge_buffer.db")
    parser.add_argument("--offline", action="store_true", help="gera e persiste sem sincronizar nesta execução")
    parser.add_argument("--sync-only", action="store_true")
    parser.add_argument("--watch", action="store_true", help="gera continuamente e sincroniza com retry durável")
    parser.add_argument("--timeout", type=float, default=float(os.getenv("EDGE_HTTP_TIMEOUT", "10")))
    parser.add_argument("--max-attempts", type=int, default=int(os.getenv("EDGE_MAX_ATTEMPTS", "5")))
    parser.add_argument("--backoff-base", type=float, default=float(os.getenv("EDGE_BACKOFF_BASE", "2")))
    parser.add_argument("--backoff-max", type=float, default=float(os.getenv("EDGE_BACKOFF_MAX", "60")))
    return parser


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = build_parser().parse_args()
    if args.count < 0 or args.max_attempts < 1:
        raise SystemExit("--count e --max-attempts devem ser válidos")
    if args.watch and (args.interval <= 0 or args.offline or args.sync_only):
        raise SystemExit("--watch exige --interval positivo e não combina com --offline/--sync-only")
    if args.watch and not args.api_key:
        raise SystemExit("FIELDNODE_API_KEY/--api-key é obrigatório para sincronizar")
    buffer = EdgeBuffer(args.buffer_path, args.device_id)
    try:
        if args.watch:
            client = EdgeClient(
                buffer,
                args.api_url,
                args.api_key,
                timeout=args.timeout,
                max_attempts=None,
                backoff_base=args.backoff_base,
                backoff_max=args.backoff_max,
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
                    payload = generate_payload(args.device_id, buffer.next_sequence(), index)
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
                                    args.api_key,
                                    timeout=args.timeout,
                                    max_attempts=None,
                                    backoff_base=args.backoff_base,
                                    backoff_max=args.backoff_max,
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
                buffer.enqueue(generate_payload(args.device_id, buffer.next_sequence(), index))
                if args.interval > 0:
                    time.sleep(args.interval)
        if not args.offline:
            if not args.api_key:
                raise SystemExit("FIELDNODE_API_KEY/--api-key é obrigatório para sincronizar")
            EdgeClient(buffer, args.api_url, args.api_key, timeout=args.timeout,
                       max_attempts=args.max_attempts, backoff_base=args.backoff_base,
                       backoff_max=args.backoff_max).synchronize()
        LOGGER.info("outbox device=%s cursor_contiguo=%d counts=%s", args.device_id, buffer.cursor(), buffer.counts())
    finally:
        buffer.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
