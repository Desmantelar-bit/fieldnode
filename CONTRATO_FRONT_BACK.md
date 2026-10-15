# CONTRATO_FRONT_BACK.md — FieldNode / Leviatã V2

> **FASE 1 — AUDITORIA DE INTEGRAÇÃO**
> Produzido por inspeção direta do código-fonte em `2026-10-15`.
> Toda afirmação deste documento é fundamentada em evidências do repositório.
> Lacunas são marcadas explicitamente como `PENDÊNCIA` ou `NÃO CONFIRMADO`.

---

## A. Identificação e Princípios de Integração

### A.1 Stack Real Encontrada

| Camada | Tecnologia | Versão (requirements.txt) |
|---|---|---|
| Framework web | Django | 5.2 |
| API REST | Django REST Framework | 3.15.2 |
| Documentação | drf-yasg (Swagger/ReDoc) | 1.21.15 |
| CORS | django-cors-headers | 4.3.0 |
| Banco primário | MySQL 8 | mysqlclient 2.2.8 |
| Banco alternativo | SQLite (quando `USE_SQLITE=True`) | – |
| Análise ML | scikit-learn | 1.8.0 |
| Serialização offline | pandas, joblib | 2.2.2 / 1.5.3 |
| Servidor produção | Gunicorn | 23.0.0 |
| LLM Externo | Gemini API (gemini-3.6-flash) | via `requests` |

**Arquivos de referência:** `requirements.txt`, `setup/settings.py`

### A.2 Base URL da API

| Ambiente | URL Base |
|---|---|
| Desenvolvimento local | `http://localhost:8000/api/` |
| CORS permitidos por padrão | `localhost:3000`, `localhost:3005`, `127.0.0.1:3000`, `127.0.0.1:3005` |
| Documentação Swagger | `http://localhost:8000/swagger/` |
| Documentação ReDoc | `http://localhost:8000/redoc/` |

A variável `CORS_ALLOWED_ORIGINS` é configurável via `.env`. O valor padrão cobre `localhost:3000` e `localhost:3005`.

**Arquivo:** `setup/settings.py` L38–L58

### A.3 Serialização e Formato de Resposta

