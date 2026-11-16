#include "telemetry_core.h"

#include <cmath>

#include "severity_contract.h"

namespace fieldnode {

Severity classify_temperature(const float value_c) {
  if (value_c >= severity_contract::TEMPERATURE_CRITICAL_C) return Severity::CRITICO;
  if (value_c >= severity_contract::TEMPERATURE_ATTENTION_C) return Severity::ATENCAO;
  return Severity::NORMAL;
}

Severity classify_vibration(const float value) {
  if (value >= severity_contract::VIBRATION_CRITICAL) return Severity::CRITICO;
  if (value >= severity_contract::VIBRATION_ATTENTION) return Severity::ATENCAO;
  return Severity::NORMAL;
}

bool valid_temperature(const float value_c) {
  return std::isfinite(value_c) && value_c >= severity_contract::TEMPERATURE_MIN_C &&
         value_c <= severity_contract::TEMPERATURE_MAX_C;
}

bool valid_vibration(const float value) {
  return std::isfinite(value) && value >= severity_contract::VIBRATION_MIN &&
         value <= severity_contract::VIBRATION_MAX;
}

bool valid_rpm(const int32_t rpm) { return rpm >= 0 && rpm <= 5000; }

bool valid_sample(const float temperature_c, const float vibration, const int32_t rpm) {
  return valid_temperature(temperature_c) && valid_vibration(vibration) && valid_rpm(rpm);
}

uint32_t next_sequence(const uint32_t current) {
  return current == UINT32_MAX ? 1U : current + 1U;
}

const char* severity_name(const Severity severity) {
  switch (severity) {
    case Severity::ATENCAO: return "ATENCAO";
    case Severity::CRITICO: return "CRITICO";
    default: return "NORMAL";
  }
}

}
