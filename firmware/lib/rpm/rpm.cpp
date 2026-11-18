#include "rpm.h"

#include <cmath>

#if defined(ARDUINO_ARCH_ESP32)
#include "freertos/FreeRTOS.h"
#include "freertos/portmacro.h"
#endif

namespace fieldnode {

namespace {
#if defined(ARDUINO_ARCH_ESP32)
portMUX_TYPE rpm_mux = portMUX_INITIALIZER_UNLOCKED;
#endif
}

RpmCounter::RpmCounter(const uint32_t debounce_us) : debounce_us_(debounce_us) {}

void RpmCounter::record_pulse_from_isr(const uint32_t now_us) {
#if defined(ARDUINO_ARCH_ESP32)
  portENTER_CRITICAL_ISR(&rpm_mux);
#endif
  if (static_cast<uint32_t>(now_us - last_pulse_us_) >= debounce_us_) {
    ++pulses_;
    last_pulse_us_ = now_us;
  }
#if defined(ARDUINO_ARCH_ESP32)
  portEXIT_CRITICAL_ISR(&rpm_mux);
#endif
}

RpmReading RpmCounter::snapshot(const uint32_t now_ms, const uint32_t window_ms,
                                const uint8_t pulses_per_rev) {
  if (!started_) {
    started_ = true;
    window_started_ms_ = now_ms;
    return {false, true, 0, 0, 0.0F};
  }
  const uint32_t elapsed = static_cast<uint32_t>(now_ms - window_started_ms_);
  if (window_ms == 0 || elapsed < window_ms || pulses_per_rev == 0) {
    return {false, true, 0, elapsed, 0.0F};
  }
  uint32_t captured = 0;
#if defined(ARDUINO_ARCH_ESP32)
  portENTER_CRITICAL(&rpm_mux);
#endif
  captured = pulses_;
  pulses_ = 0;
#if defined(ARDUINO_ARCH_ESP32)
  portEXIT_CRITICAL(&rpm_mux);
#endif
  window_started_ms_ = now_ms;
  const float value = rpm_from(captured, elapsed / 1000.0F, pulses_per_rev);
  return {true, false, captured, elapsed, value};
}

float rpm_from(const uint32_t pulses_in_window, const float window_s,
               const uint8_t pulses_per_rev) {
  if (window_s <= 0.0F || pulses_per_rev == 0 || !std::isfinite(window_s)) return NAN;
  return (static_cast<float>(pulses_in_window) / static_cast<float>(pulses_per_rev)) *
         (60.0F / window_s);
}

}  // namespace fieldnode
