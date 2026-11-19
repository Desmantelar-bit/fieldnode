# Relatório de carga S10-T7

## Estado

Estrutura de execução criada. **Resultados dos seis perfis em três repetições:
PENDENTES.** A execução foi bloqueada antes da carga por não existir uma
`DeviceCredential` ativa nem uma chave de dispositivo disponível no ambiente.
Este arquivo não contém números estimados.

## Metodologia

`scripts/load/load_test.py` mede latência HTTP, status, erros e throughput. Os
perfis A/B/C usam 10/50/200 dispositivos a 0,5 msg/s; D usa 500 mensagens; E
preserva uma janela temporal simulada de seis horas com duração real limitada;
F consulta endpoints existentes enquanto a ingestão estiver ativa.

Cada resultado deve ser preservado em `artifacts/load/`. O ponto de saturação só
será declarado quando houver crescimento observado de latência/erros, fila,
CPU, memória ou contenção no banco. O maior perfil executado não é capacidade
do produto.

## Índices auditados

Não foi criada migration ornamental. O modelo atual já possui:

| Consulta | Evidência atual |
| --- | --- |
| máquina + tempo | `LeituraTelemetria(machine, -timestamp)` e `maquina_id, -timestamp` |
| idempotência | `unique_together(device_id, message_id)` |
| Event máquina/status | `Event(machine, tipo, status, -criado_em)` |
| Decision máquina/status | `Decision(machine, status, -criado_em)` |

Os planos antes/depois devem ser anexados após uma alteração justificada. A
execução atual de `scripts/load/explain_queries.py` registrou cinco `EXPLAIN` em
`artifacts/load/explain.json`, no MySQL do Compose. Com a massa atual de 1.580
leituras, 56 eventos e 52 decisões, a consulta de Decision por máquina/status
usou `filesort`; isso é um sinal para repetir com massa representativa, não
prova isolada de que uma migration de índice seja correta.

## Inventário de scripts

| Script | Responsabilidade atual | Sobreposição | Destino |
| --- | --- | --- | --- |
| `stress_test.py` | publicação MQTT contínua | carga de transporte | preservar como teste MQTT/manual |
| `teste_carga.py` | POST concorrente HTTP | carga A-D | preservar por compatibilidade; novo executor em `scripts/load/` |
| `teste_deduplicacao.py` | replay/identidade | ingestão, não capacidade | preservar como teste funcional |
| `teste_fluxo_completo.py` | smoke do fluxo e frontend | preflight parcial | preservar; referência para gateway |
| `simular_mqtt.py` | demo MQTT autenticada | transporte/demo | preservar |
| `seed_data.py` | massa de desenvolvimento | preparação, não benchmark | preservar, nunca automático em produção |
| `simulators/teste_resiliencia.py` | outage/retry/outbox | confiabilidade, não carga | manter independente |

## Resultados

Preencher somente a partir dos JSON brutos. Até lá: gargalo, degradação,
saturação e p50/p95/p99 **NÃO DETERMINADOS**. O preflight do Compose passou,
mas isso não é benchmark.

## Limitações

Não extrapolar SQLite, máquina local ou carga sintética para capacidade de
produção. O perfil F exige identidade de usuário de teste autorizada; o perfil
E exige limite explícito e ambiente isolado.

## Validação da implementação

- `py_compile` dos executores: VERIFICADO.
- `git diff --check`: VERIFICADO.
- `docker compose config --quiet`: VERIFICADO.
- `manage.py check` no container: VERIFICADO.
- `scripts/preflight.sh`: VERIFICADO, `preflight=OK`.
- suíte pytest: NÃO VERIFICADA; o host não tem `prometheus_client` e o
  container não tem `pytest` instalado.
