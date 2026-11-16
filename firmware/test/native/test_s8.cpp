#include <cmath>
#include <random>
#include <vector>
#include <unity.h>

#include "clock_policy.h"
#include "features.h"
#include "espnow_link.h"
#include "j1939.h"

void test_vibration_features() {
  constexpr size_t n = 4096;
  constexpr float amplitude = 0.8F;
  constexpr double pi = 3.14159265358979323846;
  std::vector<float> sine(n);
  for (size_t i = 0; i < n; ++i) sine[i] = amplitude * std::sin(2.0 * pi * i / 64.0);
  const auto sine_features = fieldnode::compute_vibration_features(sine.data(), sine.size());
  TEST_ASSERT_TRUE(sine_features.valid);
  TEST_ASSERT_FLOAT_WITHIN(0.002F, amplitude / std::sqrt(2.0F), sine_features.rms_g);
  TEST_ASSERT_FLOAT_WITHIN(0.002F, amplitude, sine_features.peak_g);
  TEST_ASSERT_FLOAT_WITHIN(0.01F, 1.5F, sine_features.kurtosis);

  std::mt19937 generator(42);
  std::normal_distribution<float> normal(0.0F, 0.25F);
  std::vector<float> gaussian(n);
  for (float& sample : gaussian) sample = normal(generator);
  const auto gaussian_features = fieldnode::compute_vibration_features(gaussian.data(), gaussian.size());
  TEST_ASSERT_TRUE(gaussian_features.valid);
  TEST_ASSERT_FLOAT_WITHIN(0.15F, 3.0F, gaussian_features.kurtosis);
  TEST_ASSERT_FALSE(fieldnode::compute_vibration_features(nullptr, 0).valid);
}

void test_clock_policy() {
  using fieldnode::TimeSource;
  TEST_ASSERT_EQUAL_INT(static_cast<int>(TimeSource::RTC),
                        static_cast<int>(fieldnode::select_time_source(true, false, true, true).source));
  TEST_ASSERT_EQUAL_INT(static_cast<int>(TimeSource::UNSYNCED),
                        static_cast<int>(fieldnode::select_time_source(true, true, true, true).source));
  TEST_ASSERT_EQUAL_INT(static_cast<int>(TimeSource::UNSYNCED),
                        static_cast<int>(fieldnode::select_time_source(false, false, true, true).source));
  TEST_ASSERT_EQUAL_INT(static_cast<int>(TimeSource::UNSYNCED),
                        static_cast<int>(fieldnode::select_time_source(true, false, true, false).source));
}

void test_espnow_frame_crc_and_size() {
  fieldnode::EspNowFrame frame{};
  frame.device_idx = 7;
  frame.sequence = 42;
  frame.temperature_x100 = 8123;
  TEST_ASSERT_TRUE(fieldnode::encode_frame(frame));
  fieldnode::EspNowFrame decoded{};
  TEST_ASSERT_TRUE(fieldnode::decode_frame(reinterpret_cast<const uint8_t*>(&frame), sizeof(frame), decoded));
  TEST_ASSERT_EQUAL_UINT32(42, decoded.sequence);
  reinterpret_cast<uint8_t*>(&frame)[3] ^= 0x01;
  TEST_ASSERT_FALSE(fieldnode::decode_frame(reinterpret_cast<const uint8_t*>(&frame), sizeof(frame), decoded));
}

void test_j1939_pgn_and_parameters() {
  using namespace fieldnode::j1939;
  uint8_t eec1[8] = {0, 0, 0, 0x40, 0x1F, 0, 0, 0};  // 1000 rpm
  CanFrame frame{(6U << 26) | (0xF0U << 16) | (0x04U << 8) | 0x80U, eec1, 8, true};
  Identifier id;
  TEST_ASSERT_TRUE(parse_identifier(frame.id, true, id));
  TEST_ASSERT_EQUAL_UINT32(61444U, id.pgn);
  TEST_ASSERT_EQUAL_UINT8(6U, id.priority);
  TEST_ASSERT_EQUAL_UINT8(0x80U, id.source_address);
  Identifier pdu1;
  TEST_ASSERT_TRUE(parse_identifier((6U << 26) | (0xEFU << 16) | (0xABU << 8) | 0x80U, true, pdu1));
  TEST_ASSERT_EQUAL_UINT32(0xEF00U, pdu1.pgn);
  TEST_ASSERT_FALSE(parse_identifier(0x123U, false, pdu1));
  Parameter parameter;
  TEST_ASSERT_TRUE(decode_engine_speed(frame, parameter));
  TEST_ASSERT_FLOAT_WITHIN(0.001F, 1000.0F, parameter.value);
  eec1[3] = 0xFF; eec1[4] = 0xFF;
  TEST_ASSERT_FALSE(decode_engine_speed(frame, parameter));
}

void test_j1939_temperature_pressure_and_dm1() {
  using namespace fieldnode::j1939;
  Parameter parameter;
  uint8_t et1[8] = {110, 0, 0, 0, 0, 0, 0, 0};
  CanFrame temp{(6U << 26) | (0xFEU << 16) | (0xEEU << 8) | 0x01U, et1, 8, true};
  TEST_ASSERT_TRUE(decode_coolant_temperature(temp, parameter));
  TEST_ASSERT_FLOAT_WITHIN(0.001F, 70.0F, parameter.value);
  et1[0] = 0xFF;
  TEST_ASSERT_FALSE(decode_coolant_temperature(temp, parameter));

  uint8_t eflp1[8] = {0, 0, 0, 25, 0, 0, 0, 0};
  CanFrame oil{(6U << 26) | (0xFEU << 16) | (0xEFU << 8) | 0x01U, eflp1, 8, true};
  TEST_ASSERT_TRUE(decode_oil_pressure(oil, parameter));
  TEST_ASSERT_FLOAT_WITHIN(0.001F, 100.0F, parameter.value);

  uint8_t dm1[6] = {0, 0, 100, 0, 3, 2};  // SPN 100, FMI 3, occurrence 2, CM=0
  CanFrame diagnostic{(6U << 26) | (0xFEU << 16) | (0xCAU << 8) | 0x01U, dm1, 6, true};
  Dtc dtcs[1];
  TEST_ASSERT_EQUAL_UINT(1U, decode_dm1(diagnostic, dtcs, 1));
  TEST_ASSERT_EQUAL_UINT32(100U, dtcs[0].spn);
  TEST_ASSERT_EQUAL_UINT8(3U, dtcs[0].fmi);
  TEST_ASSERT_EQUAL_UINT8(2U, dtcs[0].occurrence_count);
}
