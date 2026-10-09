from __future__ import annotations

import json
import sqlite3

import pytest

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


@pytest.fixture
def buffers(tmp_path):
    edge = EdgeBuffer(tmp_path / "colhedora.db", "COLH-POC-01")
    mule = MuleBuffer(tmp_path / "transbordo.db", "TRB-POC-01")
    try:
        for index in range(20):
            edge.enqueue(generate_payload("COLH-POC-01", edge.next_sequence(), index, source="data_mule"))
        yield edge, mule
    finally:
        for connection in (mule, edge):
            try:
                connection.close()
            except sqlite3.ProgrammingError:
                pass


def test_data_mule_coleta_20_preserva_identidade_e_eh_idempotente(buffers):
    edge, mule = buffers

    assert len(edge.transfer_candidates()) == 20
    assert collect_from_harvester(edge, mule) == (20, 0)
    assert collect_from_harvester(edge, mule) == (0, 20)
    assert mule.counts() == {"PENDENTE": 20}

    source_rows = {row["message_id"]: row for row in edge.transfer_candidates()}
    mule_rows = {
        row["message_id"]: row
        for row in mule.connection.execute("SELECT * FROM mule_buffer")
    }
    assert set(source_rows) == set(mule_rows)
    for message_id, source in source_rows.items():
        copied = mule_rows[message_id]
        assert copied["device_id"] == source["device_id"] == "COLH-POC-01"
        assert copied["sequence_number"] == source["sequence_number"]
        assert copied["payload_hash"] == source["payload_hash"]
        assert json.loads(copied["payload"])["source"] == "data_mule"


def test_data_mule_reinicia_e_sincroniza_com_ack_por_mensagem(buffers):
    edge, mule = buffers
    collect_from_harvester(edge, mule)
    mule_path = mule.path
    mule.close()
    mule = MuleBuffer(mule_path, "TRB-POC-01")
    session = FakeSession()
    try:
        assert MuleClient(mule, "http://backend.test/api/telemetria", "secret",
                          session=session, sleep=lambda _: None).synchronize() == 20
        assert len(session.sent) == 20
        assert {item[1]["device_id"] for item in session.sent} == {"COLH-POC-01"}
        assert mule.counts() == {"SINCRONIZADA": 20}
        cursor = mule.connection.execute(
            "SELECT last_acked_sequence FROM mule_cursor WHERE device_id = ?",
            ("COLH-POC-01",),
        ).fetchone()
        assert cursor[0] == 20
    finally:
        mule.close()


def test_data_mule_rejeita_hash_conflitante_sem_sobrescrever(buffers):
    edge, mule = buffers
    collect_from_harvester(edge, mule)
    row = edge.transfer_candidates()[0]
    mule.connection.execute(
        "UPDATE mule_buffer SET payload_hash = ? WHERE message_id = ?",
        ("f" * 64, row["message_id"]),
    )
    mule.connection.commit()

    with pytest.raises(ValueError, match="hash conflitante"):
        collect_from_harvester(edge, mule)

    status = mule.connection.execute(
        "SELECT collection_status FROM mule_buffer WHERE message_id = ?",
        (row["message_id"],),
    ).fetchone()
    assert status[0] == "CONFLITO"
