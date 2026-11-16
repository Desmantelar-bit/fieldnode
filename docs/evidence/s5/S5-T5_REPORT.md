# S5-T5 - validação em dataset público

## Estado

**IMPLEMENTADO; avaliação real pendente.** O adaptador, o protocolo e os testes estão no repositório. A execução com CWRU não foi concluída porque os arquivos `.mat` oficiais não estavam disponíveis localmente e a fonte não foi tratada como licença aberta.

## Decisão

CWRU foi escolhido em vez de AI4I para a evidência principal. O CWRU fornece sinais reais de vibração de rolamentos e grupos de condição normal/defeituosa. O AI4I tem licença CC BY 4.0 e é facilmente acessível, mas a própria UCI o descreve como sintético e sem sinal bruto adequado para RMS, pico e curtose por janela.

## Código e testes

- `ml/eval/public_dataset.py`: carregamento explícito, validação, features, IF oficial, baseline e hashes.
- `ml/eval/test_public_dataset.py`: 4 testes locais, incluindo reprodutibilidade por semente.
- `api_tcc/services/anomaly_detection.py`: aceita nomes de features do adaptador sem duplicar o detector.
- `requirements.txt`: declara `scipy` para leitura dos arquivos Matlab.

## Métricas

Ainda não há tabela de resultados reais. Ela só deve ser criada após execução com os arquivos CWRU autorizados, preservando TP, FP, FN, TN, precisão, recall, F1 e falsos positivos por hora. Se o IF não superar o limiar simples, a conclusão deverá dizer isso explicitamente.

## Limite da conclusão

Este experimento valida aspectos da metodologia de detecção em um dataset público de domínio industrial distinto. Ele não comprova a eficácia do produto FieldNode em colheitadeiras, nem demonstra transferência direta de desempenho para máquinas agrícolas.
