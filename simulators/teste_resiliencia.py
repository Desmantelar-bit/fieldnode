#!/usr/bin/env python3
"""Executa o protocolo S8-T2 contra um Compose local.

O script orquestra o cliente real de ``simulators/edge_client.py``. Ele não
reimplementa outbox, retry ou ACK: mede o que o cliente e o backend fizeram.

Por padrão são executadas as três durações oficiais (30 s, 5 min e 30 min).
Para um ensaio curto de bancada, use ``--durations 1,2,3`` e não publique esse
resultado como S8-T2 oficial.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parent.parent
EDGE_CLIENT = ROOT / "simulators" / "edge_client.py"
DEFAULT_DURATIONS = (30, 300, 1800)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def seconds_between(start: str, end: str) -> float:
    return round((datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds(), 3)


def parse_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def run_command(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("$", " ".join(command), flush=True)
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout.rstrip(), flush=True)
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr, flush=True)
    if check and result.returncode:
        raise RuntimeError(f"comando falhou ({result.returncode}): {' '.join(command)}")
    return result


def compose(compose_args: list[str], *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run_command(["docker", "compose", *compose_args, *args], check=check)


def wait_for_health(url: str, timeout: float) -> str:
    deadline = time.monotonic() + timeout
    last_error = "sem resposta"
    while time.monotonic() < deadline:
        try:
            response = requests.get(url, timeout=3)
            if response.ok and response.json().get("status") == "ok":
                return now()
            last_error = f"HTTP {response.status_code}"
        except (requests.RequestException, ValueError) as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"API não ficou saudável em {timeout}s: {last_error}")


def monitor_backend_outage(url: str, stop: threading.Event, errors: list[str]) -> None:
    while not stop.wait(0.5):
        try:
            response = requests.get(url, timeout=2)
            healthy = response.ok and response.json().get("status") == "ok"
        except (requests.RequestException, ValueError):
            continue
        if healthy:
            errors.append(f"backend ficou saudável antes do fim da indisponibilidade: {now()}")
            stop.set()
            return


def read_buffer(path: Path, device_id: str) -> dict[str, Any]:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            "SELECT message_id, sequence_number, priority_class, payload_hash, "
            "created_at, status, attempts FROM outbox WHERE device_id = ? "
            "ORDER BY sequence_number",
            (device_id,),
        ).fetchall()
        return {
            "rows": [dict(row) for row in rows],
            "counts": {
                str(row["status"]): int(row["count"])
                for row in connection.execute(
                    "SELECT status, COUNT(*) AS count FROM outbox WHERE device_id = ? GROUP BY status",
                    (device_id,),
                )
            },
        }
    finally:
        connection.close()


def server_metrics(compose_args: list[str], device_id: str) -> dict[str, Any]:
    literal = json.dumps(device_id)
    code = f"""from api_tcc.models import LeituraTelemetria
import json
rows = list(LeituraTelemetria.objects.filter(device_id={literal}).values(
    'message_id', 'sequence_number', 'recebido_em'
))
rows.sort(key=lambda row: row['recebido_em'])
sequence = [int(row['sequence_number']) for row in rows]
unique_ids = {{row['message_id'] for row in rows}}
highest = 0
out_of_order = 0
for value in sequence:
    if value < highest:
        out_of_order += 1
    highest = max(highest, value)
