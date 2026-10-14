# Teste de pressão: investidor e CTO

Documento S10-T3. Referência: 14/10/2026.

A regra deste roteiro é separar código existente, evidência executada, hipótese e trabalho futuro. A resposta oral deve ser curta e verificável.

## 1. Perguntas e respostas

### 1. Qual é o diferencial do FieldNode?

**Resposta oral curta:** O FieldNode junta ingestão idempotente, qualidade da telemetria, eventos priorizados e decisão revisável por uma pessoa. O diferencial, neste estágio, é a integração rastreável desse fluxo em um protótipo offline-first.

**O que podemos provar:** `api_tcc/services/telemetria.py`, `eventos.py`, `data_health.py`, `decisions.py` e os artefatos em `artifacts/s10/`.

**Limite da afirmação:** É hipótese de diferenciação, não vantagem comprovada por clientes ou comparação controlada.

**Aprofundamento provável:** O que impede cópia? **Resposta:** Hoje, nada completamente. Uma vantagem defensável dependeria de dados, integrações e uso real acumulado.

### 2. Por que isso não é apenas um dashboard?

**Resposta oral curta:** O dashboard é a superfície de consulta. O núcleo recebe, valida, deduplica, calcula sinais de qualidade, cria eventos e registra decisão com aprovação e resultado.

**O que podemos provar:** `scripts/s10_closed_loop_demo.py`, `/api/telemetria/`, `/api/prescricoes/<maquina_id>/` e `docs/S10_EXECUCOES.md`.

**Limite da afirmação:** O ciclo termina em registro e decisão humana; não há manutenção automática.

**Aprofundamento provável:** Se ninguém agir, o que foi feito? **Resposta:** Foi criado um registro priorizado e uma recomendação pendente, com contexto preservado.

### 3. Por que não usar a solução OEM?

**Resposta oral curta:** A hipótese é oferecer uma visão operacional que atravesse fabricantes e preserve a trilha de decisão. Ainda não demonstramos que isso é melhor para um comprador específico.

**O que podemos provar:** modelo de telemetria canônica, migration `0024` e `docs/S9-T2_UNIVERSAL_TELEMETRY_MODEL.md`.

**Limite da afirmação:** Não há benchmark com OEMs nem integração de campo multi-marca comprovada.

**Aprofundamento provável:** Compararam custo e cobertura? **Resposta:** Não neste ciclo. É pesquisa futura, não resultado atual.

### 4. Onde está a propriedade tecnológica?

**Resposta oral curta:** Está na implementação integrada de identidade, outbox local, ingestão idempotente, score, eventos, decisões e adaptadores. Não está em patente nem em algoritmo secreto.

**O que podemos provar:** migrations `0014`, `0015`, `0016`, `0017`, `0018`, `0019`, `0023` e `0024`, além dos testes correspondentes.

**Limite da afirmação:** Não houve análise de patente ou liberdade de operação.

**Aprofundamento provável:** O que é mais difícil de substituir? **Resposta:** A coerência entre identidade, contexto do evento e histórico da decisão; ainda é código de protótipo.

### 5. Onde está o moat?

**Resposta oral curta:** Ainda não existe um moat comprovado. O caminho possível seria acumular dados confiáveis, integrações e histórico de decisões úteis.

**O que podemos provar:** O sistema registra `Event`, `Decision`, outcome, origem e relações.

**Limite da afirmação:** Não há clientes, retenção, dados proprietários de campo ou custo de troca medido.

**Aprofundamento provável:** Por que investir? **Resposta:** Para testar a hipótese com uso real, não para fingir que a defesa já existe.

### 6. Os dados são reais?

**Resposta oral curta:** Os dados dos ensaios são gerados por simulador e persistidos de verdade no MySQL do Compose. Eles comprovam o fluxo de software, não uma usina ou sensor físico.

**O que podemos provar:** JSONs em `artifacts/s10/`, EdgeClient e consultas de banco do executor oficial.

