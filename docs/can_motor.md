# Protótipo CAN de motor

O módulo é um **protótipo de monitoramento CAN com simulação de cenários, validação de sinais e prescrição baseada em regras determinísticas**. Não há calibração com histórico operacional real, diagnóstico confirmado, probabilidade de falha ou modelo de machine learning neste módulo.

## Limites e diagnósticos

Os intervalos de plausibilidade em `api_tcc/services/can_motor.py` e os limiares em `api_tcc/ia/prescricao_motor.py` são referências didáticas deste protótipo. Eles não são especificações verificadas para qualquer motor agrícola. Faixas e decisões exigem revisão com manuais técnicos do fabricante, modelo do motor, regime de operação e dados validados antes de uso operacional.

Os códigos SPN/FMI têm variação de descrição e aplicabilidade por fabricante e família do motor. A referência histórica `157/18` não deve ser usada como sinônimo universal de rail baixo: a documentação Detroit consultada lista SPN 157/FMI 18 como pressão de rail alta e FMI 16 como pressão baixa em determinada aplicação. O protótipo associa `157/16` apenas como referência contextual, não como configuração universal. Os códigos 100/1, 110/0 e 102/18 aparecem em material de aplicação de fabricante, mas não substituem a tabela SAE/J1939 e o manual do motor específico.

FMI é restringido a 0 a 31, faixa codificada pelo campo de 5 bits J1939. Os níveis BAIXA, MEDIA e ALTA contam canais físicos distintos que concordam com uma regra. Essa contagem é um proxy explicável, não uma medida estatística de independência, probabilidade ou confiança calibrada; correlação e independência precisam ser validadas por motor e instalação.

CRITICO exige concordância definida por subsistema e cruzamento dos limites severos ilustrativos; um sinal isolado resulta, no máximo, em ATENCAO. Prazos são conservadores: ATENCAO indica Monitoramento, enquanto CRITICO indica avaliação Imediata. Não há prazos numéricos de 4 ou 8 horas sem validação do fabricante. Isso não é instrução para parar ou operar a máquina; deve-se seguir o procedimento de segurança do fabricante.

Limiares de regra atualmente implementados em `LIMITES_PROTOCOLO`:

| Subsistema e sinal | ATENCAO | CRITICO no protótipo |
| --- | --- | --- |
| Arrefecimento: temperatura do líquido | >= 105 °C | >= 112 °C e nível <= 10% |
| Lubrificação: pressão do óleo | <= 180 kPa | pressão <= 120 kPa com temperatura >= 115 °C ou nível <= 10%; ou pressão <= 180 kPa com temperatura >= 130 °C ou nível <= 5%; ou pressão <= 180 kPa com temperatura >= 115 °C e nível <= 10% |
| Combustível: pressão do rail | <= 100000 kPa | Não atribuído por um único sinal |
| Admissão: pressão do turbo | <= 100 kPa | <= 70 kPa junto com escape >= 800 °C |
| Admissão: temperatura de escape | >= 650 °C | >= 800 °C junto com turbo <= 70 kPa |

Faixas inclusivas de plausibilidade do serviço `validar_leitura`:

| Sinal | Intervalo aceito | Unidade |
| --- | --- | --- |
| `rpm` | 0 a 6000 | rpm |
| `carga_pct`, `oleo_nivel_pct`, `liquido_nivel_pct` | 0 a 100 | % |
| `horimetro_h` | 0 a 1000000 | h |
| `oleo_pressao_kpa` | 0 a 3000 | kPa |
| `oleo_temp_c` | -40 a 250 | °C |
| `liquido_temp_c` | -40 a 180 | °C |
| `rail_pressao_kpa` | 0 a 500000 | kPa |
| `combustivel_temp_c` | -40 a 150 | °C |
| `consumo_lh` | 0 a 500 | L/h |
| `turbo_pressao_kpa` | 0 a 1000 | kPa |
| `escape_temp_c` | -40 a 1200 | °C |
| `bateria_v` | 0 a 40 | V |

