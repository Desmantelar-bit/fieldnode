# DEMO.md — Roteiro Oficial de Demo FieldNode

Tempo estimado: 8 minutos.
Ordem obrigatória: cada passo alimenta o próximo.

---

## Pré-requisito

```bash
docker compose up --build
```

Aguardar até os três serviços estarem de pé:

```
web   | Starting development server at http://0.0.0.0:8000/
frontend | Ready on http://localhost:3000
db    | ready for connections
```

Verificação rápida antes de começar:

```bash
curl http://127.0.0.1:8000/api/health/
# {"status": "ok"}
```

---

## Passo 1 — Máquina Normal

**O que mostrar:** frota operando dentro dos parâmetros, dashboard com métricas reais.

Abrir no browser:

```
http://127.0.0.1:3000/dashboard
```

O que a banca vê:
- Cards de métricas: total de máquinas cadastradas, quantas em operação, horas totais reportadas.
- Grid da frota com status de cada colheitadeira.
- Indicador "Sync offline ativo" pulsando no canto superior direito.

Complementar com a API diretamente para mostrar o dado bruto:

```bash
curl http://127.0.0.1:8000/api/leituras/ultimas/
```

Resposta esperada: array com `status_risco.rotuloRisco: "NORMAL"` para as máquinas em operação padrão.

---

## Passo 2 — Leitura Ruim

**O que mostrar:** ingestão de telemetria com valores críticos, simulando sensor de campo.

```bash
curl -X POST http://127.0.0.1:8000/api/telemetria/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: 00000000-0000-4000-8000-000000000000" \
  -d "{
    \"id\": \"550e8400-e29b-41d4-a716-446655440099\",
    \"maquina_id\": \"COLH-01\",
    \"temperatura\": 91.5,
    \"vibracao\": 0.92,
    \"rpm\": 1150,
    \"latitude\": -15.793889,
    \"longitude\": -47.882778,
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
  }"
```

Resposta esperada:

```json
{"status": "ok", "id": "550e8400-e29b-41d4-a716-446655440099", "ia": {"status": "agendado"}}
```

Ponto de defesa: o `id` UUID garante idempotência — reenviar o mesmo pacote não duplica o registro. Rodar o mesmo curl duas vezes e mostrar `{"status": "duplicata ignorada"}`.

---

## Passo 3 — Alerta

**O que mostrar:** a leitura ruim do passo 2 já classificada como CRÍTICO pela API e refletida no dashboard.

```bash
curl "http://127.0.0.1:8000/api/leituras/ultimas/?maquina_id=COLH-01"
```

Resposta esperada:

```json
[{
  "maquina_id": "COLH-01",
  "temperatura": 91.5,
  "vibracao": 0.92,
  "rpm": 1150,
  "status_risco": {
    "rotuloRisco": "CRITICO",
    "corRisco": "#ef4444",
    "iconeRisco": "🔴"
  }
}]
```

No browser, navegar para:

```
http://127.0.0.1:3000/colheitadeiras
```

O que a banca vê: card de COLH-01 com badge vermelho CRÍTICO, temperatura e vibração destacadas.

---

## Passo 4 — Prescrição

**O que mostrar:** IA gerando recomendação operacional baseada nos dados críticos.

Acionar via API:

```bash
curl "http://127.0.0.1:8000/api/prescricoes/?maquina_id=COLH-01"
```

Resposta esperada:

```json
{"status": "agendado", "maquina_id": "COLH-01", "modelos": {"prescricao": "enfileirado"}}
```

Consultar o histórico gerado:

```bash
curl "http://127.0.0.1:8000/api/prescricoes/lista/?maquina_id=COLH-01"
```

No browser, navegar para:

```
http://127.0.0.1:3000/detalhes?id=COLH-01
```

O que a banca vê:
- Gráficos de histórico de temperatura, vibração e RPM.
- Botão "Ver Decisão" no canto superior direito.
- Clicar no botão abre o modal com a prescrição gerada pela IA: severidade, ação recomendada e motivos detalhados.

---

## Passo 5 — Mapa

**O que mostrar:** posição geográfica da frota, com COLH-01 marcada em vermelho (offline/crítico).

No browser:

```
http://127.0.0.1:3000/mapa
```

O que a banca vê:
- Mapa OpenStreetMap com pins coloridos por status: verde (operando), amarelo (parada), vermelho (offline/crítico).
- Popup ao clicar no pin: ID da máquina, temperatura, RPM e timestamp da última leitura.
- Se nenhuma máquina tiver GPS real, o mapa entra em modo demo automaticamente com rota simulada e banner "Modo Demo - Rota Simulada".

Ponto de defesa: o fallback demo existe porque GPS em campo rural é intermitente. O sistema não quebra — degrada com graciosidade.

---

## Passo 6 — Exportação CSV

**O que mostrar:** relatório operacional de COLH-01 exportado como CSV com delimitador `;`.

Via API diretamente:

```bash
curl "http://127.0.0.1:8000/api/relatorio/exportar/?maquina_id=COLH-01" \
  -H "Accept: text/csv" \
  --output relatorio_COLH-01.csv

cat relatorio_COLH-01.csv
```

Conteúdo esperado: cabeçalho com metadados, seção de estatísticas (leituras, temperatura média, alertas) e linhas de telemetria com `timestamp;temperatura;vibracao;rpm;latitude;longitude;risco`.

No browser, navegar para:

```
http://127.0.0.1:3000/dashboard
```

O que a banca vê:
- Seletor de máquina ao lado do botão "Extrair relatorio".
- Selecionar COLH-01, clicar no botão.
- Browser baixa `relatorio_COLH-01_AAAA-MM-DD.csv` automaticamente — mesmo endpoint, mesmo arquivo.

---

## Resumo do Fluxo

```
ESP32 / curl  →  POST /api/telemetria/  →  deduplicação UUID  →  banco
                                                                    ↓
                                                          IA agenda em background
                                                                    ↓
dashboard  ←  GET /api/leituras/ultimas/  ←  status_risco calculado
    ↓
/detalhes  →  GET /api/prescricoes/lista/  →  modal com recomendação
    ↓
/mapa      →  GET /api/maquinas/posicao/   →  pins por status (fallback demo)
    ↓
/dashboard →  GET /api/relatorio/exportar/ →  download CSV
```

---

## Perguntas Frequentes da Banca

**Por que UUID e não ID sequencial?**
O ESP32 gera o UUID antes de enviar. Se a rede cair e ele reenviar, o servidor detecta a duplicata pelo UUID e ignora — sem dado duplicado no banco. O `seq_id` existe para consultas ordenadas por humanos.

**O que acontece se o broker MQTT cair?**
O simulador detecta `Connection refused` e entra em modo fallback HTTP, enviando direto para `/api/telemetria/`. Demonstrado em `scripts/simular_mqtt.py` com `MQTT_PORT=1884 DEMO_CYCLES=1`.

**Como a IA classifica o risco?**
Isolation Forest para anomalias + Random Forest para probabilidade de falha + regras de threshold (temperatura > 85°C, vibração > 0.8). O resultado é determinístico para os mesmos dados — não é caixa-preta.

**O frontend funciona sem internet?**
O Service Worker faz cache das páginas e enfileira telemetria offline via `QUEUE_TELEMETRY`. Quando a conexão volta, o worker drena a fila automaticamente.
