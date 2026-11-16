#include "features.h"

#include <cmath>

namespace fieldnode {

bool remove_dc(float* samples, const size_t count) {
  if (samples == nullptr || count == 0) return false;
  double mean = 0.0;
  for (size_t i = 0; i < count; ++i) {
    if (!std::isfinite(samples[i])) return false;
    mean += samples[i];
  }
  mean /= static_cast<double>(count);
  for (size_t i = 0; i < count; ++i) samples[i] -= static_cast<float>(mean);
  return true;
}

VibFeatures compute_vibration_features(const float* samples, const size_t count) {
  VibFeatures invalid{NAN, NAN, NAN, false};
  if (samples == nullptr || count < 2) return invalid;

  double mean = 0.0;
  for (size_t i = 0; i < count; ++i) {
    if (!std::isfinite(samples[i])) return invalid;
    mean += samples[i];
  }
  mean /= static_cast<double>(count);

  double second = 0.0;
  double fourth = 0.0;
  double peak = 0.0;
  for (size_t i = 0; i < count; ++i) {
    const double x = static_cast<double>(samples[i]) - mean;
    const double x2 = x * x;
    second += x2;
    fourth += x2 * x2;
    peak = fmax(peak, fabs(x));
  }
  const double variance = second / static_cast<double>(count);
  if (!std::isfinite(variance) || variance <= 1e-12) return invalid;
  const double kurtosis = (fourth / static_cast<double>(count)) / (variance * variance);
  return {static_cast<float>(sqrt(variance)), static_cast<float>(peak),
          static_cast<float>(kurtosis), std::isfinite(kurtosis)};
}

}
