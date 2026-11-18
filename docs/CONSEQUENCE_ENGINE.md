# Operation Graph v0.1

## Escopo

O Operation Graph v0.1 é a fundação relacional para representar relações
operacionais cadastradas entre máquinas. Ele não calcula impacto financeiro,
não prevê prazo de falha e não prova que um vínculo cadastrado ainda reflete o
campo. A qualidade da consulta depende de os vínculos serem mantidos pela
operação.

## Modelo

- `Organization` delimita o tenant confiável.
- `Site` representa uma unidade operacional da organização.
- `Front` representa uma frente dentro de um Site.
- `Machine` é a entidade canônica existente; `tipo` aceita `colhedora`,
  `transbordo`, `caminhao`, `trator` e `outro`. Valor nulo significa que a
  classificação ainda não foi informada.
- `MachineLink` guarda origem, destino, tipo, frente opcional e validade
  temporal.

O legado `Transbordo` permanece preservado. Esta tarefa não cria relações a
partir dele sem mapeamento explícito e não apaga seus registros.

## Semântica direcional

Os três tipos são deliberadamente limitados:

| Tipo | Direção cadastrada | Propagação usada por `afetados_por` |
|---|---|---|
| `ALIMENTA` | A alimenta B | A -> B |
| `TRANSPORTA_PARA` | A transporta para B | A -> B |
| `DEPENDE_DE` | A depende de B | B -> A, para encontrar dependentes de B |

Esta é uma regra de navegação v0.1, não uma afirmação universal sobre a
operação. Relações sem cadastro não são inferidas.

## Validade temporal

Uma relação está ativa em `em` quando `valido_de <= em` e `valido_ate` é nulo ou
maior que `em`. O fim é exclusivo. Uma relação encerrada deve ser preservada e
uma nova relação deve ser criada para um período posterior. O serviço impede
intervalos equivalentes sobrepostos.

## Isolamento

Criação e navegação exigem organização confiável. O serviço não aceita um
`organization_id` do frontend como autorização. Origem, destino, vínculo e
frente precisam pertencer à mesma organização. Máquinas sem organização não
podem ser usadas pelo serviço do grafo.

## Navegação BFS

`afetados_por(machine, em=None, max_hops=3, organization=None)` usa uma única
referência temporal por execução, carrega os vínculos ativos em lote e retorna
uma lista com `machine`, `distance` e `path`. A máquina inicial não aparece,
ciclos não repetem nós e `max_hops=0` retorna lista vazia. Profundidade negativa
é erro de entrada.

Exemplo sintético, não evidência de campo:

```text
COLHEDORA-A --ALIMENTA--> TRANSBORDO-B --TRANSPORTA_PARA--> CAMINHAO-C
afetados_por(COLHEDORA-A, max_hops=2) => B (1), C (2)
```

## Migração do legado

Não há migração automática de `Transbordo` nesta entrega. O modelo legado não
possui organização nem identidade canônica suficiente para criar vínculos com
segurança. O mapeamento futuro deve preservar IDs, capacidade e metadados,
registrar correspondências e deixar pendentes os registros sem evidência.

## Limitações conhecidas

- integridade entre tabelas é validada no modelo/serviço, não por uma única
  constraint SQL;
- prevenção de sobreposição é transacional no serviço e deve ser usada por
  toda escrita de vínculo;
- não há interface, incidente, consequência financeira ou inferência de
  alocação nesta tarefa;
- validação automatizada não equivale a validação operacional em campo.

## Consequence Engine v0.1

O serviço `api_tcc.services.consequence.avaliar` avalia um `Event` sob a regra
versionada `consequence-v0.1`. O contrato retornado contém `afetados`,
`risco_parada`, `horizonte_minutos`, `horizonte_tipo`, `premissas`, `faltantes`,
`confianca` e `needs_verification`. `horizonte_minutos` é nulo quando a série
não é elegível; não representa previsão de falha nem tempo garantido até parada.

### Regras e parâmetros

- Tipos elegíveis para risco são `TEMP_ALTA`, `ANOMALIA_ML` e
  `VIBRACAO_ALTA`, somente com severidade `CRITICO`.
- Evidência `boa` resulta em risco `alto`; `suspeita` resulta em `medio` e
  mantém `needs_verification`; `insuficiente` mantém `desconhecido`.
- A tendência usa temperatura da mesma `Machine`, janela de 30 minutos e no
  mínimo 3 pontos válidos. `R2_MIN=0.80`, inclinação positiva e limite crítico
  cadastrado em `MachineSpec.limites_json.temperatura.critico` são obrigatórios.
- A inclinação é medida em °C/min e o horizonte é
  `(limite - valor_atual) / inclinacao`, rotulado como estimativa por
  extrapolação linear. Cada cálculo inclui pontos, janela, inclinação, R² e
  limite na lista de premissas.
- Capacidade nominal de transbordo não produz cálculo de espera nesta versão;
  sua ausência aparece em `faltantes`.

O endpoint é `GET /api/events/<event_id>/consequence/` e respeita o conjunto de
máquinas da organização do usuário. Uma falha na consulta do grafo não é
tratada como grafo vazio.
