# seq_id — Documentação Consolidada

**Status:** Feature histórica — **revertida em agosto de 2026**.

Este documento consolida as informações distribuídas anteriormente nos seguintes
arquivos (preservados em `docs/archive/`):

- `ADICAO-SEQ-ID.md`
- `RESUMO-SEQID.md`
- `CONFIRMACAO-SEQID-MQTT.md`
- `CONFIRMACAO-MQTT-PRONTO.md`
- `CORRECAO-SEQID-MQTT.md`
- `GUIA-UUID-VS-SEQID.md`

---

## Definição

`seq_id` era um campo `BigIntegerField` adicionado ao model `LeituraTelemetria`
para fornecer um identificador numérico legível por humanos (ex.: `#1`, `#2`,
`#3...`), enquanto o UUID permanecia como chave primária.

---

## Objetivo original

Fornecer um ID curto e legível para uso em:

- Dashboard / UI (ex.: "Leitura #1234" em vez de um UUID)
- Relatórios para operadores
- Logs de debug
- Comunicação de suporte técnico

O UUID era e continua sendo o identificador técnico para sincronização offline,
deduplicação e integridade de dados.

---

## Implementação histórica

### Campo no model (`api_tcc/models.py`)

```python
class LeituraTelemetria(models.Model):
    id     = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    seq_id = models.BigIntegerField(
        unique=True, editable=False,
        verbose_name='ID Sequencial', null=True
    )
    # ...

    def save(self, *args, **kwargs):
        if self.seq_id is None:
            ultimo = LeituraTelemetria.objects.order_by('-seq_id').first()
            self.seq_id = (ultimo.seq_id + 1) if ultimo and ultimo.seq_id else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'#{self.seq_id} — {self.maquina_id} — {self.temperatura}°C — {self.timestamp}'
```

**Características do campo:**

| Atributo | Valor | Motivo |
|---|---|---|
| Tipo | `BigIntegerField` | Suporta até 9.2×10¹⁸ registros |
| `unique=True` | Sim | Sem duplicatas |
| `editable=False` | Sim | Não editável via admin/API |
| `null=True` | Sim | Migração suave de registros antigos |
| Auto-incremento | Via `save()` | Sem depender de AutoField |

### Serializer

```python
class LeituraTelemetriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeituraTelemetria
        fields = '__all__'
        extra_kwargs = {
            'id':          {'read_only': True},
            'seq_id':      {'read_only': True},
            'recebido_em': {'read_only': True},
        }
```

A API retornava `seq_id` em todas as respostas JSON.

### Migration de adição

`api_tcc/migrations/0003_delete_prescricao_and_more.py` — adicionou o campo.

### Script de população retroativa

`scripts/popular_seq_id.py` (arquivo histórico, removido) populava `seq_id` em
registros existentes. Resultado reportado: 10.101 registros atualizados.

---

## Correção crítica durante a implementação

**Problema identificado:** Inserções via MQTT usavam `.create()`, que em certos
cenários bypassa o método `save()` customizado, deixando `seq_id = None`.

**Solução aplicada:** Mudança em `api_tcc/services/telemetria.py` de:

```python
# ❌ Antes — bypassa save() em alguns cenários
leitura = LeituraTelemetria.objects.create(...)
```

para:

```python
# ✅ Depois — garante execução do save() customizado
leitura = LeituraTelemetria(...)
leitura.save()
```

> [!NOTE]
> Essa mudança (`create` → instanciação + `save`) está **mantida no código atual**
> em `api_tcc/services/telemetria.py`, mesmo após a remoção do `seq_id`. O padrão
> é correto independentemente do `seq_id` e não deve ser revertido.

---

## Relação com UUID

| Aspecto | UUID (`id`) | Sequencial (`seq_id`) |
|---|---|---|
| Chave primária | ✅ Sim | ❌ Não |
| Gerado no ESP32 | ✅ Sim | ❌ Não |
| Idempotência/dedup | ✅ Sim | ❌ Não |
| Legível por humanos | ❌ Não | ✅ Sim |
| Uso em UI | ❌ Não recomendado | ✅ Sim |
| Sincronização offline | ✅ Sim | ❌ Nunca |

