#pragma once

#include <stddef.h>

namespace fieldnode {

struct VibFeatures {
  float rms_g;
  float peak_g;
  float kurtosis;
  bool valid;
};

// The input must be acceleration in g. The mean is removed before statistics.
VibFeatures compute_vibration_features(const float* samples, size_t count);

// Removes the window DC component in-place. Returns false for invalid input.
bool remove_dc(float* samples, size_t count);

}
