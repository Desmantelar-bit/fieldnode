# S7-T2 - Protocolo de custódia do Data Mule

A cópia do Mule continua durável em SQLite e registra `custody_token`, estado
de custódia, histórico de saltos e ACK do backend. Coleta repetida é
idempotente e hash divergente não substitui a cópia existente.

`MuleClient` valida status, identidade, sequência e hash quando presentes no
ACK. Com `origin_buffer`, uma confirmação completa é propagada para a outbox
da origem. Sem esse vínculo, a origem permanece preservada, que é o estado
seguro.

Os testes cobrem coleta repetida, identidade, hash, reinício SQLite, entrega
idempotente e integração Django. Não é alegado transporte físico, rede rural,
assinatura criptográfica por dispositivo, descoberta de Mules ou validação em
campo. O token atual é correlação e integridade local, não assinatura
criptográfica.

