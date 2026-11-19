"""Watchdog de demonstração para alertas operacionais do FieldNode.

Não depende de Prometheus ou Alertmanager: consulta a API diretamente, mantém
um pequeno estado local para cooldown e envia um resumo por webhook e/ou SMTP.
Uso: ``python scripts/watchdog.py --once``.
"""

from __future__ import annotations

import argparse
import json
import os
import smtplib
import tempfile
import time
from email.message import EmailMessage
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default).strip()


def _get(url: str, headers: dict[str, str], timeout: int) -> tuple[int, str]:
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8")
    except HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except URLError as exc:
        raise RuntimeError(f"API indisponivel: {exc.reason}") from exc


def _metric_value(payload: str, name: str, labels: str | None = None) -> float:
    prefix = name if labels is None else f"{name}{{{labels}}}"
    for line in payload.splitlines():
        if line.startswith(prefix + " "):
            try:
                return float(line.rsplit(" ", 1)[1])
            except ValueError:
                return 0.0
    return 0.0


def _metric_sum(payload: str, prefix: str) -> float:
    total = 0.0
    for line in payload.splitlines():
        if line.startswith(prefix) and " " in line:
            try:
                total += float(line.rsplit(" ", 1)[1])
            except ValueError:
                continue
    return total


def collect_alerts(health: dict, metrics: str, previous: dict) -> list[str]:
    alerts: list[str] = []
    worker = health.get("checks", {}).get("worker", {})
    if worker.get("required") and worker.get("status") != "ok":
        alerts.append(f"worker MQTT sem heartbeat ({worker.get('status', 'unknown')})")

    dlq = _metric_value(metrics, "fieldnode_dlq_open")
    if dlq > float(_env("WATCHDOG_DLQ_THRESHOLD", "0")) and dlq > previous.get("dlq", 0):
        alerts.append(f"DLQ crescendo ({int(dlq)} itens abertos)")

    backlog = _metric_sum(metrics, "fieldnode_outbox_pending")
    if backlog > float(_env("WATCHDOG_BACKLOG_THRESHOLD", "10")):
        alerts.append(f"backlog acima do limite ({int(backlog)} pendentes)")

    failures = _metric_sum(metrics, "fieldnode_llm_failures_total")
    calls = failures + _metric_value(metrics, "fieldnode_llm_latency_seconds_count")
    failure_rate = failures / calls if calls else 0.0
    if calls and failure_rate >= float(_env("WATCHDOG_LLM_FAILURE_RATE", "0.20")):
        alerts.append(f"falhas LLM acima do limite ({failure_rate:.1%})")

    disk = health.get("checks", {}).get("disk", {})
    free_ratio = disk.get("free_ratio")
    if free_ratio is not None and float(free_ratio) < 1 - float(_env("WATCHDOG_DISK_USED_LIMIT", "0.85")):
        alerts.append(f"disco acima de {float(_env('WATCHDOG_DISK_USED_LIMIT', '0.85')):.0%} de uso")
    return alerts


def _load_state(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state), encoding="utf-8")


def notify(message: str) -> None:
    webhook = _env("WATCHDOG_WEBHOOK_URL", "")
    if webhook:
        body = json.dumps({"text": message}).encode("utf-8")
        request = Request(webhook, data=body, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=10):
            pass

    smtp_host = _env("WATCHDOG_SMTP_HOST", "")
    recipient = _env("WATCHDOG_EMAIL_TO", "")
    if not smtp_host or not recipient:
        return
    msg = EmailMessage()
    msg["Subject"] = "[FieldNode] alerta operacional"
    msg["From"] = _env("WATCHDOG_EMAIL_FROM", "fieldnode-watchdog@localhost")
    msg["To"] = recipient
    msg.set_content(message)
    with smtplib.SMTP(smtp_host, int(_env("WATCHDOG_SMTP_PORT", "587")), timeout=10) as smtp:
        if _env("WATCHDOG_SMTP_TLS", "1") == "1":
            smtp.starttls()
        user = _env("WATCHDOG_SMTP_USER", "")
        password = os.environ.get("WATCHDOG_SMTP_PASSWORD", "")
        if user:
            smtp.login(user, password)
        smtp.send_message(msg)


def check_once() -> list[str]:
    base = _env("WATCHDOG_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    token = _env("FIELDNODE_METRICS_TOKEN", "")
    timeout = int(_env("WATCHDOG_TIMEOUT_SECONDS", "10"))
    headers = {"Accept": "application/json", "X-Metrics-Token": token}
    health_status, health_body = _get(f"{base}/api/health/ready", headers, timeout)
    if health_status >= 500 and not health_body:
        raise RuntimeError(f"health indisponivel: HTTP {health_status}")
    health = json.loads(health_body)
    metrics_status, metrics = _get(f"{base}/metrics", headers, timeout)
    if metrics_status != 200:
        raise RuntimeError(f"metrics indisponivel: HTTP {metrics_status}")

    state_path = Path(_env("WATCHDOG_STATE_FILE", str(Path(tempfile.gettempdir()) / "fieldnode-watchdog-state.json")))
    state = _load_state(state_path)
    alerts = collect_alerts(health, metrics, state)
    current = {"dlq": _metric_value(metrics, "fieldnode_dlq_open"), "last_check": time.time()}
    if alerts:
        message = "FieldNode watchdog:\n- " + "\n- ".join(alerts)
        last_sent = float(state.get("last_sent", 0))
        cooldown = int(_env("WATCHDOG_COOLDOWN_SECONDS", "300"))
        if time.time() - last_sent >= cooldown:
            notify(message)
            current["last_sent"] = time.time()
    _save_state(state_path, current)
    return alerts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="faz uma verificacao e encerra")
    args = parser.parse_args()
    interval = max(15, int(_env("WATCHDOG_INTERVAL_SECONDS", "30")))
    while True:
        try:
            alerts = check_once()
            print("ALERTAS: " + ("; ".join(alerts) if alerts else "nenhum"), flush=True)
        except Exception as exc:
            print(f"WATCHDOG_ERRO: {exc}", flush=True)
        if args.once:
            return 0
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
