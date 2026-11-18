#pragma once

#include <stdint.h>

namespace fieldnode {

struct GpsReading {
  bool fix;
  bool usable;
  float hdop;
  float speed_kmh;
  double latitude;
  double longitude;
  uint32_t age_ms;
  uint32_t satellites;
};

bool gps_quality_is_usable(bool fix, float hdop, uint32_t age_ms,
                           float max_hdop, uint32_t max_age_ms,
                           double latitude, double longitude, float speed_kmh);

#if defined(ARDUINO)
class GpsAcquisition {
 public:
  void begin(uint8_t rx_pin, uint8_t tx_pin, uint32_t baud);
  void poll();
  GpsReading reading(uint32_t now_ms, float max_hdop, uint32_t max_age_ms) const;

 private:
  class TinyGPSPlusHolder;
  TinyGPSPlusHolder* parser_ = nullptr;
};
#endif

}  // namespace fieldnode
