# PROTOCOLO_TESTE_RESILIENCIA

**Responsável:** A CONFIRMAR  
**Semana:** S6  
**Status:** ESQUELETO  
**Tarefa de preenchimento:** S6-Tx (confirmar identificador exato no roadmap)  
**Última atualização:** 2026-11-04 — criação do esqueleto (S0-T4)

> **Atenção:** o status deste documento só poderá mudar de `ESQUELETO` para outro quando:
> - as seções obrigatórias estiverem preenchidas com dados reais de S6;
> - as evidências estiverem anexadas ou referenciadas;
> - os critérios de conclusão forem atendidos;
> - a revisão da semana S6 for realizada.

---

## 1. Objetivo

Registrar como será validada a resiliência do sistema FieldNode diante de
interrupções, falhas e recuperação de conectividade — distinguindo claramente
o que foi testado em simulador de software do que foi testado com interrupção
de rede real.

TODO(responsável-S6, por quê: o protocolo precisa estar definido antes da execução para que os resultados sejam comparáveis e auditáveis, quando: início de S6): definir o objetivo técnico específico, o ambiente de teste e os critérios de aceitação.

---

## 2. Escopo

### Incluído

TODO(responsável-S6, por quê: delimitar o que será testado aqui, quando: S6): listar os componentes e cenários que serão cobertos.

**Componentes conhecidos em S0 que são relevantes:**
- `simulators/edge_client.py` — outbox SQLite, prioridades A/B/C, retry, ACK
- `simulators/teste_resiliencia.py` — script de ensaio existente (protocolo S8-T2 mencionado no cabeçalho)
- `frontend-next/public/sw.js` — fila IndexedDB do Service Worker
- Backend Django — comportamento diante de requisições duplicadas (deduplicação UUID)

### Fora do escopo

TODO(responsável-S6, por quê: evitar que este protocolo substitua a validação de hardware de S8, quando: S6): registrar o que não será tratado (ex: comunicação ESP-NOW, rádio físico, campo).

---

## 3. Contexto atual do FieldNode

**Estado verificado em 2026-11-04 (S0-T3):**

- `simulators/edge_client.py` — 361 linhas; outbox SQLite com estados PENDENTE/ENVIANDO/SINCRONIZADA/ERRO; prioridades A/B/C; retry com ACK; cursor contíguo — IMPLEMENTADO em software
- `simulators/teste_resiliencia.py` — 373 linhas; script existente para ensaio de resiliência com `edge_client.py` contra Compose local; referencia "protocolo S8-T2"
- `simulators/test_edge_client.py` — 6 testes passando (pytest)
- Sem testes automatizados de interrupção de rede real
- Fila IndexedDB do Service Worker documentada no README com limitações (sem credenciais privilegiadas; payload inválido fica pendente)

TODO(responsável-S6, por quê: atualizar com o estado real na semana de execução, quando: início de S6): complementar com mudanças ocorridas após S0.

---

## 4. Especificação e conteúdo técnico

### 4.1 Objetivo do protocolo

TODO(responsável-S6, por quê: objetivo mensurável define o que "aprovado" significa, quando: S6): definir o que o protocolo quer provar e o que declarará como limitação.

### 4.2 Ambiente de teste

TODO(responsável-S6, por quê: o ambiente determina o que os resultados podem afirmar, quando: S6): especificar:
- simulador de software local vs. interrupção de rede real
- máquina(s) usadas
- versões dos componentes
- se usa Docker Compose ou SQLite local

**Nota:** `simulators/teste_resiliencia.py` já existe e executa contra Compose local. Verificar se ele é suficiente ou se S6 requer extensão.

### 4.3 Componentes envolvidos

TODO(responsável-S6, por quê: listar os componentes testados permite rastrear cobertura, quando: S6): listar cada componente e o que será verificado nele.

### 4.4 Cenários de interrupção

