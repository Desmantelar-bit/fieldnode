# S5-T8 - Assistente com ferramentas controladas

## Resultado

Implementado o executor backend da allowlist com quatro consultas somente leitura: `listar_maquinas_criticas`, `explicar_decisao`, `saude_da_maquina` e `eventos_recentes`.

## Controles

- Nome da ferramenta e argumentos são validados antes da consulta.
- Campos extras, IDs inválidos, limites fora da faixa e ferramenta desconhecida são rejeitados.
- Cada ferramenta deriva o conjunto de máquinas do usuário autenticado e filtra a organização internamente.
- Recurso de outra organização ou inexistente retorna `Não encontrada.` sem revelar existência.
- Resultados carregam IDs de máquina, decisão, evento ou evidência para rastreabilidade.
- Não existe caminho de aprovação, rejeição, ORM livre, SQL recebido ou escrita pelo executor.

## Verificação

`python -m pytest api_tcc/tests/test_s5_guardrails_assistant.py -q` - VERIFICADO, 5 testes passaram.

## Limitações

O endpoint recebe chamadas estruturadas de ferramenta. A interpretação natural via provedor ainda não foi acoplada ao `ChatFAB`; portanto o componente visual existente continua sendo o fluxo de prescrição, não um chatbot geral. Isso evita prometer uma conversa que ainda não existe.
