# S5-T7 - LLM com guardrails de evidência

## Resultado

Implementado no caminho agentic existente. O provedor recebe somente um objeto `decision.v1` validado; a saída aceita exatamente `texto` e `evidencias_citadas`.

## Guardrails

- IDs citados precisam existir em `evidencias` da decisão atual.
- Números do texto são comparados com os valores autorizados em `evidencias.valor` e `evidencias.limiar`.
- JSON, campos extras, resposta vazia e schema inválido são rejeitados.
- A chamada usa timeout de 2 segundos e temperatura 0.
- Falhas registram `DeadLetterEntry.Contexto.AGENTIC_LLM` e usam fallback determinístico sem alterar a decisão original.

## Verificação

`python -m pytest api_tcc/tests/test_agentic.py api_tcc/tests/test_s5_guardrails_assistant.py -q` - VERIFICADO, 8 testes passaram.

## Limitações

A validação textual é conservadora e não pretende provar causalidade física. O LLM continua sendo explicador; aprovação, rejeição e execução seguem fora do assistente.
