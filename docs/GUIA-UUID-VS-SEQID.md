# Guia Rápido: UUID vs seq_id

## 🎯 Quando Usar Cada Um?

### UUID (id) - Chave Primária
```python
# ✅ USE para:
leitura = LeituraTelemetria.objects.get(id="a3f2c8d1-4b5e-6789-abcd-ef0123456789")
LeituraTelemetria.objects.filter(id__in=lista_uuids)

# ✅ Sincronização offline
payload = {
    "id": str(uuid.uuid4()),  # Gerado no ESP32
    "maquina_id": "COLH-01",
    ...
}

# ✅ Deduplicação
if LeituraTelemetria.objects.filter(id=payload['id']).exists():
    return "duplicata"
```

### seq_id - ID Legível
```python
# ✅ USE para:
# Dashboard/UI
print(f"Leitura #{leitura.seq_id}")

# Relatórios
print(f"Registros processados: #{inicio_seq} até #{fim_seq}")

# Logs amigáveis
logger.info(f"Processando leitura #{leitura.seq_id} da máquina {leitura.maquina_id}")

# Busca por número
leitura = LeituraTelemetria.objects.get(seq_id=1234)
```

## 📊 Comparação Rápida

| Cenário | Use UUID | Use seq_id |
|---------|----------|------------|
| ESP32 gerando dados offline | ✅ | ❌ |
| Mostrar na tela para operador | ❌ | ✅ |
| Chave estrangeira | ✅ | ❌ |
| Relatório impresso | ❌ | ✅ |
| API externa | ✅ | ❌ |
| Suporte técnico | ❌ | ✅ |
| Deduplicação | ✅ | ❌ |
| Ordenação cronológica | ❌ | ✅ |

## 💡 Exemplos Práticos

### Frontend (Dashboard)
```javascript
// ❌ Antes (UUID confuso)
<div>ID: a3f2c8d1-4b5e-6789-abcd-ef0123456789</div>

// ✅ Depois (seq_id legível)
<div>Leitura #1234</div>
```

### Relatório CSV
```csv
# ❌ Antes
ID,Máquina,Temperatura
a3f2c8d1-4b5e-6789-abcd-ef0123456789,COLH-01,78.5

# ✅ Depois
Seq,ID,Máquina,Temperatura
1234,a3f2c8d1-4b5e-6789-abcd-ef0123456789,COLH-01,78.5
```

### Suporte Técnico
```
❌ Cliente: "Tem um erro no registro a3f2c8d1-4b5e-6789-abcd-ef0123456789"
   Suporte: "Pode repetir o ID?"

✅ Cliente: "Tem um erro no registro #1234"
   Suporte: "Encontrado! Analisando..."
```

## 🔧 Comandos Úteis

```bash
# Ver últimas 10 leituras com seq_id
python manage.py shell
>>> from api_tcc.models import LeituraTelemetria
>>> LeituraTelemetria.objects.values('seq_id', 'maquina_id', 'temperatura')[:10]

# Buscar por seq_id
>>> leitura = LeituraTelemetria.objects.get(seq_id=1234)
>>> print(leitura)
#1234 — CASE-TC5000-01 — 78.5°C — 2024-04-23 14:32:01

# Contar registros
>>> LeituraTelemetria.objects.count()
10101
```

## ⚠️ Importante

**NUNCA:**
- ❌ Usar seq_id como chave primária
- ❌ Enviar seq_id do ESP32
- ❌ Usar seq_id para deduplicação
- ❌ Expor apenas seq_id em APIs públicas

**SEMPRE:**
- ✅ Manter UUID como chave primária
- ✅ Gerar UUID no ESP32
- ✅ Usar UUID para sincronização
- ✅ Usar seq_id apenas para exibição

---

**Regra de Ouro:** UUID para máquinas, seq_id para humanos.
