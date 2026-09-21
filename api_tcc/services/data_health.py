"""
Telemetry Trust Score heuristics.

S3-T1 implements a deterministic, cheap and explainable score per reading.
The score is an initial calibrable heuristic, not a statistical probability
and not a diagnosis of the sensor or machine.

historico_recente convention: newest reading first, oldest reading last.
"""

from __future__ import annotations

from datetime import datetime
from math import isfinite
from typing import Any, Iterable

from django.db import IntegrityError, transaction

from api_tcc.models import MachineDataHealth
from api_tcc.services.sensor_limits import LIMITES


SENSOR_FIELDS = tuple(LIMITES.keys())
HISTORY_LIMIT = 5

EXPECTED_GAP_SECONDS = 5 * 60
MAX_GAP_SECONDS = 2 * 60 * 60
GAP_PENALTY_MAX = 0.25
OUT_OF_ORDER_PENALTY = 0.30

STUCK_SENSOR_MIN_REPETITIONS = 3
STUCK_SENSOR_STRONG_REPETITIONS = 5
STUCK_SENSOR_PENALTY_PER_FIELD = 0.12
STUCK_SENSOR_PENALTY_MAX = 0.42

RANGE_PROXIMITY_RATIO = 0.05
RANGE_PROXIMITY_PENALTY_PER_FIELD = 0.04
RANGE_PROXIMITY_PENALTY_MAX = 0.12

SMOOTH_CHANGE_RATIO = 0.05
ABRUPT_CHANGE_RATIO = 0.35
CONTINUITY_BONUS = 0.04
ABRUPT_CHANGE_PENALTY = 0.08

TRUST_SCORE_EMA_ALPHA = 0.2
LOW_TRUST_SCORE_THRESHOLD = 0.75

ALERT_SIGNAL_KEYS = (
    "primeira_leitura",
    "gap_temporal",
    "timestamp_fora_de_ordem",
    "timestamp_indisponivel",
    "valores_repetidos",
    "limite_fisico",
    "salto_abrupto",
    "score_baixo",
)


def calcular_trust_score(leitura: Any, historico_recente: Iterable[Any]) -> tuple[float, list[str]]:
    """
    Calculate trust_score for one accepted telemetry reading.

    The function is pure: it does not query the database, mutate inputs, use
    current time, or depend on random state. It returns a float clamped to
    0.0..1.0 plus deterministic, user-readable reasons.
    """
    historico = list(historico_recente)[:HISTORY_LIMIT]
    leitura_anterior = historico[0] if historico else None

    score = 1.0
    motivos: list[str] = []

    score += _penalidade_temporal(leitura, leitura_anterior, motivos)
    score += _penalidade_repeticao(leitura, historico, motivos)
    score += _penalidade_range(leitura, motivos)
    score += _continuidade(leitura, leitura_anterior, motivos)

    return round(_clamp(score), 4), motivos


def atualizar_machine_data_health(
    *,
    machine: Any,
    trust_score: float | None,
    motivos: Iterable[str],
    timestamp: datetime,
) -> MachineDataHealth | None:
    """
    Atualiza o estado agregado da Machine com EMA simples.

    A funcao consome apenas o estado agregado existente + a nova leitura.
    Nao consulta historico completo e nao recalcula trust_score.
    """
    if trust_score is None:
        return None

    score_atual = round(_clamp(float(trust_score)), 4)
    motivos_lista = [str(motivo) for motivo in motivos]
    sinais_atuais = _sinais_de_alerta(motivos_lista, score_atual)

    with transaction.atomic():
        try:
            health = (
                MachineDataHealth.objects
                .select_for_update()
                .get(machine=machine)
            )
        except MachineDataHealth.DoesNotExist:
            sinais = _montar_sinais_de_alerta(
                anteriores={},
                atuais=sinais_atuais,
                motivos=motivos_lista,
            )
            try:
                with transaction.atomic():
                    health, _created = MachineDataHealth.objects.update_or_create(
                        machine=machine,
                        defaults={
                            "trust_score_medio": score_atual,
                            "ultima_atualizacao": timestamp,
                            "leituras_analisadas": 1,
                            "sinais_de_alerta": sinais,
                        },
                    )
                return health
            except IntegrityError:
                health = (
                    MachineDataHealth.objects
                    .select_for_update()
                    .get(machine=machine)
                )

        score_medio = round(
            TRUST_SCORE_EMA_ALPHA * score_atual
            + (1 - TRUST_SCORE_EMA_ALPHA) * health.trust_score_medio,
            4,
        )
        health.trust_score_medio = _clamp(score_medio)
        health.ultima_atualizacao = timestamp
        health.leituras_analisadas += 1
        health.sinais_de_alerta = _montar_sinais_de_alerta(
            anteriores=health.sinais_de_alerta or {},
            atuais=sinais_atuais,
            motivos=motivos_lista,
        )
        health.save(
            update_fields=[
                "trust_score_medio",
                "ultima_atualizacao",
                "leituras_analisadas",
                "sinais_de_alerta",
            ]
        )
        return health


