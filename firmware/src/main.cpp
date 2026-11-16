#include <Arduino.h>
#include <ArduinoJson.h>
#include <DallasTemperature.h>
#include <Preferences.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <OneWire.h>
#include <esp_system.h>
#include <Wire.h>

#include "config.h"
#include "secrets.h"
#include "telemetry_core.h"
#include "clock.h"
#include "acquisition.h"

namespace {
OneWire one_wire(PIN_DS18B20);
DallasTemperature ds18b20(&one_wire);
WiFiClient wifi_client;
PubSubClient mqtt(wifi_client);
Preferences preferences;
String boot_id;
uint32_t sequence = 0;
unsigned long last_sample_ms = 0;
fieldnode::Ds3231Clock rtc;
fieldnode::Mpu6050Acquisition vibration;

void set_led(const bool on) { digitalWrite(PIN_STATUS_LED, on ? HIGH : LOW); }

String uuid_v4() {
  uint32_t words[4];
  for (auto& word : words) word = esp_random();
  words[1] = (words[1] & 0xFFFF0FFFU) | 0x00004000U;
  words[2] = (words[2] & 0x3FFFFFFFU) | 0x80000000U;
  char value[37];
  snprintf(value, sizeof(value), "%08lx-%04lx-%04lx-%04lx-%04lx%08lx",
           static_cast<unsigned long>(words[0]), static_cast<unsigned long>(words[1] >> 16),
           static_cast<unsigned long>(words[1] & 0xFFFF), static_cast<unsigned long>(words[2] >> 16),
           static_cast<unsigned long>(words[2] & 0xFFFF), static_cast<unsigned long>(words[3]));
  return String(value);
}

void connect_wifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(FIELDNODE_WIFI_SSID, FIELDNODE_WIFI_PASSWORD);
  Serial.printf("[wifi] conectando a %s", FIELDNODE_WIFI_SSID);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print('.');
  }
  Serial.printf(" conectado, IP=%s\n", WiFi.localIP().toString().c_str());
}

bool connect_mqtt() {
  if (WiFi.status() != WL_CONNECTED) return false;
  mqtt.setServer(FIELDNODE_MQTT_HOST, FIELDNODE_MQTT_PORT);
  const String client_id = String(FIELDNODE_DEVICE_ID) + "-" + boot_id;
  if (!mqtt.connect(client_id.c_str(), FIELDNODE_MQTT_USERNAME, FIELDNODE_MQTT_PASSWORD)) {
    Serial.printf("[mqtt] falha rc=%d\n", mqtt.state());
    set_led(false);
    return false;
  }
  Serial.println("[mqtt] conectado");
  set_led(true);
  return true;
}

void load_sequence() {
  preferences.begin("telemetry", false);
  sequence = preferences.getUInt("sequence", 0);
}

void publish_temperature(const float temperature_c, const fieldnode::VibrationWindow* window) {
  const auto severity = fieldnode::classify_temperature(temperature_c);
  const uint32_t next = fieldnode::next_sequence(sequence);
  const String message_id = boot_id + "-" + String(next);
  StaticJsonDocument<1536> document;
  document["device_id"] = FIELDNODE_DEVICE_ID;
  document["maquina_id"] = FIELDNODE_DEVICE_ID;
  document["message_id"] = message_id;
  document["sequence_number"] = next;
  document["boot_id"] = boot_id;
  document["uptime_ms"] = millis();
  document["time_source"] = rtc.time_source();
  const String timestamp = rtc.iso8601();
  if (timestamp.length() > 0) document["timestamp"] = timestamp;
  document["schema_version"] = TELEMETRY_SCHEMA_VERSION;
  document["temperatura"] = temperature_c;
  document["vibracao"] = 0.0F;
  document["vibracao_unit"] = TELEMETRY_VIBRATION_UNIT;
  document["rpm"] = 0;
  document["severidade"] = fieldnode::severity_name(severity);
  document["source"] = "firmware";
  document["transport"] = "mqtt";
  if (window != nullptr && window->valid) {
    document["vibracao_unit"] = "g";
    JsonObject rms = document["vibracao_rms_g"].to<JsonObject>();
    JsonObject peak = document["vibracao_pico_g"].to<JsonObject>();
    JsonObject kurtosis = document["vibracao_curtose"].to<JsonObject>();
    rms["x"] = window->x.rms_g; rms["y"] = window->y.rms_g; rms["z"] = window->z.rms_g;
    peak["x"] = window->x.peak_g; peak["y"] = window->y.peak_g; peak["z"] = window->z.peak_g;
    kurtosis["x"] = window->x.kurtosis; kurtosis["y"] = window->y.kurtosis; kurtosis["z"] = window->z.kurtosis;
  }
  char payload[1536];
  const size_t size = serializeJson(document, payload, sizeof(payload));
  const String topic = String("fieldnode/") + FIELDNODE_DEVICE_ID + "/telemetria";
  if (mqtt.publish(topic.c_str(), payload, size)) {
    sequence = next;
    preferences.putUInt("sequence", sequence);
    Serial.printf("[telemetry] publicada seq=%lu temp=%.2f severity=%s\n",
                  static_cast<unsigned long>(sequence), temperature_c,
                  fieldnode::severity_name(severity));
    set_led(true);
  } else {
    Serial.println("[mqtt] publicacao falhou; nenhuma outbox persistente e implementada nesta etapa");
    set_led(false);
  }
}
}

void setup() {
  pinMode(PIN_STATUS_LED, OUTPUT);
  set_led(false);
  Serial.begin(115200);
  boot_id = uuid_v4();
  load_sequence();
  ds18b20.begin();
  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, 100000);
  rtc.begin(Wire, PIN_I2C_SDA, PIN_I2C_SCL);
  vibration.begin(Wire, MPU6050_I2C_ADDRESS);
  Serial.printf("[boot] device=%s boot_id=%s sequence=%lu\n", FIELDNODE_DEVICE_ID,
                boot_id.c_str(), static_cast<unsigned long>(sequence));
  connect_wifi();
  connect_mqtt();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    set_led(false);
    connect_wifi();
  }
  if (!mqtt.connected()) connect_mqtt();
  mqtt.loop();
  if (millis() - last_sample_ms < SAMPLE_INTERVAL_MS) return;
  last_sample_ms = millis();
  ds18b20.requestTemperatures();
  const float temperature_c = ds18b20.getTempCByIndex(0);
  if (temperature_c == DEVICE_DISCONNECTED_C || !fieldnode::valid_temperature(temperature_c)) {
    Serial.println("[sensor] falha ou valor invalido; leitura nao publicada");
    set_led(false);
    return;
  }
  fieldnode::VibrationWindow window{};
  const bool vibration_valid = vibration.read_window(window);
  if (mqtt.connected()) publish_temperature(temperature_c, vibration_valid ? &window : nullptr);
}
