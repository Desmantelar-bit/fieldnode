"""Reconstrucao temporal localizada para leituras recebidas fora de ordem.

O servico trabalha com ``timestamp`` (event_time) para ordenar e deixa
``recebido_em`` intacto para auditoria. Ele recalcula somente a vizinhanca da
leitura tardia; nao transforma a ingestao em um replay do historico inteiro.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from api_tcc.models import LeituraTelemetria
from api_tcc.services.data_health import HISTORY_LIMIT, calcular_trust_score

logger = logging.getLogger(__name__)

# Cinco minutos e uma regra operacional explicita, nao uma afirmacao de
# sincronizacao fisica. Pode ser substituida por configuracao no futuro.
ATRASO_PADRAO = timedelta(minutes=5)


@dataclass(frozen=True)
class ResultadoReconstrucao:
    inicio: object
    fim: object
    leituras_recalculadas: int
    gaps_recalculados: int = 0


def identificar_atraso(*, event_time, received_at, time_source, clock_skew_ms=None,
                       limite: timedelta = ATRASO_PADRAO) -> bool:
    """Marca atraso somente quando a referencia temporal e utilizavel."""
    if event_time is None or received_at is None or time_source == "unsynced":
        return False
    try:
        skew = timedelta(milliseconds=int(clock_skew_ms or 0))
    except (TypeError, ValueError, OverflowError):
        skew = timedelta(0)
    return received_at - event_time - skew > limite


def reconstruir_janela(*, machine, event_time, margem: timedelta = ATRASO_PADRAO) -> ResultadoReconstrucao:
    """Recalcula Trust Score na janela afetada e preserva idempotencia.

    A margem representa a vizinhanca temporal da leitura. O contexto anterior
    limitado a HISTORY_LIMIT fornece o baseline sem tocar periodos distantes.
    """
    inicio = event_time - margem
    fim = event_time + margem
    with transaction.atomic():
        leituras = list(
            LeituraTelemetria.objects.select_for_update()
            .filter(machine=machine, timestamp__gte=inicio, timestamp__lte=fim)
            .order_by("timestamp", "sequence_number", "id")
        )
        if not leituras:
            return ResultadoReconstrucao(inicio, fim, 0)

        anterior = list(
            LeituraTelemetria.objects
            .filter(machine=machine, timestamp__lt=inicio)
            .order_by("-timestamp", "-sequence_number")[:HISTORY_LIMIT]
        )
        recalculadas = 0
        for leitura in leituras:
            historico = anterior[:HISTORY_LIMIT]
            score, motivos = calcular_trust_score(leitura, historico)
            if leitura.trust_score != score or leitura.trust_factors != motivos:
                leitura.trust_score = score
                leitura.trust_factors = motivos
                leitura.save(update_fields=["trust_score", "trust_factors"])
                recalculadas += 1
            anterior.insert(0, leitura)
            anterior = anterior[:HISTORY_LIMIT]

        logger.info(
            "Reconstrucao temporal: machine=%s inicio=%s fim=%s recalculadas=%d",
            getattr(machine, "external_code", machine), inicio, fim, recalculadas,
        )
        return ResultadoReconstrucao(inicio, fim, recalculadas)


def reconstruir_para_leitura(leitura: LeituraTelemetria) -> ResultadoReconstrucao | None:
    if not leitura.timestamp or not leitura.atrasado or not leitura.machine:
        return None
    return reconstruir_janela(machine=leitura.machine, event_time=leitura.timestamp)
