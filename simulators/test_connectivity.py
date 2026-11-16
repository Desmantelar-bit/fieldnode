from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from connectivity.manager import ConnectivityManager
from simulators.edge_client import EdgeBuffer, generate_payload


class FakeProvider:
    def __init__(self, name, *, available=True, result="acked"):
        self.name = name
        self._available = available
        self.result = result
        self.calls = 0

    def available(self):
        return self._available

    def max_payload_bytes(self):
        return 100_000

    def cost_per_msg(self):
        return 0.0

    def send(self, batch):
        self.calls += 1
        if self.result == "error":
            return []
        return [{
            "status": self.result,
            "message_id": item["message_id"],
            "device_id": item["device_id"],
            "sequence_number": item["sequence_number"],
            "payload_hash": item["payload_hash"],
        } for item in batch]


class ConnectivityManagerTest(unittest.TestCase):
    def test_fallback_applies_only_valid_acks(self):
        with tempfile.TemporaryDirectory() as directory:
            buffer = EdgeBuffer(Path(directory) / "edge.db", "DEV-1")
            try:
                buffer.enqueue(generate_payload("DEV-1", 1, 1))
                first = FakeProvider("http", result="error")
                second = FakeProvider("mule")
                result = ConnectivityManager(buffer, [first, second]).tick()
                self.assertEqual(result["acked"], 1)
                self.assertEqual(first.calls, 1)
                self.assertEqual(second.calls, 1)
                self.assertEqual(buffer.counts(), {})
            finally:
                buffer.close()

    def test_unavailable_provider_is_skipped_without_losing_outbox(self):
        with tempfile.TemporaryDirectory() as directory:
            buffer = EdgeBuffer(Path(directory) / "edge.db", "DEV-1")
            try:
                buffer.enqueue(generate_payload("DEV-1", 1, 1))
                provider = FakeProvider("http", available=False)
                result = ConnectivityManager(buffer, [provider]).tick()
                self.assertEqual(result["acked"], 0)
                self.assertEqual(len(buffer.pending()), 1)
            finally:
                buffer.close()


if __name__ == "__main__":
    unittest.main()
