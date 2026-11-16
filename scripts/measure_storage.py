#!/usr/bin/env python3
"""Mede o envelope e o custo persistido de uma amostra representativa."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulators.edge_client import EdgeBuffer, generate_payload


def percentile(values: list[int], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, round((len(ordered) - 1) * fraction))
    return float(ordered[index])


def measure(count: int = 90) -> dict:
    with tempfile.TemporaryDirectory() as tempdir:
        path = Path(tempdir) / "measure.db"
        buffer = EdgeBuffer(path, "measure-device")
        before = buffer.storage_status()["bytes"]
        by_class: dict[str, list[int]] = {"A": [], "B": [], "C": []}
        try:
            for index in range(count):
                payload = generate_payload("measure-device", buffer.next_sequence(), index)
                before_payload = len(json.dumps(payload, sort_keys=True).encode())
                row_id = buffer.enqueue(payload)
                row = buffer.connection.execute("SELECT length(payload) AS size, priority_class FROM outbox WHERE id = ?", (row_id,)).fetchone()
                by_class[str(row["priority_class"])].append(int(row["size"]))
            after = buffer.storage_status()["bytes"]
            result = {
                "sample_count": count,
                "database_bytes_before": before,
                "database_bytes_after": after,
                "growth_bytes": after - before,
                "bytes_per_message_physical": (after - before) / count,
                "classes": {},
            }
            for priority, values in by_class.items():
                if values:
                    result["classes"][priority] = {
                        "count": len(values), "mean_stored_bytes": statistics.mean(values),
                        "median_stored_bytes": statistics.median(values),
                        "p95_stored_bytes": percentile(values, 0.95), "max_stored_bytes": max(values),
                    }
            return result
        finally:
            buffer.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=90)
    args = parser.parse_args()
    if args.count <= 0:
        parser.error("--count deve ser positivo")
    print(json.dumps(measure(args.count), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
