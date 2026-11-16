#!/usr/bin/env python3
"""Calcula capacidade do outbox com premissas explícitas.

Todos os valores de entrada são premissas; uma medição real pode ser passada
por cenário. A ferramenta não transforma compressão estimada em evidência.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CapacityResult:
    duration_hours: float
    messages: int
    raw_bytes: float
    estimated_bytes: float
    raw_mb: float
    estimated_mb: float
    estimated_gb: float


def capacidade(msgs_por_s: float = 0.5, bytes_msg: float = 220,
               horas: float | None = None, dias: float | None = None,
               overhead: float = 0.6, compressao_C: float = 1.0,
               frac_C: float = 0.0, margem: float = 0.0) -> CapacityResult:
    if msgs_por_s <= 0 or bytes_msg <= 0:
        raise ValueError("msgs_por_s e bytes_msg devem ser positivos")
    if horas is None and dias is None:
        raise ValueError("informe horas ou dias")
    duration_hours = float(horas if horas is not None else float(dias) * 24)
    if duration_hours <= 0 or overhead < 0 or not 0 <= frac_C <= 1:
        raise ValueError("duração, overhead e frac_C são incoerentes")
    if not 0 < compressao_C <= 1:
        raise ValueError("compressao_C deve estar entre 0 e 1")
    seconds = duration_hours * 3600
    messages = int(round(msgs_por_s * seconds))
    raw = msgs_por_s * bytes_msg * seconds
    class_factor = frac_C * compressao_C + (1 - frac_C)
    estimated = raw * class_factor * (1 + overhead) * (1 + margem)
    return CapacityResult(duration_hours, messages, raw, estimated,
                          raw / 1e6, estimated / 1e6, estimated / 1e9)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rate", type=float, default=0.5, help="mensagens por segundo")
    parser.add_argument("--bytes", dest="bytes_msg", type=float, default=220)
    parser.add_argument("--overhead", type=float, default=0.60)
    parser.add_argument("--compression-c", type=float, default=1.0)
    parser.add_argument("--fraction-c", type=float, default=0.0)
    parser.add_argument("--margin", type=float, default=0.0)
    parser.add_argument("--hours", type=float, nargs="*")
    parser.add_argument("--days", type=float, nargs="*")
    return parser


def main() -> int:
    args = _parser().parse_args()
    durations = [("hours", value) for value in (args.hours or [])]
    durations += [("days", value) for value in (args.days or [])]
    if not durations:
        durations = [("days", value) for value in (0.5 / 24, 5 / 24, 6 / 24, 1, 3, 7, 14)]
    results = []
    for unit, value in durations:
        result = capacidade(msgs_por_s=args.rate, bytes_msg=args.bytes_msg,
                            horas=value if unit == "hours" else None,
                            dias=value if unit == "days" else None,
                            overhead=args.overhead, compressao_C=args.compression_c,
                            frac_C=args.fraction_c, margem=args.margin)
        results.append(asdict(result))
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
