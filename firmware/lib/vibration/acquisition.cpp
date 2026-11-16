#ifdef ARDUINO
#include "acquisition.h"

namespace fieldnode {
namespace {
constexpr uint8_t kPowerManagement = 0x6B;
constexpr uint8_t kConfig = 0x1A;
constexpr uint8_t kSampleRateDivider = 0x19;
constexpr uint8_t kAccelConfig = 0x1C;
constexpr uint8_t kAccelData = 0x3B;
constexpr uint16_t kWindowSamples = 128;
constexpr uint32_t kSampleIntervalMs = 10;
}

bool Mpu6050Acquisition::write_register(const uint8_t reg, const uint8_t value) {
  bus_->beginTransmission(address_);
  bus_->write(reg);
  bus_->write(value);
  return bus_->endTransmission() == 0;
}

bool Mpu6050Acquisition::begin(TwoWire& bus, const uint8_t address) {
  bus_ = &bus;
  address_ = address;
  // Wake up, 100 Hz internal sample rate, DLPF ~44 Hz, +/-2 g (16384 LSB/g).
  available_ = write_register(kPowerManagement, 0x00) &&
               write_register(kConfig, 0x03) &&
               write_register(kSampleRateDivider, 0x09) &&
               write_register(kAccelConfig, 0x00);
  Serial.printf("[vibration] MPU6050=%s address=0x%02X sample_hz=100 window=%u\n",
                available_ ? "ok" : "falha", address_, kWindowSamples);
  return available_;
}

bool Mpu6050Acquisition::read_acceleration(float& x, float& y, float& z) {
  bus_->beginTransmission(address_);
  bus_->write(kAccelData);
  if (bus_->endTransmission(false) != 0 || bus_->requestFrom(address_, static_cast<uint8_t>(6)) != 6) return false;
  const int16_t raw_x = static_cast<int16_t>((bus_->read() << 8) | bus_->read());
  const int16_t raw_y = static_cast<int16_t>((bus_->read() << 8) | bus_->read());
  const int16_t raw_z = static_cast<int16_t>((bus_->read() << 8) | bus_->read());
  x = static_cast<float>(raw_x) / 16384.0F;
  y = static_cast<float>(raw_y) / 16384.0F;
  z = static_cast<float>(raw_z) / 16384.0F;
  return true;
}

bool Mpu6050Acquisition::read_window(VibrationWindow& output) {
  output = {};
  output.expected_samples = kWindowSamples;
  if (!available_) return false;
  float x[kWindowSamples], y[kWindowSamples], z[kWindowSamples];
  for (uint16_t i = 0; i < kWindowSamples; ++i) {
    if (!read_acceleration(x[i], y[i], z[i])) break;
    ++output.valid_samples;
    delay(kSampleIntervalMs);
  }
  if (output.valid_samples != kWindowSamples) return false;
  if (!remove_dc(x, kWindowSamples) || !remove_dc(y, kWindowSamples) || !remove_dc(z, kWindowSamples)) return false;
  output.x = compute_vibration_features(x, kWindowSamples);
  output.y = compute_vibration_features(y, kWindowSamples);
  output.z = compute_vibration_features(z, kWindowSamples);
  output.valid = output.x.valid && output.y.valid && output.z.valid;
  return output.valid;
}
}
#endif