def _penalidade_temporal(leitura: Any, anterior: Any | None, motivos: list[str]) -> float:
    if anterior is None:
        motivos.append("primeira leitura da machine: sem baseline temporal")
        return 0.0

    atual_ts = _get(leitura, "timestamp")
    anterior_ts = _get(anterior, "timestamp")
    if not isinstance(atual_ts, datetime) or not isinstance(anterior_ts, datetime):
        motivos.append("timestamp indisponivel para avaliacao temporal")
        return 0.0

    delta_seconds = (atual_ts - anterior_ts).total_seconds()
    if delta_seconds < 0:
        motivos.append("timestamp fora de ordem em relacao a leitura anterior")
        return -OUT_OF_ORDER_PENALTY

    if delta_seconds <= EXPECTED_GAP_SECONDS:
        motivos.append("gap temporal dentro da heuristica inicial esperada")
        return 0.0

    excess = min(delta_seconds - EXPECTED_GAP_SECONDS, MAX_GAP_SECONDS - EXPECTED_GAP_SECONDS)
    denominator = max(MAX_GAP_SECONDS - EXPECTED_GAP_SECONDS, 1)
    penalty = GAP_PENALTY_MAX * (excess / denominator)
    motivos.append("gap temporal acima da heuristica inicial esperada")
    return -penalty


def _penalidade_repeticao(leitura: Any, historico: list[Any], motivos: list[str]) -> float:
    repeated_fields: list[str] = []

    for field in SENSOR_FIELDS:
        atual = _numeric(leitura, field)
        if atual is None:
            continue

        repetition_count = 1
        for item in historico:
            anterior = _numeric(item, field)
            if anterior is None or anterior != atual:
                break
            repetition_count += 1

        if repetition_count >= STUCK_SENSOR_MIN_REPETITIONS:
            repeated_fields.append(f"{field} x{repetition_count}")

    if not repeated_fields:
        return 0.0

    max_repetitions = max(int(entry.rsplit("x", 1)[1]) for entry in repeated_fields)
    severity = min(max_repetitions, STUCK_SENSOR_STRONG_REPETITIONS) - (STUCK_SENSOR_MIN_REPETITIONS - 1)
    penalty = min(
        len(repeated_fields) * STUCK_SENSOR_PENALTY_PER_FIELD * severity,
        STUCK_SENSOR_PENALTY_MAX,
    )
    motivos.append(
        "valores repetidos consecutivamente: possivel sensor travado ("
        + ", ".join(repeated_fields)
        + ")"
    )
    return -penalty


def _penalidade_range(leitura: Any, motivos: list[str]) -> float:
    near_limits: list[str] = []

    for field, (minimum, maximum) in LIMITES.items():
        value = _numeric(leitura, field)
        if value is None:
            continue

        span = float(maximum) - float(minimum)
        if span <= 0:
            continue

        distance_to_edge = min(value - float(minimum), float(maximum) - value)
        if distance_to_edge <= span * RANGE_PROXIMITY_RATIO:
            near_limits.append(field)

    if not near_limits:
        return 0.0

    penalty = min(
        len(near_limits) * RANGE_PROXIMITY_PENALTY_PER_FIELD,
        RANGE_PROXIMITY_PENALTY_MAX,
    )
    motivos.append("leitura proxima ao limite fisico conhecido: " + ", ".join(near_limits))
    return -penalty


def _continuidade(leitura: Any, anterior: Any | None, motivos: list[str]) -> float:
    if anterior is None:
        return 0.0

    comparable = 0
    smooth = 0
    abrupt = 0

    for field, (minimum, maximum) in LIMITES.items():
        atual = _numeric(leitura, field)
        previo = _numeric(anterior, field)
        if atual is None or previo is None:
            continue

        span = float(maximum) - float(minimum)
        if span <= 0:
            continue

        comparable += 1
        change_ratio = abs(atual - previo) / span
        if change_ratio <= SMOOTH_CHANGE_RATIO:
            smooth += 1
        elif change_ratio >= ABRUPT_CHANGE_RATIO:
            abrupt += 1

    if comparable == 0:
        return 0.0

    if abrupt:
        motivos.append("salto abrupto em relacao a leitura anterior")
        return -ABRUPT_CHANGE_PENALTY

    if smooth == comparable:
        motivos.append("continuidade suave em relacao a leitura anterior")
        return CONTINUITY_BONUS

    return 0.0


def _sinais_de_alerta(motivos: list[str], trust_score: float) -> dict[str, bool]:
    texto = " | ".join(motivos).lower()
    return {
        "primeira_leitura": "primeira leitura" in texto,
        "gap_temporal": "gap temporal acima" in texto,
        "timestamp_fora_de_ordem": "fora de ordem" in texto,
        "timestamp_indisponivel": "timestamp indisponivel" in texto,
        "valores_repetidos": "repetidos consecutivamente" in texto,
        "limite_fisico": "limite fisico" in texto,
        "salto_abrupto": "salto abrupto" in texto,
        "score_baixo": trust_score < LOW_TRUST_SCORE_THRESHOLD,
    }


def _montar_sinais_de_alerta(
    *,
    anteriores: dict[str, Any],
    atuais: dict[str, bool],
    motivos: list[str],
) -> dict[str, Any]:
    contadores_anteriores = anteriores.get("contadores", {})
    contadores = {
        key: int(contadores_anteriores.get(key, 0)) + (1 if atuais.get(key) else 0)
        for key in ALERT_SIGNAL_KEYS
    }
    payload = {key: bool(atuais.get(key, False)) for key in ALERT_SIGNAL_KEYS}
    payload["contadores"] = contadores
    payload["ultimos_motivos"] = motivos
    return payload


def _get(obj: Any, field: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(field)
    return getattr(obj, field, None)


def _numeric(obj: Any, field: str) -> float | None:
    value = _get(obj, field)
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(numeric):
        return None
    return numeric


def _clamp(value: float) -> float:
    if not isfinite(value):
        return 0.0
    return max(0.0, min(1.0, value))
