import hashlib
import json
import unittest

from api_tcc.sync_contract import validate_sync_envelope


class SyncContractTest(unittest.TestCase):
    def payload(self):
        raw = json.dumps({"temperatura": 72}, sort_keys=True).encode()
        return {
            "device_id": "COLH-03", "message_id": "msg-1", "sequence_number": 1,
            "schema_version": "1.2", "priority_class": "C",
            "payload_hash": hashlib.sha256(raw).hexdigest(), "payload": {"temperatura": 72},
        }

    def test_valid_envelope(self):
        self.assertEqual(validate_sync_envelope(self.payload()), (True, ""))

    def test_rejects_bad_hash_and_sequence(self):
        payload = self.payload()
        payload["payload_hash"] = "bad"
        self.assertFalse(validate_sync_envelope(payload)[0])
        payload = self.payload()
        payload["sequence_number"] = 0
        self.assertFalse(validate_sync_envelope(payload)[0])


if __name__ == "__main__":
    unittest.main()
