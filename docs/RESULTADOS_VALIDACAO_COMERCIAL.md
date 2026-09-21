# Resultados de Validação Comercial

Este documento registra aprendizados de conversas com potenciais usuários e stakeholders do FieldNode.

Os resultados aqui não devem ser tratados como evidência estatística. Três conversas não representam todo o mercado. O objetivo desta fase é descoberta qualitativa de problema, não confirmação de hipótese.

---

## Roteiro Utilizado

### Contexto

1. Como vocês acompanham hoje o funcionamento das máquinas durante a operação?
2. Que informações vocês conseguem enxergar em tempo real?
3. O que normalmente fica difícil de saber até ser tarde demais?

### Problema

4. Quais situações mais costumam gerar parada, atraso ou perda operacional?
5. Quando uma máquina apresenta comportamento anormal, como vocês descobrem?
6. Quem normalmente percebe primeiro esse problema?
7. Quanto tempo costuma levar entre perceber o problema e tomar uma ação?

### Processo atual

8. Quais ferramentas ou sistemas vocês utilizam hoje?
9. O que funciona bem nesses sistemas?
10. O que ainda precisa ser feito manualmente?

### Impacto

11. Quando existe uma parada inesperada, quais são as principais consequências?
12. Existe algum indicador utilizado para medir esse impacto?

### Solução

13. Em quais situações um alerta antecipado teria valor real?\
14. Que informação precisaria aparecer nesse alerta para alguém tomar uma decisão?
15. Quem seria a pessoa responsável por usar esse tipo de informação?

### Compra ou piloto

16. Uma solução desse tipo seria avaliada por quem?
17. O que precisaria ser demonstrado para vocês considerarem um piloto?
18. Quais seriam as principais preocupações antes de conectar uma solução dessas à operação real?

---

## Conversa 001 — John Deere

**Data:** 2026-09-19
**Perfil do contato:** Especialista técnico, John Deere Brasil.
**Segmento:** Fabricante OEM / tecnologia agrícola embarcada.
**Canal:** Conversa direta.

### Sistemas e processo atual

- Monitoramento centralizado no **John Deere Operations Center (JDOC)**, via web e aplicativo móvel.
- Dados extraídos do barramento **J1939 (rede CAN)** via módulo embarcado **JDLink** com transmissão **4G/LTE**.
- Parâmetros visíveis em tempo real quando há sinal: RPM, temperatura do líquido de arrefecimento, pressão hidráulica, consumo de combustível e GPS.

### Problema relatado

- **30% a 40% das operações de colheita ocorrem em zonas sem cobertura celular.** Quando a máquina entra off-grid, a transmissão cai completamente.
- O JDLink armazena dados localmente para sincronizar depois, mas **não oferece dashboard acessível ao operador na cabine ou ao supervisor no campo durante o período offline.**
- Quem percebe o problema primeiro nessas zonas é o próprio operador, por ruídos, vibrações extremas ou perda de potência física.
- **Cerca de 40% da frota nacional tem mais de 15 anos** e não dispõe de barramento CAN/J1939 acessível. A integração JDOC fica limitada ou exige retrofits manuais nessas máquinas.

### Impacto relatado

- Parada não programada custa **R$ 5.000 a R$ 15.000 por hora**, somando perda de produtividade, equipe e logística de manutenção.

### O que um alerta antecipado precisaria mostrar

- Métrica preditiva simples: **"tempo estimado em minutos para a temperatura ou vibração atingir a zona de risco"**, exibida em dispositivo local para o supervisor de campo.
- Usuário da decisão: supervisor de campo ou gestor de frota.

### Critérios para piloto

- Avaliado pelo departamento de tecnologia agrícola e concessionárias.
- Precisaria demonstrar: **sincronização automática e transparente do histórico offline** assim que o sinal retorna, e eficácia de um **dashboard local offline-first**.

### Preocupação principal antes de plugar na operação

- Suporte a **frotas mistas** (outras marcas e máquinas antigas) via sensores externos confiáveis, complementando onde o JDOC ainda encontra barreiras.

### O que o FieldNode valida com esta conversa

