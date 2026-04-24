# FieldNode 🌾

> Kit de telemetria offline-first para colheitadeiras agrícolas.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.2-green?logo=django)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

---

## O problema

Colheitadeiras operam em áreas sem sinal. Dados de temperatura, vibração e
RPM ficam presos no campo — chegam atrasados ou não chegam.
Quebras inesperadas custam caro.

**FieldNode** resolve isso com telemetria local via Wi-Fi embarcado e
sincronização automática quando a conectividade retorna.

---

## Arquitetura

```text
[Sensores] → [ESP32 #1 — Sensor Node]
                    │  ESP-NOW
                    ↓
            [ESP32 #2 — Gateway]
                    │
           ┌────────┴────────┐
           │                 │
    [Dashboard local]   [POST → API Django]
    (Wi-Fi sem internet)  (quando online)
                              │
                         [MySQL + DRF]
                              │
                    [Dashboard Web (index.html)]
```

---

## Stack

| Camada | Tecnologia |
|--------|------------|
| Hardware | ESP32 + C++ (Arduino IDE) |
| Protocolo wireless | ESP-NOW |
| Backend | Django 5.2 + DRF |
| Banco | MySQL 8 |
| Docs | drf-yasg (Swagger) |
| Frontend | HTML/CSS/JS + Chart.js |

---

## Como rodar localmente

### Requisitos

- Python 3.12+
- MySQL 8 rodando localmente
- Git

### Passos

```bash
# 1. clone o projeto
git clone https://github.com/Desmantelar-bit/Api-TCC.git
cd Api-TCC

# 2. crie e ative o virtualenv
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# 3. instale as dependências
pip install -r requirements.txt

# 4. configure o .env
copy .env.example .env
# edite o .env com suas credenciais do MySQL

# 5. crie o banco
mysql -u root -p -e "CREATE DATABASE fieldnode CHARACTER SET utf8mb4;"

# 6. aplique as migrations
python manage.py migrate

# 7. suba o servidor
python manage.py runserver

# 8. abra o frontend
# abra frontend/index.html no navegador, ou sirva com:
python -m http.server 5500 --directory frontend
```

### Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
DB_NAME=fieldnode
DB_USER=root
DB_PASSWORD=sua-senha
DB_HOST=localhost
DB_PORT=3306
```

---

## Estrutura de pastas

```text
Api-TCC/
├── api_tcc/
│   ├── api/
│   │   ├── serializers.py      # serialização dos modelos
│   │   ├── viewsets.py         # CRUD via ModelViewSet
│   │   └── views_ingestao.py   # endpoint de ingestão do ESP32
│   ├── migrations/
│   └── models.py
├── frontend/
│   ├── config.js               # URL da API (edite aqui para produção)
│   ├── index.html              # dashboard principal
│   └── maquina.html            # detalhes por máquina
├── setup/
│   ├── settings.py
│   └── urls.py
├── manage.py
├── requirements.txt
└── .env.example
```

---

## Endpoints principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET/POST | `/Colheitadeira/` | CRUD de colheitadeiras |
| GET/POST | `/Operario/` | CRUD de operários |
| GET/POST | `/Temperaturamaquina/` | Leituras de temperatura |
| POST | `/api/telemetria/` | Ingestão do ESP32 (com deduplicação UUID) |
| GET | `/swagger/` | Documentação interativa |

Documentação completa: `http://localhost:8000/swagger/`

---

## Integração com Sistemas Existentes

### Estado atual do protótipo

O FieldNode valida o pipeline completo de telemetria offline-first:
- ✅ Dados saem do ESP32 via ESP-NOW
- ✅ Gateway recebe e envia para API Django
- ✅ Deduplicação por UUID no backend
- ✅ Análise de IA em tempo real
- ✅ Dashboard web com polling a cada 3s

### Como implantar em produção hoje

Para integrar com frotas existentes (Solinftec, John Deere, Case IH):

1. **Cadastre as máquinas** no admin Django (`/admin/`) com seus IDs reais
2. **Configure os ESP32** com os `maquina_id` correspondentes
3. **Implemente o POST** periódico para `/api/telemetria/` (veja `docs/integracao.md`)

### Contrato da API

O endpoint aceita dados de telemetria com deduplicação automática:

```bash
curl -X POST http://localhost:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "uuid-v4-unico",
    "maquina_id": "CASE-TC5000-01",
    "temperatura": 78.5,
    "vibracao": 0.42,
    "rpm": 1850,
    "timestamp": "2024-04-23T14:32:01Z"
  }'
```

**Resposta de sucesso (201)**:
```json
{"status": "ok", "id": "uuid-confirmado"}
```

**Resposta de duplicata (200, idempotente)**:
```json
{"status": "duplicata ignorada", "id": "uuid"}
```

### O que precisa de desenvolvimento adicional

- **Autenticação robusta**: JWT tokens por dispositivo (atualmente sem auth)
- **Validação de `maquina_id`**: Garantir que apenas máquinas cadastradas enviem dados
- **CAN bus integration**: Leitura direta do barramento J1939 para dados nativos da máquina
- **Sensor de combustível**: Hardware adicional ou integração com ECU da máquina
- **Retreino de IA**: Com histórico real de falhas para labels supervisionados

