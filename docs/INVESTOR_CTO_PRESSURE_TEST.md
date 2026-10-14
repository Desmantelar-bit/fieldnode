# Investor / CTO pressure test - FieldNode S10

Este documento prepara respostas curtas e verificáveis para perguntas difíceis. A regra é separar o que o código demonstra, o que é inferência e o que continua sendo roadmap.

## Perguntas e respostas

### “O que está funcionando ponta a ponta?”

O fluxo demonstrável é: cliente de borda com outbox SQLite -> POST autenticado por `X-API-Key` -> persistência de `LeituraTelemetria` -> Trust Score heurístico -> Event crítico por regra de temperatura -> Decision pendente -> aprovação humana autenticada pelo dashboard -> outcome textual persistido. Cada etapa possui registro no backend.

### “Isso é previsão de falha?”

Não. A temperatura acima de 85 °C aciona uma regra determinística de Event crítico. O Isolation Forest é um sinal complementar. A PoC agentiva depende de configuração de LLM e não deve ser narrada como autonomia física.

### “O Trust Score mede a verdade do sensor?”

Não. Ele mede os critérios implementados para qualidade, atualidade e coerência da leitura. Não substitui calibração ou validação física do sensor.

### “A Decision executa a manutenção?”

Não. O sistema recomenda e exige aprovação humana. `EXECUTADA` só é correto quando uma execução correspondente foi realmente verificada. No ensaio padrão, o estado final é `APROVADA` com outcome documental.

### “Como vocês evitam duplicatas?”

O EdgeClient preserva `message_id`, `sequence_number` e hash na outbox. O backend usa a chave composta `(device_id, message_id)` e trata a constraint como proteção final contra concorrência. Reenvio retorna duplicata sem criar nova leitura.

### “Como o offline funciona?”

A leitura é persistida na outbox antes do envio. Falhas transitórias deixam a mensagem pendente para retry; o cursor só avança de forma contígua após ACK válido. O teste oficial de resiliência Compose precisa ser executado separadamente e não deve ser substituído por teste local.

### “O sistema está pronto para produção?”

Não. É um protótipo técnico funcional para TCC. Permanecem lacunas de operação, autenticação de produção, observabilidade, validação física e validação comercial com compradores. O MVP ainda documenta o token no `localStorage` como dívida técnica, não como solução final.

### “Existe validação comercial?”

A evidência registrada não contém entrevistas auditáveis com compradores ou usuários operacionais. A hipótese comercial continua exploratória. Resultado técnico não substitui conversa comercial, por mais simpático que seja o dashboard.

### “Por que não usar apenas um modelo de IA?”

Porque regras determinísticas dão um caminho explicável e testável para condições conhecidas; modelos entram como sinais complementares. A arquitetura preserva fallback e registra metodologia, sem transformar score em probabilidade calibrada sem validação.

### “Qual é o maior risco técnico agora?”

Provar repetibilidade no ambiente oficial e depois medir comportamento com dados de campo. O risco imediato desta semana é infraestrutura de apresentação: Docker Desktop, credenciais locais, dashboard e gravação. O risco de produto é validar se recomendações úteis correspondem a decisões reais de operação.

## Checklist de resposta

- [ ] citar o endpoint, modelo ou teste que sustenta a afirmação;
- [ ] distinguir simulador de sensor físico;
- [ ] distinguir regra, sinal não supervisionado, recomendação e execução;
- [ ] declarar quando a evidência ainda não existe;
- [ ] não expor chaves, tokens ou senhas;
- [ ] não prometer disponibilidade, economia ou prevenção sem medição.
