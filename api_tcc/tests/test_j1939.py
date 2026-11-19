import json
from pathlib import Path
import unittest

from api_tcc.services.j1939 import InvalidFrame, decode, extract_bits, pgn_from_id


class J1939DecoderTest(unittest.TestCase):
    def test_pdu1_e_pdu2(self):
        self.assertEqual(pgn_from_id(0x0CEF0001), 0xEF00)
        self.assertEqual(pgn_from_id(0x0CF00401), 61444)

    def test_eec1_spn190(self):
        result = decode(0x0CF00401, bytes.fromhex("FF FF FF 80 3E FF FF FF"))
        self.assertEqual(result[0].spn, 190)
        self.assertAlmostEqual(result[0].value, 2000.0)
        self.assertEqual(result[0].unit, "rpm")
        self.assertEqual(result[0].origem, "medido")

    def test_et1_offset(self):
        result = decode(0x18FEEE22, bytes.fromhex("22 FF FF FF FF FF FF FF"))
        self.assertEqual(result[0].value, -6.0)

    def test_eflp1_pressure(self):
        result = decode(0x0CFEEF01, bytes.fromhex("FF FF FF 0A FF FF FF FF"))
        self.assertEqual(result[0].value, 40.0)

    def test_special_values_do_not_become_numbers(self):
        self.assertEqual(decode(0x0CF00401, bytes.fromhex("00 00 00 FF FF 00 00 00"))[0].status, "unavailable")
        self.assertEqual(decode(0x18FEEE22, bytes.fromhex("FE FF FF FF FF FF FF FF"))[0].status, "error")

    def test_unknown_pgn_is_tolerated(self):
        result = decode(0x0C123401, b"\x00" * 8)
        self.assertEqual(result[0].status, "unsupported")

    def test_invalid_frame_and_bits(self):
        with self.assertRaises(InvalidFrame):
            decode(0x123, b"\x00" * 8)
        with self.assertRaises(InvalidFrame):
            decode(0x0CF00401, b"\x00" * 7)
        self.assertEqual(extract_bits(bytes([0b10101100]), 2, 3), 3)

    def test_table_has_sources_and_valid_geometry(self):
        path = Path(__file__).parents[1] / "adapters" / "j1939_pgn_table.json"
        table = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(table["table_version"])
        for pgn, spec in table["pgns"].items():
            self.assertTrue(spec["source"], pgn)
            for spn in spec["spns"]:
                self.assertGreaterEqual(spn["spn"], 0)
                self.assertGreaterEqual(spn["start_bit"], 0)
                self.assertGreater(spn["length"], 0)
                self.assertLessEqual(spn["start_bit"] + spn["length"], 64)
                self.assertTrue(spn["unit"])
