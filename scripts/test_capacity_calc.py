import unittest

from scripts.capacity_calc import capacidade


class CapacityCalcTest(unittest.TestCase):
    def test_calculates_raw_and_estimated_capacity(self):
        result = capacidade(msgs_por_s=0.5, bytes_msg=220, dias=14,
                            overhead=0.6, compressao_C=0.35, frac_C=0.9)
        self.assertEqual(result.messages, 604800)
        self.assertGreater(result.raw_bytes, result.estimated_bytes)
        self.assertGreater(result.estimated_gb, 0)

    def test_rejects_incoherent_inputs(self):
        with self.assertRaises(ValueError):
            capacidade(msgs_por_s=0, bytes_msg=220, dias=1)
        with self.assertRaises(ValueError):
            capacidade(msgs_por_s=1, bytes_msg=220, dias=1, frac_C=1.1)


if __name__ == "__main__":
    unittest.main()
