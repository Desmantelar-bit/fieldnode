# 🚜 FieldNode

<p align="center">
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white"/>
  <img src="https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white"/>
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/>
</p>

> **Telemetria Offline-First para o Agronegócio.**  
> O dado de campo existe. O FieldNode garante que ele chegue, mesmo sem internet.

## 🌾 O Problema

Cerca de 40% das operações de colheita no Brasil ocorrem em áreas de sombra de conectividade (sem 4G/Wi-Fi). Sistemas comerciais falham porque dependem de nuvem em tempo real. Quando um rolamento superaquece sem internet, a máquina quebra e o prejuízo é imediato.

## 🛠 A Solução

O FieldNode é um ecossistema de hardware e software focado em **resiliência**. 

1. **Módulos ESP32** na máquina coletam telemetria e transmitem via **ESP-NOW** (protocolo P2P sem necessidade de roteador).
2. Um **Gateway Local** recebe os dados e disponibiliza um dashboard em tempo real direto no campo.
3. Quando a máquina ou o Gateway encontra conectividade (chegada na sede), os dados são sincronizados automaticamente com o **Backend Django** usando deduplicação por UUID, evitando perda ou replicação de dados.

## 🏗 Arquitetura

```text
[Sensor Vibr./Temp] ---> (ESP32 Node) --[ESP-NOW]--> (ESP32 Gateway)
                                                              |
                                                       (Local Wi-Fi)
                                                              |
                                                      [Dashboard Web Local]
                                                              |
                                                       (Internet / Sync)
                                                              v
                                                      [API Django / MySQL]
```

## 🚀 Como Rodar o Projeto (Setup Local)

### Pré-requisitos
- Python 3.10+
- MySQL 8 (ou Docker)
- Node.js (opcional, para frontend)

### Com Docker (recomendado)
```bash
git clone https://github.com/Desmantelar-bit/fieldnode.git
cd fieldnode

# Windows
.\startup.cmd

# Linux/macOS
bash startup.sh
```

### Desenvolvimento Local (sem Docker)
```bash
# 1. Clone o repositório
git clone https://github.com/Desmantelar-bit/fieldnode.git
cd fieldnode

# 2. Crie seu ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate      # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o ambiente
cp .env.example .env
# Edite .env com suas credenciais de banco

# 5. Rode as migrações
python manage.py migrate

# 6. Inicie o servidor
python manage.py runserver
```

### Com Makefile (mais rápido)
```bash
make setup   # Configura ambiente virtual e instala dependências
make run     # Inicia o servidor Django
```

## 🔐 Principais Endpoints (API)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/telemetria/` | POST | Recebe batch de leitura offline (requer `X-API-Key`) |
| `/api/v1/telemetria/` | GET | Lista últimas 50 leituras (dev/debug) |
| `/api/v1/telemetria/ultimas/` | GET | Última leitura de cada máquina ativa |
| `/api/v1/anomalias/` | GET | Detecta leituras fora do padrão (Isolation Forest) |
| `/api/v1/manutencao/` | GET | Prevê probabilidade de manutenção |
| `/api/v1/metricas/` | GET | Métricas operacionais do sistema |

### Exemplo de Ingestão
```bash
curl -X POST http://localhost:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: fieldnode-demo-2024" \
  -d '{
    "id": "uuid-v4",
    "maquina_id": "CASE-TC5000-01",
    "temperatura": 78.5,
    "vibracao": 0.42,
    "rpm": 1850,
    "timestamp": "2024-04-23T14:32:01Z"
  }'
```

## 📊 Stack Técnica

| Camada | Tecnologia |
|--------|------------|
| Hardware | ESP32 + Arduino/C++ |
| Wireless | ESP-NOW + MQTT |
| Backend | Django 5.2 + DRF 3.15 |
| Banco | MySQL 8 (SQLite em dev) |
| Docs | Swagger (drf-yasg) |
| Frontend | HTML/CSS/JS + Chart.js |
| Deploy | Docker + Docker Compose |

## 🧠 Equipe e Contexto

Projeto de Conclusão de Curso (TCC) desenvolvido por estudantes técnicos em Desenvolvimento de Sistemas do SENAI-SP (2026). Tratado com engenharia e rigor de mercado.

| | | | |
|:-:|:-:|:-:|:-:|
| [Vinícius Morales](https://github.com/ViniciusMorales) | [Paola Machado](https://github.com/Paola5858) | [Ana Caroline Furlaneto](https://github.com/acfurlaneto) | Giovana D'Angelo |

## 📝 Licença

MIT