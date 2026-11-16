from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from connectivity.manager import ConnectivityManager
from connectivity.providers.sat_sim import SatelliteSimProvider
from simulators.edge_client import EdgeBuffer, generate_payload


class SatelliteSimulationTest(unittest.TestCase):
    def test_budget_block_keeps_class_a_in_outbox(self):
        with tempfile.TemporaryDirectory() as directory:
            clock = lambda: datetime(2026, 11, 16, tzinfo=timezone.utc)
            provider = SatelliteSimProvider(cost=1, daily_budget=1, clock=clock)
            buffer = EdgeBuffer(Path(directory) / "edge.db", "DEV-SAT")
            try:
                buffer.enqueue(generate_payload("DEV-SAT", 1, 0))
                buffer.enqueue(generate_payload("DEV-SAT", 2, 0))
                result = ConnectivityManager(buffer, [provider]).tick()
                self.assertEqual(result["acked"], 1)
                self.assertEqual(len(buffer.pending()), 1)
                self.assertEqual(provider.report()["blocked_budget"], 1)
                self.assertEqual(provider.report()["consumed"], 1.0)
            finally:
                buffer.close()

    def test_duplicate_identity_does_not_charge_again(self):
        provider = SatelliteSimProvider(cost=2, daily_budget=4)
        item = {"message_id": "m1", "device_id": "D1", "sequence_number": 7, "payload_hash": "a" * 64}
        self.assertEqual(provider.send([item])[0]["status"], "acked")
        self.assertEqual(provider.send([item])[0]["status"], "duplicate")
        self.assertEqual(provider.report()["consumed"], 2.0)

    def test_classes_b_and_c_are_not_eligible_in_default_policy(self):
        provider = SatelliteSimProvider()
        manager = ConnectivityManager(object(), [provider])
        self.assertEqual([item.name for item in manager._eligible("B")], [])
        self.assertEqual([item.name for item in manager._eligible("C")], [])


if __name__ == "__main__":
    unittest.main()
