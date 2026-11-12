# Attention Engine v0.2

O `Event.priority_score` é uma heurística determinística para ordenar atenção
humana. Ele não substitui `Event.severidade`, não elimina eventos e não é uma
probabilidade de falha mecânica.

---

## Separação conceitual obrigatória

O motor de atenção trata três conceitos de forma completamente independente:

| Conceito | Campo | Pergunta respondida |
|---|---|---|
| **Severidade** | `Event.severidade` | Quão grave é a ocorrência operacional? |
| **Qualidade da evidência** | `Event.evidence_quality` | O quanto podemos confiar nos dados que originaram o evento? |
| **Prioridade de atenção** | `Event.priority_score` | Com que urgência este evento exige atenção? |

**Regra inviolável:** a qualidade da evidência nunca reduz a prioridade de um
evento potencialmente grave. Um sensor com comportamento suspeito não torna uma
temperatura crítica menos urgente — torna a ocorrência inconclusiva e exige
verificação.

Exemplo central: temperatura de 120 °C com trust_score 0.20.
- `severidade`: CRITICO — a regra operacional não muda.
- `priority_score`: elevado — calculado sem participação do trust.
- `evidence_quality`: insuficiente — sensor suspeito, não confiável.
- `needs_verification`: true — precisa ser conferido no campo.

Esconder uma ocorrência grave porque o sensor está com problema é
exatamente o tipo de falha que o sistema deve prevenir.

---

## Fórmula do Priority Score

```
priority_score = S × I × U
```

Todos os fatores são limitados a `[0, 1]`. O `trust_score` não participa
da multiplicação.

### Severidade (S)

| `Event.severidade` | Valor |
|---|---|
| `NORMAL`  | 0.00 |
| `ATENCAO` | 0.50 |
| `CRITICO` | 1.00 |

### Impacto operacional (I)

Peso fixo por tipo de evento, estimado antes de ter dados operacionais rotulados.
Estes valores são hipóteses v0.1 — precisam ser recalibrados com dados reais de campo.

| `Event.tipo` | Valor |
|---|---|
| `TEMP_ALTA`             | 1.00 |
| `VIBRACAO_ALTA`         | 0.80 |
| `ANOMALIA_ESTATISTICA`  | 0.75 |
| `ANOMALIA_ML`           | 0.70 |
| `TENDENCIA_RISCO`       | 0.60 |
| Tipo desconhecido       | 0.25 (conservador, sem criar falso alarme de P1) |

### Urgência (U)

Atualidade da condição, com decaimento linear em 24 horas a partir da última
leitura anterior da mesma máquina. Uma condição nova (sem histórico) recebe
urgência 1.00. Se houver agravamento observado na métrica comparável, a urgência
pode permanecer alta mesmo com histórico antigo.

A urgência não estima tempo até falha nem altera a severidade do evento.

### Por que a confiança não participa da fórmula

Se o trust_score participasse da multiplicação como fator adicional — por exemplo
`P = S × I × U × T` — um sensor com T=0.20 reduziria o priority_score de um
evento CRITICO em 80%. Isso significa que eventos potencialmente graves
desaparecem da lista de prioridades exatamente quando o sensor está mais
suspeito, que é quando a verificação é mais necessária.

A separação conceitual resolve isso: o trust informa a qualidade da evidência
sem rebaixar a prioridade. O operador recebe "temperatura CRITICO, verificar
sensor" em vez de "temperatura NORMAL (confiança baixa)".

---

## Evidence Quality

Classificação independente da qualidade da evidência derivada do `trust_score`.

```
evidence_quality ∈ {boa, suspeita, insuficiente}
```

### Limiares (heurísticas v0.1)

| Condição | `evidence_quality` |
|---|---|
| `trust_score >= 0.8` | `boa` |
| `trust_score >= 0.5` | `suspeita` |
| `trust_score < 0.5`  | `insuficiente` |
| `trust_score` ausente/None | `insuficiente` |
| `trust_score` inválido (NaN, Inf, string) | `insuficiente` |

**Limitação metodológica:** estes limiares (0.8 e 0.5) são heurísticas de
projeto, não verdades estatísticas. Eles não foram calibrados com dados
operacionais reais de campo. Precisam ser revisados assim que houver histórico
suficiente de eventos com confirmação manual. Não converta dados inválidos em
evidência boa por nenhum motivo.

### Implementação

```python
EVIDENCE_BOA_THRESHOLD = 0.8
EVIDENCE_SUSPEITA_THRESHOLD = 0.5

def evidence_quality(trust: float | None) -> str:
    if trust is None:
        return Event.EvidenceQuality.INSUFICIENTE
    try:
        score = float(trust)
    except (TypeError, ValueError):
        return Event.EvidenceQuality.INSUFICIENTE
    if not math.isfinite(score):
        return Event.EvidenceQuality.INSUFICIENTE
    if score >= EVIDENCE_BOA_THRESHOLD:
        return Event.EvidenceQuality.BOA
    if score >= EVIDENCE_SUSPEITA_THRESHOLD:
        return Event.EvidenceQuality.SUSPEITA
    return Event.EvidenceQuality.INSUFICIENTE
```

