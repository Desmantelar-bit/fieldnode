# S7-T7 - Relatório de evidência

## Resultado

DOCUMENTAÇÃO CORRIGIDA. A demo atual está descrita com o notebook como
hospedeiro. O protótipo de bancada separa ESP32 sensor, ESP32 retransmissor e
notebook. A arquitetura com mini-PC/Raspberry está marcada como proposta.

## Auditoria realizada

| Componente | Evidência | Classificação |
| --- | --- | --- |
| Broker | `docker-compose.yml`, `mosquitto/mosquitto.conf`, `mosquitto/acl.conf` | Mosquitto em container no notebook |
| Backend | `docker-compose.yml`, serviço `web` | Django/Gunicorn em container |
| Worker | `docker-compose.yml`, serviço `worker` | `mqtt_listen` em container |
| Banco | `docker-compose.yml` | MySQL 8 em container; SQLite em desenvolvimento |
| Frontend | `docker-compose.yml`, `README.md` | Next.js em container ou processo local |
| Outbox de bancada | `simulators/edge_client.py`, `README.md` | Software Python, não firmware |
| Firmware/gateway físico | Auditoria S7-T7 encontrou o gateway ausente; S8-T1 adicionou firmware do nó sensor, sem ESP-NOW | Gateway não implementado; nó sensor existe em software |
| Proposta TCC v4 editável | `rg --files` no repositório | Não encontrada |

## Arquivos alterados

- `docs/CONECTIVIDADE.md`: auditoria de topologia, três diagramas Mermaid,
  tabela de funcionamento sem internet e limites do ESP32.
- `docs/CLAIMS_VS_CODE.md`: classificações verificáveis para notebook, gateway
  ESP32, broker local, dashboard embarcado, offline e Raspberry/mini-PC.
- `README.md`: topologia real da demo e link para a documentação detalhada.
- `docs/evidence/s7/S7-T7_REPORT.md`: este relatório.

## Correções relevantes

| Afirmação a evitar | Correção aplicada | Evidência |
| --- | --- | --- |
| ESP32 #2 é servidor/dashboard | ESP32 #2 é somente retransmissor proposto; Next.js continua no notebook ou gateway dedicado | Ausência de firmware do gateway; Compose hospeda frontend |
| Hotspot é servidor | Hotspot é rede local | Compose e portas publicadas no host |
| Offline-first prova gateway físico | Offline local depende do notebook hoje; outbox Python é simulada/bancada | `README.md`, `edge_client.py` |
| Raspberry/mini-PC existe | Arquitetura proposta, sujeita a validação | Nenhum serviço ou hardware correspondente no repositório |

## Verificações executadas

- Listagem de arquivos do repositório para localizar Compose, docs, firmware,
  proposta e evidências.
- Busca cruzada por `ESP32`, `gateway`, `servidor HTTP`, `dashboard embarcado`,
  `Raspberry`, `broker local`, `offline`, `sem internet`, `hotspot` e `Next.js`.
- Inspeção de `docker-compose.yml`, `mosquitto/mosquitto.conf`,
  `mosquitto/acl.conf`, `README.md`, `docs/CLAIMS_VS_CODE.md` e
  `simulators/edge_client.py`.
- Revisão de links e caminhos citados nos documentos alterados.
- Nenhum teste de software foi criado: a mudança é documental.

## Pendências e limites

- A Proposta TCC v4 não está disponível como arquivo editável no repositório;
  portanto a frase sobre “servidor HTTP embarcado no ESP32 #2” não foi
  alterada diretamente. A pendência está registrada, e a formulação corrigida
  está documentada em `docs/CONECTIVIDADE.md` e `docs/CLAIMS_VS_CODE.md`.
- Não há evidência de placa, sensor físico, ESP-NOW, alcance de rádio,
  persistência em flash, energia ou ensaio físico.
- Não foi feito commit automaticamente.
