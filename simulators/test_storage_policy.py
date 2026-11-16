import json
import tempfile
import unittest
from pathlib import Path

from simulators.edge_client import EdgeBuffer, generate_payload
from simulators.storage_policy import StorageFullError, StoragePolicyConfig


class StoragePolicyTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tempdir.name) / "edge.db"
        self.config = StoragePolicyConfig(max_bytes=131_072, reserve_bytes=4_096)
        self.buffer = EdgeBuffer(self.path, "storage-test", storage_config=self.config)

    def tearDown(self):
        self.buffer.close()
        self.tempdir.cleanup()

    def payload(self, index, temperature=70.0):
        payload = generate_payload("storage-test", self.buffer.next_sequence(), index)
        payload["temperatura"] = temperature
        return payload

    def test_storage_status_reports_real_files_and_config(self):
        status = self.buffer.storage_status()
        self.assertGreaterEqual(status["bytes"], 0)
        self.assertEqual(status["max_bytes"], 131_072)
        self.assertIn(status["stage"], {"NORMAL", "COMPRESS_C", "AGGREGATE_C", "DISCARD_C"})

    def test_c_loss_is_recorded_and_a_b_are_not_deleted(self):
        critical = self.payload(0, 115.0)
        self.buffer.enqueue(critical)
        warning = self.payload(1, 80.0)
        self.buffer.enqueue(warning)
        for index in range(2, 40):
            try:
                self.buffer.enqueue(self.payload(index, 70.0))
            except StorageFullError:
                break
        persisted = {row["priority_class"] for row in self.buffer.connection.execute(
            "SELECT priority_class FROM outbox"
        ).fetchall()}
        self.assertIn("A", persisted)
        self.assertIn("B", persisted)
        events = self.buffer.connection.execute(
            "SELECT event_type, priority_class, message_ids FROM storage_events"
        ).fetchall()
        for event in events:
            self.assertEqual(event["priority_class"], "C")
            self.assertTrue(json.loads(event["message_ids"]))

    def test_a_or_b_failure_is_explicit_when_reserve_is_exhausted(self):
        self.buffer.storage_policy.config = StoragePolicyConfig(max_bytes=1, reserve_bytes=0)
        with self.assertRaises(StorageFullError):
            self.buffer.enqueue(self.payload(0, 115.0))

    def test_c_is_compressed_after_90_percent(self):
        path = self.path.with_name("compressed.db")
        buffer = EdgeBuffer(path, "compressed-test",
                            storage_config=StoragePolicyConfig(max_bytes=60_000, reserve_bytes=1_024))
        try:
            buffer.enqueue(generate_payload("compressed-test", buffer.next_sequence(), 0))
            payload = generate_payload("compressed-test", buffer.next_sequence(), 1)
            buffer.enqueue(payload)
            row = buffer.connection.execute(
                "SELECT payload_encoding FROM outbox WHERE message_id = ?", (payload["message_id"],)
            ).fetchone()
            self.assertEqual(row["payload_encoding"], "gzip+base64")
        finally:
            buffer.close()

    def test_aggregate_preserves_statistics_and_marks_loss_of_granularity(self):
        path = self.path.with_name("aggregate.db")
        buffer = EdgeBuffer(path, "aggregate-test",
                            storage_config=StoragePolicyConfig(max_bytes=110_000, reserve_bytes=4_096))
        try:
            for index in range(100):
                try:
                    buffer.enqueue(generate_payload("aggregate-test", buffer.next_sequence(), index))
                except StorageFullError:
                    break
            aggregate = buffer.connection.execute(
                "SELECT sample_count, valid_count, values_json FROM c_aggregates LIMIT 1"
            ).fetchone()
            self.assertIsNotNone(aggregate)
            self.assertGreater(aggregate["sample_count"], 0)
            self.assertEqual(aggregate["sample_count"], aggregate["valid_count"])
            self.assertTrue(json.loads(aggregate["values_json"]))
        finally:
            buffer.close()


if __name__ == "__main__":
    unittest.main()
