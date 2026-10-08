import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import requests

from simulators.edge_client import (
    EdgeBuffer,
    EdgeClient,
    STATUS_ERROR,
    STATUS_PENDING,
    STATUS_SYNCED,
    classify_priority,
    generate_payload,
    payload_hash,
)


class FakeResponse:
    def __init__(self, status_code: int, body: dict):
        self.status_code = status_code
        self.body = body

    def json(self):
        return self.body


class FakeSession:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.payloads = []

    def post(self, url, *, json, headers, timeout):
        self.payloads.append(json)
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


class EdgeClientTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tempdir.name) / "edge.db"
        self.buffer = EdgeBuffer(self.path, "edge-test")

    def tearDown(self):
        self.buffer.close()
        self.tempdir.cleanup()

    def enqueue(self, index=0):
        payload = generate_payload("edge-test", self.buffer.next_sequence(), index)
        self.buffer.enqueue(payload)
        return payload

    def ack_for(self, payload):
        return FakeResponse(201, {
            "message_id": payload["message_id"],
            "payload_hash": payload_hash(payload),
        })

    def test_hash_and_priority_are_deterministic(self):
        critical = {"temperatura": 111, "vibracao": 1}
        warning = {"temperatura": 100, "vibracao": 1}
        normal = {"temperatura": 80, "vibracao": 1}
        self.assertEqual(classify_priority(critical), "A")
        self.assertEqual(classify_priority(warning), "B")
        self.assertEqual(classify_priority(normal), "C")
        payload = self.enqueue()
        self.assertEqual(payload_hash(payload), payload_hash(json.loads(
            json.dumps(payload, sort_keys=True)
        )))

    def test_persists_before_sync_and_advances_contiguous_cursor(self):
        first = self.enqueue(0)
        second = self.enqueue(1)
        session = FakeSession([self.ack_for(first), self.ack_for(second)])
        client = EdgeClient(self.buffer, "http://fieldnode/api/telemetria/", "secret",
                            session=session, backoff_base=0)
        self.assertEqual(client.api_url, "http://fieldnode/api/telemetria/")
        self.assertEqual(self.buffer.counts().get("PENDENTE"), 2)
        self.assertEqual(client.synchronize(), 2)
        self.assertEqual(self.buffer.counts().get(STATUS_SYNCED), 2)
        self.assertEqual(self.buffer.cursor(), 2)
        self.assertEqual([p["message_id"] for p in session.payloads],
                         [first["message_id"], second["message_id"]])

    def test_priority_is_a_before_b_before_c(self):
        payloads = [self.enqueue(index) for index in (0, 3, 1)]
        session = FakeSession([self.ack_for(payloads[0]), self.ack_for(payloads[1]), self.ack_for(payloads[2])])
        client = EdgeClient(self.buffer, "http://fieldnode/api/telemetria/", "secret",
                            session=session, backoff_base=0)
        client.synchronize()
        priorities = [classify_priority(payload) for payload in session.payloads]
        self.assertEqual(priorities, ["A", "B", "C"])

    def test_hash_mismatch_is_not_ack(self):
        payload = self.enqueue()
        session = FakeSession([FakeResponse(201, {
            "message_id": payload["message_id"], "payload_hash": "0" * 64,
        })])
        EdgeClient(self.buffer, "http://fieldnode/api/telemetria/", "secret",
                   session=session, backoff_base=0).synchronize()
        row = self.buffer.connection.execute("SELECT status FROM outbox").fetchone()
        self.assertEqual(row[0], STATUS_ERROR)
        self.assertEqual(self.buffer.cursor(), 0)

    def test_connection_failure_keeps_message_for_retry(self):
        payload = self.enqueue()
        session = FakeSession([requests.ConnectionError("offline")])
        EdgeClient(self.buffer, "http://fieldnode/api/telemetria/", "secret",
                   session=session, backoff_base=0).synchronize()
        row = self.buffer.connection.execute("SELECT status, attempts FROM outbox").fetchone()
        self.assertEqual(row[0], STATUS_PENDING)
        self.assertEqual(row[1], 1)
        self.assertEqual(self.buffer.cursor(), 0)


if __name__ == "__main__":
    unittest.main()
