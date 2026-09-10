# Adição de ID Sequencial ao FieldNode

## 📋 Resumo da Implementação

Foi adicionado um campo `seq_id` (ID sequencial) ao modelo `LeituraTelemetria`, mantendo o UUID como chave primária para preservar a arquitetura offline-first.

## 🎯 Objetivo

Fornecer um identificador numérico legível para humanos (ex: #1, #2, #3...) enquanto mantém o UUID para garantir:
- Idempotência na sincronização offline
- Deduplicação de leituras
- Suporte a múltiplos gateways simultâneos

## 🔧 Alterações Realizadas

### 1. Model (`api_tcc/models.py`)

```python
class LeituraTelemetria(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    seq_id      = models.BigIntegerField(unique=True, editable=False, verbose_name='ID Sequencial', null=True)
    # ... outros campos
    
    def save(self, *args, **kwargs):
        if self.seq_id is None:
            ultimo = LeituraTelemetria.objects.order_by('-seq_id').first()
            self.seq_id = (ultimo.seq_id + 1) if ultimo and ultimo.seq_id else 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'#{self.seq_id} — {self.maquina_id} — {self.temperatura}°C — {self.timestamp}'
```

**Características:**
- `BigIntegerField`: Suporta até 9.223.372.036.854.775.807 registros
- `unique=True`: Garante que não haverá IDs duplicados
- `editable=False`: Não pode ser alterado manualmente
- `null=True`: Permite registros antigos sem seq_id (migração suave)
- Auto-incremento no método `save()`: Gera próximo número automaticamente

### 2. Serializer (`api_tcc/api/serializers.py`)

```python
class LeituraTelemetriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeituraTelemetria
        fields = '__all__'
        extra_kwargs = {
            'id':          {'read_only': True},
            'seq_id':      {'read_only': True},  # ← NOVO
            'recebido_em': {'read_only': True},
        }
```

**Resultado:** A API agora retorna o `seq_id` em todas as respostas JSON.

### 3. Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

**Arquivo gerado:** `api_tcc/migrations/0003_delete_prescricao_and_more.py`

### 4. Script de População (`scripts/popular_seq_id.py`)

Script para popular o `seq_id` em registros existentes (executado uma única vez):

```bash
python scripts/popular_seq_id.py
```

**Resultado:** 10.101 registros atualizados com sucesso.

## 📊 Exemplo de Uso

### Resposta da API (antes):
```json
{
  "id": "a3f2c8d1-4b5e-6789-abcd-ef0123456789",
  "maquina_id": "CASE-TC5000-01",
  "temperatura": 78.5,
  "vibracao": 0.42,
  "rpm": 1850
}
```

### Resposta da API (depois):
```json
{
  "id": "a3f2c8d1-4b5e-6789-abcd-ef0123456789",
  "seq_id": 1234,
  "maquina_id": "CASE-TC5000-01",
  "temperatura": 78.5,
  "vibracao": 0.42,
  "rpm": 1850
}
```

### Admin Django (antes):
```
CASE-TC5000-01 — 78.5°C — 2024-04-23 14:32:01
```

### Admin Django (depois):
```
#1234 — CASE-TC5000-01 — 78.5°C — 2024-04-23 14:32:01
```

## 🎨 Onde Usar o seq_id

### ✅ Recomendado:
- **Dashboard/UI**: Mostrar "#1234" é mais amigável que UUID
- **Relatórios**: Referência rápida para operadores
- **Logs de debug**: Facilita rastreamento
- **Suporte técnico**: Cliente pode dizer "problema no registro #5678"

### ❌ NÃO usar:
- **Sincronização offline**: Continue usando UUID
- **Deduplicação**: UUID é a chave primária
- **APIs externas**: UUID garante unicidade global

## 🔐 Arquitetura Preservada

| Aspecto | UUID (id) | Sequencial (seq_id) |
|---------|-----------|---------------------|
| **Chave Primária** | ✅ Sim | ❌ Não |
| **Gerado no ESP32** | ✅ Sim | ❌ Não |
| **Idempotência** | ✅ Sim | ❌ Não |
| **Legível** | ❌ Não | ✅ Sim |
| **Uso em UI** | ❌ Não | ✅ Sim |
| **Sincronização** | ✅ Sim | ❌ Não |

## 📝 Notas Técnicas

1. **Thread-safety**: O método `save()` não é 100% thread-safe. Em produção com alta concorrência, considerar usar `F()` expressions ou sequences do banco.

2. **Performance**: O auto-incremento adiciona 1 query extra por inserção. Para ingestão em massa, considerar usar `bulk_create()` com pré-cálculo dos seq_ids.

3. **Migração**: Registros antigos podem ter `seq_id=None` até rodar o script de população.

4. **Backup**: Antes de aplicar em produção, fazer backup do banco de dados.

## 🚀 Próximos Passos (Opcional)

### Melhorias Futuras:

1. **Usar Database Sequence (PostgreSQL/MySQL 8+)**:
```python
from django.db.models import Sequence

seq_id = models.BigIntegerField(
    unique=True, 
    editable=False,
    default=Sequence('leitura_seq_id')
)
```

2. **Adicionar seq_id ao Frontend**:
```javascript
// dashboard.js
function renderLeitura(leitura) {
    return `
        <div class="leitura-card">
            <span class="seq-badge">#${leitura.seq_id}</span>
            <span class="maquina">${leitura.maquina_id}</span>
            ...
        </div>
    `;
}
```

3. **Filtro por seq_id na API**:
```python
# views_ingestao.py
def get(self, request):
    seq_id = request.query_params.get('seq_id')
    if seq_id:
        leituras = leituras.filter(seq_id=seq_id)
```

## ✅ Checklist de Validação

- [x] Campo `seq_id` adicionado ao model
- [x] Migration criada e aplicada
- [x] Serializer atualizado
- [x] Registros existentes populados (10.101 registros)
- [x] Método `__str__` atualizado para mostrar seq_id
- [x] UUID mantido como chave primária
- [x] Arquitetura offline-first preservada

## 📚 Referências

- **Django BigIntegerField**: https://docs.djangoproject.com/en/5.0/ref/models/fields/#bigintegerfield
- **UUID vs Auto-increment**: https://www.percona.com/blog/uuids-are-popular-but-bad-for-performance/
- **Offline-First Architecture**: https://offlinefirst.org/

---

**Data de Implementação:** 2024
**Autor:** Equipe FieldNode
**Status:** ✅ Concluído e Testado
