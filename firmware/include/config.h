#pragma once

#include <stdint.h>

// ESP32 DevKit comum. Confirme o GPIO na placa efetivamente usada antes do
// ensaio: esta escolha nao e evidencia de compatibilidade fisica.
#define PIN_DS18B20 4
#define PIN_STATUS_LED 2
#define PIN_I2C_SDA 21
#define PIN_I2C_SCL 22
#define MPU6050_I2C_ADDRESS 0x69

#define SAMPLE_INTERVAL_MS 2000UL
#define MQTT_KEEPALIVE_SECONDS 60
#define TELEMETRY_SCHEMA_VERSION "1.2"
#define TELEMETRY_VIBRATION_UNIT "indice_0_10"

static constexpr uint32_t SEQUENCE_MAX = 0xFFFFFFFFUL;
