#include "espnow_link.h"
#include <cstring>
namespace fieldnode {
uint16_t crc16_ccitt_false(const uint8_t* data, const uint16_t length) {
  uint16_t crc = 0xFFFF;
  for (uint16_t i = 0; i < length; ++i) {
    crc ^= static_cast<uint16_t>(data[i]) << 8;
    for (uint8_t bit = 0; bit < 8; ++bit) crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021 : crc << 1;
  }
  return crc;
}
bool encode_frame(EspNowFrame& frame) {
  frame.version = 1;
  frame.crc16 = crc16_ccitt_false(reinterpret_cast<const uint8_t*>(&frame), sizeof(frame) - sizeof(frame.crc16));
  return true;
}
bool decode_frame(const uint8_t* bytes, const uint16_t length, EspNowFrame& frame) {
  if (bytes == nullptr || length != sizeof(EspNowFrame)) return false;
  memcpy(&frame, bytes, sizeof(frame));
  return frame.version == 1 && frame.crc16 == crc16_ccitt_false(bytes, sizeof(frame) - sizeof(frame.crc16));
}
}