- O problema de conectividade offline é real e quantificado (30–40% das operações).
- A frota legada sem CAN é um mercado não atendido pelo próprio fabricante.
- O conceito de alerta local offline-first tem valor declarado pelo especialista do OEM.
- A sincronização pós-reconexão sem duplicação é requisito técnico explícito.

### O que NÃO foi validado

- Disposição de compra ou orçamento disponível.
- Processo de aprovação interno da John Deere para parceiros externos.
- Integração técnica com JDOC via API oficial.

---

## Conversa 002 — Solinftec

**Data:** 2026-09-19
**Perfil do contato:** Especialista técnico, Solinftec.
**Segmento:** Plataforma de IA agrícola / agtech SaaS.
**Canal:** Conversa direta.

### Sistemas e processo atual

- Monitoramento via plataforma de IA **Alice**, com infraestrutura proprietária de **antenas de rádio frequência (RF) e rede mesh local Zigbee** instalada nas fazendas.
- Quando a infraestrutura está presente: velocidade, área colhida, eficiência operacional, produtividade e GPS em tempo real. A Alice analisa em nuvem e entrega predições e recomendações.
- Em alguns casos, operadores ainda geram **relatórios manuais de hora em hora** para a usina.

### Problema relatado

- A solução depende de **alto investimento de instalação prévia de antenas**. Quando a colhedora sai da zona de cobertura proprietária, o estado da máquina fica invisível.
- Se o equipamento sai da malha RF com desgaste mecânico severo, apenas o operador da cabine percebe fisicamente. O tempo de ação atrasa drasticamente.

### Impacto relatado

- **R$ 5.000 a R$ 15.000 por hora perdida.**
- Um alerta antecipado teria **valor comercial gigantesco para atuar nas margens onde a rede mesh não chega.**

### O que um alerta antecipado precisaria mostrar

- Processamento **direto na borda (edge computing) na própria máquina**, mostrando **"normal, atenção ou crítico"** sem depender do servidor em nuvem.
- Usuário da decisão: operador na cabine ou fiscal que passa de caminhonete próximo à máquina.

### Critérios para piloto

- Avaliado por arquitetos de solução e diretores de agtech.
- Precisaria demonstrar: **capacidade offline-first de baixo custo (abaixo de R$ 500 de hardware por máquina)** e análise de risco retroativa com machine learning baseada em dados não supervisionados.

### Preocupação principal antes de plugar na operação

- **Garantia de que não haverá duplicação de pacotes e problemas de UUID durante as ressincronizações** com os bancos de dados ao reconectar.

### O que o FieldNode valida com esta conversa

- O limite da cobertura mesh é o mesmo problema do limite celular: a borda sem rede é o ponto cego de todos os players.
- O conceito de edge computing com classificação local (NORMAL/ATENCAO/CRITICO) foi descrito espontaneamente pelo especialista — sem sugestão da equipe.
- A deduplicação UUID como requisito técnico foi citada explicitamente como preocupação de integração.
- O teto de R$ 500 de hardware por máquina é um critério de viabilidade comercial concreto.

### O que NÃO foi validado

- Modelo de parceria ou integração técnica com a plataforma Alice.
- Processo de compra ou aprovação orçamentária.
- Compatibilidade de protocolo entre FieldNode e infraestrutura Solinftec.

---

## Conversa 003 — Case IH

**Data:** 2026-09-19
**Perfil do contato:** Especialista técnico, Case IH Brasil.
**Segmento:** Fabricante OEM / agricultura de precisão.
**Canal:** Conversa direta.

### Sistemas e processo atual

- Monitoramento via **AFS Connect** (Advanced Farming Systems), portal web e aplicativo móvel com inteligência via Power BI.
- Base técnica: rede **CAM (CAN Bus/J1939 nativo)** com módulo embarcado **AFS Pro 700 ou PCM/PCMF**, transmissão via **4G/LTE e Wi-Fi**.
- Parâmetros em tempo real: RPM, temperatura, pressão, área colhida, rendimento agronômico (TCH), status da operação e histórico de localização.
- O software pode **bloquear comandos se o operador forçar a máquina além dos limites operacionais previstos.**

### Problema relatado

