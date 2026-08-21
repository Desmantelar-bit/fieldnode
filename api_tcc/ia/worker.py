"""Supervisao do worker de IA executado em thread daemon.

O processamento em si e fornecido pelo chamador. Assim, este modulo cuida
somente do ciclo de vida da thread e nao duplica regras do pipeline.
"""
import logging
import threading
import time
from collections.abc import Callable
from typing import Optional


logger = logging.getLogger("api_tcc.ia.worker")


def processar_maquinas_ativas() -> None:
    """Analisa cada máquina ativa e persiste o snapshot do ciclo do worker."""
    from api_tcc.ia.pipeline import analisar_maquina
    from api_tcc.models import Colheitadeira

    maquina_ids = (
        Colheitadeira.objects.filter(ativo=True)
        .exclude(maquina_id__isnull=True)
        .exclude(maquina_id="")
        .values_list("maquina_id", flat=True)
    )
    for maquina_id in maquina_ids:
        analisar_maquina(maquina_id, salvar_historico=True)


def worker_loop(processar_fila: Callable[[], None], intervalo_segundos: float = 30) -> None:
    """Executa o processador continuamente sem deixar uma excecao matar a thread."""
    while True:
        try:
            processar_fila()
        except Exception:
            # exception() inclui o traceback, essencial para diagnosticar a falha.
            logger.exception("Erro no worker de IA; continuando apos pausa")

        # Deve permanecer fora do try: falhas consecutivas nao podem gerar busy loop.
        time.sleep(intervalo_segundos)


def iniciar_worker(
    processar_fila: Optional[Callable[[], None]] = None,
    intervalo_segundos: float = 30,
) -> threading.Thread:
    """Inicia o worker; sem callback, processa máquinas ativas com auditoria."""
    processador = processar_fila or processar_maquinas_ativas
    thread = threading.Thread(
        target=worker_loop,
        args=(processador, intervalo_segundos),
        daemon=True,
        name="fieldnode-ia-worker",
    )
    thread.start()
    logger.info("Worker de IA iniciado: %s", thread.name)
    return thread
