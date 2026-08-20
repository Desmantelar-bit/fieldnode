from unittest.mock import patch

from django.test import SimpleTestCase

from api_tcc.ia.worker import worker_loop


class WorkerLoopTests(SimpleTestCase):
    def test_exception_is_logged_and_next_cycle_is_executed(self):
        chamadas = 0

        def processar_fila():
            nonlocal chamadas
            chamadas += 1
            if chamadas == 1:
                raise ValueError("Teste de crash forcado")

        def dormir(_intervalo):
            if chamadas == 2:
                raise StopIteration

        with (
            patch("api_tcc.ia.worker.time.sleep", side_effect=dormir) as sleep,
            self.assertLogs("api_tcc.ia.worker", level="ERROR") as logs,
        ):
            with self.assertRaises(StopIteration):
                worker_loop(processar_fila, intervalo_segundos=0.01)

        self.assertEqual(chamadas, 2)
        self.assertEqual(sleep.call_count, 2)
        sleep.assert_called_with(0.01)
        self.assertIn("Teste de crash forcado", "\n".join(logs.output))