print(json.dumps({{
    'received_rows': len(rows),
    'received_unique': len(unique_ids),
    'duplicate_persisted': len(rows) - len(unique_ids),
    'out_of_order': out_of_order,
    'received_sequence': sequence,
}}))"""
    result = compose(compose_args, "exec", "-T", "web", "python", "manage.py", "shell", "-c", code)
    for line in reversed(result.stdout.splitlines()):
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    raise RuntimeError("não foi possível ler as métricas do banco")


def ensure_api_key(compose_args: list[str]) -> str:
    key = os.getenv("FIELDNODE_API_KEY") or parse_dotenv(ROOT / ".env").get("FIELDNODE_API_KEY")
    if key:
        return key
    result = compose(
        compose_args, "exec", "-T", "web", "sh", "-c", "printf '%s' \"$FIELDNODE_API_KEY\""
    )
    key = result.stdout.strip()
    if not key:
        raise RuntimeError("FIELDNODE_API_KEY não encontrada no ambiente do host ou do Compose")
    return key


def run_edge(args: argparse.Namespace, device_id: str, buffer_path: Path, *, count: int, offline: bool) -> None:
    command = [
        sys.executable,
        str(EDGE_CLIENT),
        "--device-id", device_id,
        "--count", str(count),
        "--buffer-path", str(buffer_path),
        "--api-url", args.api_url,
        "--interval", str(args.interval),
        "--max-attempts", str(args.max_attempts),
        "--backoff-base", str(args.backoff_base),
        "--backoff-max", str(args.backoff_max),
    ]
    if offline:
        command.append("--offline")
    else:
        command.extend(["--sync-only", "--timeout", str(args.timeout)])
    environment = os.environ.copy()
    if not offline:
        environment["FIELDNODE_API_KEY"] = args.api_key
    print("$", " ".join(command), flush=True)
    result = subprocess.run(command, cwd=ROOT, env=environment, text=True)
    if result.returncode:
        raise RuntimeError(f"edge_client falhou ({result.returncode})")


def sync_edge_and_measure(args: argparse.Namespace, device_id: str, buffer_path: Path) -> tuple[str | None, str]:
    """Sincroniza em processo separado e observa o primeiro ACK na outbox."""
    command = [
        sys.executable, str(EDGE_CLIENT), "--device-id", device_id, "--count", "0",
        "--buffer-path", str(buffer_path), "--api-url", args.api_url, "--sync-only",
        "--timeout", str(args.timeout), "--max-attempts", str(args.max_attempts),
        "--backoff-base", str(args.backoff_base), "--backoff-max", str(args.backoff_max),
    ]
    environment = os.environ.copy()
    environment["FIELDNODE_API_KEY"] = args.api_key
    print("$", " ".join(command), flush=True)
    process = subprocess.Popen(command, cwd=ROOT, env=environment, text=True)
    first: str | None = None
    while process.poll() is None:
        state = read_buffer(buffer_path, device_id)
        if first is None and any(row["status"] == "SINCRONIZADA" for row in state["rows"]):
            first = now()
        time.sleep(0.1)
    if process.returncode:
        raise RuntimeError(f"edge_client falhou ({process.returncode})")
    if first is None:
        state = read_buffer(buffer_path, device_id)
        if any(row["status"] == "SINCRONIZADA" for row in state["rows"]):
            first = now()
    return first, now()


def measure(
    args: argparse.Namespace,
    duration: int,
    index: int,
    *,
    run_id: str | None = None,
    device_id: str | None = None,
) -> dict[str, Any]:
    run_id = run_id or uuid.uuid4().hex[:12]
    device_id = device_id or f"edge-s8-t2-r{index}-{run_id}"
    buffer_path = args.output_dir / f"{device_id}.sqlite3"
    result: dict[str, Any] = {
        "scenario": f"R{index}", "run_id": run_id, "device_id": device_id,
        "downtime_requested_seconds": duration, "experiment_started_at": now(),
    }
    backend_stopped = False
    outage_monitor_stop = threading.Event()
    outage_monitor_errors: list[str] = []
    outage_monitor: threading.Thread | None = None
    try:
        compose(args.compose_args, "start", "web")
        wait_for_health(args.health_url, args.health_timeout)
        compose(args.compose_args, "stop", "web")
        backend_stopped = True
        result["backend_stopped_at"] = now()
        outage_started = time.monotonic()
        result["generation_started_at"] = now()
        outage_monitor = threading.Thread(
            target=monitor_backend_outage,
            args=(args.health_url, outage_monitor_stop, outage_monitor_errors),
            daemon=True,
        )
        outage_monitor.start()
        run_edge(args, device_id, buffer_path, count=args.count, offline=True)
        result["generation_finished_at"] = now()
        result["generated"] = len(read_buffer(buffer_path, device_id)["rows"])
        remaining = duration - (time.monotonic() - outage_started)
        while remaining > 0 and not outage_monitor_stop.wait(min(1.0, remaining)):
            remaining = duration - (time.monotonic() - outage_started)
        outage_monitor_stop.set()
        outage_monitor.join()
        if outage_monitor_errors:
            raise RuntimeError(outage_monitor_errors[0])
        result["backend_started_at"] = now()
        compose(args.compose_args, "start", "web")
        backend_stopped = False
        result["backend_ready_at"] = wait_for_health(args.health_url, args.health_timeout)
        result["downtime_actual_seconds"] = round(time.monotonic() - outage_started, 3)
        sync_started = time.monotonic()
        first_sync, last_sync = sync_edge_and_measure(args, device_id, buffer_path)
        result["first_successful_sync_at"] = first_sync
        result["last_successful_sync_at"] = last_sync
        result["total_sync_time_seconds"] = round(time.monotonic() - sync_started, 3)
        result["experiment_finished_at"] = now()
        local = read_buffer(buffer_path, device_id)
        server = server_metrics(args.compose_args, device_id)
        attempts = sum(int(row["attempts"]) for row in local["rows"])
        generated = result["generated"]
        result.update({
            "received_rows": server["received_rows"],
            "received": server["received_unique"],
            "lost": generated - server["received_unique"],
            "loss_rate": round((generated - server["received_unique"]) / generated, 6)
            if generated else None,
            "duplicate_attempts": max(0, attempts - generated),
            "duplicate_persisted": server["duplicate_persisted"],
            "out_of_order": server["out_of_order"],
            "recovery_time_seconds": seconds_between(
                result["backend_ready_at"], result["last_successful_sync_at"]
            ),
            "local_counts": local["counts"],
            "server_received_sequence": server["received_sequence"],
        })
        expected_sequences = list(range(1, args.count + 1))
        validation_errors = []
        if generated != args.count:
            validation_errors.append(f"geradas {generated} de {args.count} leituras solicitadas")
        if server["received_rows"] != generated or server["received_unique"] != generated:
            validation_errors.append(
                f"backend recebeu {server['received_rows']} linhas e "
                f"{server['received_unique']} IDs únicos de {generated} geradas"
            )
        if server["duplicate_persisted"]:
            validation_errors.append(f"{server['duplicate_persisted']} duplicatas persistidas")
        if local["counts"] != {"SINCRONIZADA": generated}:
            validation_errors.append(f"outbox não totalmente sincronizada: {local['counts']}")
        if sorted(server["received_sequence"]) != expected_sequences:
            validation_errors.append("sequências do backend ausentes, duplicadas ou inesperadas")
        result["validation_errors"] = validation_errors
        result["status"] = "VALID" if not validation_errors else "FAILED"
    finally:
        outage_monitor_stop.set()
        if outage_monitor is not None:
            outage_monitor.join()
        if backend_stopped:
            compose(args.compose_args, "start", "web", check=False)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--durations", default=",".join(map(str, DEFAULT_DURATIONS)))
    parser.add_argument("--start-index", type=int, default=1)
    parser.add_argument("--append-results", action="store_true")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--interval", type=float, default=0.0)
    parser.add_argument("--api-url", default="http://127.0.0.1:8000/api/telemetria/")
    parser.add_argument("--health-url", default="http://127.0.0.1:8000/api/health/")
    parser.add_argument("--health-timeout", type=float, default=180.0)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--backoff-base", type=float, default=0.0)
    parser.add_argument("--backoff-max", type=float, default=0.0)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts" / "resilience")
    parser.add_argument("--compose-args", nargs="*", default=[])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.count < 1:
        raise SystemExit("--count deve ser maior que zero")
    args.durations = [int(value) for value in args.durations.split(",") if value.strip()]
    if not args.durations or any(value < 0 for value in args.durations):
        raise SystemExit("--durations deve conter segundos não negativos separados por vírgula")
    if args.start_index < 1:
        raise SystemExit("--start-index deve ser maior que zero")
    if shutil.which("docker") is None:
        raise SystemExit("docker não encontrado no PATH")
    lock_path = ROOT / ".fieldnode-resilience.lock"
    try:
        with lock_path.open("x", encoding="ascii") as lock_file:
            lock_file.write(str(os.getpid()))
    except FileExistsError:
        raise SystemExit("já existe um ensaio de resiliência ativo para este Compose")

    try:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        args.api_key = ensure_api_key(args.compose_args)
        output = args.output_dir / "resultados.json"
        results: list[dict[str, Any]] = []
        if args.append_results and output.exists():
            previous = json.loads(output.read_text(encoding="utf-8"))
            if not isinstance(previous, list):
                raise SystemExit(f"formato inválido no arquivo existente: {output}")
            results.extend(previous)
        failed = False
        for index, duration in enumerate(args.durations, start=args.start_index):
            print(f"\n=== R{index}: indisponibilidade de {duration}s ===", flush=True)
            run_id = uuid.uuid4().hex[:12]
            device_id = f"edge-s8-t2-r{index}-{run_id}"
            try:
                row = measure(args, duration, index, run_id=run_id, device_id=device_id)
            except KeyboardInterrupt:
                local_path = args.output_dir / f"{device_id}.sqlite3"
                partial = read_buffer(local_path, device_id) if local_path.exists() else {"rows": [], "counts": {}}
                row = {
                    "scenario": f"R{index}", "run_id": run_id, "device_id": device_id,
                    "downtime_requested_seconds": duration, "generated": len(partial["rows"]),
                    "local_counts": partial["counts"], "status": "FAILED",
                    "error": "KeyboardInterrupt: rodada interrompida antes da conclusão",
                    "experiment_finished_at": now(),
                }
            except Exception as exc:
                row = {
                    "scenario": f"R{index}", "run_id": run_id, "device_id": device_id,
                    "downtime_requested_seconds": duration, "status": "FAILED",
                    "error": f"{type(exc).__name__}: {exc}",
                    "experiment_finished_at": now(),
                }
            results.append(row)
            output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
            if row["status"] != "VALID":
                failed = True
            if "KeyboardInterrupt" in row.get("error", ""):
                break
        output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Resultados gravados em {output}")
        print("scenario | generated | received | lost | duplicate_attempts | duplicate_persisted | out_of_order | downtime_s | recovery_s | sync_s")
        for row in results:
            print(" | ".join(str(row.get(key, "N/A")) for key in (
                "scenario", "generated", "received", "lost", "duplicate_attempts",
                "duplicate_persisted", "out_of_order", "downtime_actual_seconds",
                "recovery_time_seconds", "total_sync_time_seconds")))
        return 1 if failed else 0
    finally:
        lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
