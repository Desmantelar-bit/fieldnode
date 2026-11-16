# S5-T3 - Regime de operação e baseline contextual

## Status

IMPLEMENTADO EM SOFTWARE, COM CORTES DE BANCADA E LIMITAÇÕES DOCUMENTADAS.

## Regra implementada

`api_tcc/services/regime.py` persiste o regime derivado de RPM e, quando
presente, `velocidade_kmh`:

| condição | regime |
|---|---|
| RPM ausente ou inválido | `desconhecido` |
| RPM < 300 | `desligada` |
| RPM < 1000 e velocidade < 1 km/h | `marcha_lenta` |
| velocidade > 8 km/h e RPM < 1800 | `deslocamento` |
| demais casos válidos | `trabalhando` |

A ausência de velocidade não é tratada como medição zero para fins de
proveniência; o valor zero usado na heurística é apenas o fallback operacional
provisório pedido pelo contrato atual.

## Integração

`LeituraTelemetria` ganhou `velocidade_kmh`, `regime` e `evidence_quality`.
O cache e os artefatos do detector são separados por máquina e regime. Uma
leitura com regime desconhecido retorna estado `inconclusivo` e não gera alerta
mecânico. O detector não reutiliza silenciosamente o modelo de outro regime.

## Meta de falso positivo

Meta provisória, definida antes de qualquer avaliação final do harness:

- `maquina_desligada`: no máximo 0,05 falso positivo por hora;
- `mudanca_de_carga`: no máximo 0,05 falso positivo por hora.

A unidade é falso positivo por hora observada. A meta é de bancada, não foi
validada em campo e não autoriza declarar desempenho operacional.

## Verificação

- testes unitários dos limites e dos estados foram adicionados em
  `api_tcc/tests/test_s5_regime_training.py`;
- os testes existentes de health e cold start passaram;
- o teste legado que esperava um modelo global para uma leitura em outro regime
  ficou incompatível por desenho: uma leitura em `marcha_lenta` não deve ser
  comparada ao modelo de `trabalhando`.

## Limitações

Os cortes são heurísticos e aguardam calibração por modelo de máquina. GPS,
velocidade desatualizada e inconsistência entre RPM e deslocamento ainda são
observabilidade, não diagnóstico. Não há evidência física ou de campo neste
ciclo.
