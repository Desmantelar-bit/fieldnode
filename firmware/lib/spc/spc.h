#pragma once

namespace fieldnode::spc {

struct State {
  float mean = 0.0F;
  float var = 0.0F;
  float s_hi = 0.0F;
  float s_lo = 0.0F;
  bool initialized = false;
  bool frozen = false;
};

// Retorna +1 para deslocamento alto, -1 para deslocamento baixo e 0 normal.
// O baseline so aprende enquanto nao ha alarme.
int update(State& state, float value, float alpha, float k, float h);
void reset(State& state);

}  // namespace fieldnode::spc
