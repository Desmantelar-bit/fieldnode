"""Consequence Engine v0.1: regras explícitas e estimativas rastreáveis."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from django.utils import timezone

from api_tcc.models import Event, LeituraTelemetria, Machine, MachineLink, OrganizationPolicy
from api_tcc.services.operation_graph import afetados_por


RULE_VERSION = "consequence-v0.1"
WINDOW_MINUTES = 30
MIN_POINTS = 3
R2_MIN = 0.80


@dataclass(frozen=True)
class Trend:
    valor_atual: float
    inclinacao: float
    r2: float
    pontos: int
    unidade_tempo: str = "°C/min"


@dataclass
class ConsequenceAssessment:
    event_id: str
    rule_version: str = RULE_VERSION
    afetados: list[dict[str, Any]] = field(default_factory=list)
    risco_parada: str = "desconhecido"
    horizonte_minutos: float | None = None
    horizonte_tipo: str | None = None
    premissas: list[str] = field(default_factory=list)
    faltantes: list[str] = field(default_factory=list)
    confianca: str = "insuficiente"
    needs_verification: bool = False
    custo_estimado: Decimal | None = None
    moeda: str | None = None
    custo_hora_parada_utilizado: Decimal | None = None
    origem_premissa: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "event_id": self.event_id,
            "rule_version": self.rule_version,
            "afetados": self.afetados,
            "risco_parada": self.risco_parada,
            "horizonte_minutos": self.horizonte_minutos,
            "horizonte_tipo": self.horizonte_tipo,
            "premissas": self.premissas,
            "faltantes": self.faltantes,
            "confianca": self.confianca,
            "needs_verification": self.needs_verification,
        }
        if self.custo_estimado is not None:
            payload.update({
                "custo_estimado": str(self.custo_estimado),
                "moeda": self.moeda,
                "custo_hora_parada_utilizado": str(self.custo_hora_parada_utilizado),
                "origem_premissa": self.origem_premissa,
            })
        return payload


def _aplicar_premissa_financeira(assessment: ConsequenceAssessment, event: Event) -> None:
    """Calcula custo somente com política da própria organização e horizonte válido."""

    if assessment.horizonte_minutos is None or assessment.horizonte_minutos <= 0:
        return
    organization_id = getattr(event.machine, "organization_id", None)
    if organization_id is None:
        return
    try:
        policy = OrganizationPolicy.objects.get(organization_id=organization_id)
    except OrganizationPolicy.DoesNotExist:
        return
    if policy.custo_hora_parada is None or policy.moeda != "BRL":
        return
    try:
        horizon = Decimal(str(assessment.horizonte_minutos))
        cost = (policy.custo_hora_parada * horizon / Decimal("60")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    except (InvalidOperation, TypeError, ValueError):
        return
    assessment.custo_estimado = cost
    assessment.moeda = policy.moeda
    assessment.custo_hora_parada_utilizado = policy.custo_hora_parada
    assessment.origem_premissa = "premissa informada pelo cliente; estimativa matemática"


def _temperature_limit(machine: Machine) -> float | None:
    """Lê somente um limite explicitamente cadastrado; não cria fallback."""

    try:
        raw = machine.spec.limites_json.get("temperatura", {}).get("critico")
    except AttributeError:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def tendencia_linear(
    machine: Machine,
    parametro: str = "temperatura",
    *,
    em: datetime | None = None,
    janela_min: int = WINDOW_MINUTES,
) -> Trend | None:
    """Calcula regressão linear em °C/min para uma única máquina.

    A série é elegível apenas com três pontos válidos e dois timestamps
    distintos. R² e inclinação são calculados sem dependência estatística nova.
    """

    if parametro != "temperatura":
        return None
    reference = em or timezone.now()
    start = reference - timedelta(minutes=janela_min)
    rows = list(
        LeituraTelemetria.objects.filter(
            machine=machine,
            timestamp__gte=start,
            timestamp__lte=reference,
        )
        .exclude(timestamp__isnull=True)
        .order_by("timestamp", "id")
        .values_list("timestamp", "temperatura")
    )
    points = []
    for timestamp, value in rows:
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(number):
            points.append(((timestamp - start).total_seconds() / 60.0, number))
    if len(points) < MIN_POINTS or len({x for x, _ in points}) < 2:
        return None

    mean_x = sum(x for x, _ in points) / len(points)
    mean_y = sum(y for _, y in points) / len(points)
    ss_x = sum((x - mean_x) ** 2 for x, _ in points)
    if ss_x <= 0:
        return None
    slope = sum((x - mean_x) * (y - mean_y) for x, y in points) / ss_x
    intercept = mean_y - slope * mean_x
    ss_tot = sum((y - mean_y) ** 2 for _, y in points)
    if ss_tot <= 0:
        return None
    ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in points)
    r2 = 1.0 - ss_res / ss_tot
    current = points[-1][1]
    if not all(math.isfinite(value) for value in (slope, r2, current)):
        return None
    return Trend(current, slope, max(0.0, min(1.0, r2)), len(points))


def avaliar(event: Event, *, em: datetime | None = None) -> ConsequenceAssessment:
    assessment = ConsequenceAssessment(event_id=str(event.pk))
    reference = em or timezone.now()

    try:
        affected = afetados_por(
            event.machine,
            em=reference,
            organization=event.machine.organization,
        )
    except Exception:
        # A falha de consulta não pode virar uma lista vazia silenciosa.
        assessment.faltantes.append("não foi possível consultar os vínculos operacionais")
        assessment.confianca = "insuficiente"
        return assessment

    assessment.afetados = [
        {
            "machine_id": str(item["machine"].pk),
            "codigo": item["machine"].external_code,
            "tipo": item["machine"].tipo,
            "distance": item["distance"],
            "path": [link.tipo for link in item["path"]],
        }
        for item in affected
    ]
    if not assessment.afetados:
        assessment.faltantes.append("não existem vínculos operacionais cadastrados para esta máquina")

    eligible = {
        Event.Tipo.TEMP_ALTA,
        Event.Tipo.ANOMALIA_ML,
        Event.Tipo.VIBRACAO_ALTA,
    }
    if event.severidade == Event.Severidade.CRITICO and event.tipo in eligible:
        if event.evidence_quality == "boa":
            assessment.risco_parada = "alto"
        elif event.evidence_quality == "suspeita":
            assessment.risco_parada = "medio"
            assessment.needs_verification = True
            assessment.faltantes.append("evidência suspeita: verificar sensor")
        else:
            assessment.needs_verification = True
            assessment.faltantes.append("evidência insuficiente para classificar o risco")
    else:
        assessment.faltantes.append("evento não atende à regra de risco v0.1")

    for item in affected:
        machine = item["machine"]
        if machine.tipo == "transbordo":
            capacity = None
            try:
                capacity = machine.spec.limites_json.get("capacidade_t")
            except AttributeError:
                pass
            if capacity in (None, ""):
                assessment.faltantes.append(
                    f"capacidade do {machine.external_code} para estimar espera"
                )

    trend = tendencia_linear(event.machine, "temperatura", em=reference)
    limit = _temperature_limit(event.machine)
    if trend is None:
        assessment.faltantes.append("tendência confiável para estimar tempo até o limite")
    elif limit is None:
        assessment.faltantes.append("limite crítico de temperatura não cadastrado")
    elif trend.r2 >= R2_MIN and trend.inclinacao > 0 and limit > trend.valor_atual:
        horizon = (limit - trend.valor_atual) / trend.inclinacao
        if math.isfinite(horizon) and horizon > 0:
            assessment.horizonte_minutos = round(horizon, 2)
            assessment.horizonte_tipo = "estimativa por extrapolação linear"
            assessment.premissas.append(
                "estimativa por extrapolação linear: "
                f"temperatura, {trend.pontos} pontos, janela {WINDOW_MINUTES} min, "
                f"inclinação {trend.inclinacao:.4f} °C/min, R²={trend.r2:.2f}, "
                f"limite cadastrado {limit:g} °C"
            )
    else:
        assessment.faltantes.append(
            "tendência sem R² mínimo, crescente, ou com limite já atingido"
        )

    _aplicar_premissa_financeira(assessment, event)

    if assessment.horizonte_minutos is not None and not assessment.faltantes:
        assessment.confianca = "alta"
    elif assessment.risco_parada in {"alto", "medio"} and assessment.premissas:
        assessment.confianca = "moderada"
    elif assessment.premissas:
        assessment.confianca = "baixa"
    else:
        assessment.confianca = "insuficiente"
    return assessment
