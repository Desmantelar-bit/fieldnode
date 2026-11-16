#pragma once
#include <stdint.h>
#include "espnow_link.h"
namespace fieldnode::node {
// The implementation is intentionally gated by the physical gateway bring-up.
// wifi_channel must match the gateway's Wi-Fi channel.
bool begin(uint8_t wifi_channel);
bool send_frame(const fieldnode::EspNowFrame& frame);
}
