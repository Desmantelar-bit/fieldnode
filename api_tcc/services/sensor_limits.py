"""
Shared physical limits for telemetry sensors.

These ranges describe payload acceptance boundaries. Values outside them are
treated as sensor faults by validar_payload(); values near the edges can still
be accepted, but reduce trust_score as an initial calibrable heuristic.
"""

from api_tcc.contracts import severity_contract

LIMITES = {
    metric: tuple(definition["range"])
    for metric, definition in severity_contract()["metrics"].items()
}
