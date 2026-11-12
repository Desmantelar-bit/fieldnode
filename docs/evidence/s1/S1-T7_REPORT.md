# S1-T7 · Relatório de ingestão e limites

## Baseline

- `views_ingestao.py` tinha **929 linhas** no commit de referência (o roadmap cita 886).
- A view de lote já aceitava no máximo 500 objetos, antes de processar qualquer item, e persistia um a um por `registrar_leitura`.
- `DATA_UPLOAD_MAX_MEMORY_SIZE` já era `1 * 1024 * 1024`; a implementação mantém o valor e agora também limita a leitura de JSON nas duas views de ingestão.
- A taxa já era `120/minute`, mas a chave era derivada de `maquina_id` enviado pelo cliente.
- Baseline executado em uma cópia limpa do commit de referência, com `.env` e ambiente virtual local: `python -m pytest` → **331 passed, 7 failed**. As sete falhas foram `test_20_leituras_chegam_no_endpoint_com_identidade_da_colhedora`, `test_leitura_com_temperatura_critica_gera_event_temp_alta`, `test_duplicata_retorna_200_sem_duplicar_banco`, `test_ingestao_valida_retorna_201` e três testes de `test_transbordo_mule_client.py` que falham por hash. Os mesmos testes são comparados novamente após as mudanças.

## Mapa de responsabilidades

| Antes | Depois |
| --- | --- |
| Ingestão individual e consulta GET de telemetria | `api_tcc/api/views_ingestao.py` |
| Ingestão em lote | `api_tcc/api/views_lote.py` |
| Últimas leituras e Machine Data Health | `api_tcc/api/views_leituras.py` |
| Métricas | `api_tcc/api/views_metricas.py` |
| Anomalias, manutenção e atualidade MQTT | `api_tcc/api/views_status.py` |
| Helpers e autenticação compartilhados | `api_tcc/api/views_common.py` |
| Relatório geral, prescrições legadas e ação de decisão | `views_relatorio_operacional.py`, `views_prescricoes_legadas.py`, `views_decision_action.py` |

As classes foram movidas sem reescrever seus métodos. `api_tcc/urls.py` mantém caminhos, métodos, nomes de rotas e views correspondentes. `api_tcc/views.py` também foi atualizado para continuar exportando `PrescricaoListView` pelo caminho legado.

Rotas afetadas, sem mudança de URL ou nome:

| Caminho | Método(s) | Nome |
| --- | --- | --- |
| `telemetria/` | GET, POST | `ingestao-telemetria` |
| `telemetria/lote/` | POST | `ingestao-telemetria-lote` |
| `anomalias/` | GET | `anomalias` |
| `leituras/ultimas/` | GET | `ultimas-leituras` |
| `manutencao/` | GET | `manutencao` |
| `metricas/` | GET | `metricas` |
| `machines/<str:machine_id>/health/` | GET | `machine-data-health` |
| `status-mqtt/` | GET | `status-mqtt` |
| `decisions/<uuid:decision_id>/` | GET, PATCH | `decision-action` |
| `prescricoes/`, `prescricoes/teste/`, `prescricoes/lista/`, `relatorio/` | GET/POST conforme a view original | nomes originais preservados |

## Linhas (`wc -l`)

Referência limpa → estado final:

```text
api_tcc/api/views.py                         92 → 92
api_tcc/api/views_auth.py                   145 → 145
api_tcc/api/views_can_motor.py               84 → 84
api_tcc/api/views_decisions.py              104 → 104
api_tcc/api/views_dlq.py                     16 → 16
api_tcc/api/views_events.py                 140 → 140
api_tcc/api/views_health.py                  47 → 47
api_tcc/api/views_ingestao.py               929 → 119
api_tcc/api/views_prescricao.py             156 → 156
api_tcc/api/views_relatorio.py              229 → 229
api_tcc/api/views_common.py                   — → 151
api_tcc/api/views_lote.py                     — → 113
api_tcc/api/views_leituras.py                 — → 238
api_tcc/api/views_metricas.py                 — → 45
api_tcc/api/views_status.py                   — → 111
api_tcc/api/views_relatorio_operacional.py    — → 77
api_tcc/api/views_prescricoes_legadas.py      — → 108
api_tcc/api/views_decision_action.py          — → 83
```

