import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from simulators.edge_client import compress_batch, decompress_batch, EdgeBuffer, generate_payload
from simulators.storage_policy import StoragePolicyConfig


class S6T3Test(unittest.TestCase):
    def test_hash_is_over_uncompressed_body_and_peak_survives_stats(self):
        payloads = [generate_payload("S6-C", 1, 1), generate_payload("S6-C", 2, 2)]
        payloads[0]["temperatura"] = 70.0
        payloads[1]["temperatura"] = 97.4
        compressed, digest, metrics = compress_batch(payloads)
        self.assertEqual(decompress_batch(compressed, digest), payloads)
        self.assertLess(metrics["compressed_bytes"], metrics["serialized_bytes"])
        self.assertEqual(max(item["temperatura"] for item in payloads), 97.4)

    def test_ttl_b_c_is_registered_and_a_is_retained(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "edge.db"
            buffer = EdgeBuffer(path, "S6-TTL", storage_config=StoragePolicyConfig(max_bytes=1_000_000))
            try:
                old = datetime.now(timezone.utc) - timedelta(days=15)
                for priority, sequence in (("A", 1), ("B", 2), ("C", 3)):
                    payload = generate_payload("S6-TTL", sequence, sequence)
                    payload["temperatura"] = {"A": 115.0, "B": 80.0, "C": 70.0}[priority]
                    payload.update({"priority_class": priority, "timestamp": old.isoformat(), "time_source": "gateway"})
                    buffer.enqueue(payload)
                result = buffer.purge_expired(reference_time=datetime.now(timezone.utc))
                self.assertEqual(result["A"], 0)
                self.assertEqual(result["B"], 1)
                self.assertEqual(result["C"], 1)
                self.assertEqual(buffer.connection.execute("SELECT COUNT(*) FROM outbox WHERE priority_class='A'").fetchone()[0], 1)
                self.assertEqual(buffer.connection.execute("SELECT COUNT(*) FROM storage_events WHERE event_type='discard_ttl'").fetchone()[0], 2)
            finally:
                buffer.close()


if __name__ == "__main__":
    unittest.main()
