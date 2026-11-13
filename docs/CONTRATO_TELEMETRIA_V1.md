# Contrato de Telemetria — Schema v1.1

> **Versão:** 1.2 (S1-T5: Proveniência Temporal)
> **Status:** Vigente
> **Data de atualização:** 2026-11-12
> **Responsável:** Equipe FieldNode

## Objetivo

Este documento formaliza o contrato de dados da telemetria ingerida pelo
sistema FieldNode. Todo payload enviado via API REST (`POST /api/telemetria/`)
ou via MQTT deve obedecer a este schema.

A versão 1.1 introduz o **Contrato de Identidade e Sincronização** (S1-T5),
mudando a lógica de idempotência de UUID simples para uma chave composta por
`(device_id, message_id)` e introduzindo `sequence_number` para sincronização.

A versão 1.0 (legada) continua sendo suportada via fallbacks.

---

## Campos Obrigatórios (Negócio)

| Campo             | Tipo              | Unidade / Formato           | Range Válido       | Descrição                                                                 |
|-------------------|-------------------|-----------------------------|---------------------|---------------------------------------------------------------------------|
| `maquina_id`      | String            | —                           | Não vazio           | Código externo da máquina (ex: `CASE-TC5000-01`). Normalizado para UPPER. |
| `timestamp`       | Datetime (string) | ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`) | —            | Momento da leitura no sensor (`event_time`).                              |
| `temperatura`     | Float             | °C (graus Celsius)          | `[0.0, 150.0]`     | Temperatura do motor. Fora do range = provável falha de sensor.           |
| `vibracao`        | Float             | Unidade do sensor           | `[0.0, 10.0]` | Nível de vibração. Valores negativos impossíveis; >10 = ruído de sensor.  |
| `rpm`             | Int               | RPM (rotações por minuto)   | `[0, 5000]`        | Rotação do motor diesel agrícola. Limite prático ~4500 em carga.          |

## Campos de Identidade (Opcionais com Fallback)

| Campo             | Tipo   | Default / Fallback                                      | Descrição                                                                                     |
|-------------------|--------|---------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| `device_id`       | String | Fallback: `maquina_id.strip().upper()`                  | Identificador do dispositivo de origem. Se ausente, usa `maquina_id` normalizado.            |
| `message_id`      | String | Fallback 1: campo `id` do payload. Fallback 2: UUID gerado por envio (perde idempotência). | Identidade lógica da mensagem. Único por `device_id`. **Sem este campo, reenvios NÃO são idempotentes.** |
| `sequence_number` | Int    | `0` para persistência; ausente não cria/avança cursor      | Sequência para ordenação/cursor de sync offline.                                              |

## Campos Opcionais (Metadados e Localização)

| Campo            | Tipo   | Unidade / Formato | Default / Range     | Descrição                                    |
|------------------|--------|--------------------|---------------------|----------------------------------------------|
| `source`         | String | api, mqtt, sim     | `api`               | Fonte originadora do evento.                 |
| `transport`      | String | http, mqtt, ble    | `http`              | Protocolo de transporte utilizado.           |

## Proveniência temporal (S1-T5)

`timestamp` permanece como alias legado de `event_time`; também é aceito o
campo explícito `event_time`. Ambos representam o instante do evento e podem ser
nulos quando `time_source=unsynced` e não há âncora. `ingested_at` é gerado pelo
servidor e não substitui a hora do evento. Em respostas, os campos temporais
incluem `event_time`, `ingested_at`, `boot_id` (UUID por inicialização),
`uptime_ms` (inteiro monotônico não negativo), `time_source` (`rtc`, `gateway`,
`ntp`, `unsynced`), `clock_skew_ms` (inteiro assinado opcional) e
`event_time_confidence` (0..1, heurística explícita).

Payload legado com timestamp e sem origem preserva o timestamp recebido como
hora não verificada (`unsynced`, confiança 0.5). Payload novo sem hora confiável
pode omitir `timestamp`; a leitura persiste com `event_time=null`, confiança 0 e
`ingested_at` preservado. `boot_id` inválido, uptime negativo/não inteiro,
`time_source` desconhecido e timestamp sincronizado ausente são rejeitados.

Para um boot, a âncora mais antiga recebida com `rtc`, `ntp` ou `gateway` e
timestamp confiável reconstrói eventos relacionados por:

```text
event_time = anchor_time + (uptime_ms - anchor_uptime_ms)
```

A reconstrução é determinística, restrita ao mesmo `boot_id` e pode ser
reaplicada. Leituras sem âncora ficam sem `event_time`; o sistema não infere
evento antigo a partir do horário de chegada. `clock_skew_ms` é aceito somente
como estimativa reportada pelo gateway: diferença entre recepção e evento não é
chamada de skew, pois pode ser atraso de rede ou de sincronização.

Confiança: RTC/NTP 0.95, gateway 0.80, timestamp legado não verificado 0.50,
reconstrução por âncora no máximo 0.65, sem hora resolvida 0. Esses valores são
heurísticas de software, não probabilidades validadas em campo. O Trust Score
subtrai `1 - event_time_confidence` e expõe o fator
`hora_do_dispositivo_nao_confiavel` para `unsynced`; a lista por leitura é
persistida em `trust_factors` e exposta na API. Isso afeta qualidade da
evidência, nunca a fórmula de prioridade. A precisão de DS3231 depende da
variante, temperatura e condições de uso; a validação do componente efetivo e
do valor ±2 ppm fica para S8.

Exemplo sincronizado:

```json
{"maquina_id":"COLH-01","message_id":"m-1","temperatura":72,"vibracao":0.4,"rpm":1700,
 "timestamp":"2026-11-12T10:00:00Z","boot_id":"d42b5dd0-53c7-437a-833f-15c791d91343",
 "uptime_ms":3600000,"time_source":"rtc"}
