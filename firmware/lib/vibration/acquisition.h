#pragma once

#ifdef ARDUINO
#include <Arduino.h>
#include <Wire.h>

#include "features.h"

namespace fieldnode {

struct VibrationWindow {
  VibFeatures x;
  VibFeatures y;
  VibFeatures z;
  uint16_t expected_samples;
  uint16_t valid_samples;
  bool valid;
};

class Mpu6050Acquisition {
 public:
  bool begin(TwoWire& bus, uint8_t address = 0x68);
  bool read_window(VibrationWindow& output);
  bool available() const { return available_; }

 private:
  TwoWire* bus_ = nullptr;
  uint8_t address_ = 0x68;
  bool available_ = false;
  bool write_register(uint8_t reg, uint8_t value);
  bool read_acceleration(float& x, float& y, float& z);
};

}
#endif
