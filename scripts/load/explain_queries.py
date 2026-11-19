#!/usr/bin/env python3
"""Executa EXPLAIN nas consultas representativas sem expor credenciais."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
QUERIES = {
    "telemetry_machine_time": "SELECT id, timestamp, temperatura, vibracao, rpm FROM api_tcc_leituratelemetria WHERE machine_id = 1 AND timestamp >= '2026-01-01' ORDER BY timestamp DESC LIMIT 50",
    "telemetry_device_sequence": "SELECT id, sequence_number, message_id FROM api_tcc_leituratelemetria WHERE device_id = 'LOAD-001' ORDER BY sequence_number DESC LIMIT 100",
    "event_machine_status": "SELECT id, tipo, severidade, criado_em FROM api_tcc_event WHERE machine_id = 1 AND status = 'ABERTO' ORDER BY criado_em DESC LIMIT 20",
    "decision_machine_status": "SELECT id, severidade, criado_em FROM api_tcc_decision WHERE machine_id = 1 AND status = 'PENDENTE' ORDER BY criado_em DESC LIMIT 20",
    "dashboard_latest": "SELECT t1.id, t1.machine_id, t1.timestamp FROM api_tcc_leituratelemetria t1 WHERE t1.machine_id = 1 ORDER BY t1.timestamp DESC LIMIT 1",
}


def run(query: str, compose_file: str) -> str:
    env = os.environ.copy()
    command = ["docker", "compose", "-f", compose_file, "exec", "-T", "db", "sh", "-c",
               'MYSQL_PWD="$DB_PASSWORD" mysql --batch --raw --skip-column-names -u"$DB_USER" "$DB_NAME"']
    completed = subprocess.run(command, input=f"EXPLAIN {query};\n", text=True, capture_output=True, cwd=ROOT, env=env)
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or "mysql returned a non-zero status")
    return completed.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compose-file", default="docker-compose.yml")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "load" / "explain.json")
    args = parser.parse_args()
    result = {name: {"query": query, "plan": run(query, args.compose_file)} for name, query in QUERIES.items()}
    result["generated_at"] = datetime.now(timezone.utc).isoformat()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"raw_result={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
