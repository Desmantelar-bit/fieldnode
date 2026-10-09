# Attention Engine v0.1

O `Event.priority_score` é uma heurística determinística para ordenar atenção
humana. Ele não substitui `Event.severidade`, não elimina eventos e não é uma
probabilidade de falha mecânica.

## Fórmula

`P = S × I × U × C`, com todos os fatores limitados a `[0, 1]`:

- `S`: `NORMAL=0.00`, `ATENCAO=0.50`, `CRITICO=1.00`.
- `I`: peso fixo por tipo: `TEMP_ALTA=1.00`, `VIBRACAO_ALTA=0.80`,
  `ANOMALIA_ESTATISTICA=0.75`, `ANOMALIA_ML=0.70`, `TENDENCIA_RISCO=0.60`.
  Tipo desconhecido usa `0.25`, de forma conservadora.
- `U`: atualidade da condição, com decaimento linear em 24 horas a partir da
  última leitura anterior da mesma máquina. Uma condição nova recebe `1.00`.
  Se houver agravamento na métrica comparável, a urgência pode permanecer alta.
- `C`: `trust_score` da leitura de origem, copiado para
  `Event.trust_score_herdado`. Ausência ou valor inválido vira `0.00`.

A multiplicação é intencional: qualquer fator zero zera o score. Isso reduz a
prioridade, mas nunca apaga nem reclassifica o evento factual.

Os pesos, a janela de 24 horas e as escalas de agravamento são hipóteses de
projeto v0.1, não calibração com dados operacionais rotulados.

## Persistência e compatibilidade

Eventos criados pelos fluxos atuais de temperatura crítica e anomalia estatística
recebem o score no momento da criação. A migração adiciona o campo como
`NULL=True`; eventos históricos não recebem valor artificial porque o histórico
necessário pode não existir. Deduplicação e cooldown continuam sendo aplicados
antes da criação do evento.

## Reprodução da distribuição

Com o ambiente Django configurado, a distribuição persistida pode ser consultada
sem recalcular o histórico:

```bash
python manage.py shell -c "from django.db.models import Avg, Min, Max, Count; from api_tcc.models import Event; qs=Event.objects.exclude(priority_score__isnull=True); print(qs.count(), qs.aggregate(min=Min('priority_score'), max=Max('priority_score'), avg=Avg('priority_score'))); print(list(qs.values('severidade').annotate(total=Count('id'))))"
```

Para uma amostra, use `order_by('priority_score')[:3]` e
`order_by('-priority_score')[:3]`. Os dados devem ser identificados como reais,
de teste ou sintéticos; nenhum conjunto é ampliado artificialmente para chegar
a 800 eventos.

O Priority Score v0.1 é uma heurística determinística e explicável. Seus pesos
e limiares ainda não foram calibrados com dados operacionais rotulados de campo.
A pontuação serve para priorização experimental, não para estimar uma
probabilidade real de falha mecânica.
