# Integração com Sistemas Externos

## Visão Geral

O FieldNode é projetado para integração simples com sistemas de telemetria agrícola existentes. O endpoint de ingestão aceita dados de sensores ESP32 ou outros dispositivos IoT.

## Contrato da API de Telemetria

### Endpoint de Ingestão
```
POST /api/telemetria/
```

### Headers
```
Content-Type: application/json
```

### Corpo da Requisição
```json
{
  "id": "uuid-v4-gerado-pelo-dispositivo",
  "maquina_id": "identificador-cadastrado-no-sistema",
  "temperatura": 78.5,
  "vibracao": 0.42,
  "rpm": 1850,
  "timestamp": "2024-04-23T14:32:01.000Z"
}
```

#### Campos Obrigatórios
- `id`: UUID v4 único para deduplicação
- `maquina_id`: Identificador da máquina (cadastrado no admin Django)
- `temperatura`: Temperatura em °C (float)
- `vibracao`: Vibração adimensional 0.0-1.0 (float)
- `rpm`: Rotação por minuto (int)
- `timestamp`: Timestamp ISO 8601 do sensor

### Respostas

#### Sucesso (201 Created)
```json
{
  "status": "ok",
  "id": "uuid-confirmado-pelo-servidor"
}
```

#### Duplicata (200 OK) - Idempotente
```json
{
  "status": "duplicata ignorada",
  "id": "uuid-repetido"
}
```

#### Erro de Validação (400 Bad Request)
```json
{
  "status": "erro",
  "detalhes": {
    "maquina_id": ["Este campo não pode ser vazio."]
  }
}
```

## Fluxo de Integração

1. **Cadastro da Máquina**: Use o admin Django (`/admin/`) para cadastrar máquinas com seus `maquina_id`
2. **Configuração do Dispositivo**: Configure o ESP32 com o `maquina_id` correspondente
3. **Envio de Dados**: POST periódico para `/api/telemetria/` com dados dos sensores
4. **Monitoramento**: Acesse o dashboard em tempo real em `/`

## Exemplo de Implementação ESP32

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Configurações
const char* WIFI_SSID = "rede-agricola";
const char* WIFI_PASS = "senha-segura";
const char* API_URL = "http://seu-servidor:8000/api/telemetria/";
const char* MAQUINA_ID = "CASE-TC5000-01";

// Sensores simulados (substitua por leitura real)
float lerTemperatura() { return 75.2; }
float lerVibracao() { return 0.35; }
int lerRPM() { return 2100; }

void enviarTelemetria() {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");

  // Gera UUID v4 simples
  String uuid = "esp32-" + String(random(1000000)) + "-" + String(millis());

  // Timestamp ISO 8601
  time_t now = time(nullptr);
  char timestamp[25];
  strftime(timestamp, sizeof(timestamp), "%FT%TZ", gmtime(&now));

  // Monta JSON
  DynamicJsonDocument doc(256);
  doc["id"] = uuid;
  doc["maquina_id"] = MAQUINA_ID;
  doc["temperatura"] = lerTemperatura();
  doc["vibracao"] = lerVibracao();
  doc["rpm"] = lerRPM();
  doc["timestamp"] = timestamp;

  String jsonString;
  serializeJson(doc, jsonString);

  int httpResponseCode = http.POST(jsonString);

  if (httpResponseCode > 0) {
    Serial.println("Dados enviados com sucesso");
  } else {
    Serial.println("Erro no envio: " + String(httpResponseCode));
  }

  http.end();
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }

  // Envia a cada 30 segundos
  setInterval(enviarTelemetria, 30000);
}
```

## Considerações de Produção

- **Autenticação**: Para produção, adicione API keys ou tokens JWT
- **Rate Limiting**: Implemente controle de frequência por dispositivo
- **Validação**: Valide ranges realistas de sensores no backend
- **Compressão**: Considere gzip para payloads grandes
- **Offline**: Implemente buffer local no ESP32 para períodos sem conectividade

## Próximos Passos no Roadmap

- Autenticação por API key
- Suporte a CAN bus J1939
- Integração com Solinftec Operations Center
- Dashboard móvel para operadores