```

Exemplo sem relógio e sem âncora:

```json
{"maquina_id":"COLH-01","message_id":"m-2","temperatura":72,"vibracao":0.4,"rpm":1700,
 "boot_id":"d42b5dd0-53c7-437a-833f-15c791d91343","uptime_ms":3605000,"time_source":"unsynced"}
```

Migration incremental 0033 adiciona proveniência temporal e permite `timestamp`
nulo; a migration 0027 existente não foi alterada. Payloads legados continuam
aceitos com timestamp não verificado. Leituras não resolvidas não alimentam
eventos temporais nem o agregado `MachineDataHealth` até existir `event_time`.
| `latitude`       | Float  | Graus decimais     | `[-90.0, 90.0]`    | Latitude GPS da máquina.                     |
| `longitude`      | Float  | Graus decimais     | `[-180.0, 180.0]`  | Longitude GPS da máquina.                    |
| `schema_version` | String | SemVer             | `1.0`               | Versão do payload.                           |
| `id`             | String | UUID v4            | (Auto-gerado)       | UUID interno da linha (Não é mais usado para idempotência). |

---

## Regras de Validação e Identidade

1. **Idempotência Composta**: Um evento é considerado **duplicado** se o backend já processou outro evento com a mesma combinação exata de `device_id` e `message_id`. Replays retornam `200 OK` com `status: "duplicata ignorada"`.
2. **Monotonicidade de Cursor**: Quando informado, o `sequence_number` avança o cursor lógico (`SyncCursor`) do `device_id`. O cursor interno usa `MAX(atual, sequence_number)` e **nunca retrocede**. Replays (eventos antigos) são aceitos no banco se não duplicados, mas não movem o cursor para trás. Se o campo estiver ausente em payload legado, o valor persistido será `0`, mas nenhum cursor será criado ou avançado; isso não representa ACK.
3. **Compatibilidade Legada (Sem `message_id`)**: Se o payload omitir `message_id`, o backend gera um UUID aleatório internamente. **Consequência: o reenvio deste evento NÃO será idempotente e gerará registros duplicados.**
4. **Compatibilidade Legada (Sem `device_id`)**: Se ausente, preenchido automaticamente copiando o valor de `maquina_id` (normalizado).
5. **Máquinas on-the-fly**: `maquina_id` desconhecido cria automaticamente uma entidade `Machine`.

## Exemplos de Payload

### Payload Moderno (v1.1 - Idempotente)
```json
{
  "device_id": "esp32-harvester-99",
  "message_id": "msg-8f14c2b9",
  "sequence_number": 1042,
  "maquina_id": "CASE-TC5000-01",
  "timestamp": "2026-09-11T14:30:00Z",
  "temperatura": 85.5,
  "vibracao": 2.3,
  "rpm": 2200,
  "source": "mqtt",
  "transport": "mqtt",
  "schema_version": "1.1"
}
```

### Payload Legado (v1.0 - Fallbacks de Identidade)
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "maquina_id": "CASE-TC5000-01",
  "timestamp": "2026-09-11T14:30:00Z",
  "temperatura": 85.5,
  "vibracao": 2.3,
  "rpm": 2200
}
```
*(Neste payload, `device_id` usa o `maquina_id` normalizado e `message_id` usa o `id` como fallback. Portanto, reenviar o mesmo payload é idempotente. A perda de idempotência ocorre somente quando `message_id` e `id` estão ausentes, pois um UUID novo é gerado a cada envio.)*

---

## Anexo S3-T2: Saude agregada de dados por Machine

O endpoint abaixo retorna o estado persistido da confiabilidade da telemetria
de uma `Machine`. Ele nao recalcula o historico completo durante a consulta.

