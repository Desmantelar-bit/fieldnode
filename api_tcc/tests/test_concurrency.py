import threading
import time

from django.db import OperationalError, close_old_connections
from django.test import TransactionTestCase
from django.utils import timezone

from api_tcc.models import LeituraTelemetria


class ConcurrencySaveTestCase(TransactionTestCase):
    """Concurrent inserts rely on the UUID primary key, not a shared sequence."""

    def test_concurrent_telemetry_saves(self):
        num_threads = 20
        barrier = threading.Barrier(num_threads)
        errors = []
        errors_lock = threading.Lock()

        def criar_leitura(index):
            close_old_connections()
            try:
                barrier.wait()
                # SQLite permits one writer at a time. Retrying its transient lock
                # keeps this test portable while every attempt remains a single INSERT.
                for attempt in range(8):
                    try:
                        LeituraTelemetria.objects.create(
                            maquina_id=f"CONC-{index:02d}",
                            temperatura=70.0 + index,
                            vibracao=0.2,
                            rpm=1800 + index,
                            timestamp=timezone.now(),
                        )
                        return
                    except OperationalError as exc:
                        if "locked" not in str(exc).lower() or attempt == 7:
                            raise
                        time.sleep(0.02 * (attempt + 1))
            except Exception as exc:  # Assertion below reports every worker failure.
                with errors_lock:
                    errors.append(exc)
            finally:
                close_old_connections()

        threads = [
            threading.Thread(target=criar_leitura, args=(index,))
            for index in range(num_threads)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(errors, [], f"Erros durante gravações concorrentes: {errors}")
        self.assertEqual(LeituraTelemetria.objects.count(), num_threads)

        ids = list(LeituraTelemetria.objects.values_list("id", flat=True))
        self.assertEqual(len(ids), len(set(ids)))
