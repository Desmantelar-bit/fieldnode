"""Generate the firmware severity header from the canonical JSON contract."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "severity.v1.json"
HEADER = ROOT / "firmware" / "include" / "severity_contract.h"


def render(contract: dict) -> str:
    t = contract["metrics"]["temperatura"]
    v = contract["metrics"]["vibracao"]
    return f'''#pragma once

// Gerado de contracts/severity.v1.json por scripts/generate_firmware_contract.py.
// Os limites sao heuristicas de bancada, nao limites operacionais validados.
namespace fieldnode::severity_contract {{
constexpr float TEMPERATURE_ATTENTION_C = {t["atencao"]:.1f}F;
constexpr float TEMPERATURE_CRITICAL_C = {t["critico"]:.1f}F;
constexpr float TEMPERATURE_MIN_C = {t["range"][0]:.1f}F;
constexpr float TEMPERATURE_MAX_C = {t["range"][1]:.1f}F;
constexpr float VIBRATION_ATTENTION = {v["atencao"]:.1f}F;
constexpr float VIBRATION_CRITICAL = {v["critico"]:.1f}F;
constexpr float VIBRATION_MIN = {v["range"][0]:.1f}F;
constexpr float VIBRATION_MAX = {v["range"][1]:.1f}F;
}}
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(json.loads(CONTRACT.read_text(encoding="utf-8")))
    if args.check:
        return 0 if HEADER.read_text(encoding="utf-8") == expected else 1
    HEADER.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
