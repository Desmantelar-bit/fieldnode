# S7-T1 - ConnectivityProvider e ConnectivityManager

Criado `connectivity/` com interface, política versionada, manager e providers
HTTP, Mule lógico, LoRa stub e satélite simulado. O edge aceita o manager sem
criar uma segunda outbox. O manager calcula o tamanho serializado, ignora
providers indisponíveis, tenta fallback e aplica somente ACKs compatíveis.

O custo do satélite simulado é separado de cobrança real e pode ser limitado
por acumulador diário injetado. MQTT, rede Docker do Mule, LoRa físico,
satélite real e hardware permanecem fora desta etapa.

`compileall` e `git diff --check` foram executados. Os testes unitários do edge
e Mule e o teste Django de integração foram executados; os resultados ficam
registrados no handoff desta execução.

