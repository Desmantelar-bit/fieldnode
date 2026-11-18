#include "gps.h"

#include <cmath>

#if defined(ARDUINO)
#include <HardwareSerial.h>
#include <TinyGPSPlus.h>
#endif

namespace fieldnode {

bool gps_quality_is_usable(const bool fix, const float hdop, const uint32_t age_ms,
                           const float max_hdop, const uint32_t max_age_ms,
                           const double latitude, const double longitude,
                           const float speed_kmh) {
  return fix && std::isfinite(hdop) && hdop >= 0.0F && hdop <= max_hdop &&
         age_ms <= max_age_ms && std::isfinite(latitude) && latitude >= -90.0 &&
         latitude <= 90.0 && std::isfinite(longitude) && longitude >= -180.0 &&
         longitude <= 180.0 && std::isfinite(speed_kmh) && speed_kmh >= 0.0F &&
         speed_kmh <= 300.0F;
}

#if defined(ARDUINO)
class GpsAcquisition::TinyGPSPlusHolder {
 public:
  TinyGPSPlus parser;
  HardwareSerial serial{1};
  uint32_t last_fix_ms = 0;
};

void GpsAcquisition::begin(const uint8_t rx_pin, const uint8_t tx_pin, const uint32_t baud) {
  parser_ = new TinyGPSPlusHolder();
  parser_->serial.begin(baud, SERIAL_8N1, rx_pin, tx_pin);
}

void GpsAcquisition::poll() {
  if (parser_ == nullptr) return;
  while (parser_->serial.available() > 0) {
    if (parser_->parser.encode(static_cast<char>(parser_->serial.read())) &&
        parser_->parser.location.isValid() && parser_->parser.hdop.isValid()) {
      parser_->last_fix_ms = millis();
    }
  }
}

GpsReading GpsAcquisition::reading(const uint32_t now_ms, const float max_hdop,
                                   const uint32_t max_age_ms) const {
  if (parser_ == nullptr) return {false, false, NAN, NAN, NAN, NAN, UINT32_MAX, 0};
  const auto& p = parser_->parser;
  const uint32_t age = static_cast<uint32_t>(now_ms - parser_->last_fix_ms);
  const float hdop = p.hdop.isValid() ? static_cast<float>(p.hdop.hdop()) : NAN;
  const double lat = p.location.isValid() ? p.location.lat() : NAN;
  const double lon = p.location.isValid() ? p.location.lng() : NAN;
  const float speed = p.speed.isValid() ? static_cast<float>(p.speed.kmph()) : NAN;
  const bool usable = gps_quality_is_usable(p.location.isValid(), hdop, age, max_hdop,
                                            max_age_ms, lat, lon, speed);
  return {p.location.isValid(), usable, hdop, speed, lat, lon, age,
          p.satellites.isValid() ? static_cast<uint32_t>(p.satellites.value()) : 0};
}
#endif

}  // namespace fieldnode
