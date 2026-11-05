# Auditoria de fechamento S1-T1 / S1-T2

Data da verificação: 2026-11-05. Esta auditoria não inicia S2 e não altera
firmware, roadmap ou claims.

## Resultado executivo

- **S1-T1:** paridade v1 verificada entre backend, borda e TypeScript.
- **S1-T1:** zero divergências em 1.702 pontos; comparadores funcionais
  encontrados foram ligados ao contrato.
- **S1-T1:** grep literal tem testes, seeds, dados de UI e menções históricas;
  não foi encontrado outro limiar funcional de severidade fora do contrato.
- **S1-T2:** unidade e rejeição de `g` verificadas por teste; unidade do gráfico
  deriva do artefato do contrato.
- **S1-T2:** aceite visual **bloqueado** por
  `ERR_MEMORY_ALLOCATION_FAILED`; nenhuma imagem foi criada.
- **Semana 1:** não fechada. Firmware v1 e campos de tempo/qualidade não foram
  encontrados; ACK do Service Worker não valida hash/sequência; não há
  comparação da latência p95 antes/depois.

## Paridade

Comando reproduzível: `python scripts/check_contract_parity.py`.

```text
temperatura: 1501 pontos; divergências: 0
vibracao: 201 pontos; divergências: 0
total: 1702 pontos; divergências: 0
```

O script executa `classify()` do backend, `classify_priority()` da borda e
`statusOf()` real do frontend, compilado em memória pelo TypeScript instalado.
Varreu temperatura de 0 a 150, passo 0,1, e vibração de 0 a 10, passo 0,05.
A prioridade foi comparada com evidência boa e dado não atrasado.

Testes complementares cobrem 84,9999 °C, 85 °C e 85,0001 °C; crítico com
evidência boa, fraca ou desconhecida, atrasado ou não; atenção fraca; leitura
normal atrasada; e rejeição de `vibracao_unit="g"`. Crítico permanece classe A.

## Greps e classificação

Comando executado literalmente:

```text
git grep -nE '\b(85|95|110)\b' -- '*.py' '*.ts' '*.tsx'
```

O resultado não é vazio. As ocorrências foram classificadas por finalidade:

- Contrato/artefato: `frontend-next/src/lib/metricThresholds.ts:13` contém 85 °C.
  O arquivo é gerado a partir do JSON; ocorrência esperada.
- Testes: `api_tcc/tests/test_contract_v1.py`, `test_deteccao_multivariada.py`,
  `test_data_health.py`, `test_demo_mode.py`, `test_eventos.py`,
  `test_identity_contract.py`, `test_integration.py`, `test_permissions.py`,
  `test_telemetria.py` e `simulators/test_edge_client.py` cobrem fixtures,
  fronteiras e asserts.
- Seeds/simulação: `api_tcc/management/commands/criar_prescricoes_teste.py`,
  `api_tcc/management/commands/popular_tudo.py`, `scripts/seed_data.py` e
  `scripts/simular_mqtt.py` contêm valores de amostra, não comparadores.
- Amostras fracionárias de vibração não foram convertidas por suposição.
- Exemplos/histórico: `api_tcc/management/commands/mqtt_listen.py`,
  `api_tcc/services/telemetria.py` e `api_tcc/tests/test_integration.py` contêm
  payloads de exemplo e explicações de parsing, não regras de limiar.
- Números sem relação com severidade: CSS `scale-95`, opacidade `0.95`,
  `z-[110]`, `brightness-110`; `ReportPreview.tsx:33` usa 85 para eficiência;
  `scripts/teste_carga.py` calcula p95. Não foram alterados para maquiar o grep.

Correções funcionais: `api_tcc/ia/pipeline.py` consulta `classify()` para
temperatura e vibração; `scripts/simular_mqtt.py` usa o contrato no rótulo;
o relatório Excel obtém o crítico por `metric_definition()`. A borda encaminha
`evidence_quality` e `atrasado` a `transmission_class()`, preservando defaults
compatíveis quando os campos não vêm no payload.

Busca por unidade literal no frontend:

```text
git grep -nE "['\"]g['\"]" -- frontend-next/src/lib/**
sem ocorrências
```

O rótulo de vibração em `frontend-next/src/lib/metrics.ts` vem de
`METRIC_THRESHOLDS.vibracao.unit`. Type-check e lint passaram; não houve captura.

## Vibração e migration

`LeituraTelemetria.vibracao_unit` tem default `indice_0_10`. A migration
`0027_leituratelemetria_vibracao_unit.py` adiciona somente esse campo. Não
adiciona `boot_id`, `time_source`, `clock_skew_ms`, `evidence_quality` ou
`needs_verification`; esses campos não foram confirmados no modelo atual.

`SeverityContractV1Tests.test_vibration_unit_is_not_silently_converted` passou:
`vibracao_unit="g"` falha sem conversão. `frontend-next/src/lib` não contém a
unidade literal `'g'`.

## Estado das demais entregas S1

- **ACK: parcial.** A API devolve message id, device, sequência, hash e cursor.
- O cliente edge valida ACK/hash e testa hash divergente.
- O Service Worker aceita qualquer 2xx e apaga o item sem validar hash/sequência.
- **Service Worker por item: implementado, sem teste de navegador.** IndexedDB
  atribui `localId`; sincroniza e remove os itens individualmente.