- **Formato:** JSON (`Content-Type: application/json`)
- **Charset:** UTF-8
- **Timestamps:** ISO 8601 com fuso horário (`America/Sao_Paulo`, `USE_TZ=True`)
- **UUIDs:** string no formato padrão UUID v4 (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
- **Floats especiais:** NaN e Infinity são convertidos para `null` antes da serialização (ver `_serializar_analise()`, `_valor_json_seguro()`)
- **Erros:** retornados como `{"status": "erro", "detalhe": "..."}` ou `{"status": "erro", "detalhes": "..."}` — **há inconsistência de nome do campo entre endpoints** (ver seção I)

### A.4 Convenções de Compatibilidade Obrigatórias

1. O campo `maquina_id` é o identificador legado (string, ex: `"COLH-01"`) normalizado como `.strip().upper()`. Qualquer sistema que o envie deve respeitar esta normalização.
2. A identidade canônica de dispositivo é `external_code` no modelo `Machine` (UUID interno: `machine.id`). Os dois identificadores coexistem.
3. Campos `null` são válidos em várias respostas (ex.: `trust_score`, `latitude`, `longitude`). O frontend **não deve tratar `null` como erro**.
4. O sistema possui um modo `DEMO_MODE` que expõe um subconjunto de máquinas marcadas como `is_demo=True` para acesso anônimo. O frontend deve distinguir claramente dados de demonstração de dados de produção.
5. O campo `Deprecation: true` com `Sunset: 2026-12-31` está presente no header de resposta de `/api/prescricoes/lista/`. O frontend não deve depender desse endpoint para novas funcionalidades.

---

## B. Inventário Exato dos Endpoints

### B.1 Autenticação

#### `POST /api/auth/login/`

| Campo | Valor |
|---|---|
| Handler | `rest_framework.authtoken.views.obtain_auth_token` (DRF built-in) |
| Permissão | Pública |
| Throttle | Nenhum implementado |

**Corpo da requisição:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Resposta 200 OK:**
```json
{
  "token": "string (40 chars hex)"
}
```

**Resposta 400 Bad Request** (credenciais inválidas):
```json
{
  "non_field_errors": ["Unable to log in with provided credentials."]
}
```

**Uso:** o token retornado deve ser incluído em todas as requisições autenticadas como:
```
Authorization: Token <token>
```

---

### B.2 Telemetria — Ingestão

#### `POST /api/telemetria/`

| Campo | Valor |
|---|---|
| Handler | `IngestaoTelemetriaView.post()` |
| Autenticação | **X-API-Key** (header `X-API-Key` = `FIELDNODE_API_KEY`) — **NÃO usa Token DRF** |
| Throttle | `IngestaoThrottle` (120/minuto) |
| Permissão | `AllowAny` (proteção via X-API-Key interna) |

**Corpo da requisição — campos obrigatórios:**
```json
{
  "maquina_id": "string (ex: COLH-01)",
  "temperatura": "float (0.0–150.0 °C)",
  "vibracao": "float (0.0–10.0)",
  "rpm": "int (0–5000)",
  "timestamp": "ISO 8601 string"
}
```

**Campos opcionais:**
```json
{
  "id": "UUID string (PK da linha, não garante idempotência sem message_id)",
  "message_id": "string (chave de idempotência com device_id)",
  "device_id": "string (fallback: maquina_id normalizado)",
  "sequence_number": "int (cursor monotônico)",
  "latitude": "float (-90..90) | null",
  "longitude": "float (-180..180) | null",
  "schema_version": "string (padrão: '1.0')",
  "source": "string (padrão: 'api')",
  "transport": "string (padrão: 'http')",
  "manufacturer": "string"
}
```

**Resposta 201 Created** (leitura nova):
```json
{
  "status": "ok",
  "id": "UUID string",
  "message_id": "string",
  "device_id": "string",
  "sequence_number": "int",
  "payload_hash": "string SHA-256 hex | null",
  "sync_cursor": "int",
  "ia": {
    "maquina_id": "string",
    "status": "NORMAL | ATENCAO | CRITICO",
    "motivos": ["string"],
    "metricas": {
      "temp_media": "float | null",
      "temp_max": "float | null",
      "temp_tendencia": "float | null",
      "vib_media": "float | null",
      "rpm_std": "float | null"
    },
    "recomendacao": "string | null",
    "metodologia": "string"
  }
}
```

**Resposta 200 OK** (duplicata ignorada):
```json
{
  "status": "duplicata ignorada",
  "id": "UUID string",
  "message_id": "string",
  "device_id": "string",
  "sequence_number": "int",
  "payload_hash": "string | null",
  "sync_cursor": "int"
}
```

**Resposta 400 Bad Request** (payload inválido):
```json
{
  "status": "erro",
  "detalhes": "string (motivo)"
}
```

**Resposta 401 Unauthorized** (API key ausente ou inválida):
```json
{
  "status": "erro",
  "detalhes": "API key inválida ou ausente"
}
```

> **IMPORTANTE:** Este endpoint é destinado a dispositivos de campo (ESP32/MQTT). O frontend de dashboard **não deve** chamar este endpoint diretamente. A chave `FIELDNODE_API_KEY` é um segredo de servidor e **não deve estar no bundle do frontend**.

**Arquivo:** `api_tcc/api/views_ingestao.py` L148–L229

---

#### `GET /api/telemetria/`

| Campo | Valor |
|---|---|
| Autenticação | Token DRF **ou** Demo público |
| Parâmetro opcional | `?maquina_id=COLH-01` |

**Resposta 200 OK:** array de até 50 leituras com o schema de `LeituraTelemetriaSerializer`:

```json
[
  {
    "id": "UUID",
    "device_id": "string",
    "message_id": "string",
    "sequence_number": "int",
    "maquina_id": "string",
    "machine": "UUID | null",
    "machine_id": "UUID | null",
    "temperatura": "float",
    "vibracao": "float",
    "rpm": "int",
    "latitude": "float | null",
    "longitude": "float | null",
    "timestamp": "ISO 8601",
    "event_time": "ISO 8601 (alias de timestamp)",
    "recebido_em": "ISO 8601",
    "ingested_at": "ISO 8601 (alias de recebido_em)",
    "trust_score": "float 0..1 | null",
    "source": "string",
    "transport": "string",
    "sync_status": "string",
    "status_risco": {
      "nivelCor": "hex string",
      "nivelBg": "hex string",
      "rotuloRisco": "Normal | Alerta | Crítico"
    }
  }
]
```

**Arquivo:** `api_tcc/api/views_ingestao.py` L221–L229, `api_tcc/api/serializers.py` L264–L351

---

#### `POST /api/telemetria/lote/`

| Campo | Valor |
|---|---|
| Handler | `IngestaoLoteView.post()` |
| Autenticação | X-API-Key (mesmo mecanismo da ingestão unitária) |
| Limite | 500 leituras por request |

**Corpo:**
```json
{
  "leituras": [ /* array de payloads no mesmo formato de POST /api/telemetria/ */ ]
}
```

**Resposta 200 OK:**
```json
{
  "salvas": "int",
  "duplicadas": "int",
  "invalidas": "int",
  "erros": [
    { "id": "UUID | null", "detalhe": "string" }
  ]
}
```

**Arquivo:** `api_tcc/api/views_ingestao.py` L278–L343

---

### B.3 Leituras — Dashboard

#### `GET /api/leituras/ultimas/`

| Campo | Valor |
|---|---|
| Handler | `UltimaLeituraView.get()` |
| Autenticação | Token DRF **ou** Demo público |
| Parâmetro opcional | `?maquina_id=COLH-01` |
| Limite | Máximo 10 máquinas distintas (sem paginação implementada) |

**Resposta 200 OK:** array de objetos por máquina:

```json
[
  {
    "maquina_id": "string",
    "temperatura": "float",
    "vibracao": "float",
    "rpm": "int",
    "timestamp": "string ISO 8601",
    "status_risco": {
      "nivelCor": "hex string",
      "nivelBg": "hex string",
      "rotuloRisco": "Normal | Alerta | Crítico"
    },
    "nivel_risco": "NORMAL | ATENCAO | CRITICO",
    "total_leituras": "int",
    "data_health": {
      "machine_id": "UUID string | null",
      "external_code": "string | null",
      "status": "ok | sem_dados",
      "trust_score_medio": "float 0..1 | null",
      "ultima_atualizacao": "string ISO 8601 | null",
      "leituras_analisadas": "int",
      "sinais_de_alerta": "object | {}"
    }
  }
]
```

> **ATENÇÃO:** O filtro de máquinas ativas usa `Colheitadeira.ativo=True`. Apenas máquinas com registro `Colheitadeira` correspondente aparecem neste endpoint.

> **LIMITAÇÃO CONHECIDA:** Máximo de 10 máquinas sem paginação. Frotas maiores exigem implementação de paginação (ver seção I).

**Arquivo:** `api_tcc/api/views_ingestao.py` L346–L485

---

### B.4 Máquinas (Colheitadeiras)

#### `GET /api/colheitadeira/`

| Campo | Valor |
|---|---|
| Handler | `ColheitadeiraViewSet` (ModelViewSet) |
| Autenticação | Token DRF **ou** Demo público |
| Permissão | `IsAuthenticatedOrPublicDemo` |

**Resposta 200 OK:** array de objetos `ColheitadeiraSerializer`:

```json
[
  {
    "id": "int (PK do banco)",
    "ativo": "bool",
    "maquina_id": "string | null (ID textual legado)",
    "modelo": {
      "id": "int",
      "nome": "string",
      "marca": { "id": "int", "nome": "string" }
    },
    "combustivel": { "id": "int", "tipo": "string", "porcentagem": "float" },
    "pressao_pneus": {
      "id": "int",
      "pressao": "float",
      "unidade_de_medida": { "id": "int", "nome": "string" }
    },
    "altura_do_corte": {
      "id": "int",
      "altura": "float",
      "unidade_de_medida": { "id": "int", "nome": "string" }
    },
    "pressao_do_corte": {
      "id": "int",
      "pressao": "float",
      "unidade_de_medida": { "id": "int", "nome": "string" }
    },
    "temp_umi_ambiente": {
      "id": "int",
      "temperatura": "float",
      "umidade": "float"
    },
    "temperatura_maquina": {
      "id": "int",
      "temperatura": "float",
      "maquina": "int (FK Modelo.id)"
    },
    "operario": {
      "id": "int",
      "nome": "string",
      "tempo_de_servico": "int",
      "no_banco": "bool"
    },
    "status_de_operacao": {
      "id": "int",
      "em_operacao": "bool",
      "tempo_de_operacao": "float"
    },
    "estado_de_movimento": {
      "id": "int",
      "em_movimento": "bool",
      "velocidade": "float"
    }
  }
]
```

Suporta também: `POST`, `GET /api/colheitadeira/{id}/`, `PUT /api/colheitadeira/{id}/`, `DELETE /api/colheitadeira/{id}/` (soft delete via `ativo=False`).

**Arquivo:** `api_tcc/api/viewsets.py` L85–L105, `api_tcc/api/serializers.py` L164–L259

---

### B.5 Trust Score / Machine Data Health — S3

#### `GET /api/machines/{machine_id}/health/`

| Campo | Valor |
|---|---|
| Handler | `MachineDataHealthView.get()` |
| Parâmetro de rota | `machine_id` — **UUID da `Machine` canônica** (não o `maquina_id` textual) |
| Autenticação | Token DRF **ou** Demo público (verificado via `request_can_access_machine`) |

**Resposta 200 OK** (com dados):
```json
{
  "machine_id": "UUID string",
  "external_code": "string (ex: COLH-01)",
  "status": "ok",
  "trust_score_medio": "float 0.0..1.0",
  "ultima_atualizacao": "ISO 8601 string",
  "leituras_analisadas": "int",
  "sinais_de_alerta": {
    "primeira_leitura": "bool",
    "gap_temporal": "bool",
    "timestamp_fora_de_ordem": "bool",
    "timestamp_indisponivel": "bool",
    "valores_repetidos": "bool",
    "limite_fisico": "bool",
    "salto_abrupto": "bool",
    "score_baixo": "bool",
    "contadores": {
      "primeira_leitura": "int",
      "gap_temporal": "int",
      "timestamp_fora_de_ordem": "int",
      "timestamp_indisponivel": "int",
      "valores_repetidos": "int",
      "limite_fisico": "int",
      "salto_abrupto": "int",
      "score_baixo": "int"
    },
    "ultimos_motivos": ["string"]
  }
}
```

**Resposta 200 OK** (sem dados ainda):
```json
{
  "machine_id": "UUID string",
  "external_code": "string",
  "status": "sem_dados",
  "trust_score_medio": null,
  "ultima_atualizacao": null,
  "leituras_analisadas": 0,
  "sinais_de_alerta": {}
}
```

**Resposta 404:** `{"status": "erro", "detalhe": "machine nao encontrada"}`

> **NOTA:** O campo `trust_score_medio` é uma EMA (exponential moving average) com `alpha=0.2` calculada incrementalmente a cada ingestão. **Não representa probabilidade calibrada de falha.**

**Arquivo:** `api_tcc/api/views_ingestao.py` L232–L275, `api_tcc/services/data_health.py`

---

### B.6 Anomalias — S6

#### `GET /api/anomalias/`

| Campo | Valor |
|---|---|
| Handler | `AnomaliaView.get()` |
| Autenticação | Token DRF **ou** Demo público |
| Parâmetro obrigatório | `?maquina_id=COLH-01` |

**Resposta 200 OK** — resultado direto do pipeline de análise:
```json
{
  "maquina_id": "string",
  "status": "NORMAL | ATENCAO | CRITICO",
  "motivos": ["string"],
  "metricas": {
    "temp_media": "float | null",
    "temp_max": "float | null",
    "temp_tendencia": "float | null",
    "vib_media": "float | null",
    "rpm_std": "float | null"
  },
  "recomendacao": "string | null",
  "metodologia": "hibrido_regras_thresholds_e_isolation_forest"
}
```

**Resposta 400** (sem `maquina_id`): `{"status": "erro", "detalhe": "maquina_id é obrigatório"}`

> **ATENÇÃO — NATUREZA DOS DADOS:** Este endpoint executa o pipeline de IA síncrono a cada chamada. **Não retorna registros históricos de anomalias**, retorna a classificação atual baseada nas últimas 500 leituras. Não há paginação porque não é uma listagem — é uma análise pontual.

> **ATENÇÃO — ISOLATION FOREST:** O modelo `.pkl` (`api_tcc/ia/modelos/isolation_forest_v1.pkl`) pode não existir. Quando ausente, `FileNotFoundError` é silenciado e o sistema funciona apenas com regras determinísticas. O frontend **não deve assumir** que o campo `metodologia` sempre conterá sinal do Isolation Forest.

**Arquivo:** `api_tcc/api/views_ingestao.py` L120–L145, `api_tcc/ia/pipeline.py`

---

### B.7 Análise / Manutenção

#### `GET /api/manutencao/`

Idêntico ao `/api/anomalias/` em estrutura. Mesmo handler interno (`analisar_maquina()`), mesma resposta. Parâmetro `?maquina_id=` obrigatório.

**Arquivo:** `api_tcc/api/views_ingestao.py` L488–L511

---

### B.8 Prescrições e Decisões — S4

#### `GET /api/prescricoes/{maquina_id}/`

| Campo | Valor |
|---|---|
| Handler | `api_tcc/api/views_prescricao.py` — `PrescricaoView.get()` |
| Autenticação | Token DRF **ou** Demo público |
| Parâmetro de rota | `maquina_id` — string textual (ex: `COLH-01`) |

**Resposta 200 OK:**
```json
{
  "maquina_id": "string",
  "status": "NORMAL | ATENCAO | CRITICO",
  "metodologia": "string (ex: hibrido_regras_thresholds_e_isolation_forest | agentic_llm_poc)",
  "motivos": ["string"],
  "metricas": {
    "temp_media": "float | null",
    "temp_max": "float | null",
    "temp_tendencia": "float | null",
    "vib_media": "float | null",
    "rpm_std": "float | null"
  },
  "recomendacao": "string | null",
  "recomendacao_tecnica": "string",
  "decision_id": "UUID string",
  "decision_status": "PENDENTE | APROVADA | REJEITADA | EXECUTADA | EXPIRADA",
  "explicacao_operador": "string",
  "fonte_explicacao": "determinístico | ia_generativa | fallback_determinístico | agentic_llm_poc",
  "gerado_em": "ISO 8601 string"
}
```

> **NOTA:** Este endpoint executa `analisar_maquina()` e persiste ou reutiliza uma `Decision` pendente. **Tem efeito colateral de escrita no banco** a cada chamada (se não houver `Decision` pendente equivalente dentro de 30 minutos).

> **NOTA — LLM:** O campo `explicacao_operador` pode vir do Gemini API (se `GEMINI_API_KEY` configurada e circuito fechado) ou do fallback determinístico. O frontend **não deve tratar como fato clínico ou diagnóstico definitivo**.

**Arquivo:** `api_tcc/api/views_prescricao.py` L48–L127

---

#### `GET /api/prescricoes/`

| Campo | Valor |
|---|---|
| Handler | `PrescricaoView.get()` em `views_ingestao.py` |
| Autenticação | Token DRF **ou** Demo público |
| Parâmetro obrigatório | `?maquina_id=COLH-01` |

Comportamento idêntico a `GET /api/prescricoes/{maquina_id}/` usando `analisar_maquina()`. Retorna o resultado do pipeline + `decision_id` + `decision_status`.

**Arquivo:** `api_tcc/api/views_ingestao.py` L812–L839

---

#### `GET /api/prescricoes/lista/`

| Campo | Valor |
|---|---|
| Handler | `PrescricaoListView.get()` |
| Autenticação | Token DRF **ou** Demo público |
| Parâmetro obrigatório | `?maquina_id=COLH-01` |
| **STATUS** | ⚠️ DEPRECIADO — header `Deprecation: true`, `Sunset: 2026-12-31` |

Retorna histórico do modelo `Prescricao` (legado). Novas implementações devem usar `Event`/`Decision`.

```json
[
  {
    "id": "int",
    "maquina_id": "string",
    "titulo": "string",
    "descricao": "string",
    "status": "pendente | concluida | cancelada",
    "data_geracao": "ISO 8601"
  }
]
```

---

#### `GET /api/prescricoes/teste/`

**STATUS:** 🚫 REMOVIDO — retorna HTTP 410 Gone. Não usar.

---

#### `PATCH /api/decisions/{decision_id}/`

| Campo | Valor |
|---|---|
| Handler | `DecisionActionView.patch()` |
| Autenticação | **Token DRF obrigatório** — `IsAuthenticated` (sem demo público) |
| Parâmetro de rota | `decision_id` — UUID da `Decision` |

**Corpo da requisição** (campos extras rejeitados por `StrictSerializer`):
```json
{
  "status": "APROVADA | REJEITADA | EXECUTADA | EXPIRADA",
  "outcome_texto": "string (opcional, pode ser null ou em branco)"
}
```

**Transições de estado permitidas** (verificadas em `decisions.py`):
```
PENDENTE → APROVADA
PENDENTE → REJEITADA
PENDENTE → EXPIRADA
APROVADA → EXECUTADA
```
Qualquer outra transição retorna HTTP 400.

**Resposta 200 OK** — `DecisionSerializer`:
```json
{
  "id": "UUID",
  "machine": "UUID (machine.id)",
  "machine_external_code": "string",
  "event": "UUID | null",
  "texto": "string",
  "acao_recomendada": "string",
  "severidade": "NORMAL | ATENCAO | CRITICO",
  "confianca": "float 0..1 | null",
  "status": "string",
  "criado_em": "ISO 8601",
  "decidido_por": "int (user.id) | null",
  "decidido_por_username": "string | null",
  "decidido_em": "ISO 8601 | null",
  "outcome_texto": "string | null",
  "metodologia": "string | null"
}
```

**Resposta 403:** sem permissão para a machine (verificação de `Membership`)
**Resposta 404:** `{"status": "erro", "detalhe": "Decision nao encontrada"}`
**Resposta 400:** transição inválida ou campo desconhecido

> **IMPORTANTE:** Apenas usuários autenticados com `Membership` na `Organization` da machine podem aprovar/rejeitar/executar decisões. Roles `admin` ou `member` são necessários para escrita.

**Arquivo:** `api_tcc/api/views_ingestao.py` L760–L809, `api_tcc/services/decisions.py`

---

### B.9 Posição GPS / Mapa

#### `GET /api/maquinas/posicao/`

| Campo | Valor |
|---|---|
| Handler | `views_gps.get_maquinas_posicao()` |
| Autenticação | Token DRF **ou** Demo público |
| Parâmetro opcional | `?maquina_id=COLH-01` |

Retorna **apenas máquinas com leitura de latitude/longitude disponível**:
```json
[
  {
    "id": "int (Colheitadeira.id)",
    "maquina_id": "string",
    "modelo": "string (nome do modelo)",
    "lat": "float",
    "lng": "float",
    "status": "operando | parada | offline",
    "telemetria": {
      "temperatura": "float",
      "rpm": "int",
      "timestamp": "ISO 8601"
    }
  }
]
```

Status definido como:
- `"operando"`: leitura recebida nos últimos 10 min **e** `status_de_operacao.em_operacao=True`
- `"parada"`: leitura recebida nos últimos 10 min, mas não operando
- `"offline"`: última leitura há mais de 10 min

**Arquivo:** `api_tcc/views_gps.py` L53–L113

---

#### `GET /api/mapas/demo/`

| Campo | Valor |
|---|---|
| Handler | `views_gps.gps_demo()` |
| Autenticação | Token DRF **ou** Demo público |
| Dados | **GERADOS ARTIFICIALMENTE** — posições e telemetria são dados fixos + ruído aleatório |

> **ATENÇÃO:** Este endpoint retorna dados **completamente simulados**. O frontend deve identificar claramente quando está exibindo dados de demonstração.

---

### B.10 Métricas Operacionais

#### `GET /api/metricas/`

| Campo | Valor |
|---|---|
| Handler | `MetricasView.get()` |
| Autenticação | Token DRF **ou** Demo público |

**Resposta 200 OK:**
```json
{
  "leituras_validas": "int",
  "leituras_invalidas": "int",
  "taxa_rejeicao_pct": "float",
  "maquinas_ativas": "int"
}
```

> Em modo Demo público, `leituras_invalidas` é sempre `0` (deliberado).

**Arquivo:** `api_tcc/api/views_ingestao.py` L514–L547

---

### B.11 Status MQTT

#### `GET /api/status-mqtt/`

| Campo | Valor |
|---|---|
| Handler | `StatusMQTTView.get()` |
| Autenticação | Token DRF **ou** Demo público |

**Resposta 200 OK** (com leituras):
```json
{
  "mqtt_conectado": "bool",
  "ultima_leitura_segundos_atras": "int",
  "status": "online | offline"
}
```

**Resposta 200 OK** (sem nenhuma leitura):
```json
{
  "mqtt_conectado": false,
  "ultima_leitura_segundos_atras": null,
  "status": "offline",
  "detalhes": "Nenhuma leitura recebida ainda"
}
```

Considera `online` se última leitura foi há < 10 segundos.

**Arquivo:** `api_tcc/api/views_ingestao.py` L550–L588

---

### B.12 Saúde da API

#### `GET /api/health/`

| Campo | Valor |
|---|---|
| Handler | `HealthView.get()` |
| Autenticação | **Nenhuma** — completamente público |

**Resposta 200 OK:**
```json
{
  "status": "ok | degradado",
  "database": "ok | erro",
  "mqtt_last_seen_seconds": "int | null",
  "version": "string (padrão: '1.0')"
}
```

**Arquivo:** `api_tcc/api/views_health.py`

---

### B.13 Dead Letter Queue

#### `GET /api/dlq/`

| Campo | Valor |
|---|---|
| Handler | `DeadLetterEntryListView.get()` |
| Autenticação | **Token DRF obrigatório** — `IsAuthenticated` |

Retorna entradas de falha não resolvidas. Destinado a uso administrativo.

**Arquivo:** `api_tcc/api/views_dlq.py`

---

### B.14 Relatório

#### `GET /api/relatorio/`

| Campo | Valor |
|---|---|
| Handler | `RelatorioView.get()` |
| Autenticação | Token DRF **ou** Demo público |
| Parâmetro opcional | `?formato=json` (padrão) ou `?formato=csv` |

**Resposta JSON:**
```json
{
  "periodo": "Últimas 24 horas",
  "total_leituras": "int",
  "maquinas_ativas": "int",
  "alertas_gerados": "int",
  "eficiencia_operacional": "float"
}
```

**Resposta CSV:** `Content-Type: text/csv; charset=utf-8` com `Content-Disposition: attachment`.

---

#### `GET /api/relatorio/exportar/`

| Campo | Valor |
|---|---|
| Handler | `RelatorioExportarView` (dois handlers distintos — ver abaixo) |
| Autenticação | Token DRF **ou** Demo público |
| Parâmetros obrigatórios | `?maquina_id=COLH-01` |
| Parâmetros opcionais | `?data_inicio=AAAA-MM-DD&data_fim=AAAA-MM-DD` |

> **ATENÇÃO — DOIS HANDLERS COM O MESMO NOME:**
> - `api_tcc/api/views_ingestao.py` — exporta CSV (delimitador `;`, `Content-Disposition: attachment`)
> - `api_tcc/api/views_relatorio.py` — exporta Excel `.xlsx`
> A URL `/api/relatorio/exportar/` está mapeada para `RelatorioExportarView` de `views_relatorio.py` (Excel). O handler CSV de `views_ingestao.py` está acessível via o mesmo caminho (conflito de importação — **PENDÊNCIA**).

**Arquivo:** `api_tcc/urls.py` L61, `api_tcc/api/views_ingestao.py` L649–L701, `api_tcc/api/views_relatorio.py`

---

### B.15 Router — ViewSets CRUD

Todos os recursos abaixo suportam `GET` (lista), `POST`, `GET /{id}/`, `PUT /{id}/`, `DELETE /{id}/`.
Permissão: `IsAuthenticatedOrPublicDemo`.

| Prefixo | Modelo | Serializer |
|---|---|---|
| `/api/unidadedemedida/` | `UnidadedeMedida` | `UnidadedeMedidaSerializer` |
| `/api/marca/` | `Marca` | `MarcaSerializer` |
| `/api/modelo/` | `Modelo` | `ModeloSerializer` |
| `/api/combustivel/` | `Combustivel` | `CombustivelSerializer` |
| `/api/operario/` | `Operario` | `OperarioSerializer` |
| `/api/pressaopneus/` | `PressaoPneus` | `PressaoPneusSerializer` |
| `/api/alturadocorte/` | `AlturadoCorte` | `AlturadoCorteSerializer` |
| `/api/pressaodocorte/` | `PressaodoCorte` | `PressaodoCorteSerializer` |
| `/api/tempumi_ambiente/` | `TempUmi_Ambiente` | `TempUmi_AmbienteSerializer` |
| `/api/temperaturamaquina/` | `TemperaturaMaquina` | `TemperaturaMaquinaSerializer` |
| `/api/statusdeoperacao/` | `StatusdeOperacao` | `StatusdeOperacaoSerializer` |
| `/api/estadodemovimento/` | `EstadodeMovimento` | `EstadodeMovimentoSerializer` |
| `/api/transbordo/` | `Transbordo` | `TransbordoSerializer` |
| `/api/colheitadeira/` | `Colheitadeira` | `ColheitadeiraSerializer` |

**Arquivo:** `api_tcc/urls.py` L26–L40, `api_tcc/api/viewsets.py`

---

## C. Autenticação e Segurança do Frontend

### C.1 Dois Mecanismos de Autenticação Distintos

O sistema usa **dois mecanismos independentes** que o frontend deve tratar separadamente:

#### Mecanismo 1 — Token DRF (para o frontend de dashboard)

```
POST /api/auth/login/
Body: { "username": "...", "password": "..." }
Response: { "token": "<40-char-hex>" }
```

Todas as requisições autenticadas devem incluir:
```
Authorization: Token <token>
```

- Autenticação por sessão e básica também estão ativas (`SessionAuthentication`, `BasicAuthentication`), mas **Token é o mecanismo recomendado para SPA**.
- Não há endpoint de refresh/expiração implementado (DRF `TokenAuthentication` por padrão não expira).

#### Mecanismo 2 — X-API-Key (para dispositivos de campo)

```
Header: X-API-Key: <FIELDNODE_API_KEY>
```

Usado **exclusivamente** em `POST /api/telemetria/` e `POST /api/telemetria/lote/`. Esta chave é um segredo de servidor armazenado em variável de ambiente.

> **REGRA ABSOLUTA:** `FIELDNODE_API_KEY` **não deve jamais aparecer no bundle do frontend**, em variáveis `NEXT_PUBLIC_*`, ou em qualquer lugar acessível ao browser.

### C.2 Endpoints Públicos (sem autenticação)

| Endpoint | Condição |
|---|---|
| `GET /api/health/` | Sempre público |
| `GET /api/swagger/` | Sempre público |
| `GET /api/redoc/` | Sempre público |
| Endpoints com `IsAuthenticatedOrPublicDemo` | Público apenas se `DEMO_MODE=True` (leitura) |

### C.3 Modo Demo Público

Quando `DEMO_MODE=True` (variável de ambiente):
- Usuários **não autenticados** podem fazer requisições `GET` em todos os endpoints marcados com `IsAuthenticatedOrPublicDemo`.
- Os dados retornados são filtrados para `machine__is_demo=True`.
- Requisições de escrita (`POST`, `PUT`, `PATCH`, `DELETE`) sempre exigem autenticação.

### C.4 Autorização por Organização

Para usuários autenticados, o acesso às máquinas é filtrado pelo modelo `Membership`:
```
User → Membership(role) → Organization → Machine
```

Roles disponíveis: `admin`, `member`, `viewer`.
- Escrita (PATCH em Decision): exige `admin` ou `member`.
- Leitura: qualquer role com membership na organização.

**Arquivo:** `api_tcc/permissions.py`

### C.5 Expiração e Renovação de Token

**NÃO IMPLEMENTADO.** O `TokenAuthentication` padrão do DRF não expira tokens. Não há endpoint de logout/revogação implementado. O frontend deve considerar o token válido até que o servidor retorne 401.

**Status:** PENDÊNCIA MÉDIA — sem risco imediato no protótipo, bloqueador em produção.

---

## D. Contrato das Máquinas e Relacionamentos

### D.1 Dois Identificadores Coexistentes

| Identificador | Campo | Tipo | Usado em |
|---|---|---|---|
| ID legado textual | `maquina_id` | `string` (ex: `"COLH-01"`) | `LeituraTelemetria`, `Colheitadeira`, parâmetros de query |
| ID canônico externo | `Machine.external_code` | `string`, normalizado `.strip().upper()` | `Machine`, `Event`, `Decision` |
| UUID interno | `Machine.id` | `UUID` | URL de `/api/machines/{uuid}/health/`, FKs internas |

O `external_code` e o `maquina_id` são **o mesmo valor normalizado** — a `Machine` canônica é criada automaticamente na ingestão via `get_or_create(external_code=maquina_id_normalizado)`.

### D.2 Colheitadeira vs. Machine

| Modelo | Propósito | Campo de link |
|---|---|---|
| `Colheitadeira` | Entidade de configuração agrícola (modelo, operário, etc.) | `maquina_id` (string), `machine` (FK para `Machine`, nullable) |
| `Machine` | Entidade canônica de hardware | `external_code`, `id` (UUID) |

- `Colheitadeira.machine` é FK opcional (nullable) — nem toda colheitadeira tem `Machine` canônica vinculada.
- O sistema cria `Machine` automaticamente ao receber telemetria. Colheitadeiras existentes no banco antes da telemetria podem não ter `Machine` vinculada.

### D.3 Serialização de Relacionamentos

- Em `LeituraTelemetriaSerializer`: `machine` retorna o UUID da `Machine`, `machine_id` também é UUID.
- Em `ColheitadeiraSerializer`: `modelo`, `combustivel`, etc. são objetos **aninhados** (read), mas escritos por `modelo_id`, `combustivel_id` (IDs inteiros) — padrão DRF.
- Em `DecisionSerializer`: `machine` retorna UUID da `Machine`, `machine_external_code` retorna a string legível.

### D.4 Regras de Integridade

- `Colheitadeira.ativo=False` é soft delete — máquina não aparece nos endpoints de listagem.
- `Machine.ativo=False` exclui a máquina do filtro de membership.
- `Machine.is_demo=True` indica dado de demonstração — o frontend deve sinalizar visualmente.
- Ao deletar `Colheitadeira` via API, o sistema usa `ativo=False` (não apaga fisicamente).

---

## E. Trust Score — S3

### E.1 Arquitetura do Trust Score

O Trust Score é calculado em **dois níveis**:

**Nível 1 — Por Leitura (`LeituraTelemetria.trust_score`)**
- Campo `float | null` (null = dado histórico não pontuado)
- Calculado por `calcular_trust_score()` em `api_tcc/services/data_health.py`
- Heurística determinística baseada em: gap temporal, repetição de sensor, proximidade a limites físicos, continuidade
- Retornado no campo `trust_score` do `LeituraTelemetriaSerializer`

**Nível 2 — Agregado por Machine (`MachineDataHealth.trust_score_medio`)**
- EMA com `alpha=0.2` atualizada a cada ingestão
- Acessível via `GET /api/machines/{uuid}/health/`
- Também embutido em `GET /api/leituras/ultimas/` (campo `data_health`)

### E.2 Campos do MachineDataHealth (confirmados no modelo)

| Campo | Tipo | Significado |
|---|---|---|
| `machine` | OneToOne FK | Machine canônica |
| `trust_score_medio` | `float` (default 0.0) | EMA 0..1 das leituras pontuadas |
| `ultima_atualizacao` | `DateTimeField` | Timestamp da última leitura considerada |
| `leituras_analisadas` | `PositiveIntegerField` | Quantidade de leituras com trust_score |
| `sinais_de_alerta` | `JSONField` | Ver estrutura abaixo |
| `anomalias_detectadas` | `PositiveIntegerField` | Contador de anomalias |

### E.3 Estrutura de `sinais_de_alerta`

```json
{
  "primeira_leitura": "bool",
  "gap_temporal": "bool",
  "timestamp_fora_de_ordem": "bool",
  "timestamp_indisponivel": "bool",
  "valores_repetidos": "bool",
  "limite_fisico": "bool",
  "salto_abrupto": "bool",
  "score_baixo": "bool",
  "contadores": {
    "primeira_leitura": "int",
    "gap_temporal": "int",
    "timestamp_fora_de_ordem": "int",
    "timestamp_indisponivel": "int",
    "valores_repetidos": "int",
    "limite_fisico": "int",
    "salto_abrupto": "int",
    "score_baixo": "int"
  },
  "ultimos_motivos": ["string"]
}
```

### E.4 Limiar de Trust Score

| Limiar | Valor | Definição |
|---|---|---|
| `LOW_TRUST_SCORE_THRESHOLD` | 0.75 | Score individual abaixo → sinal `score_baixo=True` |
| `TRUST_SCORE_EMA_ALPHA` | 0.2 | Peso da nova leitura na média móvel |

**Arquivo:** `api_tcc/services/data_health.py` L45–L46

### E.5 Thresholds de Risco (calcular_status_risco)

Usados em `/api/leituras/ultimas/` e no serializer:

| Nível | Condição |
|---|---|
| `Crítico` | `temperatura > 110.0` **ou** `vibracao > 8.0` |
| `Alerta` | `temperatura > 95.0` **ou** `vibracao > 5.0` |
| `Normal` | Demais casos |

**Arquivo:** `api_tcc/services/telemetria.py` L472–L498

### E.6 Limites de Validação de Payload

| Sensor | Mínimo | Máximo |
|---|---|---|
| `temperatura` | 0.0 °C | 150.0 °C |
| `vibracao` | 0.0 | 10.0 |
| `rpm` | 0 | 5000 |

**Arquivo:** `api_tcc/services/sensor_limits.py`

---

## F. Anomalias — S6

### F.1 Fluxo de Detecção

```
Ingestão → validar_payload() → registrar_leitura()
    → calcular_trust_score()
    → detect_anomaly() [Isolation Forest via REGISTRY]
    → atualizar_machine_data_health()
    → avaliar_leitura() [Event generation]
    → se anomaly_score >= 0.70: criar_evento_anomalia_estatistica() + persistir_decision_da_anomalia()
```

### F.2 Dois Sistemas de Anomalia Coexistentes

| Sistema | Arquivo | Trigger | Resultado |
|---|---|---|---|
| Thresholds determinísticos | `api_tcc/ia/pipeline.py` | Sob demanda (query GET) | `ResultadoAnalise` (NORMAL/ATENCAO/CRITICO) |
| Isolation Forest por leitura | `api_tcc/services/anomaly_detection.py` | A cada ingestão POST | `Event` + `Decision` persistidos |

O endpoint `GET /api/anomalias/` usa apenas o **sistema 1** (thresholds). O **sistema 2** opera na ingestão e persiste `Event`/`Decision` — não há endpoint para listar Events diretamente.

### F.3 Thresholds do Pipeline de Análise

| Condição | Limiar | Motivo |
|---|---|---|
| Temperatura máxima | > 85°C | `'temperatura acima de 85°C'` |
| Tendência de temperatura | > 0.5 (média de diff) | `'tendência de aumento sustentado'` |
| Vibração média | > 5.0 | `'vibração média acima do padrão'` |
| Classificação CRITICO | >= 2 motivos | – |
| Classificação ATENCAO | 1 motivo | – |

**Arquivo:** `api_tcc/ia/pipeline.py` L52–L90

### F.4 Isolation Forest

- Modelo em: `api_tcc/ia/modelos/isolation_forest_v1.pkl`
- Features: `temperatura`, `vibracao`, `rpm`
- `contamination=0.05`, `n_estimators=100`
- **Se o arquivo `.pkl` não existir**: `FileNotFoundError` é silenciado, sistema funciona só com regras
- Score de anomalia exposto na `Decision.confianca` quando persiste via ingestão
- **Não exposto diretamente** em `GET /api/anomalias/` (apenas motivo textual se ativo)

**Arquivo:** `api_tcc/ia/deteccao_multivariada.py`

### F.5 Dados Demonstrativos vs. Reais

- `Machine.is_demo=True` marca máquinas de demonstração
- `GET /api/mapas/demo/` retorna **dados completamente gerados artificialmente** (posição hardcoded + ruído aleatório + telemetria aleatória)
- O frontend deve identificar e sinalizar dados demo de forma inequívoca

---

## G. Eventos, Decisões e Auditoria de Ações — S4

### G.1 Modelo Decision

```
Decision.status:
  PENDENTE → {APROVADA, REJEITADA, EXPIRADA}
  APROVADA → EXECUTADA
  (outros estados são terminais — sem transição de saída)
```

### G.2 Não Há Endpoint de Listagem de Decisions

> **PENDÊNCIA ALTA:** Não existe `GET /api/decisions/` para listar decisões de uma máquina. O frontend só obtém `decision_id` e `decision_status` embutidos na resposta de `GET /api/prescricoes/{maquina_id}/`. Para exibir um painel de decisões, é necessário implementar este endpoint no backend.

### G.3 Não Há Endpoint de Listagem de Events

> **PENDÊNCIA ALTA:** O modelo `Event` (com tipos `TEMP_ALTA`, `VIBRACAO_ALTA`, `ANOMALIA_ML`, etc.) não tem endpoint REST de listagem exposto. Os Events são criados automaticamente na ingestão mas não podem ser consultados via API atualmente.

### G.4 Campos Auditados na Decision Após PATCH

Após `PATCH /api/decisions/{id}/`:
- `status` — novo status
- `decidido_por` — `user.id` do usuário autenticado (apenas na primeira decisão)
- `decidido_em` — timestamp da decisão (apenas na primeira decisão)
- `outcome_texto` — texto descritivo (se fornecido)

O campo `decidido_por` é preenchido **apenas uma vez** — se a decision já tinha `decidido_por`, não é sobrescrito.

### G.5 Decision Gerada por LLM Agentic

O campo `Decision.detalhes.metodologia` pode conter `"agentic_llm_poc"`. Neste caso, `GET /api/prescricoes/{maquina_id}/` retorna o texto da decision agentic em vez do pipeline determinístico.

**Status:** funcionalidade experimental — não depender desta branch como comportamento estável.

---

## H. Convenções Obrigatórias para o Frontend

### H.1 Base URL e Configuração

```typescript
// Correto — variável de ambiente não exposta como secret
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api'

// ERRADO — chave de ingestão de dispositivo nunca deve estar no frontend
// const API_KEY = process.env.NEXT_PUBLIC_FIELDNODE_API_KEY  // ← PROIBIDO
```

### H.2 Token de Autenticação

```typescript
// Obter token
const { token } = await fetch(`${API_URL}/auth/login/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
}).then(r => r.json())

