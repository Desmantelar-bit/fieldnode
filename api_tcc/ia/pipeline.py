"""
api_tcc/ia/pipeline.py

Pipeline centralizado de leitura e execucao dos modelos de IA.

Views e futuros workers devem chamar este modulo em vez de montar queries e
orquestrar modelos por conta propria. Menos duplicacao, menos surpresa, menos
API esperando cada pedaco do sistema bancar o chef e o garcom ao mesmo tempo.
"""
import logging
from queue import Empty, Queue
from threading import Event, Thread

import pandas as pd

from api_tcc.models import LeituraTelemetria

logger = logging.getLogger(__name__)
_ia_work_queue = Queue()
_stop_ia_worker = Event()


def _ia_worker():
    logger.info("Worker de IA em background iniciado")
    while not _stop_ia_worker.is_set():
        try:
            maquina_id, modelos = _ia_work_queue.get(timeout=1.0)
        except Empty:
            continue

        try:
            logger.debug(
                "Processando IA em background para %s, modelos=%s",
                maquina_id,
                modelos,
            )
            rodar_modelos(maquina_id, modelos=modelos)
        except Exception:
            logger.exception(
                "Falha no processamento de IA agendado para %s", maquina_id
            )
        finally:
            _ia_work_queue.task_done()


def agendar_processamento_ia(maquina_id, modelos=None):
    """Enfileira o processamento de IA e retorna imediatamente."""
    if not maquina_id:
        return {
            "status": "erro",
            "detalhe": "maquina_id e obrigatorio",
        }

    modelos = tuple(modelos) if modelos else ("anomalias", "estado", "manutencao")
    _ia_work_queue.put((maquina_id, modelos))

    return {
        "status": "agendado",
        "maquina_id": maquina_id,
        "modelos": list(modelos),
    }


def carregar_dados(maquina_id, limite=300, minimo=10):
    """
    Carrega as ultimas leituras validas de uma maquina como DataFrame.

    Retorna um dict de erro quando nao ha maquina_id ou quando nao existe volume
    minimo de dados para os modelos.
    """
    if not maquina_id:
        return {
            "status": "erro",
            "detalhe": "maquina_id e obrigatorio",
        }

    registros = list(
        LeituraTelemetria.objects.filter(maquina_id=maquina_id)
        .order_by("-timestamp")
        .values("id", "maquina_id", "temperatura", "vibracao", "rpm", "timestamp")[:limite]
    )

    if len(registros) < minimo:
        return {
            "status": "dados_insuficientes",
            "minimo": minimo,
            "atual": len(registros),
        }

    df = pd.DataFrame(registros).dropna()

    if len(df) < minimo:
        return {
            "status": "dados_insuficientes",
            "minimo": minimo,
            "atual": len(df),
        }

    return df


def rodar_modelos(maquina_id, modelos=None):
    """
    Executa modelos por um ponto unico de entrada.

    Imports locais evitam ciclo entre modulos. Esse contrato tambem permite
    plugar um worker de background depois sem reescrever as views.
    """
    if not maquina_id:
        return {"status": "erro", "detalhe": "maquina_id e obrigatorio"}

    modelos = set(modelos or ("anomalias", "estado", "manutencao"))
    resultado = {"status": "ok", "maquina_id": maquina_id}

    if "anomalias" in modelos:
        from api_tcc.ia.anomalias import detectar_anomalias

        resultado["anomalias"] = detectar_anomalias(maquina_id=maquina_id)

    if "estado" in modelos:
        from api_tcc.ia.estado import classificar_estado

        resultado["estado"] = classificar_estado(maquina_id=maquina_id)

    if "manutencao" in modelos:
        from api_tcc.ia.manutencao import prever_manutencao

        resultado["manutencao"] = prever_manutencao(maquina_id=maquina_id)

    if "prescricao" in modelos:
        from api_tcc.ia.prescricoes import gerar_prescricao

        resultado["prescricao"] = gerar_prescricao(maquina_id=maquina_id)

    return resultado


_thread = Thread(target=_ia_worker, daemon=True, name="FieldNodeIAWorker")
_thread.start()
