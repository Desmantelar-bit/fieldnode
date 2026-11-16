from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import requests


class HttpProvider:
    name = "http"

    def __init__(self, api_url: str, device_id: str, device_key: str, *, timeout: float = 10.0,
                 session: Any | None = None, max_bytes: int = 2 * 1024 * 1024) -> None:
        self.api_url = api_url.rstrip("/") + "/"
        self.device_id = device_id
        self.device_key = device_key
        self.timeout = timeout
        self.session = session or requests.Session()
        self._max_bytes = max_bytes

    def available(self) -> bool:
        return bool(self.api_url and self.device_id and self.device_key)

    def max_payload_bytes(self) -> int:
        return self._max_bytes

    def cost_per_msg(self) -> float:
        return 0.0

    def send(self, batch: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        acks: list[dict[str, Any]] = []
        for payload in batch:
            try:
                wire_payload = dict(payload)
                # payload_hash is the outbox fingerprint, not part of the
                # logical body hashed by the existing Django endpoint.
                wire_payload.pop("payload_hash", None)
                response = self.session.post(self.api_url, json=wire_payload, headers={
                    "X-Device-Id": self.device_id, "X-Device-Key": self.device_key,
                    "Content-Type": "application/json"}, timeout=self.timeout)
                body = response.json()
                if isinstance(body, dict):
                    acks.append(body)
            except (requests.RequestException, ValueError):
                continue
        return acks
