# S9-T2 / S9-T3 — evidência de implementação

## Entregue

- Tela `/frentes` para associação de máquinas, listagem dos vínculos e upload
  do CSV `origem,destino,tipo,front,de,ate`.
- API `operation-graph/` com isolamento por organização e validação antes da
  persistência; importação transacional sem gravação parcial.
- Comando `importar_links` com relatório de linhas rejeitadas no stdout.
- `ConsequenceAssessment` determinístico, versionado como `consequence-v0.1`,
  com afetados, risco, horizonte opcional, premissas, faltantes e confiança.
- Endpoint `GET /api/events/<event_id>/consequence/`.

## Verificações executadas

- `python manage.py check` — passou.
- `python -m pytest api_tcc/tests/test_consequence.py api_tcc/tests/test_operation_graph.py -q` — 16 testes passaram.
- `npm run lint` em `frontend-next` — passou.
- `npm run build` em `frontend-next` — passou; a rota `/frentes` foi gerada.
- `git diff --check` — passou; o Git apenas reportou avisos de conversão LF/CRLF em arquivos já modificados fora desta entrega.

Os testes do motor usam série sintética determinística para conferir 40 minutos
manualmente, série com R² abaixo do mínimo, ausência de vínculos, capacidade
ausente e evidência suspeita. São dados de teste, não evidência de campo.

## Limites preservados

Não foram calculados tempo de espera, custo, produtividade, vida útil ou
parada garantida. A ausência de limite, tendência elegível, capacidade ou
vínculos aparece como dado faltante. A validação E2E com uma operação real e a
validação física/comercial continuam pendentes.
