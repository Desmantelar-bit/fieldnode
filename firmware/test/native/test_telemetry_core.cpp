#include <cmath>
#include <unity.h>

#include "telemetry_core.h"

void test_vibration_features();
void test_clock_policy();
void test_espnow_frame_crc_and_size();
void test_j1939_pgn_and_parameters();
void test_j1939_temperature_pressure_and_dm1();

void test_severity_boundaries() {
  using namespace fieldnode;
  TEST_ASSERT_EQUAL_INT(static_cast<int>(Severity::NORMAL), static_cast<int>(classify_temperature(74.999F)));
  TEST_ASSERT_EQUAL_INT(static_cast<int>(Severity::ATENCAO), static_cast<int>(classify_temperature(75.0F)));
  TEST_ASSERT_EQUAL_INT(static_cast<int>(Severity::CRITICO), static_cast<int>(classify_temperature(85.0F)));
}

void test_sample_validation_and_sequence() {
  using namespace fieldnode;
  TEST_ASSERT_TRUE(valid_sample(20.0F, 0.0F, 0));
  TEST_ASSERT_FALSE(valid_sample(-127.0F, 0.0F, 0));
  TEST_ASSERT_FALSE(valid_sample(NAN, 0.0F, 0));
  TEST_ASSERT_FALSE(valid_sample(20.0F, 10.001F, 0));
  TEST_ASSERT_FALSE(valid_sample(20.0F, 0.0F, 5001));
  TEST_ASSERT_EQUAL_UINT32(1, next_sequence(0));
  TEST_ASSERT_EQUAL_UINT32(1, next_sequence(UINT32_MAX));
}

void setUp(void) {}
void tearDown(void) {}

int run_all_tests() {
  UNITY_BEGIN();
  RUN_TEST(test_severity_boundaries);
  RUN_TEST(test_sample_validation_and_sequence);
  RUN_TEST(test_vibration_features);
  RUN_TEST(test_clock_policy);
  RUN_TEST(test_espnow_frame_crc_and_size);
  RUN_TEST(test_j1939_pgn_and_parameters);
  RUN_TEST(test_j1939_temperature_pressure_and_dm1);
  return UNITY_END();
}

#if defined(ARDUINO)
void setup() {
  run_all_tests();
}

void loop() {}
#else
int main(int argc, char **argv) {
  return run_all_tests();
}
#endif

