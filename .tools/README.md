# Ferramentas de desenvolvimento

Scripts utilitários para desenvolvimento e testes locais. Não requeridos para rodar a aplicação.

| Script | Propósito |
|--------|-----------|
| `diagnostico.py` | Verifica integridade do ambiente (BD, MQTT, dependências) |
| `esp_simulator_multi.py` | Simula múltiplos ESP32 enviando telemetria |
| `simular_dados.py` | Popula BD com dados de teste |
| `testar_api.py` | Testa endpoints REST |
| `testar_dashboard.py` | Verifica conectividade do frontend |

## Uso

```bash
# Verificar ambiente
python .tools/diagnostico.py

# Simular ESP32
python .tools/esp_simulator_multi.py

# Popular banco de teste
python .tools/simular_dados.py
```

Todos requerem o virtualenv ativo e `.env` configurado.
