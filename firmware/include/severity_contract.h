#pragma once

// Gerado de contracts/severity.v1.json por scripts/generate_firmware_contract.py.
// Os limites sao heuristicas de bancada, nao limites operacionais validados.
namespace fieldnode::severity_contract {
constexpr float TEMPERATURE_ATTENTION_C = 75.0F;
constexpr float TEMPERATURE_CRITICAL_C = 85.0F;
constexpr float TEMPERATURE_MIN_C = 0.0F;
constexpr float TEMPERATURE_MAX_C = 150.0F;
constexpr float VIBRATION_ATTENTION = 5.0F;
constexpr float VIBRATION_CRITICAL = 8.0F;
constexpr float VIBRATION_MIN = 0.0F;
constexpr float VIBRATION_MAX = 10.0F;
}
