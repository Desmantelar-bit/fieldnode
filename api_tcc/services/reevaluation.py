"""Reavaliação determinística e rastreável de uma WorkOrder."""

from collections.abc import Iterable, Mapping
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from api_tcc.models import LeituraTelemetria, Reevaluation, WorkOrder


RESULTS = Reevaluation.Resultado
TRUSTED_TIME_SOURCES = {"rtc", "gateway", "ntp"}


def _reading_value(reading, parameter):
    return reading.get(parameter) if isinstance(reading, Mapping) else getattr(reading, parameter, None)


def _reading_id(reading):
    value = reading.get("id") if isinstance(reading, Mapping) else getattr(reading, "id", None)
    return str(value) if value is not None else None


def _reading_time(reading):
    value = reading.get("event_time") if isinstance(reading, Mapping) else getattr(reading, "timestamp", None)
    return value


def _valid_series(series: Iterable, rule: Mapping):
    parameter = rule.get("parameter")
    origin = None
    unique = {}
    for reading in series:
        event_time = _reading_time(reading)
        value = _reading_value(reading, parameter)
        source = reading.get("time_source") if isinstance(reading, Mapping) else getattr(reading, "time_source", None)
        confidence = reading.get("event_time_confidence") if isinstance(reading, Mapping) else getattr(reading, "event_time_confidence", 0)
        data_origin = reading.get("data_origin") if isinstance(reading, Mapping) else getattr(reading, "data_origin", None)
        if event_time is None or value is None or source not in TRUSTED_TIME_SOURCES or float(confidence or 0) < 0.5 or not data_origin:
            continue
        if origin is None:
            origin = data_origin
        if data_origin != origin:
            return None, "origens de dados misturadas"
        key = _reading_id(reading) or f"{event_time.isoformat()}:{value}"
        unique[key] = (event_time, float(value), _reading_id(reading))
    return sorted(unique.values(), key=lambda item: item[0]), None


def _percentage(series, rule):
    direction = rule.get("direction")
    threshold = rule.get("threshold")
    if direction not in {"above", "below"} or not isinstance(threshold, (int, float)):
        return None
    matches = sum(value >= threshold if direction == "above" else value <= threshold for _, value, _ in series)
    return matches / len(series)


def avaliar(antes, depois, regra):
    """Classifica duas séries usando somente uma regra explícita e versionada."""
    required = {"version", "parameter", "threshold", "direction", "min_readings", "cessou_at_most", "persiste_at_least", "before_window_minutes", "after_window_minutes"}
    if not isinstance(regra, Mapping) or not required.issubset(regra) or regra.get("min_readings", 0) <= 0:
        return RESULTS.DADOS_INSUFICIENTES
    before, before_error = _valid_series(antes, regra)
    after, after_error = _valid_series(depois, regra)
    minimum = int(regra["min_readings"])
    if before_error or after_error or before is None or after is None or len(before) < minimum or len(after) < minimum:
        return RESULTS.DADOS_INSUFICIENTES
    before_pct = _percentage(before, regra)
    after_pct = _percentage(after, regra)
    if before_pct is None or after_pct is None or before_pct < float(regra.get("persiste_at_least", 0)):
        return RESULTS.DADOS_INSUFICIENTES
    if after_pct <= float(regra["cessou_at_most"]):
        return RESULTS.SINTOMA_CESSOU
    if after_pct >= float(regra["persiste_at_least"]):
        return RESULTS.SINTOMA_PERSISTE
    return RESULTS.DADOS_INSUFICIENTES


def _policy_for(order):
    policy = getattr(order.machine.organization, "policy", None)
    config = (policy.reevaluation_policy or {}) if policy else {}
    return config.get(str(order.decision_id)) or config.get(order.decision.severidade) or config.get("default")


def reevaluate_work_order(order: WorkOrder):
    rule = _policy_for(order)
    if not isinstance(rule, dict) or not rule.get("version"):
        rule = {"version": "unconfigured", "parameter": "temperatura", "reason": "política de reavaliação não configurada"}
    version = str(rule["version"])
    reference = order.concluida_em or order.decision.decidido_em
    if reference is None:
        result = RESULTS.DADOS_INSUFICIENTES
        reason = "ordem ainda não foi concluída"
        before = after = []
    else:
        queryset = LeituraTelemetria.objects.filter(machine=order.machine, timestamp__isnull=False).order_by("timestamp", "id")
        all_readings = list(queryset)
        before_start = reference - timedelta(minutes=int(rule["before_window_minutes"]))
        after_end = reference + timedelta(minutes=int(rule["after_window_minutes"]))
        before = [reading for reading in all_readings if before_start <= reading.timestamp <= reference]
        after = [reading for reading in all_readings if reference < reading.timestamp <= after_end]
        result = avaliar(before, after, rule)
        reason = "" if result != RESULTS.DADOS_INSUFICIENTES else "leituras insuficientes ou regra sem parâmetros válidos"
    with transaction.atomic():
        record, _ = Reevaluation.objects.get_or_create(work_order=order, regra_versao=version, defaults={"decision": order.decision, "machine": order.machine, "regra": rule, "resultado": result})
        if record.resultado == RESULTS.DADOS_INSUFICIENTES or record.resultado == result:
            record.regra = rule
            record.resultado = result
            record.referencia_conclusao = reference
            record.janela_antes_inicio = reference - timedelta(minutes=int(rule["before_window_minutes"])) if reference and "before_window_minutes" in rule else None
            record.janela_antes_fim = reference
            record.janela_depois_inicio = reference
            record.janela_depois_fim = reference + timedelta(minutes=int(rule["after_window_minutes"])) if reference and "after_window_minutes" in rule else None
            record.leituras_antes = len(before)
            record.leituras_depois = len(after)
            record.leitura_ids_antes = [_reading_id(item) for item in before]
            record.leitura_ids_depois = [_reading_id(item) for item in after]
            record.motivo_insuficiencia = reason
            record.origem_dados = next((getattr(item, "data_origin", "") for item in before + after if getattr(item, "data_origin", "")), "")
            record.metricas = {"antes": _percentage(_valid_series(before, rule)[0], rule) if before and "threshold" in rule else None, "depois": _percentage(_valid_series(after, rule)[0], rule) if after and "threshold" in rule else None}
            record.save()
    return record
