from __future__ import annotations

import json
import logging
from collections.abc import Callable, Iterable
from datetime import date
from typing import Any

from .base import Ack, ConnectivityProvider
from .policy import load_policy

LOGGER = logging.getLogger("fieldnode.connectivity")


def _wire_size(envelope: dict[str, Any]) -> int:
    return len(json.dumps(envelope, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8"))


class ConnectivityManager:
    """Selects transports and releases outbox rows only for valid ACKs."""

    def __init__(self, outbox: Any, providers: Iterable[ConnectivityProvider], *, policy: dict[str, Any] | None = None,
                 daily_cost: Callable[[str, date], float] | None = None,
                 record_cost: Callable[[str, date, float], None] | None = None,
                 max_attempts: int | None = 5) -> None:
        self.outbox = outbox
        self.providers = {provider.name: provider for provider in providers}
        self.policy = load_policy(policy)
        self.daily_cost = daily_cost or (lambda _provider, _day: 0.0)
        self.record_cost = record_cost or (lambda _provider, _day, _amount: None)
        self.max_attempts = max_attempts

    def _batch(self, rows: list[Any], provider: ConnectivityProvider) -> list[tuple[Any, dict[str, Any]]]:
        selected: list[tuple[Any, dict[str, Any]]] = []
        used = 0
        for row in rows:
            payload = self.outbox._decode_row(row)
            # The persisted row is the source of truth for transport identity;
            # old payloads may predate the explicit envelope fields.
            payload.setdefault("device_id", row["device_id"])
            payload.setdefault("message_id", row["message_id"])
            payload.setdefault("sequence_number", row["sequence_number"])
            payload.setdefault("payload_hash", row["payload_hash"])
            payload.setdefault("priority_class", row["priority_class"])
            size = _wire_size(payload)
            if size > provider.max_payload_bytes():
                LOGGER.warning("connectivity provider=%s message=%s skipped=payload_limit", provider.name, row["message_id"])
                continue
            if selected and used + size > provider.max_payload_bytes():
                break
            selected.append((row, payload))
            used += size
        return selected

    def _eligible(self, priority: str) -> list[ConnectivityProvider]:
        config = self.policy["classes"].get(priority, {})
        result: list[ConnectivityProvider] = []
        for name in config.get("order", []):
            provider = self.providers.get(name)
            if provider is None:
                LOGGER.info("connectivity provider=%s skipped=not_configured class=%s", name, priority)
                continue
            try:
                available = provider.available()
            except Exception as exc:  # provider boundary: a broken channel is not a broken outbox
                LOGGER.warning("connectivity provider=%s skipped=availability_error type=%s", name, type(exc).__name__)
                continue
            if available:
                result.append(provider)
            else:
                LOGGER.info("connectivity provider=%s skipped=unavailable class=%s", name, priority)
        return result

    @staticmethod
    def _valid_ack(row: Any, ack: Ack) -> bool:
        return (
            ack.get("status") in {"acked", "duplicate"}
            and ack.get("message_id") == row["message_id"]
            and ack.get("device_id") == row["device_id"]
            and ack.get("sequence_number") == row["sequence_number"]
            and ack.get("payload_hash") == row["payload_hash"]
        )

    def tick(self) -> dict[str, int]:
        result = {"sent": 0, "acked": 0, "pending": 0, "providers": 0}
        for priority in ("A", "B", "C"):
            rows = [row for row in self.outbox.pending() if row["priority_class"] == priority]
            if self.max_attempts is not None:
                eligible = []
                for row in rows:
                    if int(row["attempts"]) >= self.max_attempts:
                        self.outbox.mark_error(int(row["id"]), "MAX_ATTEMPTS atingido")
                    else:
                        eligible.append(row)
                rows = eligible
            if not rows:
                continue
            remaining = rows
            config = self.policy["classes"].get(priority, {})
            for provider in self._eligible(priority):
                if not remaining:
                    break
                if provider.name in {"sat", "sat_sim"} and not getattr(provider, "budget_managed", False) and config.get("max_cost_day") is not None:
                    today = date.today()
                    cost = self.daily_cost(provider.name, today)
                    unit_cost = provider.cost_per_msg()
                    if unit_cost is None or cost + unit_cost > float(config["max_cost_day"]):
                        LOGGER.info("connectivity provider=SIMULADO:%s skipped=daily_budget class=%s", provider.name, priority)
                        continue
                batch = self._batch(remaining, provider)
                if not batch:
                    continue
                result["providers"] += 1
                result["sent"] += len(batch)
                for row, payload in batch:
                    self.outbox.mark_sending(int(row["id"]))
                try:
                    acks = provider.send([payload for _row, payload in batch])
                except Exception as exc:
                    acks = [{"status": "error", "error": type(exc).__name__}]
                    LOGGER.warning("connectivity provider=%s failed type=%s", provider.name, type(exc).__name__)
                by_id = {ack.get("message_id"): ack for ack in acks}
                confirmed: list[Any] = []
                for row, _payload in batch:
                    ack = by_id.get(row["message_id"])
                    if ack and self._valid_ack(row, ack):
                        self.outbox.mark_synced(int(row["id"]))
                        confirmed.append(row)
                        result["acked"] += 1
                    else:
                        self.outbox.mark_retryable(int(row["id"]), f"provider {provider.name}: ACK ausente ou inválido")
                result["pending"] += len(batch) - len(confirmed)
                confirmed_ids = {row["message_id"] for row in confirmed}
                remaining = [row for row in remaining if row["message_id"] not in confirmed_ids]
                if confirmed:
                    amount = (provider.cost_per_msg() or 0.0) * len(confirmed)
                    if provider.name in {"sat", "sat_sim"} and amount:
                        self.record_cost(provider.name, date.today(), amount)
                LOGGER.info("connectivity policy=%s class=%s provider=%s batch=%d acked=%d pending=%d",
                            self.policy["version"], priority, provider.name, len(batch), len(confirmed), len(remaining))
            result["pending"] += len(remaining)
        return result
