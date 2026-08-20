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

## 🏗 Arquitetura Final

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

### Componentes Principais

- **ESP32 Nodes**: Coleta de dados de sensores (temperatura, vibração, RPM) e transmissão via ESP-NOW.
- **ESP32 Gateway**: Recebe dados via ESP-NOW, expõe API local para dashboard e gerencia sincronização com backend.
- **Backend Django**: API REST para ingestão, processamento de IA (detecção de anomalias, prescrições) e relatórios.
- **Banco de Dados**: MySQL 8 (produção) / SQLite (desenvolvimento) para armazenamento de telemetria e modelos de IA.
- **Frontend Local**: Dashboard web estático (HTML/CSS/JS) servido pelo Django para visualização em tempo real no campo.
- **Sincronização Offline-First**: UUID v4 garante idempotência; tentativas de reenvio até confirmação de sucesso.

## 🚀 Como Rodar o Projeto (Setup Local)

### Pré-requisitos
- Python 3.10+
- MySQL 8 (ou use SQLite em desenvolvimento)
- Node.js (opcional, para frontend)

### Início Rápido (2 minutos)

```bash
# 1. Clone o repositório
git clone https://github.com/Desmantelar-bit/fieldnode.git
cd fieldnode

# 2. Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o ambiente
cp .env.example .env
# Edite .env se necessário (valores padrão funcionam para dev)

# 5. Rode as migrações
python manage.py migrate

# 6. Inicie o servidor
python manage.py runserver
```

### Acessar o Sistema

**Dashboard Operacional (recomendado):**
```
http://127.0.0.1:8000/frontend/dashboard.html
```

**Landing Page:**
```
http://127.0.0.1:8000/frontend/
```

**Documentação da API (Swagger):**
```
http://127.0.0.1:8000/swagger/
```

### Popular com Dados de Demonstração

```bash
# Em outro terminal (com o servidor rodando):
python scripts/demo_pane.py
```

Isso iniciará um simulador MQTT que envia telemetria de 3 máquinas em tempo real.
O dashboard atualizará automaticamente a cada 3 segundos.

## 🔐 Principais Endpoints (API)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/telemetria/` | POST | Recebe batch de leitura offline (requer `X-API-Key`) |
| `/api/telemetria/` | GET | Lista últimas 50 leituras (dev/debug) |
| `/api/telemetria/ultimas/` | GET | Última leitura de cada máquina ativa |
| `/api/anomalias/` | GET | Detecta leituras fora do padrão (Isolation Forest) |
| `/api/manutencao/` | GET | Prevê probabilidade de manutenção (Random Forest) |
| `/api/prescricoes/` | GET | Gera prescrições de manutenção com IA (combina IA + regras) |
| `/api/relatorio/` | GET | Relatório operacional (JSON/CSV) |
| `/api/metricas/` | GET | Métricas operacionais do sistema |
| `/api/status-mqtt/` | GET | Status de conectividade MQTT |

### Exemplo de Prescrição
```bash
curl -X GET "http://localhost:8000/api/prescricoes/?maquina_id=CASE-TC5000-01"
```

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
| Wireless | ESP-NOW + MQTT (para simulação) |
| Backend | Django 5.2 + DRF 3.15 |
| Banco | MySQL 8 (SQLite em dev) |
| IA/ML | scikit-learn (Isolation Forest, Random Forest) |
| Docs | Swagger (drf-yasg) |
| Frontend | HTML/CSS/JS + Chart.js |
| Deploy | Docker + Docker Compose (produção) |

## 🧠 Equipe e Contexto

Projeto de Conclusão de Curso (TCC) desenvolvido por estudantes técnicos em Desenvolvimento de Sistemas do SENAI-SP (2026). Tratado com engenharia e rigor de mercado.

| | | | |
|:-:|:-:|:-:|:-:|
| [Vinícius Morales](https://github.com/ViniciusMorales) | [Paola Machado](https://github.com/Paola5858) | [Ana Caroline Furlaneto](https://github.com/acfurlaneto) | Giovana D'Angelo |

## 📝 Licença

MIT

---

## 📚 Documentação Adicional

- **[INSTRUCOES-APRESENTACAO.md](INSTRUCOES-APRESENTACAO.md)** — Guia completo para apresentação na banca (15 min)
- **[CHEAT-SHEET-APRESENTACAO.md](CHEAT-SHEET-APRESENTACAO.md)** — Resumo de uma página para consulta rápida
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — Diagnóstico e solução de problemas comuns
- **[docs/FASE-1-CONCLUIDA.md](docs/FASE-1-CONCLUIDA.md)** — Relatório das correções implementadas

### Documentação Técnica Existente

- **[docs/CORRECOES-FINAIS.md](docs/CORRECOES-FINAIS.md)** — Histórico de correções e decisões técnicas
- **[docs/DEFESA-BANCA.md](docs/DEFESA-BANCA.md)** — Argumentos técnicos para defesa
- **[docs/GUIA-RAPIDO-SIMULACAO.md](docs/GUIA-RAPIDO-SIMULACAO.md)** — Como usar os simuladores
- **[docs/faq_banca.md](docs/faq_banca.md)** — Perguntas frequentes da banca com respostas preparadas