---

## Needs Verification

```
needs_verification = (evidence_quality != "boa")
```

| `evidence_quality` | `needs_verification` |
|---|---|
| `boa`          | `false` |
| `suspeita`     | `true` |
| `insuficiente` | `true` |

`needs_verification` é um **selo informativo**, não um fator de priorização.
Ele indica que a ocorrência precisa ser conferida no campo — não que ela é
menos grave ou menos urgente.

Não use `needs_verification` como critério de ordenação na API. A ordenação
correta é sempre `ORDER BY priority_score DESC`.

---

## Comportamento diante de sensores suspeitos

Cenário: temperatura de 120 °C com trust_score de 0.20.

```
severidade:        CRITICO
priority_score:    1.0 × 1.0 × 1.0 = 1.0  (sem decaimento, condição nova)
evidence_quality:  insuficiente  (trust 0.20 < 0.50)
needs_verification: true
```

O evento aparece no topo da lista de prioridades com o selo "verificar sensor".
O operador sabe que: (a) existe uma leitura potencialmente crítica, e (b) o sensor
está suspeito, então precisa verificar fisicamente.

O sistema não tomou a decisão pelo operador de ignorar a ocorrência porque o
sensor tem problema — isso seria um ponto cego operacional.

---

## Campos no banco (Event)

| Campo | Tipo | Descrição |
|---|---|---|
| `priority_score` | `DecimalField(5,4)` | Heurística 0..1 calculada na criação; NULL para eventos históricos |
| `evidence_quality` | `CharField(choices)` | `boa / suspeita / insuficiente` |
| `needs_verification` | `BooleanField` | Derivado de `evidence_quality != boa` |
| `trust_score_herdado` | `FloatField` | Trust Score copiado da leitura de origem |
| `severidade` | `CharField(choices)` | Severidade operacional independente do trust |

---

## API e ordenação

### Campos expostos

`GET /api/events/` retorna por evento:
- `priority_score`
- `evidence_quality`
- `needs_verification`
- `severidade`
- `trust_score_herdado`

### Ordenação

```sql
ORDER BY priority_score DESC NULLS LAST, criado_em DESC
```

`needs_verification` nunca é critério de ordenação. Eventos com evidência
insuficiente têm a mesma prioridade que eventos equivalentes com evidência boa —
o que muda é o selo de verificação, não a posição na lista.

### Filtros disponíveis

- `maquina_id`: filtra por máquina
- `tipo`: filtra por `Event.Tipo`
- `severidade`: filtra por `Event.Severidade`
- `status`: filtra por `Event.Status`
- `page` / `page_size`: paginação (default: 20, max: 100)

---

## Persistência e compatibilidade

Os campos `evidence_quality`, `needs_verification` foram adicionados na migration
`0028_event_evidence_quality` com defaults seguros:
- `evidence_quality`: default `insuficiente`
- `needs_verification`: default `True`

Eventos históricos receberam `evidence_quality=insuficiente` e
`needs_verification=True` porque não há trust_score disponível para
reclassificação retroativa. Isso é conservador e correto: eventos antigos
precisam de verificação antes de qualquer conclusão.

A migration `0028` é reversível pelo Django via `RemoveField` automático
(campos sem lógica personalizada de backward).

---

## Reprodução da distribuição

Com o ambiente configurado (`USE_SQLITE=True` ou banco ativo):

```bash
python manage.py shell -c "
from django.db.models import Avg, Min, Max, Count
from api_tcc.models import Event
qs = Event.objects.exclude(priority_score__isnull=True)
print(qs.count(), qs.aggregate(min=Min('priority_score'), max=Max('priority_score'), avg=Avg('priority_score')))
print(list(qs.values('evidence_quality').annotate(total=Count('id'))))
print(list(qs.values('needs_verification').annotate(total=Count('id'))))
"
```

---

## Limitações e calibração futura

1. **Pesos de impacto operacional** (I) são estimativas sem base em dados rotulados.
   Precisam ser revistos com histórico real de falhas confirmadas.

2. **Urgência temporal** usa decaimento linear em 24h, sem evidência de que
   esse é o horizonte correto para colheitadeiras de cana.

3. **Limiares de evidence_quality** (0.8 e 0.5) são arbitrários. O trust_score
   em si é uma heurística composta que inclui clock_skew, continuidade e
   completude de campos. Antes de calibrar os limiares, o próprio trust_score
   precisa ser validado com eventos de campo rotulados.

4. **Ruído por sensores suspeitos**: a decisão de manter priority_score alto
   para evidências insuficientes pode gerar muitos eventos P1 com
   `needs_verification=True` quando vários sensores de uma máquina estão
   degradados simultaneamente. A mitigação planejada é agrupamento por máquina
   na interface (S3-T5) e cooldown de eventos (já implementado: 15 min).

5. **O Priority Score não é uma probabilidade** de falha mecânica. É uma
   pontuação de priorização operacional heurística, determinística e explicável.
   Não extrapolar para "probabilidade de quebra de 80%" ou similar.
