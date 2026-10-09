"""Normalizacao v0.1 de telemetria bruta para parametros canonicos."""

from api_tcc.models import CanonicalTelemetry, FabricanteMapping, RawTelemetry


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

    raw_telemetry.quality = "mapped"
    raw_telemetry.save(update_fields=["quality"])
    canonical, _ = CanonicalTelemetry.objects.get_or_create(
        raw_telemetry=raw_telemetry,
        canonical_parameter=mapping.canonical_parameter,
        defaults={
            "value": raw_telemetry.raw_value * mapping.unit_conversion_factor,
            "unit": raw_telemetry.unit,
            "quality": "mapped",
            "mapping_version": mapping.mapping_version,
        },
    )
    return canonical


def registrar_e_normalizar(
    *, machine, manufacturer, raw_parameter, raw_value, unit, source_protocol_simulado, payload_original
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
    )
    return raw, normalizar(raw)