**Para detalhes completos de implantação em produção, custos e cronograma, veja [`docs/RESPOSTA-INTEGRACAO-PRODUCAO.md`](docs/RESPOSTA-INTEGRACAO-PRODUCAO.md)**

Documentação técnica da API em [`docs/integracao.md`](docs/integracao.md)

---

## Notas de segurança

- O endpoint `/api/telemetria/` não tem autenticação. Em produção, adicione uma API key simples.
- `ALLOWED_HOSTS` em `settings.py` precisa ser preenchido antes do deploy.
- Em produção, defina `DEBUG=False` no `.env` — o CORS será restrito automaticamente.

---

## Limitações conhecidas do protótipo

- **Validação de `maquina_id`**: O endpoint `/api/telemetria/` aceita qualquer string como `maquina_id` sem validar se a máquina está cadastrada na tabela `Colheitadeira`. Em produção, adicione validação no serializer para garantir que apenas máquinas cadastradas podem enviar dados.
- **Pipeline MQTT**: O `mqtt_listen.py` também aceita qualquer `maquina_id` via MQTT sem validação.
- **Combustível**: O protótipo atual não possui sensor de nível de combustível no hardware físico. O dashboard exibe "N/D" para este campo. Implementação futura requer sensor adicional ou leitura via barramento CAN/J1939.
- **Labels de IA**: O modelo de manutenção preditiva usa labels baseados em padrões operacionais documentados (limites térmicos de motores diesel, análise de vibração mecânica). Em produção com histórico real de falhas, retreinar com dados supervisionados.

---

## Roadmap

- [x] API REST com Django + DRF
- [x] Deduplicação de leituras por UUID
- [x] Dashboard web com Chart.js
- [x] Documentação Swagger
- [x] Pipeline MQTT: ESP32 → broker → Django → MySQL
- [x] Detecção de anomalias com Isolation Forest
- [x] Manutenção preditiva com Random Forest
- [x] Dashboard com polling em tempo real (3s)
- [x] Script de demo de pane para apresentação
- [ ] Autenticação nos endpoints
- [ ] Alertas via WhatsApp (Twilio / Z-API)
- [ ] Integração ESP32 → Gateway → API (sync completo)
- [ ] Testes automatizados com pytest

---

## Créditos

Desenvolvido por estudantes do curso técnico de Informática do **SENAI**
como Trabalho de Conclusão de Curso.

<table>
  <tr>
    <td align="center" width="200">
      <a href="https://github.com/ViniciusMorales">
        <img src="https://github.com/ViniciusMorales.png" width="72"
             style="border-radius:50%" alt="Vinícius Morales"/>
      </a>
      <br/>
      <strong>Vinícius Morales</strong>
      <br/>
      <a href="https://github.com/ViniciusMorales">
        <img src="https://img.shields.io/badge/GitHub-181717?logo=github"
             alt="GitHub"/>
      </a>
      <a href="https://www.linkedin.com/in/vin%C3%ADcius-morales-609744368/">
        <img src="https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin"
             alt="LinkedIn"/>
      </a>
      <br/>
      <sub>viniciusmorales09@gmail.com</sub>
    </td>
    <td align="center" width="200">
      <a href="https://github.com/Paola5858">
        <img src="https://github.com/Paola5858.png" width="72"
             style="border-radius:50%" alt="Paola Machado"/>
      </a>
      <br/>
      <strong>Paola Machado</strong>
      <br/>
      <a href="https://github.com/Paola5858">
        <img src="https://img.shields.io/badge/GitHub-181717?logo=github"
             alt="GitHub"/>
      </a>
      <a href="https://www.linkedin.com/in/paolasoaresmachado/">
        <img src="https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin"
             alt="LinkedIn"/>
      </a>
      <br/>
      <sub>paolasesi351@gmail.com</sub>
    </td>
    <td align="center" width="200">
      <a href="https://github.com/acfurlaneto">
        <img src="https://github.com/acfurlaneto.png" width="72"
             style="border-radius:50%" alt="Ana Caroline Furlaneto"/>
      </a>
      <br/>
      <strong>Ana Caroline Furlaneto</strong>
      <br/>
      <a href="https://github.com/acfurlaneto">
        <img src="https://img.shields.io/badge/GitHub-181717?logo=github"
             alt="GitHub"/>
      </a>
      <a href="https://www.linkedin.com/in/ana-furlaneto-a47746368/">
        <img src="https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin"
             alt="LinkedIn"/>
      </a>
      <br/>
      <sub>ana.furlaneto19@icloud.com</sub>
    </td>
    <td align="center" width="200">
      <img src="https://ui-avatars.com/api/?name=Giovana+Machado&size=72&background=0D1117&color=fff&rounded=true"
           width="72" alt="Giovana Machado D'Angelo"/>
      <br/>
      <strong>Giovana Dangelo</strong>
      <br/>
      <a href="https://www.linkedin.com/in/giovanamdangelo/">
        <img src="https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin"
             alt="LinkedIn"/>
      </a>
      <br/>
      <sub>giovanamachadodangelo@gmail.com</sub>
    </td>
  </tr>
</table>

---

## Licença

MIT
