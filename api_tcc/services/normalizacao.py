"""Normalizacao v0.1 de telemetria bruta para parametros canonicos."""

from api_tcc.models import CanonicalTelemetry, FabricanteMapping, RawTelemetry
from api_tcc.services.conversoes import convert_value


def normalizar(raw_telemetry: RawTelemetry) -> CanonicalTelemetry | None:
    """Normaliza um registro bruto usando o mapeamento ativo mais recente.

    Retorna None para parametros ainda nao suportados. O bruto permanece
    persistido e recebe quality=unsupported_parameter; isso e intencional para
    nao transformar falta de adaptador em perda silenciosa de dado.
    """
    mapping = (
        FabricanteMapping.objects.filter(
            manufacturer=raw_telemetry.manufacturer,
            raw_parameter=raw_telemetry.raw_parameter,
            ativo=True,
        )
        .order_by("-mapping_version", "-id")
        .first()
    )
    if mapping is None:
        if raw_telemetry.quality != "unsupported_parameter":
            raw_telemetry.quality = "unsupported_parameter"
            raw_telemetry.save(update_fields=["quality"])
        return None

    try:
        value, unit, factor, offset = convert_value(
            raw_telemetry.raw_value,
            raw_telemetry.unit,
            mapping.canonical_parameter,
        )
    except ValueError:
        raw_telemetry.quality = "unsupported_unit"
        raw_telemetry.save(update_fields=["quality"])
        return None

    raw_telemetry.quality = "mapped"
    raw_telemetry.save(update_fields=["quality"])
    canonical, _ = CanonicalTelemetry.objects.get_or_create(
        raw_telemetry=raw_telemetry,
        canonical_parameter=mapping.canonical_parameter,
        defaults={
            "value": value * mapping.unit_conversion_factor + mapping.unit_conversion_offset,
            "unit": unit,
            "quality": "mapped",
            "mapping_version": mapping.mapping_version,
            "origem": raw_telemetry.origem,
            "fonte": raw_telemetry.source_protocol_simulado,
            "unidade_original": raw_telemetry.unit,
            "fator_conversao": factor,
            "offset_conversao": offset,
        },
    )
    return canonical


def registrar_e_normalizar(
    *, machine, manufacturer, raw_parameter, raw_value, unit, source_protocol_simulado,
    payload_original, origem="simulado"
):
    """Persiste o bruto antes de tentar normaliza-lo."""
    raw = RawTelemetry.objects.create(
        machine=machine,
        manufacturer=manufacturer,
        raw_parameter=raw_parameter,
        raw_value=float(raw_value),
        unit=unit or "",
        source_protocol_simulado=source_protocol_simulado,
        payload_original=dict(payload_original),
        origem=origem or "simulado",
    )
    return raw, normalizar(raw)
