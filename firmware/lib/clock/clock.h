#pragma once

#ifdef ARDUINO
#include <Arduino.h>
#include <Wire.h>
#include <stdint.h>

#include "clock_policy.h"

namespace fieldnode {

class Ds3231Clock {
 public:
  bool begin(TwoWire& bus, int sda, int scl, uint32_t frequency_hz = 100000);
  bool sync_from_gateway(uint32_t unix_epoch);
  bool now(uint32_t& unix_epoch) const;
  const char* time_source() const { return time_source_name(source_); }
  bool available() const { return available_; }
  bool oscillator_stop() const { return oscillator_stop_; }
  String iso8601() const;

 private:
  TwoWire* bus_ = nullptr;
  TimeSource source_ = TimeSource::UNSYNCED;
  bool available_ = false;
  bool oscillator_stop_ = true;
  bool previously_synced_ = false;
  uint8_t bcd_to_dec(uint8_t value) const;
  uint8_t dec_to_bcd(uint8_t value) const;
  bool read_register(uint8_t reg, uint8_t& value) const;
  bool write_register(uint8_t reg, uint8_t value) const;
  bool read_epoch(uint32_t& epoch) const;
  bool write_epoch(uint32_t epoch) const;
  bool plausible(uint32_t epoch) const;
  void select_state(uint32_t epoch);
};

}
#endif
