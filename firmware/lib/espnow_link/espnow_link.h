#pragma once

#include <stdint.h>

namespace fieldnode {
struct __attribute__((packed)) EspNowFrame {
  uint8_t version; uint8_t class_flags; uint16_t device_idx; uint32_t sequence;
  uint32_t event_time_unix_s; int16_t temperature_x100; uint16_t vibration_x100;
  uint16_t rpm; int32_t latitude_x1e5; int32_t longitude_x1e5; uint16_t crc16;
};
static_assert(sizeof(EspNowFrame) == 28, "ESP-NOW frame must remain 28 bytes");
uint16_t crc16_ccitt_false(const uint8_t* data, uint16_t length);
bool encode_frame(EspNowFrame& frame);
bool decode_frame(const uint8_t* bytes, uint16_t length, EspNowFrame& frame);
}
