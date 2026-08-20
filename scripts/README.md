# Scripts do FieldNode

Scripts utilitários para gerenciar o sistema.

## Scripts Principais

### `limpar_banco.py`
Limpa completamente o banco de dados, removendo todos os dados em ordem correta de dependências.

```bash
# Docker
docker compose exec web python scripts/limpar_banco.py

# Local
python scripts/limpar_banco.py
```

### `popular_banco.py`
Script oficial para popular o banco com dados de teste. Cria:
- 3 colheitadeiras (COLH-01, COLH-02, COLH-03)
- 3 operários (João Silva, Maria Santos, Pedro Costa)
- 3 marcas e modelos (Case IH TC5000, John Deere S780, New Holland CR9090)
- Unidades de medida e dependências

```bash
# Docker
docker compose exec web python scripts/popular_banco.py

# Local
python scripts/popular_banco.py
```

## Scripts de Teste

### `teste_fluxo_completo.py`
Valida o fluxo completo de ingestão e consulta de telemetria.

### `validar_sistema.py`
Valida a estrutura de arquivos do projeto.

### `simular_mqtt.py`
Simula envio de telemetria via MQTT para testes.

### `stress_test.py`
Teste de carga para a API de ingestão.

## Fluxo Recomendado

1. Limpar o banco:
```bash
docker compose exec web python scripts/limpar_banco.py
```

2. Popular com dados:
```bash
docker compose exec web python scripts/popular_banco.py
```

3. Validar funcionamento:
```bash
docker compose exec web python scripts/teste_fluxo_completo.py
```
