import json
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import requests
from api_tcc.contracts import ContractError

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
            "status": "acked",
            "message_id": payload["message_id"],
            "device_id": payload["device_id"],
            "sequence_number": payload["sequence_number"],
            "payload_hash": payload_hash(payload),
            "last_acked_sequence": payload["sequence_number"],
        })

    def test_hash_and_priority_are_deterministic(self):
        critical = {"temperatura": 111, "vibracao": 1}
        warning = {"temperatura": 80, "vibracao": 1}
        normal = {"temperatura": 70, "vibracao": 1}
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
        self.assertEqual(self.buffer.counts().get(STATUS_SYNCED, 0), 0)
        self.assertEqual(self.buffer.counts(), {})
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

    def test_conflict_blocks_item_without_removing_it(self):
        payload = self.enqueue()
        session = FakeSession([FakeResponse(409, {
            "status": "conflict", "message_id": payload["message_id"],
            "device_id": payload["device_id"], "sequence_number": payload["sequence_number"],
            "payload_hash": payload_hash(payload),
        })])
        EdgeClient(self.buffer, "http://fieldnode/api/telemetria/", "secret",
                   session=session, backoff_base=0).synchronize()
        row = self.buffer.connection.execute("SELECT status FROM outbox").fetchone()
        self.assertEqual(row[0], "BLOCKED")
        self.assertEqual(self.buffer.cursor(), 0)

    def test_retry_after_lost_ack_resends_same_message_then_removes(self):
        payload = self.enqueue()
        session = FakeSession([requests.ConnectionError("response lost"), FakeResponse(200, {
            "status": "duplicate", "message_id": payload["message_id"],
            "device_id": payload["device_id"], "sequence_number": payload["sequence_number"],
            "payload_hash": payload_hash(payload), "last_acked_sequence": payload["sequence_number"],
        })])
        client = EdgeClient(self.buffer, "http://fieldnode/api/telemetria/", "secret",
                            session=session, backoff_base=0)
        self.assertEqual(client.synchronize(), 0)
        self.assertEqual(self.buffer.counts().get(STATUS_PENDING), 1)
        self.assertEqual(client.synchronize(), 1)
        self.assertEqual(session.payloads[0], session.payloads[1])
        self.assertEqual(self.buffer.counts(), {})
        self.assertEqual(self.buffer.cursor(), payload["sequence_number"])

    def test_partial_http_500_preserves_only_unconfirmed_message(self):
        first, second = self.enqueue(0), self.enqueue(1)
        session = FakeSession([self.ack_for(first), FakeResponse(500, {})])
        client = EdgeClient(self.buffer, "http://fieldnode/api/telemetria/", "secret",
                            session=session, backoff_base=0)
        self.assertEqual(client.synchronize(), 1)
        rows = self.buffer.connection.execute("SELECT message_id, status FROM outbox").fetchall()
        self.assertEqual([(row["message_id"], row["status"]) for row in rows],
                         [(second["message_id"], STATUS_PENDING)])
        self.assertEqual(self.buffer.cursor(), 1)

    def test_incomplete_or_unknown_ack_never_removes_message(self):
        first, second, third = self.enqueue(0), self.enqueue(1), self.enqueue(2)
        session = FakeSession([
            FakeResponse(201, {"status": "acked", "device_id": first["device_id"],
                               "sequence_number": first["sequence_number"],
                               "payload_hash": payload_hash(first)}),
            FakeResponse(201, {"status": "acked", "message_id": second["message_id"],
                               "device_id": second["device_id"],
                               "sequence_number": second["sequence_number"]}),
            FakeResponse(200, {"status": "maybe", "message_id": third["message_id"],
                               "device_id": third["device_id"],
                               "sequence_number": third["sequence_number"],
                               "payload_hash": payload_hash(third)}),
        ])
        EdgeClient(self.buffer, "http://fieldnode/api/telemetria/", "secret",
                   session=session, backoff_base=0).synchronize()
        states = {row["message_id"]: row["status"] for row in self.buffer.connection.execute(
            "SELECT message_id, status FROM outbox").fetchall()}
        self.assertEqual(states[first["message_id"]], STATUS_ERROR)
        self.assertEqual(states[second["message_id"]], STATUS_ERROR)
        self.assertEqual(states[third["message_id"]], STATUS_PENDING)
        self.assertEqual(self.buffer.cursor(), 0)

    def test_falha_sqlite_na_confirmacao_recupera_no_reinicio(self):
        payload = self.enqueue()
        client = EdgeClient(self.buffer, "http://fieldnode/api/telemetria/", "secret",
                            session=FakeSession([self.ack_for(payload)]), backoff_base=0)
        with patch.object(self.buffer, "_advance_contiguous_cursor",
                          side_effect=sqlite3.OperationalError("disk full")):
            with self.assertRaises(sqlite3.OperationalError):
                client.synchronize()
        self.buffer.close()
        self.buffer = EdgeBuffer(self.path, "edge-test")
        self.assertEqual(self.buffer.counts().get(STATUS_PENDING), 1)
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

    def test_continuous_gateway_retries_pending_data_without_attempt_limit(self):
        first = self.enqueue(0)
        second = self.enqueue(1)
        session = FakeSession([
            requests.ConnectionError("offline"),
            self.ack_for(first),
            self.ack_for(second),
        ])
        client = EdgeClient(
            self.buffer,
            "http://fieldnode/api/telemetria/",
            "secret",
            max_attempts=None,
            session=session,
            backoff_base=0,
        )

        self.assertEqual(client.synchronize(stop_on_retryable_failure=True), 0)
        self.assertEqual(self.buffer.counts().get(STATUS_PENDING), 2)
        self.assertEqual(len(session.payloads), 1)

        self.buffer.close()
        self.buffer = EdgeBuffer(self.path, "edge-test")
        client = EdgeClient(
            self.buffer,
            "http://fieldnode/api/telemetria/",
            "secret",
            max_attempts=None,
            session=session,
            backoff_base=0,
        )
        self.assertEqual(client.synchronize(stop_on_retryable_failure=True), 2)
        self.assertEqual(self.buffer.counts().get(STATUS_SYNCED, 0), 0)
        self.assertEqual(self.buffer.counts(), {})
        self.assertEqual(self.buffer.cursor(), 2)

    def test_edge_priority_matches_shared_golden_contract(self):
        fixture_path = Path(__file__).resolve().parents[1] / "contracts" / "fixtures" / "classificacao.json"
        fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))
        for case in fixtures:
            with self.subTest(case_id=case["id"]):
                if case.get("expected_error") == "range":
                    with self.assertRaises(ContractError):
                        classify_priority(case)
                else:
                    self.assertEqual(classify_priority(case), case["classe"])


if __name__ == "__main__":
    unittest.main()
