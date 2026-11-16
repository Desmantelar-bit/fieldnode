#include "j1939.h"

#include <cmath>

namespace fieldnode::j1939 {
namespace {
constexpr uint32_t ID_MASK_29_BITS = 0x1FFFFFFFU;
constexpr uint32_t RESERVED_BIT = 1U << 25;

bool frame_for_pgn(const CanFrame& frame, uint32_t expected_pgn, Identifier& id) {
  return frame.data != nullptr && frame.length == 8U && parse_identifier(frame.id, frame.extended, id) &&
         id.pgn == expected_pgn;
}

bool valid_u8(const uint8_t raw) { return raw != 0xFFU; }
bool valid_u16(const uint16_t raw) { return raw != 0xFFFFU; }
}  // namespace

bool parse_identifier(const uint32_t id, const bool extended, Identifier& out) {
  if (!extended || (id & ~ID_MASK_29_BITS) != 0U || (id & RESERVED_BIT) != 0U) return false;
  out.priority = static_cast<uint8_t>((id >> 26) & 0x07U);
  out.data_page = ((id >> 24) & 0x01U) != 0U;
  out.pdu_format = static_cast<uint8_t>((id >> 16) & 0xFFU);
  out.pdu_specific = static_cast<uint8_t>((id >> 8) & 0xFFU);
  out.source_address = static_cast<uint8_t>(id & 0xFFU);
  const uint32_t page = out.data_page ? 0x10000U : 0U;
  out.pgn = page | (static_cast<uint32_t>(out.pdu_format) << 8);
  if (out.pdu_format >= 240U) out.pgn |= out.pdu_specific;
  return true;
}

bool decode_engine_speed(const CanFrame& frame, Parameter& out) {
  Identifier id;
  if (!frame_for_pgn(frame, PGN_EEC1, id)) return false;
  const uint16_t raw = static_cast<uint16_t>(frame.data[3]) | (static_cast<uint16_t>(frame.data[4]) << 8);
  // SPN 190 public tables define 0..8031.875 rpm; above 0xFAFF is reserved.
  if (!valid_u16(raw) || raw > 0xFAFFU) return false;
  out = {"engine.rpm", static_cast<float>(raw) * 0.125F, "rpm", 190U, PGN_EEC1, true};
  return true;
}

bool decode_coolant_temperature(const CanFrame& frame, Parameter& out) {
  Identifier id;
  if (!frame_for_pgn(frame, PGN_ET1, id)) return false;
  const uint8_t raw = frame.data[0];
  if (!valid_u8(raw) || raw > 250U) return false;
  out = {"engine.coolant_temp", static_cast<float>(raw) - 40.0F, "C", 110U, PGN_ET1, true};
  return true;
}

bool decode_oil_pressure(const CanFrame& frame, Parameter& out) {
  Identifier id;
  if (!frame_for_pgn(frame, PGN_EFLP1, id)) return false;
  const uint8_t raw = frame.data[3];
  if (!valid_u8(raw) || raw > 250U) return false;
  out = {"engine.oil_pressure", static_cast<float>(raw) * 4.0F, "kPa", 100U, PGN_EFLP1, true};
  return true;
}

size_t decode_dm1(const CanFrame& frame, Dtc* out, const size_t capacity) {
  Identifier id;
  if (out == nullptr || capacity == 0U || frame.data == nullptr || frame.length < 2U ||
      !parse_identifier(frame.id, frame.extended, id) || id.pgn != PGN_DM1 || ((frame.length - 2U) % 4U) != 0U)
    return 0U;
  size_t count = 0U;
  for (size_t offset = 2U; offset + 4U <= frame.length && count < capacity; offset += 4U) {
    const uint8_t* bytes = frame.data + offset;
    if (bytes[0] == 0xFFU && bytes[1] == 0xFFU && bytes[2] == 0xFFU && bytes[3] == 0xFFU) continue;
    const uint32_t spn = static_cast<uint32_t>(bytes[0]) | (static_cast<uint32_t>(bytes[1]) << 8) |
                         (static_cast<uint32_t>(bytes[2] & 0xE0U) << 11);
    if (spn == 0x7FFFFU || (bytes[2] & 0x1FU) == 0x1FU || bytes[3] == 0xFFU) continue;
    out[count++] = {spn, static_cast<uint8_t>(bytes[2] & 0x1FU), static_cast<uint8_t>(bytes[3] & 0x7FU),
                    (bytes[3] & 0x80U) != 0U};
  }
  return count;
}
}  // namespace fieldnode::j1939
