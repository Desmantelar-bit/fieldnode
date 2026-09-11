# Contrato de Telemetria — Schema v1.1

> **Versão:** 1.1 (S1-T5: Contrato de Identidade)
> **Status:** Vigente
> **Data de atualização:** 2026-09-11
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

## Histórico de Versões

| Versão | Data       | Alteração                                                             |
|--------|------------|-----------------------------------------------------------------------|
| 1.1    | 2026-09-11 | **S1-T5**: Idempotência composta (`device_id`, `message_id`) e SyncCursor (`sequence_number`). |
| 1.0    | 2026-09-10 | Versão inicial. Idempotência por UUID (`id`). Ranges de validação física. |
