#!/usr/bin/env python3
"""Carga controlada contra os endpoints reais do FieldNode.

Este executor mede tempo de resposta HTTP, não tempo interno de persistência.
Os resultados brutos são JSON e nunca incluem credenciais.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import statistics
import sys
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "artifacts" / "load"
PROFILES = {"a": 10, "b": 50, "c": 200}


@dataclass
class Sample:
    status: int
    latency_ms: float
    sent_at: str
    error: str | None = None


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    rank = (len(values) - 1) * p
    lower = int(rank)
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (rank - lower)


def payload(device: str, sequence: int, event_time: datetime) -> dict[str, Any]:
    message_id = f"load-{device}-{sequence}-{uuid.uuid4().hex[:8]}"
    return {
        "id": message_id,
        "message_id": message_id,
        "device_id": device,
        "maquina_id": device,
        "sequence_number": sequence,
        "temperatura": 70.0 + (sequence % 5),
        "vibracao": 1.2,
        "rpm": 1800,
        "timestamp": event_time.isoformat().replace("+00:00", "Z"),
        "source": "load_test",
        "data_origin": "simulado",
    }


def post_one(session: requests.Session, url: str, device: str, sequence: int,
             event_time: datetime, timeout: float) -> Sample:
    started = time.perf_counter()
    try:
        response = session.post(url, json=payload(device, sequence, event_time), timeout=timeout)
        return Sample(response.status_code, (time.perf_counter() - started) * 1000,
                      datetime.now(timezone.utc).isoformat(),
                      None if response.ok else response.text[:160])
    except requests.RequestException as exc:
        return Sample(0, (time.perf_counter() - started) * 1000,
                      datetime.now(timezone.utc).isoformat(), type(exc).__name__)


def session_for(args: argparse.Namespace) -> requests.Session:
    session = requests.Session()
    if args.device_key:
        session.headers.update({"X-Device-Key": args.device_key})
    return session


def run_ingestion(args: argparse.Namespace, devices: int, duration: float | None,
                  count: int | None, scenario: str) -> dict[str, Any]:
    started = time.perf_counter()
    samples: list[Sample] = []
    lock = threading.Lock()
    deadline = time.perf_counter() + duration if duration is not None else None
    planned = count if count is not None else max(1, int(devices * args.rate * duration))

    def worker(device_number: int) -> None:
        session = session_for(args)
        seq = 0
        next_tick = time.perf_counter() + device_number / max(devices * args.rate, 1)
        while len(samples) < planned if count is not None else (deadline is None or time.perf_counter() < deadline):
            if count is None and time.perf_counter() < next_tick:
                time.sleep(min(0.01, next_tick - time.perf_counter()))
            seq += 1
            sample = post_one(session, args.api_url, f"load-{scenario}-{device_number:03d}",
                              seq, datetime.now(timezone.utc), args.timeout)
            with lock:
                samples.append(sample)
                if count is not None and len(samples) >= planned:
                    break
            next_tick += 1 / max(args.rate, 0.001)

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(args.workers, devices)) as pool:
        futures = [pool.submit(worker, n) for n in range(devices)]
        for future in futures:
            future.result()

    elapsed = time.perf_counter() - started
    latencies = [s.latency_ms for s in samples]
    ok = sum(1 for s in samples if s.status in (200, 201))
    return {
        "scenario": scenario,
        "planned": planned,
        "sent": len(samples),
        "accepted_http": ok,
        "errors": len(samples) - ok,
        "error_rate": (len(samples) - ok) / len(samples) if samples else None,
        "throughput_msg_s": len(samples) / elapsed if elapsed else None,
        "elapsed_seconds": elapsed,
        "latency_ms": {"p50": percentile(latencies, .50), "p95": percentile(latencies, .95),
                       "p99": percentile(latencies, .99)},
        "status_counts": {str(code): sum(1 for s in samples if s.status == code)
                          for code in sorted({s.status for s in samples})},
        "samples": [asdict(s) for s in samples],
    }


def dashboard_probe(args: argparse.Namespace) -> dict[str, Any]:
    paths = ["health/", "status-mqtt/", "colheitadeira/", "leituras/ultimas/", "events/?page_size=5"]
    started = time.perf_counter()
    samples: list[Sample] = []

    def get(path: str) -> Sample:
        t = time.perf_counter()
        try:
            response = requests.get(f"{args.api_root.rstrip('/')}/{path}",
                                    headers={"Authorization": f"Token {args.token}"} if args.token else {},
                                    timeout=args.timeout)
            return Sample(response.status_code, (time.perf_counter() - t) * 1000,
                          datetime.now(timezone.utc).isoformat(), None if response.ok else response.text[:160])
        except requests.RequestException as exc:
            return Sample(0, (time.perf_counter() - t) * 1000, datetime.now(timezone.utc).isoformat(), type(exc).__name__)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.dashboard_users) as pool:
        futures = [pool.submit(get, paths[i % len(paths)]) for i in range(args.dashboard_requests)]
        samples = [f.result() for f in futures]
    elapsed = time.perf_counter() - started
    latencies = [s.latency_ms for s in samples]
    return {"scenario": "f-dashboard", "requests": len(samples), "elapsed_seconds": elapsed,
            "errors": sum(s.status < 200 or s.status >= 300 for s in samples),
            "latency_ms": {"p50": percentile(latencies, .5), "p95": percentile(latencies, .95), "p99": percentile(latencies, .99)},
            "status_counts": {str(code): sum(1 for s in samples if s.status == code) for code in sorted({s.status for s in samples})},
            "samples": [asdict(s) for s in samples]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", choices=["a", "b", "c", "d", "e", "f"])
    parser.add_argument("--api-url", default=os.getenv("FIELDNODE_LOAD_API_URL", "http://127.0.0.1:8000/api/telemetria/"))
    parser.add_argument("--api-root", default=os.getenv("FIELDNODE_LOAD_API_ROOT", "http://127.0.0.1:8000/api"))
    parser.add_argument("--device-key", default=os.getenv("FIELDNODE_LOAD_DEVICE_KEY", ""), help="device key; not written to output")
    parser.add_argument("--token", default=os.getenv("FIELDNODE_LOAD_TOKEN", ""), help="dashboard token; not written to output")
    parser.add_argument("--rate", type=float, default=.5)
    parser.add_argument("--duration-seconds", type=float, default=30)
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--dashboard-users", type=int, default=10)
    parser.add_argument("--dashboard-requests", type=int, default=100)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--confirm-replay", action="store_true", help="required for profile e")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.profile == "e" and not args.confirm_replay:
        parser.error("profile e exige --confirm-replay; use --duration-seconds para limitar a execução")
    if args.profile == "f":
        result = dashboard_probe(args)
    elif args.profile == "d":
        result = run_ingestion(args, 1, None, args.count, "d")
    elif args.profile == "e":
        result = run_ingestion(args, 200, args.duration_seconds, None, "e-replay-6h-simulated")
        result["simulated_hours"] = 6
        result["theoretical_messages_200x0.5x6h"] = 2_160_000
    else:
        result = run_ingestion(args, PROFILES[args.profile], args.duration_seconds, None, args.profile)
    result["generated_at"] = datetime.now(timezone.utc).isoformat()
    result["api_url"] = args.api_url if args.profile != "f" else args.api_root
    destination = args.output / f"{result['scenario']}-{int(time.time())}.json"
    destination.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in {"samples"}}, indent=2))
    print(f"raw_result={destination}")
    return 0 if result.get("errors", 0) == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
