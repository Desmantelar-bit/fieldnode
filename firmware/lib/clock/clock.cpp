#ifdef ARDUINO
#include "clock.h"

#include <time.h>

namespace fieldnode {
namespace {
constexpr uint8_t kAddress = 0x68;
constexpr uint8_t kStatus = 0x0F;
constexpr uint8_t kOsf = 0x80;
}

uint8_t Ds3231Clock::bcd_to_dec(const uint8_t value) const { return (value >> 4) * 10 + (value & 0x0F); }
uint8_t Ds3231Clock::dec_to_bcd(const uint8_t value) const { return ((value / 10) << 4) | (value % 10); }

bool Ds3231Clock::read_register(const uint8_t reg, uint8_t& value) const {
  bus_->beginTransmission(kAddress);
  bus_->write(reg);
  if (bus_->endTransmission(false) != 0 || bus_->requestFrom(kAddress, static_cast<uint8_t>(1)) != 1) return false;
  value = bus_->read();
  return true;
}

bool Ds3231Clock::write_register(const uint8_t reg, const uint8_t value) const {
  bus_->beginTransmission(kAddress);
  bus_->write(reg);
  bus_->write(value);
  return bus_->endTransmission() == 0;
}

bool Ds3231Clock::read_epoch(uint32_t& epoch) const {
  uint8_t raw[7];
  bus_->beginTransmission(kAddress);
  bus_->write(0);
  if (bus_->endTransmission(false) != 0 || bus_->requestFrom(kAddress, static_cast<uint8_t>(7)) != 7) return false;
  for (auto& byte : raw) byte = bus_->read();
  tm value{};
  value.tm_sec = bcd_to_dec(raw[0] & 0x7F);
  value.tm_min = bcd_to_dec(raw[1] & 0x7F);
  value.tm_hour = bcd_to_dec(raw[2] & 0x3F);
  value.tm_mday = bcd_to_dec(raw[4] & 0x3F);
  value.tm_mon = bcd_to_dec(raw[5] & 0x1F) - 1;
  value.tm_year = 100 + bcd_to_dec(raw[6]);
  value.tm_isdst = 0;
  epoch = static_cast<uint32_t>(timegm(&value));
  return plausible(epoch);
}

bool Ds3231Clock::write_epoch(const uint32_t epoch) const {
  const time_t seconds = static_cast<time_t>(epoch);
  tm value{};
  gmtime_r(&seconds, &value);
  bus_->beginTransmission(kAddress);
  bus_->write(0);
  bus_->write(dec_to_bcd(value.tm_sec));
  bus_->write(dec_to_bcd(value.tm_min));
  bus_->write(dec_to_bcd(value.tm_hour));
  bus_->write(dec_to_bcd(value.tm_wday == 0 ? 7 : value.tm_wday));
  bus_->write(dec_to_bcd(value.tm_mday));
  bus_->write(dec_to_bcd(value.tm_mon + 1));
  bus_->write(dec_to_bcd(value.tm_year - 100));
  return bus_->endTransmission() == 0;
}

bool Ds3231Clock::plausible(const uint32_t epoch) const {
  return epoch >= 1577836800UL && epoch <= 4102444800UL;
}

void Ds3231Clock::select_state(const uint32_t epoch) {
  const auto decision = select_time_source(available_, oscillator_stop_, plausible(epoch), previously_synced_);
  source_ = decision.source;
}

bool Ds3231Clock::begin(TwoWire& bus, const int sda, const int scl, const uint32_t frequency_hz) {
  bus_ = &bus;
  bus_->begin(sda, scl, frequency_hz);
  bus_->setTimeOut(50);
  uint8_t status = 0;
  available_ = read_register(kStatus, status);
  oscillator_stop_ = !available_ || (status & kOsf) != 0;
  // A clear OSF is the DS3231's persisted evidence that its oscillator was not
  // interrupted. A plausible date alone is never enough.
  previously_synced_ = available_ && !oscillator_stop_;
  uint32_t epoch = 0;
  const bool valid = available_ && read_epoch(epoch);
  select_state(epoch);
  Serial.printf("[rtc] i2c=%s osf=%s time_source=%s\n", available_ ? "ok" : "falha",
                oscillator_stop_ ? "ativo" : "inativo", time_source());
  return valid && source_ != TimeSource::UNSYNCED;
}

bool Ds3231Clock::sync_from_gateway(const uint32_t unix_epoch) {
  if (!available_ || !plausible(unix_epoch) || !write_epoch(unix_epoch)) return false;
  uint32_t verified = 0;
  if (!read_epoch(verified) || verified < unix_epoch - 1 || verified > unix_epoch + 1) return false;
  uint8_t status = 0;
  if (!read_register(kStatus, status) || !write_register(kStatus, status & ~kOsf)) return false;
  oscillator_stop_ = false;
  previously_synced_ = true;
  source_ = TimeSource::GATEWAY;
  Serial.printf("[rtc] sincronizado por gateway epoch=%lu confirmado\n", static_cast<unsigned long>(verified));
  return true;
}

bool Ds3231Clock::now(uint32_t& unix_epoch) const {
  if (source_ == TimeSource::UNSYNCED || !read_epoch(unix_epoch)) return false;
  return true;
}

String Ds3231Clock::iso8601() const {
  uint32_t epoch = 0;
  if (!now(epoch)) return String();
  const time_t seconds = static_cast<time_t>(epoch);
  tm value{};
  gmtime_r(&seconds, &value);
  char output[25];
  strftime(output, sizeof(output), "%Y-%m-%dT%H:%M:%SZ", &value);
  return String(output);
}
}
#endif
