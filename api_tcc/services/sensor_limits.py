"""
Shared physical limits for telemetry sensors.

These ranges describe payload acceptance boundaries. Values outside them are
treated as sensor faults by validar_payload(); values near the edges can still
be accepted, but reduce trust_score as an initial calibrable heuristic.
"""

LIMITES = {
    "temperatura": (0.0, 150.0),  # Celsius
    "vibracao": (0.0, 10.0),
    "rpm": (0, 5000),
}
