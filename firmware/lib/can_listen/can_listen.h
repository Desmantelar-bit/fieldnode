#pragma once

#include <stddef.h>
#include <stdint.h>

namespace fieldnode::can_listen {

struct Frame {
  uint32_t identifier = 0;
  bool extended = false;
  uint8_t data[8] = {};
  uint8_t length = 0;
};

using FrameSink = void (*)(const Frame& frame);

// LISTEN_ONLY e uma garantia de software. O TX do transceptor tambem deve
// permanecer fisicamente desconectado durante a validacao em bancada.
bool begin(int tx_pin, int rx_pin, bool j1939_250k);
size_t poll(FrameSink sink);
bool is_started();
bool is_listen_only();

}  // namespace fieldnode::can_listen
