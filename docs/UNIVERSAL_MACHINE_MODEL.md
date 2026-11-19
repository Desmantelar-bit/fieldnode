# Modelo universal de máquina

## Proveniência canônica

`CanonicalTelemetry` preserva o valor canônico junto com `origem`, `fonte`,
`unidade_original`, `fator_conversao`, `offset_conversao` e `mapping_version`.

`origem` é controlada no backend: `medido`, `calculado`, `estimado` ou
`simulado`. Ela não é sinônimo de qualidade. `fonte` descreve o transporte ou
referência disponível, como `sensor:simulado` ou `j1939:pgn=61444:spn=190`.

Valores históricos recebem `origem=simulado` na migration 0058 como uma
classificação conservadora para completar o contrato. Isso não prova que cada
registro antigo foi produzido por um simulador. A unidade original vazia
continua explicitamente desconhecida.

## Conversões

As regras ficam em `api_tcc/services/conversoes.py`, indexadas por grandeza,
unidade de origem e unidade de destino. Atualmente há °F→°C e psi→kPa. A
temperatura usa fator e offset, portanto não é reduzida a uma multiplicação
enganosa. Unidade ausente, desconhecida ou incompatível impede a criação do
valor canônico e mantém o bruto com `quality=unsupported_unit`.

Para adicionar uma regra, registre a grandeza física, unidades, fator, offset e
versão na tabela declarativa, associe o parâmetro canônico à unidade de destino
e crie testes com valores conhecidos. Não use uma regra genérica para converter
grandezas diferentes.

## J1939 no backend

`api_tcc/services/j1939.py` é puro Python. Ele extrai PGN de identificadores
CAN estendidos de 29 bits, diferencia PDU1/PDU2, extrai campos little-endian
LSB-first e preserva estados `unavailable`, `error` e `unsupported` sem
transformá-los em números físicos.

A tabela versionada é `api_tcc/adapters/j1939_pgn_table.json`. Esta entrega
implementa somente:

| PGN | SPN | Parâmetro | Unidade |
| ---: | ---: | --- | --- |
| 61444 / EEC1 | 190 | rotação do motor | rpm |
| 65262 / ET1 | 110 | temperatura do líquido | C |
| 65263 / EFLP1 | 100 | pressão do óleo | kPa |

As fontes públicas registradas na própria tabela são o FMS-Standard para
SPN 190, uma publicação que reproduz a definição J1939/71 para SPN 110 e o
guia BridgeWay para SPN 100. Elas servem como referências públicas de
implementação, não como certificação da SAE nem como integração com Case,
John Deere ou outro fabricante.

Os vetores em `api_tcc/tests/test_j1939.py` são calculados a partir dessas
definições e cobrem PDU1/PDU2, offset, escala, indisponível, erro, PGN
desconhecido, payload inválido e geometria da tabela. A revisão independente
da tabela ainda está pendente; a tabela não deve ser chamada de revisada até
que outra pessoa confira linha a linha fonte, bits, escala e vetores.

O decoder não persiste nem descarta o quadro bruto. A integração com um
gateway deve persistir o payload primeiro em `RawTelemetry`, depois mapear os
`Param` decodificados para a normalização, mantendo a origem física ou
simulada informada pelo gateway. Não há endpoint de transmissão CAN nesta
entrega.

## SDK de adaptadores

O contrato puro está em `api_tcc/adapters/base.py`. Um adaptador implementa
`_parse(payload)`, `fingerprint()` e usa `Adapter.parse(payload)` como entrada
pública. A saída passa por `validar_param`, que reutiliza `sensor_limits` para
os parâmetros que possuem faixa física. Registro é explícito por código com
`@register("manufacturer_id")`; o payload não escolhe módulos nem executa
código.

Há dois formatos autorais demonstrativos em `api_tcc/adapters/examples.py`:

- `demo_metrics_v1`: métricas agrupadas por nome.
- `demo_readings_v1`: lista de leituras nomeadas.

Ambos são formatos demonstrativos inspirados em padrões públicos de
telemática. Não são APIs oficiais, integrações homologadas ou formatos reais
de fabricantes. Campos desconhecidos retornam `Param(status="unsupported")`
com referência ao campo e valor bruto, enquanto os campos válidos continuam
seguindo o pipeline.

### Pesquisa AEMP / ISO 15143-3

Consulta realizada em 19/11/2026. A norma ISO/TS 15143-3 descreve respostas
XML ou JSON e um modelo de acesso protegido, mas a própria especificação
indica que o provedor entrega credenciais após o registro da frota. A
[referência pública do AEMP](https://cdn.ymaws.com/aemp.site-ym.com/resource/resmgr/AEMP_Technology_Support_Guid.pdf)
descreve a evolução do padrão e OAuth2. Documentações de provedores confirmam
que o acesso operacional depende de credenciais, organização, assinatura ou
configuração do fornecedor, por exemplo a [documentação John Deere](https://developer.deere.com/dev-docs/aemp)
e a [API Bobcat](https://developer.bobcat.com/).

Por isso, um adaptador AEMP permanece `ARCHITECT_NOW`. O FieldNode não possui
credenciais, contrato de provedor, endpoint autorizado nem teste de resposta
real para implementá-lo com honestidade. A futura implementação precisará de
provedor escolhido, contrato de acesso, OAuth2, schemas XML/JSON, paginação,
limites de consulta, mapeamento de elementos e evidência autorizada.

## Conformidade controlada

`api_tcc/tests/test_umm_conformidade.py` cruza três caminhos reais: decoder
J1939, `demo_metrics_v1` e `demo_readings_v1`. RPM de referência 2000 e
temperatura de referência 80 C são representados por cada formato, passam por
`RawTelemetry` e `normalizar`, e chegam a `CanonicalTelemetry` com os mesmos
parâmetros, unidades e valores dentro de tolerância de 0,001. A tolerância é
menor que a resolução do exemplo e cobre somente erro numérico de ponto
flutuante; não é uma margem de equivalência de sensores.

A origem permanece distinta: J1939 é `medido` no teste controlado e os dois
formatos autorais são `simulado`. O resultado demonstra convergência de
representação canônica em bancada de software, não interoperabilidade validada
com máquinas, OEMs ou sensores reais.
