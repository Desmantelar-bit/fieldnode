# FieldNode

> Telemetria offline-first para colheitadeiras agrícolas

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.2-green?logo=django)
![Docker](https://img.shields.io/badge/Docker-enabled-2496ED?logo=docker)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## O Problema

Colheitadeiras operam em áreas sem sinal. Dados de temperatura, vibração e RPM ficam presos no campo — chegam atrasados ou não chegam. Quebras inesperadas custam caro.

**FieldNode** resolve com telemetria local via Wi-Fi e sincronização automática quando conecta.

---

## Arquitetura

```
[Sensores] → [ESP32 Nó #1]
                 │ (ESP-NOW)
              [ESP32 Gateway]
              ┌──────┴──────┐
              │             │
         [Dashboard]    [API Django]
        (local offline)    │
                      [MySQL + DRF]
                           │
                    [Dashboard Web]
```

---

## Stack

| Camada | Tecnologia |
|--------|------------|
| Hardware | ESP32 + Arduino |
| Wireless | ESP-NOW + MQTT |
| Backend | Django 5.2 + DRF |
| Banco | MySQL 8 |
| Docs | Swagger (drf-yasg) |
| Frontend | HTML/CSS/JS + Chart.js |
| Deploy | Docker + Docker Compose |

---

## Como Rodar

### Com Docker (recomendado)

**Pré-requisitos**: Docker e Docker Compose

```bash
git clone <repo-url> && cd fieldnode

# Windows
.\.startup.cmd

# Linux/macOS
bash .startup.sh
```

Ou manualmente:
```bash
docker-compose up -d
docker exec fieldnode-api python manage.py createsuperuser  # primeira vez
```

**Endpoints**:
- **API**: http://localhost:8000
- **Swagger**: http://localhost:8000/swagger/
- **Admin**: http://localhost:8000/admin/
- **MQTT**: localhost:1883

### Desenvolvimento Local (sem Docker)

**Pré-requisitos**: Python 3.12, MySQL 8, Git

```bash
git clone <repo-url> && cd fieldnode

python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux/macOS

pip install -r requirements.txt
cp .env.example .env        # edite DB_HOST para localhost
python manage.py migrate
python manage.py runserver
```

---

## API

### Endpoint Principal

**POST `/api/telemetria/`**

Ingestão de dados do ESP32 com deduplicação automática por UUID.

```bash
curl -X POST http://localhost:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "uuid-v4",
    "maquina_id": "CASE-TC5000-01",
    "temperatura": 78.5,
    "vibracao": 0.42,
    "rpm": 1850,
    "timestamp": "2024-04-23T14:32:01Z"
  }'
```

**Resposta (201)**: `{"status": "ok", "id": "uuid"}`  
**Resposta (200, duplicata)**: `{"status": "duplicata ignorada", "id": "uuid"}`

### CRUD

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET/POST | `/Colheitadeira/` | Máquinas |
| GET/POST | `/Operario/` | Operários |
| GET/POST | `/Temperaturamaquina/` | Histórico de temperatura |

Documentação interativa: `http://localhost:8000/swagger/`

---

## Roadmap

- [x] API REST com Django + DRF
- [x] Deduplicação por UUID
- [x] Dashboard web com Chart.js
- [x] Swagger + Admin
- [x] Pipeline MQTT: ESP32 → broker → Django → MySQL
- [x] Detecção de anomalias (Isolation Forest)
- [x] Manutenção preditiva (Random Forest)
- [x] Polling em tempo real (3s)
- [ ] Autenticação (JWT)
- [ ] Alertas (WhatsApp)
- [ ] Integração ESP32 → Gateway completa
- [ ] Suite de testes (pytest)

---

## Créditos

Trabalho de Conclusão de Curso — SENAI Informática

| | | | |
|:-:|:-:|:-:|:-:|
| [Vinícius Morales](https://github.com/ViniciusMorales) | [Paola Machado](https://github.com/Paola5858) | [Ana Caroline Furlaneto](https://github.com/acfurlaneto) | Giovana D'Angelo |

---

## Licença

MIT