TODO(responsável-S6, por quê: cenários explícitos evitam que "passou nos testes" signifique algo vago, quando: S6): definir os cenários. Referência inicial:
- [ ] Backend indisponível por 30 segundos durante envio
- [ ] Backend indisponível por 5 minutos com coleta contínua
- [ ] Backend indisponível por 30 minutos (duração definida em `teste_resiliencia.py`)
- [ ] Reinicialização do cliente durante outbox pendente
- [ ] Payload duplicado enviado duas vezes (deduplicação UUID)
- [ ] Payload inválido na fila do Service Worker

### 4.5 Comportamento esperado

TODO(responsável-S6, por quê: definir o comportamento esperado antes do teste é o que transforma "observação" em "validação", quando: S6): para cada cenário, descrever o resultado esperado verificável.

### 4.6 Persistência e recuperação

TODO(responsável-S6, por quê: comprovar que nenhum dado é perdido silenciosamente, quando: S6): documentar como será verificada a recuperação completa após cada interrupção.

### 4.7 Idempotência

TODO(responsável-S6, por quê: idempotência é critério de correção, não de robustez, quando: S6): verificar e documentar que reenvios não criam duplicatas no banco.

### 4.8 Duplicidade e ordenação

TODO(responsável-S6, por quê: edge cases de ordering são frequentes em ambientes intermitentes, quando: S6): documentar o comportamento esperado quando mensagens chegam fora de ordem.

### 4.9 Critérios de aprovação

TODO(responsável-S6, por quê: sem critério de aprovação, o teste não pode ser declarado aprovado, quando: S6): definir métricas e limiares. Exemplo: "100% das leituras gravadas localmente chegam ao banco após reconnect, sem duplicatas, em todos os cenários de até 30 minutos".

### 4.10 Resultados por cenário

TODO(responsável-S6, por quê: preencher apenas após a execução, quando: após execução de S6): tabela com resultado real de cada cenário.

**Resultado:** NÃO EXECUTADO — aguardando S6.

### 4.11 Limitações da simulação

TODO(responsável-S6, por quê: documentar o que a simulação não prova é tão importante quanto o que prova, quando: S6): listar o que a simulação de software não consegue validar.

### 4.12 Diferenças entre simulador, rede local e ambiente de campo

TODO(responsável-S6, por quê: evitar que resultados de simulador sejam confundidos com validação de campo, quando: S6): tabela comparando as três condições de teste.

---

## 5. Evidências e validação

TODO(responsável-S6, por quê: evidências verificáveis são o que separa afirmação de fato, quando: após execução de S6): adicionar:
- log de execução do protocolo com timestamps
- contagem de leituras enviadas vs. confirmadas
- dump do banco após recuperação
- comando exato de execução

**Referências existentes em S0:**
- `simulators/teste_resiliencia.py` — script de ensaio existente
- `simulators/test_edge_client.py` — 6 testes de comportamento do cliente
- `docs/evidence/s0/tests_pytest_after_2026-11-04.txt` — confirma que testes do simulador passam

---

## 6. Limitações e riscos

TODO(responsável-S6, por quê: registro antecipado evita surpresas, quando: S6): complementar.

**Limitações conhecidas em S0:**
- Todos os testes atuais são em software — sem interrupção de rede física testada
- `simulators/teste_resiliencia.py` requer Compose ativo (Docker indisponível na auditoria S0)
- A fila IndexedDB do Service Worker não tem teste automatizado de interrupção
- O comportamento do Service Worker depende do browser — não testado em produção

---

## 7. Critérios de conclusão

TODO(responsável-S6, por quê: critérios claros permitem verificação objetiva, quando: S6): definir critérios verificáveis.

**Critérios propostos (a confirmar em S6):**
- [ ] Todos os cenários definidos foram executados
- [ ] Resultados tabulados com evidência (log, dump de banco)
- [ ] Limitações documentadas explicitamente
- [ ] Diferença entre simulação e campo claramente declarada
- [ ] Revisão por outro membro realizada

---

## 8. Histórico de alterações

| Data | Responsável | Alteração |
|---|---|---|
| 2026-11-04 | S0-T4 (Antigravity) | Criação do esqueleto com estado verificado em S0 |