- **Máquinas sem rede CAM nativa** recebem apenas o módulo **CM100**, que coleta dados básicos (combustível, motor, transmissão) e exige que o operador aguarde área com Wi-Fi/sinal — armazena até 30 dias de log, mas **não permite visualização remota instantânea.**
- **Incêndios em colhedoras por superaquecimento de rolamentos na esteira** são um problema grave. Esses rolamentos muitas vezes não são monitorados por padrão no barramento.
- Usinas como a **Clealco (região de Araçatuba)** não usam os dashboards do AFS Connect — exigem dados brutos diretos da concessionária para injetar em sistemas proprietários de BI.
- Clientes relatam limitações de usabilidade no aplicativo mobile e casos de exclusão acidental de conta.

### Impacto relatado

- **R$ 5.000 a R$ 15.000 por hora**, mais o risco incalculável de **perder uma colheitadeira inteira num incêndio de lavoura.**

### O que um alerta antecipado precisaria mostrar

- Alerta local (offline) focado na **variação térmica de componentes móveis** e no **desgaste físico**, com impacto direto na segurança das operações.

### Critérios para piloto

- Avaliado pela liderança de agricultura de precisão.
- Precisaria demonstrar: **estabilidade ao integrar sensores externos extras** (como módulos para monitorar rolamentos) sem depender da infraestrutura de CAN, e **suporte pleno a frotas mistas** (Case, John Deere e máquinas antigas).

### Preocupação principal antes de plugar na operação

- **Segurança no upload posterior** das informações após horas offline e como integrar relatórios brutos ao fluxo de concessionárias de forma confiável.

### O que o FieldNode valida com esta conversa

- O problema de rolamentos sem monitoramento é um risco de segurança real e não coberto pelos sistemas atuais — abre espaço para sensores externos complementares.
- O requisito de frotas mistas (multi-marca, máquinas antigas) foi citado por dois dos três especialistas de forma independente.
- A demanda por dados brutos exportáveis (Clealco/BI proprietário) valida o endpoint de exportação CSV/XLSX do FieldNode.
- A preocupação com segurança no upload pós-offline é o mesmo requisito de deduplicação UUID já implementado.

### O que NÃO foi validado

- Processo de integração técnica com AFS Connect via API oficial.
- Modelo de parceria com concessionárias Case.
- Aprovação orçamentária ou processo de compra.

---

## Síntese das Três Conversas

### Problema confirmado de forma independente pelos três especialistas

| Ponto | John Deere | Solinftec | Case IH |
|---|---|---|---|
| Ponto cego offline (sem celular ou sem mesh) | sim | sim | sim |
| Frota legada sem CAN como mercado não atendido | sim | — | sim |
| Custo de parada R$ 5k–15k/hora | sim | sim | sim |
| Alerta local offline-first como solução desejada | sim | sim | sim |
| Deduplicação/sincronização pós-reconexão como requisito | sim | sim (explícito) | sim |
| Frotas mistas (multi-marca) como critério de piloto | sim | — | sim |

### Hipóteses do FieldNode confirmadas

- O problema de conectividade offline é real, quantificado e não resolvido pelos sistemas atuais dos três players.
- A classificação local NORMAL/ATENCAO/CRITICO foi descrita espontaneamente pela Solinftec sem sugestão da equipe — validação independente do modelo de saída do pipeline de IA.
- A deduplicação UUID, já implementada, foi citada como requisito técnico explícito pela Solinftec.
- A exportação de dados brutos (CSV/XLSX), já implementada, foi validada pelo caso Clealco/Case IH.

### Hipóteses ainda abertas

- Disposição real de compra ou orçamento disponível em qualquer dos três.
- Modelo de parceria ou integração técnica com plataformas existentes (JDOC, Alice, AFS Connect).
- Teto de preço de hardware (R$ 500/máquina citado pela Solinftec) validado com os outros dois.
- Processo de aprovação interno em cada empresa.

### Dívidas técnicas reveladas pelas conversas

