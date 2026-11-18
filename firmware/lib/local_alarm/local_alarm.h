#pragma once

namespace fieldnode::local_alarm {

using Output = void (*)(bool active, const char* code, const char* message);

struct State {
  bool active = false;
  const char* code = nullptr;
  const char* message = nullptr;
};

void trigger(State& state, const char* code, const char* message, Output output = nullptr);
void clear(State& state, Output output = nullptr);

}  // namespace fieldnode::local_alarm
