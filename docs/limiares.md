# Limiares da análise determinística

Os limites estabelecidos (Temperatura > 85°C, Tendência > 0.5°C, Vibração Média > 5) foram definidos empiricamente com dataset de bancada e servirão como regras de detecção de anomalias primárias para o protótipo de TCC.

Esses valores são específicos do estágio de prototipação e não representam limites universais de operação. A origem é o conjunto de leituras simuladas de bancada usado para validar o fluxo de telemetria. Em produção, devem ser recalibrados com dados históricos reais, especificações do fabricante e validação de especialistas de manutenção.

O pipeline aplica as regras à janela de até 500 leituras mais recentes de cada máquina:

- Temperatura máxima acima de 85°C.
- Tendência média de temperatura acima de 0.5°C entre leituras consecutivas.
- Vibração média acima de 5.

Uma regra disparada resulta em `ATENCAO`; duas ou mais resultam em `CRITICO`; sem regras disparadas, o status é `NORMAL`.
