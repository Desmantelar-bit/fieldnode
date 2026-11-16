from __future__ import annotations

import random
import unittest
from datetime import datetime, timezone

from connectivity.codec_compact import CompactFrameError, FRAME_SIZE, decode_frame, encode_frame


class CompactCodecTest(unittest.TestCase):
    def payload(self, index: int) -> dict:
        rng = random.Random(index)
        return {
            "priority_class": "ABC"[index % 3], "regime": [None, "desligada", "marcha_lenta", "trabalhando", "deslocamento"][index % 5],
            "time_source": ["rtc", "gateway", "ntp", "unsynced"][index % 4], "sequence_number": index + 1,
            "temperatura": round(rng.uniform(-120, 250), 2), "vibracao": round(rng.uniform(0, 10), 2),
            "rpm": rng.randrange(0, 5001), "latitude": None, "longitude": None,
        }

    def test_10000_deterministic_round_trips(self):
        for index in range(10000):
            payload = self.payload(index)
            if index % 2:
                payload["latitude"], payload["longitude"] = -33.0 + index / 100000, -53.0 - index / 100000
            if payload["time_source"] != "unsynced":
                payload["timestamp"] = datetime.fromtimestamp(1700000000 + index, timezone.utc).isoformat()
            frame = encode_frame(payload, device_idx=17)
            self.assertEqual(len(frame), FRAME_SIZE)
            decoded = decode_frame(frame, device_id="DEV-17")
            self.assertEqual(decoded["device_id"], "DEV-17")
            self.assertEqual(decoded["priority_class"], payload["priority_class"])
            self.assertEqual(decoded["sequence_number"], payload["sequence_number"])
            self.assertAlmostEqual(decoded["temperatura"], payload["temperatura"], places=2)
            self.assertAlmostEqual(decoded["vibracao"], payload["vibracao"], places=2)
            self.assertEqual(decoded["rpm"], payload["rpm"])
            self.assertAlmostEqual(decoded["latitude"], payload["latitude"], places=5)
            self.assertAlmostEqual(decoded["longitude"], payload["longitude"], places=5)

    def test_crc_detects_each_frame_bit_and_invalid_shapes(self):
        payload = {**self.payload(1), "priority_class": "A", "time_source": "gateway", "timestamp": "2026-11-16T12:00:00+00:00"}
        frame = encode_frame(payload, device_idx=1)
        for byte_index in range(26):
            corrupted = bytearray(frame)
            corrupted[byte_index] ^= 0x01
            with self.subTest(byte_index=byte_index):
                with self.assertRaises(CompactFrameError):
                    decode_frame(bytes(corrupted), device_id="DEV-1")
        with self.assertRaises(CompactFrameError):
            decode_frame(frame[:-1], device_id="DEV-1")
        with self.assertRaises(CompactFrameError):
            decode_frame(frame + b"\x00", device_id="DEV-1")

    def test_unsynced_and_unknown_device_are_explicit(self):
        frame = encode_frame({**self.payload(2), "time_source": "unsynced"}, device_idx=9)
        decoded = decode_frame(frame, device_registry={9: "DEV-9"})
        self.assertEqual(decoded["event_time_unix_s"], 0)
        with self.assertRaises(CompactFrameError):
            decode_frame(frame)


if __name__ == "__main__":
    unittest.main()