**Limite da afirmação:** Não há série de campo, calibração, instalação ou operação prolongada comprovada.

**Aprofundamento provável:** O que a demo mede? **Resposta:** Recebimento, persistência, relações, priorização e aprovação de uma leitura simulada.

### 7. A IA é defensável?

**Resposta oral curta:** A IA não é apresentada como prova de falha mecânica. Há regras determinísticas, Isolation Forest, Random Forest auxiliar e uma PoC de LLM com aprovação humana.

**O que podemos provar:** `api_tcc/ia/`, `services/agentic.py`, prompt versionado, `test_agentic.py` e `docs/HONESTIDADE_METODOLOGICA_ML.md`.

**Limite da afirmação:** Não há precisão, calibração probabilística ou conjunto de campo suficientes para afirmar previsão validada.

**Aprofundamento provável:** Score é probabilidade? **Resposta:** Não. É score operacional; calibração exige dados rotulados e avaliação fora da amostra.

### 8. Como funciona sem internet?

**Resposta oral curta:** O cliente grava primeiro em SQLite e tenta sincronizar depois. O cursor só avança após confirmação, e a chave composta impede duplicação no reenvio.

**O que podemos provar:** `simulators/edge_client.py`, Data Mule, testes e `docs/PROTOCOLO_TESTE_RESILIENCIA_OFFLINE.md`.

**Limite da afirmação:** É resiliência simulada de bancada, não 30 dias em hardware ou operação rural contínua.

**Aprofundamento provável:** E fora de ordem? **Resposta:** O contrato preserva sequência e cursor; não devemos prometer ordenação física universal sem ensaio de campo.

### 9. Como escala?

**Resposta oral curta:** API, banco, worker MQTT e frontend estão separados e reproduzidos por Compose. Isso é base de implantação, não medição de escala.

**O que podemos provar:** `docker-compose.yml`, health checks, Gunicorn e worker MQTT.

**Limite da afirmação:** Não há carga representativa, SLO, alta disponibilidade ou multi-tenant funcional medidos.

**Aprofundamento provável:** Quantas máquinas suporta? **Resposta:** Não há número defensável; o próximo passo é medir ingestão, latência, banco e filas.

### 10. Como protege dados?

**Resposta oral curta:** A ingestão exige `X-API-Key`, decisões usam autenticação e autorização, o modo demo filtra máquinas de demonstração e segredos não devem ir ao browser.

**O que podemos provar:** `setup/settings.py`, `api_tcc/permissions.py`, testes de auth, permissões e demo.

**Limite da afirmação:** Não há auditoria externa, identidade de produção, isolamento multi-tenant completo ou rotação demonstrada.

**Aprofundamento provável:** E se a chave vazar? **Resposta:** Deve ser revogada e substituída fora do código. Valores históricos devem ser tratados como potencialmente comprometidos.

### 11. Como lida com múltiplos fabricantes?

**Resposta oral curta:** Há telemetria bruta e canônica, com mapeamento por fabricante. Parâmetros desconhecidos são preservados como não suportados.

**O que podemos provar:** migration `0024`, `services/normalizacao.py`, testes e `docs/S9-T2_UNIVERSAL_TELEMETRY_MODEL.md`.

**Limite da afirmação:** Os adaptadores são simulados; Trust Score e Event Engine ainda consomem o modelo legado.

**Aprofundamento provável:** Interoperabilidade está pronta? **Resposta:** A camada e os testes existem; integração total e equipamentos reais continuam pendentes.

### 12. Como prova que as decisões estão corretas?

**Resposta oral curta:** Não prova correção só porque criou uma decisão. Registra justificativa, aprovação e outcome; a correção precisa ser comparada com resultado operacional real.

**O que podemos provar:** Relações `Event`-`Decision`, campos de outcome e aprovação autenticada nos três ensaios.

**Limite da afirmação:** Os outcomes dos ensaios são documentais; não há taxa de acerto validada.

