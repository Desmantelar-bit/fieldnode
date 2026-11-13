"""Provision/revoke the eight individual devices used by simular_mqtt.py."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEVICE_IDS = tuple(f"COLH-{index:02d}" for index in range(1, 9))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument("--rotate", action="store_true")
    operation.add_argument("--revoke", action="store_true")
    args = parser.parse_args()
    script = ROOT / "scripts" / "provision_device.py"
    print("Perfil demo: cada dispositivo recebe uma credencial individual.")
    for device_id in DEVICE_IDS:
        command = [sys.executable, str(script)]
        if args.rotate:
            command.append("--rotate")
        elif args.revoke:
            command.append("--revoke")
        command.append(device_id)
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            print(f"Perfil interrompido em {device_id}; execute novamente após corrigir a falha.", file=sys.stderr)
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