```http
GET /api/machines/<machine_id>/health/
```

### Resposta com health existente

```json
{
  "machine_id": "2f2d8c8d-24cf-42e4-9cf1-59a31d0c4f58",
  "external_code": "CASE-TC5000-01",
  "status": "ok",
  "trust_score_medio": 0.84,
  "ultima_atualizacao": "2026-09-21T18:30:00Z",
  "leituras_analisadas": 127,
  "sinais_de_alerta": {
    "primeira_leitura": false,
    "gap_temporal": true,
    "timestamp_fora_de_ordem": false,
    "timestamp_indisponivel": false,
    "valores_repetidos": false,
    "limite_fisico": false,
    "salto_abrupto": false,
    "score_baixo": false,
    "contadores": {
      "primeira_leitura": 1,
      "gap_temporal": 4,
      "timestamp_fora_de_ordem": 0,
      "timestamp_indisponivel": 0,
      "valores_repetidos": 2,
      "limite_fisico": 3,
      "salto_abrupto": 0,
      "score_baixo": 5
    },
    "ultimos_motivos": [
      "gap temporal acima da heuristica inicial esperada"
    ]
  }
}
```

### Machine existente sem health

Ausencia de dados nao e interpretada como telemetria excelente.

```json
{
  "machine_id": "2f2d8c8d-24cf-42e4-9cf1-59a31d0c4f58",
  "external_code": "CASE-TC5000-01",
  "status": "sem_dados",
  "trust_score_medio": null,
  "ultima_atualizacao": null,
  "leituras_analisadas": 0,
  "sinais_de_alerta": {}
}
```

### Semantica

`trust_score_medio` e um agregado incremental normalizado em `0..1`.
Ele usa media movel exponencial simples:

```text
novo_score = alpha * trust_score_da_leitura + (1 - alpha) * score_anterior
```

O `alpha` atual e `0.2`. Esse valor e uma heuristica operacional: define o
peso da leitura nova no estado agregado, nao uma probabilidade estatistica.

`leituras_analisadas` contabiliza somente leituras efetivamente incorporadas ao
agregado. Replays idempotentes retornam duplicata e nao incrementam esse valor.

`ultima_atualizacao` representa o timestamp da ultima leitura considerada pelo
agregado. `sinais_de_alerta` deriva dos motivos reais gerados pelo trust score
individual em S3-T1.

### Chamada manual documentada

Exemplo sanitizado para ambiente local:

```bash
curl -X GET \
  http://localhost:8000/api/machines/<MACHINE_UUID>/health/
```

Este endpoint de leitura segue a politica atual dos endpoints publicos do
prototipo. Quando `DEMO_MODE=True` e a requisicao for anonima, uma Machine real
nao marcada como `is_demo=True` retorna `404`.

---

## Histórico de Versões

| Versão | Data       | Alteração                                                             |
|--------|------------|-----------------------------------------------------------------------|
| 1.2    | 2026-09-21 | **S3-T2**: `MachineDataHealth`, EMA incremental por Machine e `GET /api/machines/<id>/health/`. |
| 1.1    | 2026-09-11 | **S1-T5**: Idempotência composta (`device_id`, `message_id`) e SyncCursor (`sequence_number`). |
| 1.0    | 2026-09-10 | Versão inicial. Idempotência por UUID (`id`). Ranges de validação física. |

---

## Anexo S4-T2: Decision operacional

`Decision` e a memoria persistente de uma recomendacao operacional gerada pelo
FieldNode. Ela nao substitui `Event`: `Event` registra uma ocorrencia relevante
observada na telemetria; `Decision` registra a recomendacao produzida a partir
da analise atual, opcionalmente associada a um `Event` aberto da mesma
`Machine`.

Fluxo inicial:

```text
LeituraTelemetria -> Event opcional -> analise de prescricao -> Decision PENDENTE
```

`GET /api/prescricoes/?maquina_id=<codigo>` preserva o JSON de analise e adiciona:

```json
{
  "decision_id": "uuid-da-decision"
}
```

Para o offcanvas operacional, a mesma resposta tambem inclui
`decision_status` com o status persistido da Decision. O frontend usa esses
dois campos estruturados, sem inferir estado pelo texto da recomendacao.

Campos centrais: `machine`, `event`, `texto`, `acao_recomendada`,
`severidade`, `confianca`, `status`, `criado_em`, `decidido_por`,
`decidido_em` e `outcome_texto`.

Para evitar duplicacao por refresh, o backend reutiliza uma `Decision` pendente
equivalente criada nos ultimos 30 minutos. A equivalencia considera `machine`,
`event`, `texto`, `acao_recomendada`, `severidade` e `status=PENDENTE`.
Decisions em outros status nao bloqueiam uma nova recomendacao equivalente.

