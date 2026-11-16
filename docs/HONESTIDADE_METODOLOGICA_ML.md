# Honestidade metodológica de ML

Este é o documento central para descrever o que o FieldNode implementa e o que as evidências permitem afirmar. `IMPLEMENTADO` significa código executável no repositório; `EXPERIMENTAL` significa avaliação independente, sem adoção automática em produção; `ROADMAP` significa planejamento, não capacidade disponível.

## Arquitetura real

1. **Evidências:** telemetria, timestamp, origem, qualidade e contexto operacional.
2. **Regras determinísticas:** validação, thresholds e classificação de severidade. São triagem, não um modelo aprendido.
3. **Detecção:** Isolation Forest quando há histórico elegível; caso contrário, baseline estatístico ou estado inconclusivo.
4. **Explicação:** o pipeline organiza evidências e pode encaminhar contexto a uma LLM habilitada. A LLM não mede a falha e não substitui autorização humana.
5. **Humano:** decisões podem permanecer pendentes, ser aprovadas ou rejeitadas, e devem manter rastreabilidade.

## Matriz de componentes

| Componente | Tipo | Dados utilizados | Dados de treino | Rótulo | É preditivo? | Confiança científica | Estado |
|---|---|---|---|---|---|---|---|
| Isolation Forest | Detector não supervisionado | temperatura, vibração e rpm por máquina/regime | histórico elegível da máquina, sem rótulo | nenhum | Não | moderada para atipicidade no domínio observado; limitada para falha mecânica | IMPLEMENTADO |
| Baseline estatístico / z-score | Cálculo estatístico | histórico e leitura atual | não há treino supervisionado | nenhum | Não | baixa a moderada, depende da estabilidade do histórico | IMPLEMENTADO |
| Thresholds de severidade | Regra determinística | métricas operacionais e limites configurados | não se aplica | rótulo derivado da regra | Não | depende da justificativa e revisão dos limites | IMPLEMENTADO |
| Classificação de regime | Regra determinística | rpm e velocidade | não se aplica | categoria derivada | Não | operacional, não evidência de falha | IMPLEMENTADO |
| Qualidade de evidência / Trust Score | Cálculo determinístico | completude, recência e coerência da telemetria | não se aplica | score derivado | Não | indicador de qualidade do dado, não de saúde mecânica | IMPLEMENTADO |
| LLM de explicação/prescrição | Modelo generativo condicionado | evidências e contexto registrados | modelo externo; não treinado pelo FieldNode | sem rótulo próprio | Não | não validada como detector ou prognosticador | EXPERIMENTAL |
| Feedback humano | Processo de revisão | evento, decisão e resultado informado | não se aplica | feedback operacional | Não | evidência de processo, não validação causal | IMPLEMENTADO |
| Classificador supervisionado de falha futura | Modelo supervisionado | dataset rotulado independente | não há modelo validado no código atual | não disponível | Não | insuficiente | NÃO IMPLEMENTADO |
| RUL / data de falha | Prognóstico | série de degradação e horizonte temporal | não há dataset ou modelo | não disponível | Não | inexistente | NÃO IMPLEMENTADO |

## Detecção, previsão e prescrição

Detecção de anomalia identifica um padrão estatisticamente incomum frente ao histórico ou baseline. Isso não comprova uma falha mecânica.

Classificação de condição coloca uma leitura em categoria definida por regra ou modelo. No FieldNode, thresholds são regras de triagem e não foram validados como prognóstico.

Previsão de falha estima um evento futuro em horizonte definido. O Isolation Forest não faz isso. Ele produz um **score de anomalia**, não probabilidade de quebra, data de falha ou RUL.

RUL é vida útil restante. Não pode ser calculada a partir de um score de anomalia.

Prescrição operacional é recomendação contextual baseada em evidências, regras e revisão humana. Não converte automaticamente uma anomalia em ordem de manutenção.

## Model card resumido do Isolation Forest

- **Uso pretendido:** sinalizar observações atípicas em telemetria histórica da máquina e apoiar triagem operacional.
- **Entradas:** `temperatura`, `vibracao`, `rpm`; treino por máquina/regime com escala calculada no histórico.
- **Treino:** não supervisionado, `random_state=42` e `contamination=0.05` no detector oficial.
- **Saída:** `anomaly_score`, método, feature contribuinte e estado de detecção.
- **Fora de escopo:** diagnóstico causal, probabilidade de falha, previsão temporal, RUL, garantia de disponibilidade e validação de campo.
- **Limitações:** sensibilidade ao histórico, drift, cobertura de regimes, falsos positivos, falsos negativos e confusão entre mudança operacional legítima e defeito.
- **Evidência:** benchmark sintético em `ml/eval/fixtures/benchmark_v1.json` e avaliação CWRU em `docs/AVALIACAO_ANOMALIA.md`; nenhuma valida transferência para colheitadeiras.

## Vocabulário permitido

Preferir: “score de anomalia”, “padrão atípico”, “detecção não supervisionada”, “triagem por regra”, “evidência”, “decisão pendente”.

Evitar: “probabilidade de quebra”, “previsão de falha”, “data de falha”, “vida útil restante”, “falha confirmada” e “modelo validado em campo”, salvo se avaliação futura sustentar exatamente a afirmação.

Resultados desfavoráveis permanecem visíveis. Ajustar o detector para favorecer os próprios cenários seria overfitting metodológico, não validação.