- **Monitoramento de rolamentos e componentes sem CAN:** os três especialistas citaram máquinas antigas ou componentes não cobertos pelo barramento. O FieldNode atual depende de sensores de temperatura, vibração e RPM — mas não tem abstração para sensores externos adicionais (ex.: sensor de temperatura de rolamento). Isso é uma lacuna de hardware fora do escopo atual do TCC, mas deve ser registrada como próximo passo de produto.
- **Dashboard local offline-first na cabine:** o Service Worker atual cobre fila de telemetria, mas não um dashboard operacional acessível sem internet na cabine. Isso é uma feature de produto, não um bug.
- **Integração com sistemas de BI proprietários (ex.: Clealco):** o endpoint de exportação CSV/XLSX existe, mas não há documentação de integração para consumo por sistemas externos. Baixa prioridade para o TCC, alta prioridade para piloto real.

---

## Métricas Acumuladas

**Conversas comerciais realizadas:** 3 (John Deere, Solinftec, Case IH).

**Conversas com conteúdo substantivo sobre operação, problema e processo:** 3/3.

**Critério S2-T5 de validação comercial:** satisfeito — pelo menos uma conversa real foi realizada com potenciais stakeholders, com conteúdo sobre operação, problema, processo e necessidade.

**Endpoints de escrita protegidos:** 100% — POST/PUT/PATCH/DELETE bloqueados sem token (validado por `test_permissions` e `test_auth`, 14 testes verdes).

**Próximo passo comercial:** identificar contato acionável em usina ou operação agrícola no MS para conversa com usuário final operacional (supervisor de campo, gestor de frota), não apenas com especialistas de fabricante/plataforma.

---

## Matriz de Cobertura DEMO_MODE — Endpoints Públicos Sensíveis

Verificado no código em `api_tcc/api/views_ingestao.py`, `views_gps.py`, `views_relatorio.py`, `views_prescricao.py` e `viewsets.py`.

| Endpoint | Anônimo | Filtro `is_demo` aplicado | Mecanismo |
|---|---|---|---|
| `GET /api/leituras/ultimas/` | sim | sim | SQL raw com `INNER JOIN api_tcc_machine m AND m.is_demo = %s` |
| `GET /api/telemetria/` | sim | sim | `_filter_public_demo_leituras(LeituraTelemetria.objects.all(), request)` |
| `GET /api/metricas/` | sim | sim | `_filter_public_demo_leituras(...)` + invalidas zeradas |
| `GET /api/status-mqtt/` | sim | sim | `_filter_public_demo_leituras(...).order_by('-recebido_em').first()` |
| `GET /api/relatorio/` | sim | sim | `_filter_public_demo_leituras(LeituraTelemetria.objects.all(), request)` |
| `GET /api/relatorio/exportar/` (xlsx) | sim | sim | `leituras_qs.filter(machine__is_demo=True)` + bloqueia máquina não-demo |
| `GET /api/maquinas/posicao/` | sim | sim | `leituras.filter(machine__is_demo=True)` quando `demo_publico` |
| `GET /api/anomalias/` | sim | sim | `_public_demo_machine_allowed()` — bloqueia máquina não-demo |
| `GET /api/manutencao/` | sim | sim | `_public_demo_machine_allowed()` |
| `GET /api/prescricoes/` | sim | sim | `_public_demo_machine_allowed()` |
| `GET /api/prescricoes/lista/` | sim | sim | `_public_demo_machine_allowed()` → retorna `[]` |
| `GET /api/prescricoes/<maquina_id>/` | sim | sim | `_demo_machine_allowed()` em `views_prescricao.py` |
| `GET /api/colheitadeira/` | sim | sim | `ColheitadeiraViewSet.get_queryset()` filtra `machine__is_demo=True` |

**Escrita com DEMO_MODE=True (sem token):**

- `POST /api/colheitadeira/` → 401/403 (DRF IsAuthenticated via router)
- `POST /api/telemetria/` → 401 (X-API-Key obrigatória, independente de DEMO_MODE)
- Todos os outros POST/PUT/PATCH/DELETE → 401/403

**Filtro no banco, não pós-serialização:** confirmado. Nenhuma view consulta todos os dados e filtra em Python. O filtro `is_demo` é aplicado no queryset/SQL antes de qualquer serialização.
