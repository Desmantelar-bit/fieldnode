#pragma once

#include <stdint.h>

// ESP32 DevKit comum. Confirme o GPIO na placa efetivamente usada antes do
// ensaio: esta escolha nao e evidencia de compatibilidade fisica.
#define PIN_DS18B20 4
#define PIN_STATUS_LED 2
#define PIN_LOCAL_BUZZER 26 // confirme no hardware antes do ensaio; saida local, nunca CAN
#define PIN_I2C_SDA 21
#define PIN_I2C_SCL 22
#define MPU6050_I2C_ADDRESS 0x69
#define PIN_RPM 27
#define PIN_GPS_RX 16
#define PIN_GPS_TX 17
#define GPS_BAUD 9600
#define RPM_PULSES_PER_REV 1
#define RPM_DEBOUNCE_US 500
#define GPS_MAX_HDOP 5.0F
#define GPS_MAX_AGE_MS 3000UL

#define SAMPLE_INTERVAL_MS 2000UL
#define MQTT_KEEPALIVE_SECONDS 60
#define TELEMETRY_SCHEMA_VERSION "1.2"
#define TELEMETRY_VIBRATION_UNIT "indice_0_10"

static constexpr uint32_t SEQUENCE_MAX = 0xFFFFFFFFUL;
