# Contrato de Telemetria — Schema v1.0

> **Versão:** 1.0
> **Status:** Vigente
> **Data de criação:** 2026-09-10
> **Responsável:** Equipe FieldNode

## Objetivo

Este documento formaliza o contrato de dados da telemetria ingerida pelo
sistema FieldNode. Todo payload enviado via API REST (`POST /api/telemetria/`)
ou via MQTT deve obedecer a este schema.

A partir desta versão, payloads **devem** incluir o campo `schema_version`.
Payloads sem o campo ainda serão aceitos por retrocompatibilidade, mas gerarão
um **DeprecationWarning** no log do servidor. Em versões futuras, o campo se
tornará obrigatório.

**Versões suportadas:** `1.0`. O código atual ainda não rejeita valores de
`schema_version` desconhecidos; portanto, um valor como `999.0` é aceito sem
alteração. Essa é uma ressalva arquitetural que deve ser resolvida antes da
publicação de uma nova versão do contrato.

---

## Campos Obrigatórios

| Campo             | Tipo              | Unidade / Formato           | Range Válido       | Descrição                                                                 |
|-------------------|-------------------|-----------------------------|---------------------|---------------------------------------------------------------------------|
| `id`              | UUID (string)     | UUID v4                     | —                   | Opcional. Identificador único da leitura, usado para deduplicação (idempotência). |
| `maquina_id`      | String            | —                           | Não vazio           | Código externo da máquina (ex: `CASE-TC5000-01`). Normalizado para UPPER. |
| `timestamp`       | Datetime (string) | ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`) | —            | Momento da leitura no sensor. Convertido para timezone-aware se naive.    |
| `temperatura`     | Float             | °C (graus Celsius)          | `[0.0, 150.0]`     | Temperatura do motor. Fora do range = provável falha de sensor.           |
| `vibracao`        | Float             | Unidade não definida / unidade do sensor | `[0.0, 10.0]` | Nível de vibração. Valores negativos impossíveis; >10 = ruído de sensor.  |
| `rpm`             | Int               | RPM (rotações por minuto)   | `[0, 5000]`        | Rotação do motor diesel agrícola. Limite prático ~4500 em carga.          |
| `schema_version`  | String            | SemVer simplificado         | `"1.0"` (atual)    | Versão do schema do payload. **Novo — obrigatório a partir de v2.0.**     |

## Campos Opcionais

| Campo       | Tipo   | Unidade / Formato | Range Válido       | Descrição                                    |
|-------------|--------|--------------------|--------------------|----------------------------------------------|
| `latitude`  | Float  | Graus decimais     | `[-90.0, 90.0]`    | Latitude GPS da máquina no momento da leitura.|
| `longitude` | Float  | Graus decimais     | `[-180.0, 180.0]`  | Longitude GPS da máquina no momento da leitura.|

---

## Regras de Validação

1. **Campos obrigatórios ausentes ou `null`** → payload rejeitado (`400 Bad Request`).
2. **Valores fora do range físico** → payload rejeitado com mensagem indicando possível falha de sensor.
3. **`schema_version` ausente** → aceito com injeção automática de `"1.0"` + log `DeprecationWarning`.
4. **UUID duplicado** → payload ignorado com `200 OK` (idempotência).
5. **`maquina_id` desconhecido** → máquina criada automaticamente via `Machine.get_or_create`.

## Exemplos de Payload Válido

### Payload completo (recomendado)

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "maquina_id": "CASE-TC5000-01",
  "timestamp": "2026-09-10T14:30:00Z",
  "temperatura": 85.5,
  "vibracao": 2.3,
  "rpm": 2200,
  "schema_version": "1.0",
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

### Payload legado (aceito com aviso de depreciação)

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "maquina_id": "CASE-TC5000-01",
  "timestamp": "2026-09-10T14:30:00Z",
  "temperatura": 85.5,
  "vibracao": 2.3,
  "rpm": 2200
}
```

---

## Histórico de Versões

| Versão | Data       | Alteração                                                             |
|--------|------------|-----------------------------------------------------------------------|
| 1.0    | 2026-09-10 | Versão inicial. Formaliza campos, tipos, ranges e `schema_version`.   |

---

## Plano de Evolução

- **v1.1** (planejada): Adição de campos OEM-specific (ex: `modelo`, `safra`).
- **v2.0** (futura): `schema_version` torna-se estritamente obrigatório; payloads sem o campo serão rejeitados.
