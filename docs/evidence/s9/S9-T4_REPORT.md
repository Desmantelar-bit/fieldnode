# S9-T4 - Política da organização e custo de parada

Implementado no backend em `OrganizationPolicy` com `custo_hora_parada` opcional
(`NULL` sem configuração), moeda explícita `BRL` e validação de valor não
negativo. `prazo_por_severidade` foi mantido e passou a rejeitar severidades
desconhecidas e prazos não inteiros positivos. Não há custo padrão.

O Consequence Engine só inclui campos financeiros na resposta quando existe
política da mesma organização, custo configurado e horizonte válido. Usa
`Decimal`, mantém zero configurado como zero e rotula a origem como premissa
informada pelo cliente e estimativa matemática.

Evidência automatizada: `python -m pytest api_tcc/tests/test_s9_t4_t5.py api_tcc/tests/test_consequence.py -q` passou com 12 testes. A validação cobre ausência de política, cálculo controlado de R$ 1.200/h por 30 minutos, zero explícito e validação de política.

Limitação: não havia tela de configurações organizacionais no frontend deste
checkout, portanto nenhuma tela financeira foi inventada. A configuração pode
ser persistida pelo backend/admin existente; uma tela dedicada permanece
pendente. Nenhum valor financeiro foi adicionado ao pitch.
