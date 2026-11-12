# Protocolo de sincronização v1

## Garantia

A sincronização é **at-least-once**. O edge mantém a leitura na outbox até
receber e validar um ACK. A idempotência do servidor por `(device_id,
message_id)` evita duplicar o efeito para replays aceitos; isso não equivale a
uma garantia geral de entrega exatamente uma vez.

## Identidade e fingerprint

`device_id + message_id` é a identidade lógica. O UUID `id` identifica a linha
interna e é excluído do `payload_hash`, para permitir replay do mesmo conteúdo
com novo UUID interno. O hash usa as chaves do payload ordenadas e a codificação
JSON compatível com Python. Edge, Service Worker e backend aplicam a mesma regra.

Por compatibilidade, o servidor aceita um hash legado com `id` quando ele
coincide com o hash já persistido para a mensagem. A outbox antiga não precisa
ser regravada: edge e Service Worker recalculam o fingerprint lógico do payload
antes de validar o ACK.

## Resposta do servidor

```json
{
  "ack": {
    "status": "acked",
    "message_id": "...",
    "device_id": "...",
    "sequence_number": 42,
    "payload_hash": "sha256-hex",
    "last_acked_sequence": 42
  }
}
```

- HTTP 201 e `status=acked`: leitura persistida.
- HTTP 200 e `status=duplicate`: replay com o mesmo conteúdo lógico.
- HTTP 409 e `status=conflict`: identidade reutilizada com conteúdo diferente;
  o servidor registra a ocorrência na DLQ `SYNC`.
- Payload inválido retorna HTTP 400; falhas transitórias podem retornar 5xx.

## Regra de remoção

O cliente só remove a leitura após conferir `status`, `message_id`, `device_id`,
`sequence_number`, `payload_hash` e cursor cumulativo. Hash ou identidade divergente,
ACK ausente ou JSON inválido mantém o item para revisão; não é sucesso.

No edge, falhas permanentes ficam em estado de erro e não avançam o cursor
contíguo. No Service Worker, itens inválidos ficam `rejected`; 401 pausa a fila
como `auth_blocked`; rede, 408, 429 e 5xx ficam `retrying` com backoff. Itens
posteriores continuam sendo processados quando um item é rejeitado.

## Hardware

O firmware real permanece no contrato v0. Este protocolo foi exercitado com o
backend, o cliente edge e o Service Worker do repositório; não comprova ACK do
hardware até uma migração de firmware versionada.
