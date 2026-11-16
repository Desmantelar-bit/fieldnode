#include <cmath>
#include <random>
#include <vector>
#include <unity.h>

#include "clock_policy.h"
#include "features.h"

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