**Aprofundamento provável:** Qual evidência faltaria? **Resposta:** Resultado definido, ação registrada, confirmação independente e análise de acertos e erros em campo.

### 13. O que acontece quando o sistema erra?

**Resposta oral curta:** A recomendação exige aprovação humana e pode ser rejeitada. Falhas da etapa agentiva podem ir para a DLQ, e o histórico preserva decisão e resultado informado.

**O que podemos provar:** `services/dlq.py`, `test_dlq.py`, endpoints de decisão e testes de autorização.

**Limite da afirmação:** Não há programa completo de incidentes, rollback físico ou garantia de detectar todo erro.

**Aprofundamento provável:** Como lidar com falso alerta? **Resposta:** Usar contexto, explicação, revisão humana e registro; a taxa ainda precisa ser medida.

### 14. Como fecha o ciclo operacional?

**Resposta oral curta:** O ciclo de software é leitura, validação, persistência, Trust Score, Event, Decision pendente, revisão humana e outcome. Nos ensaios, o estado final foi `APROVADA`; nenhuma intervenção mecânica ocorreu.

**O que podemos provar:** `scripts/s10_run_official_trials.py`, `docs/S10_EXECUCOES.md`, screenshots e vídeo do terceiro ensaio.

**Limite da afirmação:** O ciclo físico não está fechado. `APROVADA` não significa `EXECUTADA`.

**Aprofundamento provável:** Controla a colheitadeira? **Resposta:** Não; produz e registra recomendação.

### 15. Qual parte já foi validada em campo?

**Resposta oral curta:** Nenhuma parte foi validada em campo no sentido de instalação e operação em máquina real. Validamos software local e Compose com simulador.

**O que podemos provar:** `docs/REPOSICIONAMENTO_ESCOPO_HARDWARE.md`, `docs/S10_EXECUCOES.md` e `docs/RESULTADOS_VALIDACAO_COMERCIAL.md`.

**Limite da afirmação:** Não há usina, ESP32 instalado, rádio, armazenamento prolongado ou comprador usando o produto.

**Aprofundamento provável:** Por que apresentar? **Resposta:** Para demonstrar a fundação de software e seus limites, sem vender simulação como campo.

## 2. Ensaio oral

### Nível 1: fundamentos

Perguntas sobre problema, diferencial, funcionamento e dado simulado. Cobrir fluxo e escopo. Evitar dizer que alerta é falha ou que aprovação é execução. Referências: perguntas 1, 2 e 6.

### Nível 2: pressão técnica

Perguntas sobre duplicação, offline, score, segurança, persistência, DLQ e telemetria canônica. Citar testes e reconhecer a lacuna de integração. Referências: 7 a 11 e 13.

### Nível 3: perguntas difíceis

Perguntas sobre clientes, campo, moat, taxa de acerto e decisão errada. A resposta correta pode ser “ainda não medimos”. Referências: 5, 12 e 15.

### Protocolo

1. Distribuir perguntas entre os integrantes.
2. Responder sem ler, em até 90 segundos.
3. Fazer aprofundamento após cada resposta.
4. Pedir que outro integrante marque afirmações sem evidência.
5. Registrar dúvidas e divergências.
6. Corrigir o documento após conferir código ou artefato.
7. Repetir as respostas mais fracas e cronometrar o roteiro.

**Estado:** roteiro preparado, ensaio humano não comprovado. Os vídeos em `artifacts/s10/videos/` comprovam demonstração de software, não participação dos integrantes.

## 3. Referências

- `docs/AUDITORIA_FINAL_S10.md`
- `docs/S10_EXECUCOES.md`
- `docs/S10_CONSOLIDADO.md`
- `docs/ROTEIRO_DEMO_BANCA.md`
- `docs/HONESTIDADE_METODOLOGICA_ML.md`
- `docs/RESULTADOS_VALIDACAO_COMERCIAL.md`
- `docs/REPOSICIONAMENTO_ESCOPO_HARDWARE.md`
