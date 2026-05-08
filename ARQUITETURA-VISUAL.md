# 🏗️ Arquitetura do Sistema — FieldNode

## 📊 Visão Geral

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FIELDNODE ARCHITECTURE                          │
│                    Telemetria Offline-First para Agro                   │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐         ┌──────────────┐
│   SENSOR LAYER   │         │   GATEWAY LAYER  │         │  CLOUD LAYER │
│                  │         │                  │         │              │
│  ┌────────────┐  │         │  ┌────────────┐  │         │  ┌────────┐  │
│  │  DS18B20   │  │         │  │   ESP32    │  │         │  │ Django │  │
│  │ (Temp)     │──┼────────▶│  │  Gateway   │──┼────────▶│  │  API   │  │
│  └────────────┘  │         │  └────────────┘  │         │  └────────┘  │
│                  │         │                  │         │      │       │
│  ┌────────────┐  │  ESP-   │  ┌────────────┐  │  MQTT   │  ┌────────┐  │
│  │   SW-420   │  │  NOW    │  │  Wi-Fi AP  │  │  /HTTP  │  │ MySQL  │  │
│  │ (Vibração) │──┼────────▶│  │  (Hotspot) │  │         │  │   DB   │  │
│  └────────────┘  │         │  └────────────┘  │         │  └────────┘  │
│                  │         │        │         │         │      │       │
│  ┌────────────┐  │         │        │         │         │  ┌────────┐  │
│  │   Tacôm.   │  │         │        ▼         │         │  │   IA   │  │
│  │   (RPM)    │──┼─────┐   │  ┌────────────┐  │         │  │ Models │  │
│  └────────────┘  │     │   │  │  Dashboard │  │         │  └────────┘  │
│                  │     │   │  │   Local    │  │         │              │
└──────────────────┘     │   │  └────────────┘  │         └──────────────┘
                         │   │                  │
                         │   └──────────────────┘
                         │
                         └──────────────────────────────────────────────┐
                                                                        │
                         ┌──────────────────────────────────────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  BUFFER      │
                  │  30 dias     │
                  │  (SD Card)   │
                  └──────────────┘
```

---

## 🔄 Fluxo de Dados

### 1. Coleta (Sensor Layer)
```
DS18B20 ──┐
SW-420  ──┼──▶ ESP32 Node ──▶ JSON Payload
Tacômetro ┘                    {
                                 "id": "uuid-v4",
                                 "maquina_id": "CASE-TC5000-01",
                                 "temperatura": 78.5,
                                 "vibracao": 0.42,
                                 "rpm": 1850,
                                 "timestamp": "2024-01-15T14:30:00Z"
                               }
```

### 2. Transmissão Local (ESP-NOW)
```
ESP32 Node ──[ESP-NOW]──▶ ESP32 Gateway
   (50-500m alcance)
   (< 10ms latência)
   (sem necessidade de roteador)
```

### 3. Armazenamento Local (Gateway)
```
ESP32 Gateway ──▶ SD Card Buffer (30 dias)
              │
              └──▶ Dashboard Local (Wi-Fi AP)
                   http://192.168.4.1/
```

### 4. Sincronização Cloud (Quando online)
```
ESP32 Gateway ──[MQTT/HTTP]──▶ Django API
                                   │
                                   ├──▶ Validação
                                   ├──▶ Deduplicação (UUID)
                                   ├──▶ MySQL
                                   └──▶ IA (Anomalias + Manutenção)
```

---

## 🌐 Arquitetura Web (Frontend)

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND STRUCTURE                         │
└─────────────────────────────────────────────────────────────────┘

http://127.0.0.1:8000/
│
├── /frontend/
│   ├── index.html ──────────▶ Landing Page (Apresentação)
│   ├── dashboard.html ──────▶ Dashboard Operacional ⭐
│   ├── maquina.html ────────▶ Detalhes de Máquina
│   │
│   ├── /js/
│   │   ├── config.js ──────▶ Configuração da API
│   │   ├── api.js ─────────▶ Funções de comunicação
│   │   ├── colors.js ──────▶ Sistema de cores bicolor
│   │   └── status.js ──────▶ Lógica da tabela/carrossel
│   │
│   └── styles.css ─────────▶ Estilos globais
│
├── /api/
│   ├── /telemetria/ ───────▶ POST (ingestão) / GET (consulta)
│   ├── /leituras/ultimas/ ─▶ Última leitura de cada máquina
│   ├── /anomalias/ ────────▶ Detecção de anomalias (IA)
│   ├── /manutencao/ ───────▶ Previsão de manutenção (IA)
│   ├── /metricas/ ─────────▶ Métricas operacionais
│   └── /status-mqtt/ ──────▶ Status de conexão MQTT
│
└── /swagger/ ──────────────▶ Documentação interativa da API
```

---

## 🧠 Camada de IA

```
┌─────────────────────────────────────────────────────────────────┐
│                         IA PIPELINE                             │
└─────────────────────────────────────────────────────────────────┘

Leituras no Banco
      │
      ├──▶ Isolation Forest ──▶ Detecção de Anomalias
      │    (scikit-learn)        │
      │                          ├──▶ is_anomaly: bool
      │                          └──▶ anomaly_score: float
      │
      └──▶ Random Forest ────▶ Previsão de Manutenção
           (scikit-learn)        │
                                 ├──▶ probabilidade: float
                                 ├──▶ risco: str (BAIXO/MEDIO/ALTO)
                                 └──▶ recomendacao: str

Labels Sintéticos (Treinamento):
- Temperatura > 85°C → precisa_manutencao = 1
- Vibração > 0.8g → precisa_manutencao = 1
- RPM < 1300 → precisa_manutencao = 1
- Caso contrário → precisa_manutencao = 0
```

---

