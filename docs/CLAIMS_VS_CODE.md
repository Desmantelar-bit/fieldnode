# Claims versus código

| Afirmação | Situação verificável |
|---|---|
| Existe um detector oficial | `api_tcc/services/anomaly_detection.py` concentra o contrato e a execução; o módulo legado apenas encaminha compatibilidade. |
| O sistema usa modelo treinado | Somente quando há artefato compatível e íntegro; caso contrário, o resultado é `baseline_estatistico` ou indisponível. |
| O detector prevê falhas | Não sustentado pelo código ou pelo benchmark sintético. |
| O benchmark valida campo | Não. O relatório identifica explicitamente métricas sintéticas, não de campo. |
| Artefato pode ser auditado | Metadados incluem versão, features, amostras, hash do dataset e hash derivado do modelo. |
| Avaliação pública valida o produto | Não. CWRU é experimento independente de sinais de rolamento; não demonstra transferência para colheitadeiras. |
| O IF fornece probabilidade de quebra ou RUL | Não. A saída é score de anomalia. |