Nenhum arquivo de view ultrapassa 300 linhas.

## Limites, body e throttling

- O lote com 501 itens retorna 400 antes de chamar persistência. O lote de 500 é aceito pelo limite de quantidade e segue validação item a item.
- Um lote real de 500 payloads gerados por `simulators.edge_client.generate_payload`, serializado como JSON compacto, mediu **223.843 bytes**. O limite de 1 MiB comporta mais de quatro vezes esse tamanho e permite cerca de 2 KiB por leitura em média.
- `BoundedTelemetryJSONParser` lê no máximo limite + 1 byte antes de rejeitar o JSON; o teste cobre rejeição com 400 e ausência de persistência. Form e multipart continuam disponíveis e sob os limites Django.
- A configuração `ingestao` permanece `120/minute`.
- A chave do throttle não usa `device_id` nem `maquina_id` arbitrários do corpo. Usa a identidade `device_id` autenticada por uma chave única em `FIELDNODE_DEVICE_API_KEYS`, o usuário autenticado, ou o hash da chave global legada. Uma chave global compartilhada tem uma cota comum; payload com ID falsificado não ganha outra cota.
- Chaves provisionadas por dispositivo são comparadas em tempo constante e o `device_id` do payload deve corresponder ao vínculo configurado. `FIELDNODE_DEVICE_API_KEYS` é um mapa JSON opcional descrito em `.env.example`; chaves reais devem ser provisionadas fora do repositório.
- O ambiente legado só dispõe da chave global compartilhada; não há chave individual real que possa ser atribuída com segurança no código. Até provisionar uma credencial única por dispositivo nos respectivos gateways e configurar o mapa no deployment, esses dispositivos compartilham uma única cota. A rota de migração está implementada e coberta, mas a ativação operacional individual depende dessas credenciais.
- Produção (`USE_SQLITE=False`) usa `DatabaseCache` sobre o banco principal, compartilhado entre workers; a migration `0035_create_throttle_cache` cria a tabela. SQLite de desenvolvimento usa LocMem, sem alegar cota global entre processos. Falha do backend de cache propaga erro e não libera a requisição.
- Testes confirmam chaves de dispositivo A e B independentes, mismatch de identidade rejeitado, chave global sem bypass via payload, 429 com `Retry-After`, ausência de processamento no lote limitado e recuperação após a janela.

## Contratos e validação

Os campos de lote anteriores (`salvas`, `invalidas`, `duplicadas`, `erros` e `items`) permanecem. `accepted`, `rejected` e `duplicates` são aditivos; conflito de hash incrementa `rejected`, nunca `duplicates`. O erro global de persistência retorna os contadores dos itens já confirmados e mantém os IDs pendentes.

## Resultado

- Baseline: **331 passed, 7 failed**.
- Estado final: **342 passed, 7 failed**. Os sete IDs de teste que falham são exatamente os mesmos do baseline limpo: quatro expectativas/cálculos em Data Mule, uma expectativa antiga de `evidence_quality` e duas expectativas antigas de status HTTP body (`ok`/`duplicata ignorada`). Não houve falha nova na suíte completa.
- Suíte direcionada de telemetria, contrato, gerador, severidade e borda: **48 passed**.
- `python manage.py check`: sem problemas.
- `git diff --check`: sem problemas.

As falhas do baseline foram mantidas e identificadas, sem alteração de seus módulos ou enfraquecimento dos testes. A execução hospedada do workflow ocorre quando a alteração for enviada ao CI.

**Classificação técnica:** extração, limite de volume, parser, armazenamento compartilhado e backpressure seguro estão implementados. A individualização da cota para a frota que ainda usa a chave global depende de provisionamento externo de segredos por dispositivo.

**Classificação do aceite:** PARCIAL até provisionar chaves únicas por dispositivo. `FIELDNODE_DEVICE_API_KEYS` está ausente no `.env` atual; por segurança, esse ambiente mantém uma cota compartilhada para a chave legada. Não preencher o mapa com `device_id` do payload sem associar cada ID a uma credencial individual.

**Classificação técnica:** extração, limite de volume, parser, armazenamento compartilhado e backpressure seguro estão implementados. A individualização da cota para a frota que ainda usa a chave global permanece dependente de provisionamento externo de segredos por dispositivo.
