"""Valida a presença e a estrutura mínima do protocolo S8-T14.

Este script verifica documentação e checklists. Ele não simula bancada nem
marca um degrau como aprovado.
"""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = ROOT / "docs" / "INTEGRACAO_HARDWARE.md"
CHECKLIST_DIR = ROOT / "firmware" / "tests" / "bancada"
CHECKLISTS = [CHECKLIST_DIR / f"D{i}_{name}.md" for i, name in enumerate(
    (
        "sensor_serial",
        "wifi_mqtt",
        "backend_persistencia",
        "rtc_sequencia",
        "outbox_recuperacao",
        "espnow_gateway",
        "lora",
        "alarme_local",
    ),
    start=1,
)]


def main() -> int:
    errors = []
    if not PROTOCOL.is_file():
        errors.append(f"protocolo ausente: {PROTOCOL}")
    else:
        content = PROTOCOL.read_text(encoding="utf-8")
        for step in range(1, 9):
            if f"D{step} -" not in content:
                errors.append(f"protocolo sem D{step}")
    for checklist in CHECKLISTS:
        if not checklist.is_file():
            errors.append(f"checklist ausente: {checklist.name}")
        elif "- [ ]" not in checklist.read_text(encoding="utf-8"):
            errors.append(f"checklist sem itens: {checklist.name}")
    if errors:
        for error in errors:
            print(f"ERRO: {error}")
        return 1
    print("S8-T14 documentation/checklists: OK")
    print("Physical execution status is not changed by this script.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
