# S5-T1 · Unificação dos detectores

## Status

IMPLEMENTADO COM LIMITAÇÕES DOCUMENTADAS.

O serviço oficial é `api_tcc/services/anomaly_detection.py`. O caminho legado em `ia/deteccao_multivariada.py` permanece apenas como fachada de compatibilidade e encaminha a execução para o serviço oficial.

## Evidência

- `detect_anomaly` mantém o caminho de ingestão por máquina.
- `detect_from_history` e `detect_many_from_history` permitem avaliação reproduzível sem banco.
- O contrato identifica `detection_method`, `model_version`, `detection_status` e `data_quality`.
- `model_registry.py` valida estrutura e hash do modelo carregado.
- `treinar_modelo_anomalia` continua sendo o comando oficial por máquina.
- Artefatos gerados em `api_tcc/ia/modelos/*.pkl` foram adicionados à política de ignorados; o artefato histórico ainda precisa ser removido do índice Git em uma operação de limpeza revisada.

## Limitações

O estado da janela em `REGISTRY` é local ao processo. Reinício de worker limpa o cache e múltiplos workers não compartilham esse estado; a janela é reconstruída do banco quando necessário. Atualização de modelo sem reinício não foi implementada.

O antigo comando `treinar_isolation_forest` ainda existe como compatibilidade histórica e deve ser removido em tarefa de limpeza após confirmação dos consumidores.
