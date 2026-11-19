# Política de validação de campo

Status: **POLÍTICA DOCUMENTAL; validação física e piloto não realizados.**

Este documento define uma escada de evidência para impedir que teste local,
bancada de software ou simulação seja apresentado como validação em máquina
agrícola. A ordem é obrigatória: um degrau superior não pode ser declarado
concluído enquanto o critério de saída do degrau anterior não estiver atendido.

## Resposta curta para a banca

**Não. O FieldNode ainda não foi validado em campo.** O checkout comprova
implementação de software, testes automatizados e simulações controladas. Os
relatórios S8 registram como não verificados a placa, o sensor, a publicação
MQTT física, ESP-NOW, CAN em veículo e a operação em máquina real. Um piloto
operacional continua sendo uma hipótese futura.

## Estados e regra de progressão

- **NÃO INICIADO:** não há execução ou evidência suficiente.
- **EM ANDAMENTO:** execução começou, mas o critério de saída não foi atingido.
- **PARCIALMENTE VALIDADO:** parte dos cenários foi executada; as lacunas estão explícitas.
- **CONCLUÍDO COM EVIDÊNCIAS:** todos os critérios aplicáveis de saída têm registro auditável.
- **BLOQUEADO:** há uma dependência que impede execução segura ou interpretação do resultado.
- **NÃO APLICÁVEL:** somente quando a justificativa estiver registrada.

Nenhum teste automatizado, vídeo interno ou demonstração de bancada autoriza
por si só a progressão para máquina real. Falha, critério pendente ou ausência
de registro mantém o degrau fora de concluído.

## Matriz central

| Degrau | Objetivo | Ambiente | Critério de entrada | Método e métrica | Evidência exigida | Critério de saída | Estado atual |
|---|---|---|---|---|---|---|---|
| 1. Validação local | Verificar contratos, API, deduplicação, persistência, análise e UI | Checkout local/CI | Código e dependências identificados | Testes executados; resultado por suíte; `manage.py check` quando aplicável | Log datado, comando, versão e artefatos | Suítes aplicáveis passam e falhas conhecidas estão registradas | **CONCLUÍDO COM EVIDÊNCIAS** para o escopo documentado; reexecutar no release |
| 2. Validação de bancada | Verificar integração física real, alimentação, firmware e transporte | Bancada identificada | Componentes disponíveis, setup e riscos registrados | Repetições, mensagens, ACK, reinício e integridade; limiares ainda devem ser definidos por ensaio | Fotos, placa/firmware, log serial, payload, banco e responsável | Setup reproduzível, resultados e falhas revisados; nenhum limiar inventado | **PARCIALMENTE VALIDADO**: software/host e contratos; hardware físico não comprovado |
| 3. Simulação de campo | Reproduzir cenários operacionais sem alegar máquina real | Simulador, replay ou bancada controlada | Cenários e dados sintéticos identificados | Cobertura de cenários, perda/reenvio, ordenação, backlog e recuperação | Script, entrada, saída, tempos e limites | Cenários planejados executados e lacunas listadas | **PARCIALMENTE VALIDADA**: simulação e continuidade local; cobertura operacional incompleta |
| 4. Máquina real | Observar o sistema em máquina agrícola autorizada, sem controlar a máquina | Equipamento real supervisionado | Autorização, máquina, sensores, segurança, plano e critérios de interrupção | Integridade, disponibilidade, falhas e observação; métricas definidas antes | Autorização, fotos, logs, configuração, dados brutos e relatório | Plano completo executado, dados íntegros e revisão assinada | **NÃO VALIDADO** |
| 5. Piloto operacional | Testar a hipótese de uso limitado em ambiente real | Operação real aprovada | Degraus 1–4, responsável, escopo, indicadores e contingência aprovados | Indicadores acordados antes; sem prometer eficácia ou resultado financeiro | Termo/ata, participantes, dados, incidentes e encerramento | Avaliação conjunta e decisão explícita de continuar, ajustar ou parar | **NÃO REALIZADO; HIPÓTESE FUTURA** |

## Requisitos por degrau

### 1. Validação local

Registrar testes de payload, autenticação, deduplicação, persistência, eventos,
decisões, API, frontend, sincronização e estados de erro quando aplicáveis.
O resultado comprova comportamento do software no ambiente testado. Não
comprova sensor, rádio, alimentação, calibração ou resistência mecânica.

### 2. Validação de bancada

Antes de executar, identificar cada placa, sensor, fonte, firmware, broker,
gateway e versão. Registrar o diagrama do setup, procedimento reproduzível,
falhas e condições de interrupção. Não usar metas como “50 quedas”, “30 dias”
ou alcance de rádio sem ensaio e definição de método. O relatório S8 atual
mantém esses itens pendentes.

### 3. Simulação de campo

Distinguir explicitamente: simulação computacional, replay, teste físico em
bancada, simulação operacional e observação em máquina real. Um simulador pode
mostrar a cadeia telemetria → evento → decisão e a tolerância a interrupções,
mas não pode ser descrito como sensor instalado ou validação agrícola.

### 4. Máquina real

Exigir autorização do responsável, identificação do ambiente, configuração da
máquina, instalação documentada, análise de risco, supervisor, plano de coleta,
critérios de interrupção e integridade dos dados. O FieldNode permanece somente
monitoramento e apoio à observação: não envia comandos à ECU nem interfere na
operação.

### 5. Piloto operacional

Piloto não é prêmio por terminar a documentação. É uma hipótese a ser testada
com escopo limitado, responsabilidades, privacidade, segurança, contingência,
indicadores previamente acordados e critério de encerramento. Não introduzir
meta comercial ou eficácia presumida.

## Registro mínimo de evidência

Cada execução deve conter: identificador, data real, responsável, ambiente,
hardware, firmware, software, versões, cenário, procedimento, resultado,
falhas, limitações, arquivos vinculados, critério avaliado, estado final e
decisão de progressão. Quando algo não existir, registrar **AUSENTE** ou
**NÃO VERIFICADO**, nunca preencher por inferência.

## Linguagem permitida e proibida

Não afirmar, sem evidência específica: “validado em campo”, “funciona em
qualquer colheitadeira”, “pronto para piloto”, “reduziu downtime”, “comprovou
precisão operacional” ou “validado em diferentes fabricantes”.

Preferir: “implementado no código”, “verificado em teste local”, “simulado com
dados sintéticos”, “parcialmente validado em bancada” e “validação em máquina
real planejada, ainda não realizada”. Isolation Forest é um sinal não
supervisionado de anomalia; regras e thresholds são triagem, não previsão
supervisionada de falha.

## Evidências consultadas

- [`docs/evidence/s8/S8-T1_REPORT.md`](evidence/s8/S8-T1_REPORT.md)
- [`docs/evidence/s8/S8-T4_S8-T5_IMPLEMENTATION.md`](evidence/s8/S8-T4_S8-T5_IMPLEMENTATION.md)
- [`docs/evidence/s8/S8-T12_REPORT.md`](evidence/s8/S8-T12_REPORT.md)
- [`docs/evidence/s8/S8-T14_REPORT.md`](evidence/s8/S8-T14_REPORT.md)
- [`docs/ROTEIRO_DEMO_BANCA.md`](ROTEIRO_DEMO_BANCA.md)
- [`docs/REPOSICIONAMENTO_ESCOPO_HARDWARE.md`](REPOSICIONAMENTO_ESCOPO_HARDWARE.md)

Não foram inventadas datas, responsáveis, resultados físicos ou aprovação de
piloto.
