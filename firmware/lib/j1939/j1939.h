#pragma once

#include <stddef.h>
#include <stdint.h>

namespace fieldnode::j1939 {

constexpr uint32_t PGN_EEC1 = 61444U;
constexpr uint32_t PGN_ET1 = 65262U;
constexpr uint32_t PGN_EFLP1 = 65263U;
constexpr uint32_t PGN_DM1 = 65226U;

struct CanFrame {
  uint32_t id = 0;
  const uint8_t* data = nullptr;
  size_t length = 0;
  bool extended = false;
};

struct Identifier {
  uint8_t priority = 0;
  bool data_page = false;
  uint8_t pdu_format = 0;
  uint8_t pdu_specific = 0;
  uint8_t source_address = 0;
  uint32_t pgn = 0;
};

struct Parameter {
  const char* name = nullptr;
  float value = 0.0F;
  const char* unit = nullptr;
  uint32_t spn = 0;
  uint32_t pgn = 0;
  bool present = false;
};

struct Dtc {
  uint32_t spn = 0;
  uint8_t fmi = 0;
  uint8_t occurrence_count = 0;
  bool conversion_method_2 = false;
};

bool parse_identifier(uint32_t id, bool extended, Identifier& out);
bool decode_engine_speed(const CanFrame& frame, Parameter& out);
bool decode_coolant_temperature(const CanFrame& frame, Parameter& out);
bool decode_oil_pressure(const CanFrame& frame, Parameter& out);
size_t decode_dm1(const CanFrame& frame, Dtc* out, size_t capacity);

}  // namespace fieldnode::j1939
