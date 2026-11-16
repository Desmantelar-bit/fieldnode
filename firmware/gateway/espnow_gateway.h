#pragma once
#include <stdint.h>
namespace fieldnode::gateway {
// The callback must count send failures; ACK is emitted only after app ACK.
bool begin(uint8_t wifi_channel);
}
