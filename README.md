# FieldNode 🌾

> Kit de telemetria offline-first para colheitadeiras agrícolas.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.2-green?logo=django)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

---

## O problema

Colheitadeiras operam em áreas sem sinal. Dados de temperatura, vibração e RPM ficam presos no campo — chegam atrasados ou não chegam. Quebras inesperadas custam caro.

**FieldNode** resolve isso com telemetria local via Wi-Fi embarcado e sincronização automática quando a conectividade retorna.

---

## Arquitetura

```
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

```
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

## Notas de segurança

- O endpoint `/api/telemetria/` não tem autenticação. Em produção, adicione uma API key simples.
- `ALLOWED_HOSTS` em `settings.py` precisa ser preenchido antes do deploy.
- Em produção, defina `DEBUG=False` no `.env` — o CORS será restrito automaticamente.

---

## Roadmap

- [x] API REST com Django + DRF
- [x] Deduplicação de leituras por UUID
- [x] Dashboard web com Chart.js
- [x] Documentação Swagger
- [ ] Autenticação nos endpoints
- [ ] Alertas via WhatsApp (Twilio / Z-API)
- [ ] Modelo de ML para detecção de anomalias (scikit-learn)
- [ ] Integração ESP32 → Gateway → API (sync completo)
- [ ] Testes automatizados com pytest

---

## Créditos

Desenvolvido com carinho por estudantes do curso técnico de Informática do **SENAI** como Trabalho de Conclusão de Curso.

| Nome | GitHub | LinkedIn | E-mail |
|------|--------|----------|--------|
| Vinícius Morales | [![GitHub](https://img.shields.io/badge/GitHub-ViniciusMorales-181717?logo=github)](https://github.com/ViniciusMorales) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Vinícius-0A66C2?logo=linkedin)](https://www.linkedin.com/in/vin%C3%ADcius-morales-609744368/) | viniciusmorales09@gmail.com |
| Paola Machado | [![GitHub](https://img.shields.io/badge/GitHub-Paola5858-181717?logo=github)](https://github.com/Paola5858) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Paola-0A66C2?logo=linkedin)](https://www.linkedin.com/in/paolasoaresmachado/) | paolasesi351@gmail.com |
| Ana Caroline Furlaneto | [![GitHub](https://img.shields.io/badge/GitHub-acfurlaneto-181717?logo=github)](https://github.com/acfurlaneto) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Ana%20Caroline-0A66C2?logo=linkedin)](https://www.linkedin.com/in/ana-furlaneto-a47746368/) | ana.furlaneto19@icloud.com |
| Giovana Dangelo | — | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Giovana-0A66C2?logo=linkedin)](https://www.linkedin.com/in/giovanamdangelo/) | giovanamachadodangelo@gmail.com |

---

## Licença

MIT
