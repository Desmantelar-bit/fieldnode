# S6-T3 - compressao, checksum, agregacao e TTL

## Estado verificado

- O checksum continua sendo SHA-256 do JSON canonico descomprimido. A
  representacao gzip nao muda a identidade da mensagem.
- `compress_batch()` rejeita lote acima de 2 MiB descomprimido ou 512 KiB
  comprimido e `decompress_batch()` valida gzip, limite e hash antes de expor
  os itens.
- A classe C usa estatisticas `mean`, `min`, `max` e `n` por variavel
  numerica, janela de 60 segundos e IDs de origem. A e B nao entram nessa
  agregacao.
- O backend possui `TelemetryAggregate`, separado de `LeituraTelemetria`,
  para nao apresentar uma media como leitura instantanea.
- TTL efetivo no edge: A sem expiracao automatica, B 72 horas e C 14 dias.
  Dados sem referencia temporal confiavel sao preservados. Cada descarte gera
  `storage_events.event_type=discard_ttl`.

## Evidencia executada

Comando:

```powershell
venv\Scripts\python.exe -m unittest simulators.test_s6_t3
```

Resultado observado nesta execucao: `Ran 2 tests ... OK`. O teste controla uma
leitura de 97,4 graus junto de leituras menores e verifica que o maximo nao e
substituido pela media. O mesmo teste valida o hash depois de gzip e registra a
expiracao de B/C mantendo A.

O percentual de reducao depende do lote real. O teste registra
`serialized_bytes` e `compressed_bytes`; nao ha percentual fixo publicado sem
uma medicao do perfil de payload usado no edge.

## Limites

O transporte HTTP legado ainda envia cada item descomprimido por compatibilidade
com `/api/telemetria/`. O codec de lote esta pronto e validado, mas a rota
HTTP comprimida de lote e uma etapa posterior de contrato, nao deve ser contada
como concluida aqui.