**Regra de ouro:** UUID para máquinas; seq_id para humanos.

---

## Relação com MQTT

O `seq_id` era atribuído no servidor no momento da inserção. O ESP32 **nunca**
enviava `seq_id` no payload. O fluxo MQTT era:

```
ESP32 → MQTT Broker → mqtt_listen → services/telemetria.py → .save() → seq_id gerado
```

Duplicatas detectadas pelo UUID não geravam novo `seq_id`. Payloads inválidos
também não consumiam `seq_id`.

---

## Limitações técnicas documentadas

1. **Thread-safety:** O método `save()` não era 100% thread-safe. Com múltiplos
   workers MQTT simultâneos, podia haver race condition no cálculo do próximo
   `seq_id`, podendo resultar em `IntegrityError` (unique constraint), tratado
   pela camada de serviço com retentativa implícita.

2. **`bulk_create()` bypassa `save()`:** Inserções em massa com `bulk_create`
   também não acionavam o método customizado. Requeria pré-cálculo manual dos
   `seq_id`s:

   ```python
   ultimo = LeituraTelemetria.objects.order_by('-seq_id').first()
   seq_atual = (ultimo.seq_id + 1) if ultimo else 1
   leituras = []
   for dados in batch:
       leituras.append(LeituraTelemetria(seq_id=seq_atual, ...))
       seq_atual += 1
   LeituraTelemetria.objects.bulk_create(leituras)
   ```

3. **Performance:** O auto-incremento via `save()` adicionava 1 query extra por
   inserção (buscar o último `seq_id`). Para ingestão em massa, isso seria um
   gargalo.

---

## Decisões registradas

- **UUID permanece como chave primária** — nenhuma mudança para facilitar uso
  de `seq_id`.
- **`seq_id` não deve ser enviado pelo ESP32** — é responsabilidade do servidor.
- **`seq_id` não deve ser usado para sincronização ou deduplicação** — apenas
  para exibição.
- Migração adotou `null=True` para compatibilidade retroativa.

---

## Estado atual — divergência com a documentação histórica

> [!WARNING]
> **`seq_id` foi removido do model em agosto de 2026.**
>
> A migration `api_tcc/migrations/0009_remove_leituratelemetria_seq_id.py`
> (gerada em 2026-08-14) executou:
>
> ```python
> migrations.RemoveField(
>     model_name='leituratelemetria',
>     name='seq_id',
> )
> ```
>
> O model `LeituraTelemetria` **não possui mais o campo `seq_id`**.
>
> O teste `api_tcc/tests/test_telemetria.py` (linha 97) confirma:
>
> ```python
> self.assertNotIn("seq_id", serialized)
> ```
>
> A documentação histórica preservada em `docs/archive/` descreve o sistema
> **durante a fase em que `seq_id` estava ativo**. Ela não descreve o estado atual.

### Consequências do estado atual

- A API **não retorna `seq_id`** nas respostas.
- O Django Admin **não exibe `seq_id`**.
- O `__str__` de `LeituraTelemetria` usa UUID: `#<uuid> — <maquina_id> — ...`.
- `scripts/popular_seq_id.py` e `api_tcc/management/commands/popular_seq_id.py`
  foram removidos junto com o campo.

---

## Melhorias futuras (caso seq_id seja reimplementado)

Se `seq_id` for readicionado em versão futura, considerar:

1. **Database Sequence (PostgreSQL)** em vez de método `save()` — elimina o
   problema de thread-safety.
2. **Filtro na API** por `seq_id` para facilitar busca por operadores.
3. **Exibição no frontend** para melhor UX do operador.

---

*Consolidado em S1-T4 (setembro de 2026) a partir de 6 documentos históricos
arquivados em `docs/archive/`.*
