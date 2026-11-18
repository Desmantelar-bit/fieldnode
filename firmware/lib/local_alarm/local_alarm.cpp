#include "local_alarm.h"

namespace fieldnode::local_alarm {

void trigger(State& state, const char* code, const char* message, const Output output) {
  state = {true, code, message};
  if (output != nullptr) output(true, code, message);
}

void clear(State& state, const Output output) {
  state = {};
  if (output != nullptr) output(false, nullptr, nullptr);
}

}  // namespace fieldnode::local_alarm
