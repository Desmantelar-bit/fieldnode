#pragma once

#include <stdint.h>

namespace fieldnode {

enum class Severity { NORMAL, ATENCAO, CRITICO };

Severity classify_temperature(float value_c);
Severity classify_vibration(float value);
bool valid_temperature(float value_c);
bool valid_vibration(float value);
bool valid_rpm(int32_t rpm);
bool valid_sample(float temperature_c, float vibration, int32_t rpm);
uint32_t next_sequence(uint32_t current);
const char* severity_name(Severity severity);

}
