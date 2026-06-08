# Lógica de Alertas do FieldNode

## 1. Classificação de Risco (Backend)

**Arquivo:** `api_tcc/services/telemetria.py` — função `calcular_status_risco()`

A classificação é feita por ponto (cada leitura individual), não por média. A cada ingestão de telemetria, o backend calcula:

| Condição | Nível | Cor |
|----------|-------|-----|
| `temperatura > 110°C` **ou** `vibracao > 8.0g` | Crítico | Vermelho (`#FF5252`) |
| `temperatura > 95°C` **ou** `vibracao > 5.0g` | Atenção | Amarelo (`#FFD740`) |
| Qualquer valor abaixo dos limites acima | Normal | Verde (`#4CAF50`) |

**Observações:**
- RPM **não influencia** a classificação de risco atual (apenas temperatura e vibração).
- A classificação é exibida no dashboard via campo `status_risco` na resposta da API.
- A função está centralizada em `calcular_status_risco()` e é usada tanto pela view `UltimaLeituraView` quanto pelo serializer `LeituraTelemetriaSerializer`.

---

## 2. Linhas de Referência nos Gráficos (Frontend)

**Arquivo:** `frontend-next/src/components/HistoryChart.tsx`

Os gráficos de detalhes agora exibem duas linhas horizontais de referência por métrica:

| Métrica | Linha de Atenção | Linha Crítica |
|---------|------------------|---------------|
| Temperatura | 95°C (tracejado âmbar) | 110°C (tracejado vermelho) |
| Vibração | 0.5g (tracejado âmbar) | 0.8g (tracejado vermelho) |
| RPM | 1400 RPM (tracejado âmbar) | 1200 RPM (tracejado vermelho) |

**Interpretação visual:**
- **Acima da linha vermelha (crítica):** Ponto de atenção imediato — possível falha de sensor ou condição operacional fora do padrão.
- **Entre âmbar e vermelho:** Estado de alerta — monitorar com frequência.
- **Abaixo da linha âmbar:** Operação considerada normal/bom.

---

## 3. Filtros no Dashboard

O dashboard (`/colheitadeiras`) agrupa as leituras recentes por nível de risco:

- **Cards de alerta** mostram quantidade de máquinas em `CRITICO` e `ATENCAO`.
- A **cor do card** muda conforme a gravidade: vermelho para crítico, amarelo para atenção, verde para normal.

## 4. Validação na Ingestão

Além da classificação, o backend rejeita valores fora de ranges físicos no `POST /api/telemetria/`:

- `temperatura`: 0°C a 150°C
- `vibracao`: 0 a 10
- `rpm`: 0 a 5000

Payloads inválidos são salvos em `TelemetriaInvalida` para auditoria e não geram alertas — são descartados silenciosamente do fluxo principal.
