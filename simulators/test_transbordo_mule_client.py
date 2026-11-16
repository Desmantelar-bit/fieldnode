from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

try:
    from .edge_client import EdgeBuffer, generate_payload
    from .transbordo_mule_client import MuleBuffer, MuleClient, collect_from_harvester
except ImportError:
    from edge_client import EdgeBuffer, generate_payload
    from transbordo_mule_client import MuleBuffer, MuleClient, collect_from_harvester


class FakeResponse:
    status_code = 201

    def __init__(self, payload: dict):
        self.payload = payload

    def json(self):
        return {
            "message_id": self.payload["message_id"],
            "payload_hash": _hash(self.payload),
        }


class FakeSession:
    def __init__(self):
        self.sent = []

    def post(self, url, *, json, headers, timeout):
        self.sent.append((url, json, headers, timeout))
        return FakeResponse(json)


def _hash(payload):
    try:
        from .edge_client import payload_hash
    except ImportError:
        from edge_client import payload_hash
    return payload_hash(payload)


class DataMuleClientTest(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        tmp_path = Path(self._temp_dir.name)
        self.edge = EdgeBuffer(tmp_path / "colhedora.db", "COLH-POC-01")
        self.mule = MuleBuffer(tmp_path / "transbordo.db", "TRB-POC-01")
        for index in range(20):
            self.edge.enqueue(generate_payload("COLH-POC-01", self.edge.next_sequence(), index, source="data_mule"))

    def tearDown(self):
        for connection in (self.mule, self.edge):
            try:
                connection.close()
            except sqlite3.ProgrammingError:
                pass
        self._temp_dir.cleanup()

    def test_data_mule_coleta_20_preserva_identidade_e_eh_idempotente(self):
        self.assertEqual(len(self.edge.transfer_candidates()), 20)
        self.assertEqual(collect_from_harvester(self.edge, self.mule), (20, 0))
        self.assertEqual(collect_from_harvester(self.edge, self.mule), (0, 20))
        self.assertEqual(self.mule.counts(), {"PENDENTE": 20})

        source_rows = {row["message_id"]: row for row in self.edge.transfer_candidates()}
        mule_rows = {
            row["message_id"]: row
            for row in self.mule.connection.execute("SELECT * FROM mule_buffer")
        }
        self.assertEqual(set(source_rows), set(mule_rows))
        for message_id, source in source_rows.items():
            copied = mule_rows[message_id]
            self.assertEqual(copied["device_id"], source["device_id"])
            self.assertEqual(copied["device_id"], "COLH-POC-01")
            self.assertEqual(copied["sequence_number"], source["sequence_number"])
            self.assertEqual(copied["payload_hash"], source["payload_hash"])
            self.assertEqual(json.loads(copied["payload"])["source"], "data_mule")

    def test_data_mule_reinicia_e_sincroniza_com_ack_por_mensagem(self):
        collect_from_harvester(self.edge, self.mule)
        mule_path = self.mule.path
        self.mule.close()
        self.mule = MuleBuffer(mule_path, "TRB-POC-01")
        session = FakeSession()
        try:
            self.assertEqual(
                MuleClient(self.mule, "http://backend.test/api/telemetria", "secret",
                           session=session, sleep=lambda _: None).synchronize(),
                20,
            )
            self.assertEqual(len(session.sent), 20)
            self.assertEqual({item[1]["device_id"] for item in session.sent}, {"COLH-POC-01"})
            self.assertEqual(self.mule.counts(), {"SINCRONIZADA": 20})
            cursor = self.mule.connection.execute(
                "SELECT last_acked_sequence FROM mule_cursor WHERE device_id = ?",
                ("COLH-POC-01",),
            ).fetchone()
            self.assertEqual(cursor[0], 20)
        finally:
            self.mule.close()

    def test_data_mule_rejeita_hash_conflitante_sem_sobrescrever(self):
        collect_from_harvester(self.edge, self.mule)
        row = self.edge.transfer_candidates()[0]
        self.mule.connection.execute(
            "UPDATE mule_buffer SET payload_hash = ? WHERE message_id = ?",
            ("f" * 64, row["message_id"]),
        )
        self.mule.connection.commit()

        with self.assertRaises(ValueError) as ctx:
            collect_from_harvester(self.edge, self.mule)
        self.assertIn("hash conflitante", str(ctx.exception))

        status = self.mule.connection.execute(
            "SELECT collection_status FROM mule_buffer WHERE message_id = ?",
            (row["message_id"],),
        ).fetchone()
        self.assertEqual(status[0], "CONFLITO")
