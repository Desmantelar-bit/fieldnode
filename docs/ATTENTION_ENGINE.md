# Attention Engine v0.2

`Event.priority_score` é uma heurística determinística de atenção humana. Não é probabilidade de falha mecânica e não substitui a severidade contratual `severity.v1`.

## Dimensões separadas

- **Severidade (`S`)**: gravidade classificada pelos limiares do contrato de severidade vigente. Esta tarefa não muda os limiares.
- **Qualidade da evidência**: rótulo da confiança herdada da leitura: `boa`, `suspeita` ou `insuficiente`.
- **Necessidade de verificação**: selo operacional derivado como `needs_verification = evidence_quality != "boa"`.
- **Impacto (`I`)**: peso heurístico conforme o tipo do evento.
- **Urgência (`U`)**: atualidade e agravamento calculados com o histórico da máquina.
- **Prioridade**: posição operacional calculada por `priority_score`.

## Fórmula oficial

`priority_score = clamp(severidade × impacto × urgência, 0, 1)`.

`S`: `NORMAL=0.00`, `ATENCAO=0.50`, `CRITICO=1.00`.

`I`: `TEMP_ALTA=1.00`, `VIBRACAO_ALTA=0.80`, `ANOMALIA_ESTATISTICA=0.75`, `ANOMALIA_ML=0.70`, `TENDENCIA_RISCO=0.60`; tipo desconhecido usa `0.25`.

`U`: leitura nova recebe `1.00`; a atualidade decai linearmente em 24 horas, e agravamento pode manter urgência alta. Não estima tempo até falha.

Trust Score **não** entra na multiplicação nem rebaixa score. A listagem da API ordena por `priority_score DESC`; criação mais recente e ID são desempates estáveis. `needs_verification` é um selo, não um critério de ordem.

## Qualidade da evidência

Os limites são heurísticos calibráveis, ainda sem calibração por dados operacionais rotulados:

- `trust >= 0.8`: `boa`;
- `0.5 <= trust < 0.8`: `suspeita`;
- `trust < 0.5`, ausente, não finito ou fora de `[0, 1]`: `insuficiente`.

`needs_verification = evidence_quality != "boa"`. O valor desconhecido não é promovido a evidência boa. Os limites devem ser revistos com dados reais.

## Exemplo operacional: sensor em 120 °C

Se o contrato classificar a leitura como crítica e o Trust Score for baixo, o evento permanece crítico e sua prioridade continua sendo calculada por severidade, impacto e urgência. A qualidade será insuficiente e `needs_verification` será verdadeiro, sinalizando verificar o sensor. Isso não confirma uma falha mecânica; indica um alerta grave cuja evidência precisa ser investigada.

Sensores ruins podem gerar muitos eventos que demandam atenção. O cooldown existente continua ativo; agrupamento por máquina na UI está reservado para S3-T5.

## Persistência e compatibilidade

Eventos novos persistem score e qualidade no momento da criação. Registros anteriores recebem `evidence_quality=insuficiente` e `needs_verification=True`, sem reclassificar severidade histórica. Eventos históricos mantêm score nulo se não houver contexto confiável para reconstrução.

Pesos de impacto, janela temporal e escalas de agravamento são hipóteses de projeto, não medições de campo.

## Reprodução da distribuição

Com Django configurado, consulte distribuição e extremos sem recalcular histórico:

```bash
python manage.py shell -c "from django.db.models import Avg, Min, Max, Count; from api_tcc.models import Event; qs=Event.objects.exclude(priority_score__isnull=True); print(qs.count(), qs.aggregate(min=Min('priority_score'), max=Max('priority_score'), avg=Avg('priority_score'))); print(list(qs.values('severidade').annotate(total=Count('id'))))"
```
