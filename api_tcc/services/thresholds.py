"""Thresholds effective for a machine, with contract safety as the final authority."""

import math
from datetime import timedelta

from django.utils import timezone

from api_tcc.contracts import metric_definition
from api_tcc.models import Machine, ThresholdOverride


def _number(value, field):
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} deve ser numerico") from None
    if not math.isfinite(result):
        raise ValueError(f"{field} deve ser finito")
    return result


def effective_thresholds(machine: Machine, metric: str, *, at=None) -> dict:
    contract = metric_definition(metric)
    if "critico" not in contract or "atencao" not in contract:
        raise ValueError(f"metrica sem limiares calibraveis: {metric}")
    at = at or timezone.now()
    piso, teto = contract["range"][0], contract["critico"]
    override = (
        ThresholdOverride.objects.filter(machine=machine, metric=metric, expira_em__gt=at)
        .order_by("-criado_em")
        .first()
    )
    requested = {
        "atencao": contract["atencao"],
        "critico": contract["critico"],
    }
    spec = getattr(machine, "spec", None)
    spec_values = spec.limites_json.get(metric) if spec and isinstance(spec.limites_json, dict) else None
    if isinstance(spec_values, dict) and "atencao" in spec_values and "critico" in spec_values:
        requested = {"atencao": spec_values["atencao"], "critico": spec_values["critico"]}
        source = "machine_spec_clamped"
    else:
        source = "contrato_central"
    if override is not None:
        requested = {"atencao": override.atencao, "critico": override.critico}
        source = "threshold_override_clamped"
    critico = min(max(_number(requested["critico"], "critico"), piso), teto)
    atencao = min(max(_number(requested["atencao"], "atencao"), piso), critico)
    return {
        "metric": metric,
        "atencao": atencao,
        "critico": critico,
        "contrato_atencao": contract["atencao"],
        "contrato_critico": contract["critico"],
        "override_id": str(override.id) if override is not None else None,
        "expira_em": override.expira_em if override is not None else None,
        "limite_origem": source,
        "limite_especifico_aplicado": source != "contrato_central",
    }


def create_threshold_override(*, machine, metric, atencao, critico, motivo, criado_por, expira_em):
    if not isinstance(machine, Machine):
        raise ValueError("maquina invalida")
    definition = metric_definition(metric)
    if "critico" not in definition or "atencao" not in definition:
        raise ValueError("metrica nao possui contrato de limiar fixo")
    atencao = _number(atencao, "atencao")
    critico = _number(critico, "critico")
    if not str(motivo or "").strip():
        raise ValueError("motivo obrigatorio")
    if expira_em <= timezone.now():
        raise ValueError("expira_em deve estar no futuro")
    piso, teto = definition["range"][0], definition["critico"]
    if not piso <= atencao <= critico <= teto:
        raise ValueError(f"limiares devem respeitar a faixa segura [{piso}, {teto}]")
    return ThresholdOverride.objects.create(
        machine=machine,
        metric=metric,
        atencao=atencao,
        critico=critico,
        motivo=str(motivo).strip(),
        criado_por=criado_por,
        expira_em=expira_em,
    )


def classify_machine_metric(machine, metric, value, *, at=None):
    value = _number(value, metric)
    thresholds = effective_thresholds(machine, metric, at=at)
    if value >= thresholds["critico"]:
        return "CRITICO"
    if value >= thresholds["atencao"]:
        return "ATENCAO"
    return "NORMAL"
