import threading
import time

from django.db import OperationalError, close_old_connections
from django.test import TransactionTestCase
from django.utils import timezone

from api_tcc.models import LeituraTelemetria
from api_tcc.services.telemetria import registrar_leitura


class ConcurrencySameKeyTestCase(TransactionTestCase):
    """
    OBRIGATÓRIO S1-T5 — Race condition real de idempotência.

    N threads tentam registrar simultaneamente o MESMO (device_id, message_id).
    Resultado obrigatório:
    - exatamente 1 LeituraTelemetria persistida
    - zero IntegrityError escapando
    - todas as respostas são "criado" ou "duplicata", nunca "erro"

    Nota de portabilidade: SQLite permite apenas um writer por vez.
    O teste usa retry em OperationalError ("locked") para ser portável,
    exatamente como ConcurrencySaveTestCase. O invariante testado é
    que a constraint (device_id, message_id) + o handler de IntegrityError
    garantem count==1 sem exceção escapando.
    """

    def test_race_mesmo_device_mesmo_message_id(self):
        from api_tcc.models import Machine

        # Pré-criar a Machine antes das threads para eliminar contenção
        # no get_or_create da Machine (que é externo à transação atômica).
        Machine.objects.get_or_create(external_code="CONC-SAME")

        num_threads = 20
        barrier = threading.Barrier(num_threads)
        resultados = []
        resultados_lock = threading.Lock()

        payload_base = {
            "maquina_id": "CONC-SAME",
            "device_id": "CONC-SAME",
            "message_id": "msg-race-001",
            "sequence_number": 1,
            "temperatura": 75.0,
            "vibracao": 0.3,
            "rpm": 1800,
            "timestamp": "2026-09-11T10:00:00Z",
            "schema_version": "1.0",
        }

        def tentar_registrar():
            close_old_connections()
            try:
                barrier.wait()
                # Retry em OperationalError (SQLite "locked") — mesmo padrão
                # de ConcurrencySaveTestCase para portabilidade com SQLite.
                for attempt in range(32):
                    try:
                        status, id_ret = registrar_leitura(dict(payload_base))
                        # registrar_leitura captura OperationalError e retorna
                        # ("erro", "database table is locked"). Tratar como
                        # retry transitório, igual ao padrão do SQLite.
                        if status == "erro" and "locked" in (id_ret or "").lower():
                            if attempt < 31:
                                time.sleep(0.02 * (attempt + 1))
                                continue
                        with resultados_lock:
                            resultados.append((status, id_ret))
                        return
                    except Exception as exc:
                        if "locked" not in str(exc).lower() or attempt == 31:
                            with resultados_lock:
                                resultados.append(("excecao", str(exc)))
                            return
                        time.sleep(0.02 * (attempt + 1))
            finally:
                close_old_connections()

        threads = [
            threading.Thread(target=tentar_registrar) for _ in range(num_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Exatamente 1 linha no banco
        self.assertEqual(
            LeituraTelemetria.objects.count(),
            1,
            f"Race condition gerou duplicatas. count={LeituraTelemetria.objects.count()}",
        )

        # Nenhuma thread retornou "erro" ou lançou exceção
        status_invalidos = [
            r for r in resultados if r[0] not in ("criado", "duplicata")
        ]
        self.assertEqual(
            status_invalidos,
            [],
            f"IntegrityError ou erro escapou: {status_invalidos}",
        )

        # Exatamente 1 "criado", restante "duplicata"
        criados = [r for r in resultados if r[0] == "criado"]
        duplicatas = [r for r in resultados if r[0] == "duplicata"]
        self.assertEqual(len(criados), 1, f"Esperado 1 criado, obtido {len(criados)}")
        self.assertEqual(
            len(duplicatas),
            num_threads - 1,
            f"Esperado {num_threads - 1} duplicatas, obtido {len(duplicatas)}",
        )

        # Todos os IDs retornados apontam para a mesma leitura
        ids = {r[1] for r in resultados}
        self.assertEqual(len(ids), 1, f"IDs divergentes: {ids}")


class ConcurrencySaveTestCase(TransactionTestCase):
    """Concurrent inserts rely on the UUID primary key, not a shared sequence."""

    def test_concurrent_telemetry_saves(self):
        num_threads = 20
        barrier = threading.Barrier(num_threads)
        errors = []
        errors_lock = threading.Lock()

        def criar_leitura(index):
            import uuid
            close_old_connections()
            try:
                barrier.wait()
                # SQLite permits one writer at a time. Retrying its transient lock
                # keeps this test portable while every attempt remains a single INSERT.
                for attempt in range(32):
                    try:
                        LeituraTelemetria.objects.create(
                            maquina_id=f"CONC-{index:02d}",
                            device_id=f"CONC-{index:02d}",
                            message_id=str(uuid.uuid4()),
                            temperatura=70.0 + index,
                            vibracao=0.2,
                            rpm=1800 + index,
                            timestamp=timezone.now(),
                        )
                        return
                    except OperationalError as exc:
                        if "locked" not in str(exc).lower() or attempt == 31:
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