Esses intervalos servem apenas para detectar valores impossíveis ou incompatíveis com a bancada; não são envelope de operação de um motor comercial.

Referências consultadas:

- SAE J1939-71 disponibilizada em cópia pública: https://www.autonerdz.com/yabbfiles/Attachments/j1939-71.pdf. A edição consultada é histórica (até dezembro de 2001), então não é usada como base normativa atual.
- Daimler Truck North America, boletim suplementar de códigos de falha para aplicação GHG14: https://www.empiretruck.com/fckimages/pdf/DDC-SVC-BRO-0115%20fault%20codes.pdf. O material lista definições SPN/FMI por aplicação e confirma divergência de rail entre fabricantes/modelos.
- NHTSA, boletim de referência suplementar SAE J1939: https://static.nhtsa.gov/odi/tsbs/2018/MC-10141869-9999.pdf. O documento alerta que a lista não é abrangente nem substitui o diagnóstico do fabricante.

## Qualidade dos dados

`validar_leitura` rejeita campos de identidade/tempo ausentes, ausência total de sinais, valores não numéricos/não finitos, valores fora dos intervalos de plausibilidade e um sinal que repete o mesmo valor exato nas quatro amostras anteriores. Valores estatisticamente extremos não são descartados apenas por serem incomuns. Campos individuais ausentes são contabilizados e mantêm a amostra se ela ainda contiver sinais utilizáveis.

A consulta do motor de prescrição utiliza apenas leituras aceitas. O endpoint mantém contagens de recebidas, aceitas e descartadas, além de contadores de campos ausentes e congelados. Duplicidade exata de máquina e timestamp é impedida por restrição de banco; tentativas equivalentes do simulador são ignoradas.

## Estimativa de horas

A projeção aplica regressão linear aos últimos 60 pontos válidos e relaciona o sinal ao horímetro. Exige ao menos 12 pontos, pelo menos 0,5 hora de extensão do horímetro, avanço estritamente crescente, tendência na direção do limite e R² de pelo menos 0,60. Uma inclinação com razão inferior a 2 entre inclinação e erro-padrão é considerada sem evidência suficiente. A resposta também informa o sinal, o valor, a unidade e a direção do limite ilustrativo utilizado. Se qualquer requisito falhar, a API retorna `horas_ate_limite: null` com o motivo.

A saída representa **horas de motor estimadas**, não horas de relógio. Mesmo quando calculada, é uma extrapolação matemática de dados simulados/operacionais recentes; não equivale a vida útil restante, previsão validada de falha ou prazo de manutenção aprovado pelo fabricante.

## Simulador

Execute `python canmotor.py --maquina COLH-01 --cenario normal --intervalo 5 --duracao 5`. Os cenários aceitos são `normal`, `arrefecimento`, `lubrificacao`, `combustivel` e `admissao`. Cada leitura é gravada pelo ORM com `simulado=True`. Nos cenários de degradação, os sinais evoluem gradualmente; cerca de 1,5% das amostras recebe falha intencional para demonstração do serviço de qualidade. No início de cada execução, somente DTCs simulados da máquina escolhida são desativados; ao reaparecerem, sua ocorrência e `ultima_vez` são atualizadas.

Os cenários e suas saídas são sintéticos. Nenhum valor deve ser tratado como medição de uma colheitadeira real.

## Telemetria e laboratório

O módulo CAN não substitui laudos laboratoriais de óleo. Telemetria operacional pode apontar mudança de comportamento com maior frequência; resultados laboratoriais podem complementar a investigação, mas a data da amostra, o tempo de processamento, mudanças de produto/formulação e inconsistências de horímetro devem permanecer separados. Este checkout não contém PDFs laboratoriais versionados nem dados de amostras anonimizadas para cruzamento validado; não foram inventadas fixtures laboratoriais.

## Evoluções fora do escopo desta versão

Calibração com telemetria real por fabricante, ingestão certificada de DM1, validação oficial SPN/FMI por configuração do motor, análise de óleo anonimizada, quantis conservadores, calibração de limiares e módulos CAN de outros subsistemas permanecem pendentes de dados e validação.
