# S5-T4 - Critérios de treino e baseline de grupo

## Status

IMPLEMENTADO EM SOFTWARE, COM PARÂMETROS INICIAIS PROVISÓRIOS.

## Política

`pode_treinar(machine)` é a decisão central. Exige cumulativamente:

- pelo menos 100 leituras elegíveis;
- 8 horas de cobertura temporal;
- pelo menos dois regimes diferentes, sem contar `desconhecido`;
- trust médio mínimo de 0,8;
- nenhum evento crítico aberto na janela;
- leitura de treino no regime `trabalhando` com `evidence_quality=boa`.

Os valores 100 e 8 horas são parâmetros de bancada. Não há distribuição de
campo suficiente neste repositório para tratá-los como valores científicos;
devem ser recalibrados com dados rotulados e uma janela de validação separada.

## Fallback e API

`selecionar_fonte_modelo` procura, nesta ordem, modelo individual elegível,
baseline de grupo do mesmo `Modelo` e da mesma organização, baseline estatístico
ou estado `none`. A resposta de `/api/machines/<id>/health/` agora expõe
`model_health`, com leituras, cobertura, regimes, trust, evento crítico, origem
do modelo e motivos de recusa.

## Champion/challenger

`aprovar_challenger` exige métrica F1 definida, validação disponível e melhora
estrita sobre o champion. Empates, métricas ausentes e validação insuficiente
mantêm o champion. A troca física/atômica do artefato ainda depende do fluxo de
persistência do registry e não é declarada como validação operacional.

## Testes

Os testes adicionados cobrem recusa por falta de dados, limites de regime e
rejeição de challenger inferior ou sem métrica. O teste legado que cria cem
leituras sem trust, regime e qualidade explícitos passa a ser corretamente
recusado pela nova política e precisa ser migrado para o contrato S5-T4.

## Pendências

Não há dados de campo, rótulos confiáveis ou política autorizada de
compartilhamento entre organizações para validar um baseline de grupo. O
fallback estatístico continua inconclusivo quando não há evidência mínima.