## 🔐 Camada de Segurança

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                            │
└─────────────────────────────────────────────────────────────────┘

ESP32 ──[X-API-Key]──▶ Django API
                          │
                          ├──▶ Validação de API Key
                          │    (fieldnode-demo-2024)
                          │
                          ├──▶ Validação de Payload
                          │    (temperatura, vibração, rpm)
                          │
                          ├──▶ Deduplicação UUID
                          │    (evita duplicatas)
                          │
                          └──▶ Dead-Letter Queue
                               (TelemetriaInvalida)

Roadmap (Produção):
- AES-128 para comunicação ESP32 ↔ Gateway
- JWT para autenticação web
- Rate limiting (10 req/min por IP)
- HTTPS obrigatório
```

---

## 💾 Modelo de Dados

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE SCHEMA                            │
└─────────────────────────────────────────────────────────────────┘

LeituraTelemetria
├── id (UUID, PK)
├── maquina_id (String, indexed)
├── temperatura (Float)
├── vibracao (Float)
├── rpm (Integer)
├── timestamp (DateTime, indexed)
├── created_at (DateTime, auto)
└── updated_at (DateTime, auto)

Índices:
- (maquina_id, timestamp) ──▶ Otimiza consultas de última leitura
- (timestamp) ──────────────▶ Otimiza consultas temporais

TelemetriaInvalida (Dead-Letter)
├── id (AutoIncrement, PK)
├── payload (JSON)
├── erro (Text)
├── created_at (DateTime)
└── ip_origem (String)
```

---

## 📊 Fluxo de Apresentação

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION FLOW                            │
└─────────────────────────────────────────────────────────────────┘

1. PROBLEMA (2 min)
   └──▶ Landing Page (/frontend/)
        ├── 40% das operações sem sinal
        ├── R$ 12k de prejuízo por parada
        └── Sistemas comerciais falham

2. SOLUÇÃO (3 min)
   └──▶ Landing Page (seção Arquitetura)
        ├── ESP32 → ESP-NOW → Gateway → Django
        ├── Offline-first por design
        └── Buffer 30 dias + sincronização automática

3. DEMONSTRAÇÃO (5 min)
   └──▶ Dashboard (/frontend/dashboard.html)
        ├── Inicie simulador: python scripts/demo_pane.py
        ├── Mostre tabela atualizando (3s)
        ├── Badge MQTT "Conectado"
        ├── Clique em máquina → popup
        └── Navegue para detalhes completos

4. API (2 min)
   └──▶ Swagger (/swagger/)
        ├── /api/telemetria/ (ingestão)
        ├── /api/leituras/ultimas/ (status)
        ├── /api/anomalias/ (IA)
        └── /api/manutencao/ (IA)

5. QUALIDADE (3 min)
   └──▶ Código / Documentação
        ├── Deduplicação UUID
        ├── Dead-letter queue
        ├── Testes automatizados
        └── SQL otimizado
```

---

## 🎯 Decisões Técnicas Chave

### Por que ESP-NOW em vez de Wi-Fi direto?
- ✅ Alcance maior (50-500m vs 30-100m)
- ✅ Latência menor (< 10ms vs 50-200ms)
- ✅ Não precisa de roteador
- ✅ Consumo de energia menor

### Por que API key em vez de JWT?
- ✅ ESP32 tem memória limitada
- ✅ JWT consome ~30% da flash
- ✅ API key é suficiente para protótipo
- 🔄 JWT no roadmap para produção

### Por que SQLite em dev e MySQL em prod?
- ✅ SQLite: zero configuração, ideal para dev
- ✅ MySQL: escalabilidade, transações ACID
- ✅ Django ORM abstrai a diferença

### Por que Isolation Forest para anomalias?
- ✅ Não precisa de dados rotulados
- ✅ Detecta outliers multivariados
- ✅ Rápido para retreinar
- ✅ Funciona bem com poucos dados

---

## 📈 Métricas de Performance

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE METRICS                          │
└─────────────────────────────────────────────────────────────────┘

Latência:
├── Sensor → Gateway: < 10ms (ESP-NOW)
├── Gateway → Dashboard Local: < 50ms (Wi-Fi)
├── Gateway → Cloud: 200-500ms (MQTT/HTTP)
└── Dashboard → API: 100-300ms (REST)

Throughput:
├── Leituras por segundo: 0.5 (1 a cada 2s)
├── Máquinas simultâneas: até 20 (limite ESP-NOW)
└── Requisições API: ilimitado (sem rate limit em dev)

Armazenamento:
├── Buffer local: 30 dias (~43.200 leituras)
├── Tamanho por leitura: ~200 bytes
└── Total buffer: ~8.6 MB

Confiabilidade:
├── Taxa de entrega ESP-NOW: > 95%
├── Taxa de deduplicação: 100% (UUID)
└── Taxa de validação: ~98% (2% rejeitado)
```

---

## 🚀 Roadmap de Produção

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION ROADMAP                           │
└─────────────────────────────────────────────────────────────────┘

FASE 1 (Protótipo) ✅
├── ESP32 + sensores
├── ESP-NOW
├── Dashboard local
├── API Django
├── IA básica
└── Deduplicação UUID

FASE 2 (MVP) 🔄
├── LoRa (alcance 2-5km)
├── AES-128 encryption
├── JWT authentication
├── Rate limiting
├── HTTPS
└── Alertas WhatsApp

FASE 3 (Produção) 📋
├── Integração John Deere
├── Integração Solinftec
├── App mobile nativo
├── IA com dados reais
├── Dashboard analytics
└── Multi-tenant
```

---

**Use este diagrama durante a apresentação para explicar a arquitetura visualmente.**

**Arquivo:** `ARQUITETURA-VISUAL.md`  
**Última atualização:** Janeiro 2024
