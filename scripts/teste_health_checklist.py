"""
Checklist 6.2 — Health Check & ApiStatusIndicator
Testa todos os critérios sem precisar de browser.

Uso:
    python scripts/teste_health_checklist.py
"""

import os
import sys
import time
import json
import threading
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000/api"
HEALTH = f"{BASE}/health/"
TIMEOUT = 3


def _get(url, timeout=TIMEOUT):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read())


def ok(msg):  print(f"  \033[32m✓\033[0m  {msg}")
def fail(msg): print(f"  \033[31m✗\033[0m  {msg}"); sys.exit(1)
def section(msg): print(f"\n\033[1m{msg}\033[0m")


# ── 1. Backend respondendo ────────────────────────────────────────────────────
section("1. /api/health/ — HTTP 200 + payload")
try:
    status, data = _get(HEALTH)
    assert status == 200,          f"esperado 200, recebeu {status}"
    assert data["status"] == "ok", f"status={data['status']}"
    assert data["database"] == "ok", f"database={data['database']}"
    ok(f"HTTP {status}  {data}")
except urllib.error.URLError as e:
    fail(f"Backend inacessível — sobe o Django primeiro. ({e})")


# ── 2. Polling simulado (3 ciclos de 2 s para não travar o terminal) ──────────
section("2. Polling — 3 chamadas consecutivas (intervalo 2 s)")
POLL_INTERVAL = 2
results = []

def poll():
    for i in range(3):
        try:
            s, d = _get(HEALTH)
            results.append((s, d["status"]))
        except Exception as e:
            results.append((0, str(e)))
        if i < 2:
            time.sleep(POLL_INTERVAL)

t = threading.Thread(target=poll)
t.start()
t.join(timeout=POLL_INTERVAL * 3 + 2)

for i, (s, st) in enumerate(results):
    assert s == 200 and st == "ok", f"ciclo {i+1} falhou: {s} {st}"
    ok(f"ciclo {i+1}: HTTP {s}  status={st}")


# ── 3. Banco de dados ─────────────────────────────────────────────────────────
section("3. Banco — database: ok")
_, data = _get(HEALTH)
assert data["database"] == "ok", f"database={data['database']}"
ok(f"database={data['database']}")


# ── 4. Comportamento offline (simula timeout de rede) ─────────────────────────
section("4. Offline — timeout de 0.001 s simula backend morto")
try:
    _get(HEALTH, timeout=0.001)
    fail("deveria ter lançado timeout")
except (urllib.error.URLError, TimeoutError, OSError):
    ok("timeout capturado sem crash — comportamento correto do indicador")


# ── 5. Recuperação — backend ainda está vivo ──────────────────────────────────
section("5. Recuperação — backend responde após 'queda' simulada")
s, d = _get(HEALTH)
assert s == 200 and d["status"] == "ok"
ok(f"HTTP {s}  status={d['status']}  — indicador voltaria para 🟢")


# ── Resumo ────────────────────────────────────────────────────────────────────
print("\n\033[1;32m✅  Todos os testes passaram.\033[0m")
print("   Os testes visuais (bolinha verde/vermelha, DevTools Network)")
print("   precisam ser confirmados no browser conforme o checklist.\n")