- **Views de ingestão: implementadas** em `api_tcc/api/views_ingestao.py`.
  O system check Django passou.
- **Contrato cruzado: comprovado.** 1.702 pontos, zero divergências.
- **Firmware/S1-T8: bloqueado externamente.** Nenhum arquivo foi encontrado;
  a documentação mantém hardware real no contrato v0.
- **Latência p95: parcial.** `scripts/teste_carga.py` calcula p50/p95, mas não há
  medição antes/depois que comprove melhoria.
- **Campos de tempo/qualidade: ausentes.** Migration 0027 só adiciona
  `vibracao_unit`; os demais campos não foram confirmados.

## Comandos e resultados

- `manage.py test ...`: 16 testes passaram; warnings de versão do sklearn
  permanecem.
- `manage.py test api_tcc.tests.test_contract_v1`: 4 testes passaram após
  incluir fronteiras e casos explícitos.
- `scripts/check_contract_parity.py`: 1.702 pontos; zero divergências.
- `scripts/gen_contracts.py --check`: passou; TypeScript sincronizado.
- `manage.py check`: sem problemas.
- `manage.py makemigrations --check --dry-run`: nenhuma alteração pendente.
- `npm run type-check` e `npm run lint`: passaram.
- `npm run dev -- --hostname 127.0.0.1 --port 3000`: bloqueado por
  `ERR_MEMORY_ALLOCATION_FAILED`; nenhuma captura foi produzida.

## Arquivos alterados nesta auditoria

- `api_tcc/ia/pipeline.py`
- `api_tcc/api/views_relatorio.py`
- `api_tcc/tests/test_deteccao_multivariada.py`
- `api_tcc/tests/test_contract_v1.py`
- `simulators/edge_client.py`
- `simulators/test_edge_client.py`
- `scripts/simular_mqtt.py`
- `scripts/check_contract_parity.py`
- `frontend-next/src/lib/metrics.ts`
- `frontend-next/src/components/MetricTrendChart.tsx`
- `docs/evidence/s1/S1-CLOSURE_AUDIT.md`

O worktree já continha alterações S1 e o arquivo não rastreado
`FIELDNODE_LEVIATA_ROADMAP_V5.md`; foram preservados. Nada foi staged ou
commitado. A captura visual permanece pendente; a Semana 1 continua aberta.

## Atualização de continuidade S1 (2026-11-05)

Este complemento supersede os estados de ACK, tempo e qualidade acima. Não
inicia S2 e não altera o roadmap.

- **S1-T3:** prioridade `P = S × I × U`; Trust Score não multiplica o score.
  `Event.evidence_quality` e `needs_verification` são persistidos e serializados.
  Hora `unsynced` reduz Trust Score em 0,25 e registra fator em Data Health.
- **S1-T4/T6:** ACK exige status, identidade, sequência, hash e cursor.
  Divergência não remove item; conflitos recebem HTTP 409 e DLQ `SYNC`.
  SW tem estados por item, retry/backoff, bloqueio de autenticação e reprocesso.
- **Hash:** exclui `id` interno; `(device_id, message_id)` segue como identidade.
  Backend, edge e SW passaram pelo mesmo vetor SHA-256. Hashes legados são
  aceitos quando coincidem exatamente; filas antigas recalculam o hash do payload.
- **S1-T5:** migration `0029_telemetry_time_contract.py` adiciona
  `boot_id`, `uptime_ms`, `time_source`, `clock_skew_ms` e âncora única por
  dispositivo/boot. Leituras `unsynced` sem hora recebem horário provisório;
  uma âncora confiável do mesmo boot reconstrói o event time. Testes cobrem
  atraso de seis horas, isolamento entre boots e Trust Score baixo.
- **Clock skew:** permanece nulo sem medição explícita de gateway. O servidor
  não confunde latência de entrega com desvio do relógio. A regra está em
  `docs/CONTRATO_TELEMETRIA_V1.md`.
- **ACK normativo:** `docs/SYNC_PROTOCOL_V1.md` descreve at-least-once,
  duplicate/conflict, remoção da outbox e compatibilidade com firmware v0.

Validação consolidada após as correções: 90 testes Django passaram, incluindo
contrato, eventos, trust, tempo, ingestão/ACK, identidade e edge; 13 testes Node
do Service Worker passaram; type-check e lint do frontend passaram. A migration
0029 está sincronizada com os modelos. O hash lógico comum foi verificado no
backend, edge e SW, inclusive replay com UUID interno novo e hash legado.

## Pendências ainda abertas

- **S1-T2 visual:** Next.js/Turbopack iniciou, mas a rota de telemetria pelo
  proxy oscilou entre 503 e abortos, apesar da API temporária responder direto.
  Não foi salva captura incompleta. A unidade está implementada, mas a evidência
  de UI continua bloqueando o aceite visual.
- **Firmware/S1-T8:** nenhum firmware está neste checkout; hardware real continua
  no contrato v0. Não há paridade de firmware comprovada.
- **S1-T7:** `views_ingestao.py` continua contendo várias views; a divisão prevista
  não foi implementada nesta rodada.
- **p95:** `scripts/teste_carga.py` mede uma execução, sem baseline comparável
  anterior à separação. Nenhuma melhoria foi afirmada.
- **Semana 1:** permanece aberta. Nenhum arquivo foi staged ou commitado.
