# FieldNode - Inventário Técnico de Estado

*Auditoria gerada na Semana 1 do Roadmap Técnico.*

| Componente | Estado (🟢🟡🔴⚪) | Evidência do Problema (Descoberta Técnica) | Prioridade |
| :--- | :---: | :--- | :--- |
| Ingestão HTTP | 🟢 | `IngestaoTelemetriaView` expõe `POST /api/telemetria/`, valida `X-API-Key`, aplica `IngestaoThrottle` só em POST e chama `registrar_leitura()`. Teste via `Django Client` confirmou: primeiro POST retornou 201 com `status: ok`; sem API key retornou 401. | Crítica |
| Ingestão MQTT | 🟡 | Existe comando `api_tcc/management/commands/mqtt_listen.py`, importa `paho.mqtt.client`, escuta `fieldnode/#` e reutiliza `registrar_leitura()`. Porém `BROKER_HOST = localhost` e `BROKER_PORT = 1883` estão hardcoded; `mosquitto`/`mosquitto_pub` não foram encontrados no ambiente local, então não houve teste de broker real. | Crítica |
| Deduplicação UUID | 🟢 | `registrar_leitura()` consulta UUID existente antes de salvar e trata `IntegrityError` como corrida de duplicata quando o UUID já existe. Teste via `Django Client`: mesmo UUID enviado 2 vezes retornou 201 depois 200 `duplicata ignorada`; contagem no banco para o UUID ficou em 1. | Crítica |
| Dashboard (gráficos) | 🟡 | O fluxo de detalhe protege 0 leituras com `EmptyState`, e `HistoryChart` também retorna "Sem leituras no período" se o array vier vazio. Com 1 leitura, o ponto é centralizado. Com 100 leituras, não deve crashar, mas `xTicks` usa o índice do array filtrado em vez do índice original, então os marcadores do eixo X ficam tecnicamente incorretos. | Crítica |
| Botão voltar (prescrição) | 🔴 | Crash confirmado por stale state. Requer Ctrl+Shift+R. Congelado nesta semana. | Crítica |
| Mapa (GPS) | 🔴 | Tela preta confirmada. O componente usa `dynamic(..., { ssr: false })`, importa Leaflet no cliente e tenta fallback demo, mas a falha visual permanece reportada. Também há dependência externa de tile/CSS via `unpkg` e `tile.openstreetmap.org`, pontos frágeis para renderização local. Congelado nesta semana. | Alta |
| Relatório/Exportação | 🟡 | Há exportação CSV em `RelatorioExportarView` com BOM, delimitador `;`, filtros de período e dados detalhados. Ainda é CSV simples, sem formatação visual de planilha, estilos, XLSX ou layout pronto para apresentação. | Alta |
| Ícone aba relatórios | 🔴 | `navItems` inclui `{ icon: "report" }`, mas o dicionário `icons` define apenas `grid`, `map`, `machine` e `users`. Resultado: a aba Relatórios renderiza sem ícone. | Baixa |
| Pipeline de IA | 🟡 | `api_tcc/ia/pipeline.py` inicia `Thread(..., daemon=True)` no import e o worker possui `try/except Exception` por job, evitando morte por erro comum. Porém não há watchdog, healthcheck, restart do worker, persistência da fila ou controle de ciclo de vida fora do processo Django. | Alta |
| Autenticação da API | 🟡 | Ingestão HTTP usa API key própria via header `X-API-Key`, mas viewsets principais não declaram `permission_classes` e o `REST_FRAMEWORK` não define permissão padrão. Há views antigas de relatório com `IsAuthenticated`, enquanto endpoints de ingestão/relatório/prescrição em `views_ingestao.py` ficam com política própria ou pública. Mistura real de modelos de autenticação. | Média |

## Legenda

- 🟢 Funcional e estável.
- 🟡 Funciona com ressalvas, dívida técnica ou UX ruim.
- 🔴 Quebrado, crashando ou não utilizável.
- ⚪ Não implementado / Fora de escopo atual.

## Congelamento da Semana 1

Qualquer item marcado ⚪ ou fora do fluxo principal `telemetria -> anomalia -> risco -> prescrição -> relatório` fica congelado. Nesta auditoria não foi identificado item ⚪ entre os 10 componentes listados, mas os itens 🔴 reportados ficam registrados como problema conhecido, sem correção neste bloco.

## Verificações Executadas

- `.\venv\Scripts\python.exe manage.py test api_tcc.tests.test_telemetria --verbosity 2`: 3 testes executados e aprovados para ingestão válida, payload inválido e UUID duplicado.
- `Django Client` manual com `HTTP_HOST=127.0.0.1`: POST válido retornou 201, POST duplicado retornou 200, POST sem API key retornou 401 e o banco manteve 1 registro para o UUID auditado.
- `python` global não possui Django instalado; a validação foi repetida corretamente usando `venv`.
- `mosquitto` e `mosquitto_pub` não foram encontrados no PATH local, então MQTT ficou validado por inspeção de código e import de `paho`, não por broker real.
- Tentativa inicial com `Django Client` usando host padrão `testserver` retornou `DisallowedHost`, coerente com `ALLOWED_HOSTS` fechado para `127.0.0.1,localhost`.

## Critério de Aceite da Semana 1

- Repositório sem segredo no histórico: não verificado neste bloco.
- CORS fechado: configuração usa `CORS_ALLOWED_ORIGINS` por env com default restrito a localhost/127.0.0.1 nas portas 3000 e 3005.
- Rate limit ativo: ingestão usa `IngestaoThrottle` e `DEFAULT_THROTTLE_RATES['ingestao'] = '120/minute'`.
- Tabela de inventário preenchida: concluído neste arquivo.
- Compartilhar com Vinícius e Giovana: pendente de ação humana fora do repositório.
