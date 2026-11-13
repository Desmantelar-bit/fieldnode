# S3-T4 · Trust Score com explicação legível

**Status: parcial.** O backend agora expõe códigos estáveis para motivos realmente gravados e a tela de detalhes apresenta o Trust agregado junto de uma explicação acessível. Cards de máquinas e o mapa ainda não foram integrados.

## Auditoria do cálculo

- `calcular_trust_score` parte de 1,0 e aplica confiança temporal, intervalo temporal, repetição de valores, proximidade de limite e continuidade/mudança abrupta; o resultado é limitado a 0..1.
- A confiança temporal pode reduzir pela diferença `1 - event_time_confidence`; relógio não sincronizado é registrado quando `time_source=unsynced`.
- Os outros motivos refletem regras do serviço `api_tcc/services/data_health.py`. Continuidade suave pode somar 0,04; mudança abrupta reduz 0,08; os limites e demais penalidades estão definidos no serviço.
- `MachineDataHealth.trust_score_medio` é EMA (alpha 0,2). `LeituraTelemetria.trust_factors` guarda motivos como strings, não contribuições individuais. Logo, não é possível atribuir pesos rastreáveis à média existente sem mudar seu cálculo/armazenamento.
- O endpoint retorna o score agregado e `fatores_ultima_leitura`, isto é, condições presentes na leitura mais recente. Cada fator usa `peso: null`; isso comunica explicitamente que sua contribuição individual na EMA não é rastreável.

## Alterações

- `/api/machines/<id>/health/` serializa motivos reais para códigos estáveis, detalhe original e peso nulo. Score ausente continua `null`.
- `frontend-next/src/lib/trustFactors.ts` centraliza os textos em português e fornece fallback `Outro fator (código)`.
- `TrustBadge` apresenta escala 0–100 e usa `<details>/<summary>` para explicação acessível por teclado e toque. Informa que fatores são da leitura mais recente e não uma decomposição do Trust agregado.
- A tela `/detalhes` consulta o endpoint de saúde e mostra o badge.
- Teste de contrato percorre todos os códigos do dicionário e verifica título/descrição não vazios e fallback desconhecido.

## Fatores mapeados

`RELOGIO_NAO_CONFIAVEL`, `GAP_TEMPORAL`, `TIMESTAMP_FORA_DE_ORDEM`, `TIMESTAMP_INDISPONIVEL`, `VALORES_REPETIDOS`, `PROXIMO_LIMITE_FISICO`, `SALTO_ABRUPTO`, `CONTINUIDADE_SUAVE` e `PRIMEIRA_LEITURA`. Um motivo não reconhecido pelo backend vira `FATOR_NAO_CLASSIFICADO` e preserva o texto original em detalhe.

## Validação, limites e pendências

- Teste frontend de cobertura do dicionário e código desconhecido: **VERIFICADO** (incluído em `npm run test:contracts`, 3 testes aprovados).
- `npm run type-check`, `npm run lint`, `python manage.py check`, `git diff --check` e 22 testes focados de saúde/faixa: **VERIFICADO**.
- Uma execução backend mais ampla incluiu 1 falha no teste `test_leitura_com_temperatura_critica_gera_event_temp_alta`, que esperava `evidence_quality="boa"` e recebeu `insuficiente`. A regra S1-T3 foi preservada; a divergência permanece para investigação.
- Capturas desktop/mobile: **NÃO GERADAS**.
- Integração no `TelemetryMachineCard` e no mapa: **PENDENTE**. A leitura agregada das posições do mapa não carrega Trust e buscar health por máquina no carregamento criaria N+1; exige ampliar a resposta existente com dados agregados.
- A explicação não atribui pesos à EMA porque a persistência atual não conserva essa decomposição. Ajustar persistência e recalcular histórico exigiria uma decisão explícita de compatibilidade; não foi inventado peso.
- `docs/CLAIMS_VS_CODE.md` não existe neste checkout.