`confianca` fica null enquanto o pipeline atual nao produzir score proprio de
confianca da recomendacao. Ela nao reutiliza `trust_score`, que mede a qualidade
do dado de entrada.

Limite atual: a consistencia temporal do treinamento da IA segue como divida de
S5. O feedback humano passa a ser registrado em S4-T3, mas ainda nao deve ser
tratado como dataset supervisionado pronto para treino.

---

## Anexo S4-T3: Acao humana sobre Decision

`PATCH /api/decisions/<decision_id>/` registra a acao humana sobre uma
`Decision`. O endpoint exige autenticacao DRF por token e aceita somente:

```json
{
  "status": "APROVADA",
  "outcome_texto": "Operador autorizou a inspecao."
}
```

`status` e obrigatorio. `outcome_texto` e opcional e pode ser `null`.
Campos como `machine`, `event`, `texto`, `acao_recomendada`, `confianca`,
`criado_em`, `decidido_por` e `decidido_em` nao sao editaveis por esse endpoint.

### Maquina de estados

| Origem | Destino | Resultado |
|--------|---------|-----------|
| `PENDENTE` | `APROVADA` | permitido |
| `PENDENTE` | `REJEITADA` | permitido |
| `PENDENTE` | `EXPIRADA` | permitido |
| `PENDENTE` | `EXECUTADA` | bloqueado |
| `APROVADA` | `EXECUTADA` | permitido |
| `APROVADA` | `REJEITADA` | bloqueado |
| `APROVADA` | `APROVADA` | bloqueado |
| `REJEITADA` | qualquer outro estado | bloqueado |
| `EXECUTADA` | qualquer outro estado | bloqueado |
| `EXPIRADA` | qualquer outro estado | bloqueado |

Estados terminais nesta versao: `REJEITADA`, `EXECUTADA` e `EXPIRADA`.

### Auditoria

Em uma transicao valida, o backend registra `decidido_por` a partir de
`request.user` e `decidido_em` com timestamp do servidor quando esses campos
ainda nao existem. Na transicao `APROVADA -> EXECUTADA`, o aprovador original e
preservado quando ja estiver registrado.

### Resposta de sucesso

`200 OK` retorna a `Decision` atualizada, incluindo `id`, `machine`,
`machine_external_code`, `event`, `texto`, `acao_recomendada`, `severidade`,
`confianca`, `status`, `criado_em`, `decidido_por`, `decidido_em` e
`outcome_texto`.

### Erros esperados

| Caso | HTTP |
|------|------|
| Sem token ou token invalido | `401 Unauthorized` |
| Decision inexistente | `404 Not Found` |
| Payload invalido ou campo nao permitido | `400 Bad Request` |
| Transicao invalida | `400 Bad Request` |

### Chamada manual documentada

Exemplo sanitizado para ambiente local:

```bash
curl -X PATCH \
  http://localhost:8000/api/decisions/<DECISION_UUID>/ \
  -H "Authorization: Token <SEU_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "APROVADA",
    "outcome_texto": "Operador autorizou a inspecao."
  }'
```

Fluxo operacional:

```text
Decision PENDENTE
        -> PATCH APROVADA
Decision APROVADA
        -> PATCH EXECUTADA
Decision EXECUTADA
```

No frontend Next.js, a prescricao e exibida no modal operacional existente.
`PENDENTE` permite aprovar ou rejeitar; `APROVADA` permite marcar como
executada; estados terminais apenas exibem o status. Sem sessao, a tentativa
de acao redireciona para `/login` e preserva o caminho de retorno. A resposta
do PATCH e a fonte de verdade para atualizar o modal, sem reload da pagina.
# Contrato de vibração e severidade v1 (S1)

O contrato canônico e versionado está em `contracts/severity.v1.json`. D-01 usa fronteiras inclusivas (`>=`). D-02 define `vibracao` como índice adimensional `indice_0_10`, faixa 0–10. Payload sem `vibracao_unit` é aceito para compatibilidade e interpretado como essa unidade; unidade desconhecida, inclusive `g`, é rejeitada. Não existe conversão automática nem reinterpretar magnitude como aceleração.

`vibracao_rms_g`, `vibracao_pico_g` e `vibracao_curtose` são campos futuros e distintos; não são produzidos pelo sistema atual. Registros históricos não tiveram valores convertidos. O default adicionado pela migration identifica a escala do modelo, mas não comprova a proveniência física dos dados legados.

Os limiares são heurísticos de bancada, não limites operacionais validados. Valores do contrato v1 não migram o firmware: hardware permanece no v0 até migração por versão. Para atualizar artefatos frontend execute `python scripts/gen_contracts.py`; para conferir sem modificar use `python scripts/gen_contracts.py --check`.