// Usar token em requisições
fetch(`${API_URL}/leituras/ultimas/`, {
  headers: { 'Authorization': `Token ${token}` }
})
```

### H.3 Tratamento de Erros Obrigatório

O frontend deve tratar os seguintes HTTP status:
- `200` / `201` — sucesso
- `400` — erro de validação (ler campo `detalhe` ou `detalhes` da resposta — **inconsistência existente**)
- `401` — não autenticado → redirecionar para login
- `403` — sem permissão → exibir mensagem adequada
- `404` — recurso não encontrado
- `410` — recurso removido (`/api/prescricoes/teste/`)
- `500` — falha interna → não expor detalhe técnico ao usuário

### H.4 Campos Nulos e Ausentes

| Campo | Comportamento correto |
|---|---|
| `trust_score: null` | Exibir "sem pontuação" ou indicador neutro — não calcular % |
| `confianca: null` | `Decision` sem score de confiança — não inferir valor |
| `latitude: null` / `longitude: null` | Não plotar no mapa |
| `data_health: null` | Machine sem leituras analisadas ainda |
| `metricas.*: null` | Janela de leituras insuficiente |

### H.5 Identidade das Entidades

- **Usar `maquina_id` (string legado)** em query params e referências internas ao frontend.
- **Usar `Machine.id` (UUID)** ao acessar `/api/machines/{uuid}/health/`.
- **Nunca substituir** um UUID de Decision ou Machine por uma string genérica — preservar o ID exato retornado pela API.
- Após `PATCH /api/decisions/{id}/`, atualizar o estado local da decision com a resposta do servidor — não assumir sucesso pelo clique.

### H.6 Separação Demo / Produção

- Dados de máquinas com `is_demo=True` devem ser sinalizados visualmente.
- `/api/mapas/demo/` retorna dados simulados — jamais apresentar como telemetria real.
- Em modo demo, o campo `leituras_invalidas` de `/api/metricas/` é sempre `0` — não representativo da realidade.

### H.7 Atualização de Dados Após Mutações

- Após `PATCH /api/decisions/{id}/`, invalidar/refetch o estado da decision e da prescrição associada.
- Após qualquer operação bem-sucedida de escrita, não assumir consistência imediata do dado agregado (`MachineDataHealth`) — ele é atualizado assincronamente na ingestão.

---

## I. Matriz de Compatibilidade e Pendências

| Recurso | Implementação encontrada | Contrato comprovado | Pendência ou risco | Arquivos de referência |
|---|---|---|---|---|
| **Autenticação Token** | `POST /api/auth/login/` → `{"token": "..."}` | ✅ VERIFICADO | Sem expiração/refresh implementado | `api_tcc/urls.py:44`, `setup/settings.py:208` |
| **X-API-Key (ingestão)** | Header `X-API-Key` validado no handler | ✅ VERIFICADO | Segredo de servidor — jamais expor no frontend | `views_ingestao.py:166-168` |
| **Máquinas / Colheitadeiras** | `GET /api/colheitadeira/` com serializer aninhado | ✅ VERIFICADO | Limite 10 máquinas em `/leituras/ultimas/` sem paginação — **ALTO** | `viewsets.py`, `serializers.py` |
| **Telemetria — ingestão** | `POST /api/telemetria/` com idempotência `(device_id, message_id)` | ✅ VERIFICADO | Endpoint apenas para ESP32/gateway | `views_ingestao.py:148` |
| **Telemetria — leitura** | `GET /api/telemetria/` + `GET /api/leituras/ultimas/` | ✅ VERIFICADO | `leituras/ultimas/` limitado a 10 máquinas sem paginação — **ALTO** | `views_ingestao.py:221,346` |
| **Trust Score (por leitura)** | `LeituraTelemetria.trust_score` calculado na ingestão | ✅ VERIFICADO | Histórico anterior a S3 tem `null` | `services/data_health.py` |
| **Trust Score (agregado)** | `GET /api/machines/{uuid}/health/` | ✅ VERIFICADO | `machine_id` deve ser UUID, não string textual — risco de confusão — **MÉDIO** | `views_ingestao.py:232` |
| **Anomalias (threshold)** | `GET /api/anomalias/` executa pipeline síncrono | ✅ VERIFICADO | Não persiste histórico de anomalias — só classifica estado atual — **MÉDIO** | `views_ingestao.py:120`, `ia/pipeline.py` |
| **Anomalias (Isolation Forest)** | Modelo `.pkl` carregado na ingestão | ⚠️ CONDICIONAL | `.pkl` pode não existir — sistema degrada graciosamente | `ia/deteccao_multivariada.py`, `services/anomaly_detection.py` |
| **Eventos (Event model)** | Modelo `Event` completo com tipos e severidades | ❌ SEM ENDPOINT | **BLOQUEADOR:** não há `GET /api/events/` para listar eventos por máquina | `models.py:303` |
| **Decisions — listagem** | Modelo `Decision` completo | ❌ SEM ENDPOINT | **BLOQUEADOR:** não há `GET /api/decisions/` para listar por máquina | `models.py:381` |
| **Decisions — ação (PATCH)** | `PATCH /api/decisions/{uuid}/` com validação de transição | ✅ VERIFICADO | Apenas autenticados com membership podem agir | `views_ingestao.py:760` |
| **Prescrições (legado)** | `GET /api/prescricoes/lista/` depreciado | ⚠️ DEPRECIADO | Header `Sunset: 2026-12-31` — não usar em novas funcionalidades — **MÉDIO** | `views_ingestao.py:717` |
| **Prescrições / análise atual** | `GET /api/prescricoes/{maquina_id}/` | ✅ VERIFICADO | Efeito colateral de escrita (persiste Decision) — **MÉDIO** | `views_prescricao.py` |
| **GPS / Posição** | `GET /api/maquinas/posicao/` (dados reais) | ✅ VERIFICADO | Retorna vazio se sem leituras com lat/lng | `views_gps.py:53` |
| **GPS / Demo** | `GET /api/mapas/demo/` | ✅ VERIFICADO — DADOS SIMULADOS | Posição e telemetria completamente artificiais | `views_gps.py:27` |
| **Relatório JSON** | `GET /api/relatorio/` | ✅ VERIFICADO | `eficiencia_operacional` é métrica sintética (maquinas_ativas/total_leituras*100) | `views_ingestao.py:591` |
| **Relatório Excel** | `GET /api/relatorio/exportar/` → `.xlsx` | ✅ VERIFICADO | Handler conflitante com CSV no mesmo path — **MÉDIO** | `views_relatorio.py`, `urls.py:61` |
| **Inconsistência de campo de erro** | Alguns endpoints usam `detalhe`, outros `detalhes` | ⚠️ INCONSISTÊNCIA | Frontend deve tentar ambos os campos — **BAIXO** | `views_ingestao.py` múltiplos |
| **Multi-tenant (Organization)** | Modelos `Organization` e `Membership` existem | ⚠️ PARCIAL | Endpoints não expõem Organization via API — acesso filtrado implicitamente | `models.py:577`, `permissions.py` |
| **Expiração de token** | Não implementada | ❌ AUSENTE | Token DRF padrão não expira — **MÉDIO** em produção | `setup/settings.py:208` |
| **Paginação** | Não implementada em nenhum endpoint | ❌ AUSENTE | `/leituras/ultimas/` limitado a 10 máquinas — **ALTO** para frotas maiores | `views_ingestao.py:424` |

### Classificação de Prioridade

| Prioridade | Pendência |
|---|---|
| 🔴 **BLOQUEADOR** | `GET /api/events/` inexistente — painel de eventos não pode ser implementado |
| 🔴 **BLOQUEADOR** | `GET /api/decisions/` inexistente — painel de histórico de decisões não pode ser implementado |
| 🟠 **ALTO** | Paginação ausente em `/leituras/ultimas/` — frota com > 10 máquinas não é suportada |
| 🟠 **ALTO** | Sem renovação/expiração de token — sessão infinita em produção |
| 🟡 **MÉDIO** | Confusão `machine_id` (UUID) vs. `maquina_id` (string) — risco de erro de path na URL |
| 🟡 **MÉDIO** | `GET /api/prescricoes/{maquina_id}/` tem efeito colateral de escrita — não é um GET puro |
| 🟡 **MÉDIO** | Conflito de handler para `/api/relatorio/exportar/` (CSV vs. Excel) |
| 🟡 **MÉDIO** | `DEMO_MODE` expõe dados artificiais de GPS — necessita sinalização visual clara |
| 🟢 **BAIXO** | Inconsistência `detalhe` vs. `detalhes` nos payloads de erro |
| 🟢 **BAIXO** | Endpoint `/api/prescricoes/lista/` depreciado mas ainda ativo |

---

## Apêndice — Arquivos Inspecionados

| Arquivo | Conteúdo |
|---|---|
| `setup/urls.py` | Roteamento principal |
| `setup/settings.py` | Configuração Django completa |
| `requirements.txt` | Dependências Python |
| `api_tcc/urls.py` | Roteamento da aplicação |
| `api_tcc/models.py` | Todos os modelos Django (885 linhas) |
| `api_tcc/permissions.py` | Classes e funções de permissão |
| `api_tcc/api/views_ingestao.py` | Views de ingestão, anomalias, decisões, relatório |
| `api_tcc/api/views_prescricao.py` | View de prescrição com LLM |
| `api_tcc/api/views_health.py` | Endpoint de saúde da API |
| `api_tcc/api/views_dlq.py` | Dead Letter Queue |
| `api_tcc/api/views_relatorio.py` | Exportação Excel |
| `api_tcc/api/viewsets.py` | ViewSets CRUD |
| `api_tcc/api/serializers.py` | Serializers completos |
| `api_tcc/views_gps.py` | GPS real e demo |
| `api_tcc/ia/pipeline.py` | Pipeline de análise de anomalias |
| `api_tcc/ia/deteccao_multivariada.py` | Isolation Forest |
| `api_tcc/ia/explicacao_llm.py` | Integração Gemini API |
| `api_tcc/services/telemetria.py` | Serviço de ingestão e trust score |
| `api_tcc/services/decisions.py` | Serviço de decisões e transições |
| `api_tcc/services/data_health.py` | Cálculo de trust score e MachineDataHealth |
| `api_tcc/services/sensor_limits.py` | Limites físicos dos sensores |

---

> **Confirmação de escopo:** Nenhuma alteração funcional foi realizada no repositório durante esta auditoria. Este arquivo (`CONTRATO_FRONT_BACK.md`) é o único arquivo criado.
>
> **Data de auditoria:** 2026-10-15
> **Versão do documento:** 1.0

