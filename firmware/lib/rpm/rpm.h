#pragma once

#include <stdint.h>

namespace fieldnode {

struct RpmReading {
  bool valid;
  bool stale;
  uint32_t pulses;
  uint32_t window_ms;
  float rpm;
};

class RpmCounter {
 public:
  explicit RpmCounter(uint32_t debounce_us = 500);
  void record_pulse_from_isr(uint32_t now_us);
  RpmReading snapshot(uint32_t now_ms, uint32_t window_ms, uint8_t pulses_per_rev);

 private:
  volatile uint32_t pulses_ = 0;
  volatile uint32_t last_pulse_us_ = 0;
  uint32_t debounce_us_;
  uint32_t window_started_ms_ = 0;
  bool started_ = false;
};

float rpm_from(uint32_t pulses_in_window, float window_s, uint8_t pulses_per_rev);

}  // namespace fieldnode
