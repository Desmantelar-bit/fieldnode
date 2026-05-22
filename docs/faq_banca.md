# FAQ para a Banca - FieldNode

Este documento contém respostas preparadas para perguntas difíceis que podem surgir durante a banca do projeto FieldNode.

## Validação dos Alertas

**Pergunta:** Como o FieldNode valida seus alertas para garantir que não sejam falsos positivos ou que realmente indicam um problema iminente?

**Resposta:** O FieldNode utiliza uma abordagem em camadas para validação de alertas:
1. **Detecção de Anomalias (Isolation Forest):** Identifica leituras que se desviam significativamente do padrão histórico da máquina específica, reduzindo falsos positivos causados por variações normais de operação.
2. **Modelo de Risco de Manutenção (Random Forest):** Combina múltiplas variáveis (temperatura, vibração, RPM, tendências) para prever a probabilidade de necessidade de manutenção, treinado com regras baseadas em conhecimento de domínio agrícola.
3. **Regras Manuais de Threshold:** Limites operacionais definidos por especialistas (ex: temperatura >85°C ou vibração >0.8) são aplicados como validação final, garantindo que alertas críticos sejam acionados mesmo que os modelos de ML não os capturem em casos extremos.
4. **Correlação Temporal:** Alertas só são considerados válidos se persistirem por múltiplas leituras consecutivas (configurável), evitando gatilhos por ruído momentâneo.

Além disso, o sistema registra todas as leituras (válidas e inválidas) para análise posterior, permitindo ajustes finos nos modelos conforme mais dados são coletados no campo.

## Diferenciais em Relação a Soluções de Mercado

**Pergunta:** Quais são os diferenciais do FieldNode em relação a soluções comerciais de telemetria agrícola disponíveis no mercado?

**Resposta:** O FieldNode se destaca em três pilares principais:

1. **Resiliência de Conectividade (Offline-First):**
   - Enquanto soluções comerciais dependem de conexão constante com a nuvem (4G/Wi-Fi), o FieldNode opera totalmente offline no campo usando ESP-NOW entre nós e gateway.
   - Os dados são armazenados localmente e sincronizados apenas quando há conectividade disponível, usando deduplicação por UUID v4 para evitar perda ou duplicação.
   - Isso é crítico considerando que 40% das operações de colheita ocorrem em áreas sem conectividade.

2. **Arquitetura Edge para Baixa Latência:**
   - O processamento de IA (detecção de anomalias, prescrições) ocorre no backend local (gateway ou servidor na sede), não dependendo de nuvem externa.
   - Isso permite alertas em tempo real no dashboard local, essencial para intervenções imediatas que evitam quebras coûteiras.

3. **Custo e Acessibilidade:**
   - Utiliza hardware de baixo custo (ESP32 ~$10 por nó) em vez de módulos proprietários caros.
   - Software de código aberto (Django, Python, Arduino/C++) sem taxas de licenciamento.
   - Focado em pequenos e médios produtores que não podem pagar por soluções de alta complexidade e custo.

4. **Especificidade para Colheitadeiras:**
   - Enquanto muitas soluções genéricas de telemetria veicular monitoram apenas localização e basicamente RPM/temperatura, o FieldNode inclui sensores de vibração (indicativo de desgaste mecânico) e modelos de IA adaptados aos padrões de falha específicos de colheitadeiras (ex: superaquecimento do motor, desgaste de rolamentos).

## Prevenção de Excesso de Alertas (Alert Fatigue)

**Pergunta:** Como o FieldNode evita o excesso de alertas que pode levar à desatenção do operador ("alert fatigue")?

**Resposta:** Para evitar alert fatigue, o FieldNode implementa várias estratégias:

1. **Hierarquia de Severidade:** Alertas são classificados em NORMAL, ATENCAO e CRITICO, com recomendações de ação proporcionais à gravidade. Apenas alertas de ATENCAO e CRITICO exigem ação imediata.
2. **Supressão de Alertas Recorrentes:** Se uma máquina já estiver em estado de alerta (ex: temperatura elevada persistente), novos alertas do mesmo tipo não são gerados até que o estado retorne ao normal por um período configurável.
3. **Limite de Frequência:** Alertas do mesmo tipo para a mesma máquina não são repetidos em menos de 30 minutos (configurável), mesmo que as condições persistem.
4. **Contexto na Notificação:** Cada alerta inclui:
   - Valor atual vs limite (ex: "Temperatura 87.2°C (limite 85°C)")
   - Ação recomendada específica e prática
   - Nível de confiança do modelo (quando aplicável)
   Isso ajuda o operador a priorizar e entender a urgência sem precisar interpretar dados brutos.
5. **Modo de Silêncio Temporário:** Durante operações conhecidas que causam leituras fora do padrão (ex: operação em terreno muito acidentado), o operador pode colocar a máquina em modo de observação aumentada sem alertas sonoros por um período definido.
6. **Feedback do Operador:** O sistema permite que o operador marque um alerta como "falso positivo" ou "reconhecido", alimentando um mecanismo de aprendizado que ajusta os thresholds pessoais para aquela máquina específica ao longo do tempo.

Essas medidas garantem que os alertas sejam ação, relevantes e respeitem o limite cognitivo do operador, aumentando a aderência ao sistema.
