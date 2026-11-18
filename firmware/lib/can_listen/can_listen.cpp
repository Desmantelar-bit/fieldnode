#include "can_listen.h"

#if defined(ARDUINO_ARCH_ESP32)
#include <driver/twai.h>
#endif

namespace fieldnode::can_listen {
namespace {
bool started = false;
bool listen_only = false;
}

bool begin(const int tx_pin, const int rx_pin, const bool j1939_250k) {
#if defined(ARDUINO_ARCH_ESP32)
  // Nao trocar por TWAI_MODE_NORMAL: este modulo nunca deve transmitir.
  twai_general_config_t general = TWAI_GENERAL_CONFIG_DEFAULT(
      static_cast<gpio_num_t>(tx_pin), static_cast<gpio_num_t>(rx_pin), TWAI_MODE_LISTEN_ONLY);
  twai_timing_config_t timing = j1939_250k ? TWAI_TIMING_CONFIG_250KBITS() : TWAI_TIMING_CONFIG_500KBITS();
  twai_filter_config_t filter = TWAI_FILTER_CONFIG_ACCEPT_ALL();
  if (twai_driver_install(&general, &timing, &filter) != ESP_OK) return false;
  if (twai_start() != ESP_OK) {
    twai_driver_uninstall();
    return false;
  }
#else
  (void)tx_pin;
  (void)rx_pin;
  (void)j1939_250k;
#endif
  started = true;
  listen_only = true;
  return true;
}

size_t poll(const FrameSink sink) {
  if (!started || sink == nullptr) return 0U;
  size_t count = 0U;
#if defined(ARDUINO_ARCH_ESP32)
  twai_message_t message;
  while (twai_receive(&message, 0) == ESP_OK) {
    Frame frame;
    frame.identifier = message.identifier;
    frame.extended = message.extd;
    frame.length = message.data_length_code > 8U ? 8U : message.data_length_code;
    for (uint8_t i = 0; i < frame.length; ++i) frame.data[i] = message.data[i];
    sink(frame);
    ++count;
  }
#endif
  return count;
}

bool is_started() { return started; }
bool is_listen_only() { return listen_only; }

}  // namespace fieldnode::can_listen
