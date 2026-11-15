# S4-T5 · Reavaliação e resultado verificável

## Implementado

- `Reevaluation` vincula WorkOrder, Decision e máquina, preservando regra, versão, janelas, métricas, IDs das leituras, origem e motivo de insuficiência.
- `services/reevaluation.py` expõe `avaliar(antes, depois, regra)`. A regra precisa declarar limiar, direção, quantidade mínima, janelas e percentuais de cessação/persistência.
- Leituras são ordenadas por `timestamp`/`event_time`, deduplicadas por ID, filtradas por fonte temporal confiável e não misturam `data_origin`.
- Ausência de política ou evidência retorna `DADOS_INSUFICIENTES`.
- `python manage.py reavaliar_decisoes` processa OS concluídas, é repetível e não interrompe todas as OS por uma falha.
- A execução de uma Decision fecha a WorkOrder com `concluida_em`; o relato continua em `outcome_texto`.
- A central exibe `Resultado informado` e `Verificado por telemetria` em blocos separados.

## Verificação

- VERIFICADO: três cenários da função pura e leituras fora de ordem em `api_tcc/tests/test_s4_t4_t5.py`.
- VERIFICADO: migration aplicada localmente (`0043`), `manage.py check` e `makemigrations --check --dry-run`.
- VERIFICADO: 25 testes backend focados/regressivos verdes (`S4-T4/T5`, `S4-T2/T3`, `test_decisions`).
- VERIFICADO: `npm run lint` e `npm run build`.
- PENDENTE: captura visual das três situações e validação com telemetria de campo. O resultado não afirma causalidade nem eficácia da intervenção.

## Política

Os parâmetros vivem em `OrganizationPolicy.reevaluation_policy`. Sem configuração explícita, o sistema não inventa janela ou limiar: registra dados insuficientes.
