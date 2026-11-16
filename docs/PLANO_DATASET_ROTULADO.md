# S5-T9 · Plano de dataset rotulado

Este plano materializa exemplos operacionais concluídos. Ele não treina Random Forest e não transforma correlação em causalidade.

## Regras decision-outcome-v1

| Condição verificável | Rótulo | Fonte |
|---|---|---|
| Decision.EXECUTADA + Reevaluation.SINTOMA_CESSOU | acao_associada_resolucao | ambos |
| Decision.REJEITADA + motivo_rejeicao=FALSO_ALARME | negativo | humano |
| evento CRITICO posterior em até 24h, sem WorkOrder | positivo | telemetria |

O primeiro caso registra associação temporal. Não prova que a ação preveniu falha. Rejeição por outro motivo, sintoma persistente, dados insuficientes, janelas contraditórias e ausência de registro ficam fora da exportação elegível. Ausência de registro não prova ausência de ação.

## Modelo e exportação

LabeledWindow guarda máquina, organização, decisão, janela, features existentes, rótulo, categoria, fonte, justificativa e versão da regra. A restrição (decision, regra_versao) impede duplicação silenciosa.

    python manage.py exportar_dataset_rotulado --output docs/evidence/s5/S5-T9_dataset_exemplo.csv

O comando usa UTF-8, separador ;, ordenação por máquina, início da janela e UUID. Não sobrescreve arquivo existente sem --overwrite. O cabeçalho é:

example_id;machine;decision_id;window_start;window_end;rule_version;feature_temperatura;feature_vibracao;feature_rpm;feature_evidence_quality;feature_reevaluation_before_pct;feature_reevaluation_after_pct;feature_followup_event_type;feature_followup_severity;label;label_category;label_source;justification;eligible

Features ausentes permanecem vazias. O exportador não inclui observações livres, credenciais ou dados pessoais.

## Critério D-03

Não iniciar avaliação de Random Forest antes de pelo menos 200 decisões com desfecho elegível. Esse número é uma porta de viabilidade, não garantia estatística. Ainda são obrigatórios equilíbrio mínimo por classe, separação por máquina/período, controle de vazamento temporal e revisão da origem dos rótulos. Nenhum treino é implementado nesta tarefa.

## Limitações

Rótulo fraco é aproximação operacional. Um evento crítico posterior pode ter outra causa; uma reavaliação depende da política e da qualidade temporal configuradas. A amostra sintética de evidência não representa 200 decisões reais.
