# S9-T3 — PoC de decisão agentiva via cron + LLM

Esta PoC propõe uma `Decision` a partir dos `Event` de maior `priority_score` das últimas 24 horas, agrupados por `Machine`. Ela não executa ações e grava a proposta como `PENDENTE`, no mesmo fluxo de revisão humana das decisões existentes.

## Execução

```bash
python manage.py gerar_decisao_agentiva
```

Opções úteis para demonstração:

```bash
python manage.py gerar_decisao_agentiva --machine AGENTIC-DEMO-01 --force
python manage.py gerar_decisao_agentiva --horas 24 --limite-eventos 5
```

`--force` ignora a deduplicação de uma proposta agentiva por máquina dentro da janela informada. Sem essa opção, o comando serve para agendamento diário simples.

## Contrato e auditoria

- A chave fica em `GEMINI_API_KEY`, somente no backend.
- O prompt auditável está em `api_tcc/prompts/agentic_decision_v1.txt`.
- A resposta precisa ser JSON com `texto`, `acao_recomendada`, `severidade` e `confianca`.
- A decisão recebe `detalhes.metodologia=agentic_llm_poc`, `prompt_version` e os Events usados.
- A API expõe `metodologia` como campo de leitura da `Decision`.
- Falha de rede, chave ausente ou resposta inválida vai para a DLQ com contexto `AGENTIC_LLM`.
- O Operation Graph ainda não está disponível nesta PoC; o contexto enviado declara essa limitação e usa somente `Machine` + `Event`.

## Estado da evidência

Os testes de resposta válida, resposta inválida e integração com o endpoint consumido pelo dashboard estão em `api_tcc/tests/test_agentic.py`. A suíte Django completa passou com 241 testes, o check do Django passou, o lint frontend passou e o build frontend passou usando a CA do sistema.

A execução real contra o Gemini ainda não foi marcada como concluída: `GEMINI_API_KEY` está vazia e a base local não possui Events elegíveis nas últimas 24 horas. Sem essas duas pré-condições, qualquer Decision agentiva no banco seria fabricada ou não teria origem externa verificável.
