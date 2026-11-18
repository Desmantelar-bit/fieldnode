#include "spc.h"

#include <cmath>

namespace fieldnode::spc {

int update(State& state, const float value, const float alpha, const float k, const float h) {
  if (!std::isfinite(value) || !std::isfinite(alpha) || !std::isfinite(k) || !std::isfinite(h) ||
      alpha <= 0.0F || alpha > 1.0F || k < 0.0F || h <= 0.0F) {
    return 0;
  }
  if (!state.initialized) {
    state.mean = value;
    state.var = 0.0F;
    state.initialized = true;
    return 0;
  }

  const float delta = value - state.mean;
  const float standard_deviation = std::sqrt(state.var) + 1e-3F;
  // Limita um pico isolado: ele pode contribuir, mas nao atravessa o
  // horizonte h sozinho. Um deslocamento sustentado ainda acumula CUSUM.
  const float z = fmaxf(-3.0F, fminf(3.0F, delta / standard_deviation));
  state.s_hi = fmaxf(0.0F, state.s_hi + z - k);
  state.s_lo = fmaxf(0.0F, state.s_lo - z - k);
  const bool alarm = state.s_hi > h || state.s_lo > h;

  if (!state.frozen && !alarm) {
    state.mean += alpha * delta;
    state.var = (1.0F - alpha) * (state.var + alpha * delta * delta);
  }
  state.frozen = state.frozen || alarm;
  return alarm ? (state.s_hi > h ? 1 : -1) : 0;
}

void reset(State& state) { state = {}; }

}  // namespace fieldnode::spc
