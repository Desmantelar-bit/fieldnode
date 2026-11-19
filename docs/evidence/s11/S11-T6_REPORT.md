# S11-T6 - Data Passport v0.1

## Entrega

- `api_tcc/services/passport.py` implementa ZIP versionado com `manifest.json`, `telemetry.csv`, `events.json`, `decisions.json`, `work_orders.json`, `provenance.json` e `FORMAT.md`.
- A telemetria usa CSV UTF-8 com schema fixo e leitura em batches (`iterator`); Parquet não foi adicionado para evitar dependência e duplicação de formato no v0.1.
- O manifesto registra escopo, intervalo solicitado/incluído, contagens, tamanhos, hashes SHA-256, limitações e assinatura HMAC-SHA256 configurável por `FIELDNODE_PASSPORT_SIGNING_KEY`.
- O importador valida ZIP, traversal, versão, arquivos declarados, hashes e assinatura configurada antes da transação. Importação sem assinatura exige `allow_unsigned=True` explícito.
- Colisões de IDs e chaves de idempotência são remapeadas de forma determinística para não substituir dados existentes; isso fica refletido na organização de destino e não é restauração irrestrita.
- `exportar_passport` fornece a operação administrativa por organização/máquina.

## Evidência executada

```text
venv\Scripts\python.exe manage.py test api_tcc.tests.test_s11_passport_v1 --verbosity 1
Ran 3 tests ... OK
```

O teste cobre exportar, validar assinatura/hashes, importar com eventos/decisões/OS e comparar contagens; também verifica que o ZIP não contém caminhos extras nem segredo de política.

## Limitações

- A assinatura atual é HMAC-SHA256, dependente de uma chave confiável configurada no ambiente. Sem chave, o pacote é explicitamente não assinado.
- Anexos externos e evidências em filesystem não são copiados; a limitação está no manifesto.
- Isto comprova portabilidade e integridade da representação exportada, não a veracidade física das medições.
