# FieldNode Sync Protocol v1 (inicial)

## Identidade e hash

Uma mensagem é identificada por `(device_id, message_id)`; `sequence_number`
ordena mensagens do dispositivo. O cliente conserva a identidade e o payload
original nas tentativas. `payload_hash` é SHA-256 do JSON canonicalizado por
chaves ordenadas, calculado sobre o payload recebido. Mesmo identificador e
hash iguais são replay legítimo; hash divergente é conflito e não substitui o
registro já persistido.

Quando `message_id` está presente, o campo auxiliar legado `id` é excluído do
hash: ele identifica a linha física local e pode mudar sem alterar o conteúdo
lógico da mensagem.

## Resposta e confirmação

POST unitário retorna `status` canônico `acked`, `duplicate`, `rejected` ou
`conflict`, mais `message_id`, `device_id`, `sequence_number`, `payload_hash` e
`last_acked_sequence`. HTTP 201 corresponde a `acked`, 200 a `duplicate`, 400 a
`rejected` e 409 a `conflict`. `acked` só é construído após
`registrar_leitura()` retornar da transação que salvou a leitura. Falha de
persistência retorna erro HTTP e não é ACK.

`duplicate` significa que identidade e hash coincidem. `conflict` registra
evidência na DLQ com contexto `SYNC`; a linha original não é alterada. Em lote,
`items` contém confirmação por mensagem e o hash do payload processado. Erros
de validação e conflitos permanecem individualizados; itens persistidos antes
de falha posterior não são desfeitos.

Se a persistência de um item do lote falhar, a API retorna HTTP 500 contendo os
ACKs já confirmados em `items`, o item que falhou em `failure` e identificadores
posteriores em `pending_message_ids`. A resposta não rotula falha interna como
`rejected` nem confirma item pendente.

## Outbox do cliente

O cliente remove a mensagem da outbox somente após validar status de sucesso,
identidade/dispositivo/sequência e hash. `rejected` fica preservado em estado
de erro; `conflict` permanece em `BLOCKED`; HTTP 5xx, falha de rede ou resposta
incompleta não avança cursor. A confirmação é gravada em `edge_acknowledgement`,
o cursor contíguo é atualizado e a linha removida na mesma transação SQLite.
Após reinício, uma mensagem cujo POST chegou ao servidor, mas cujo ACK não foi
persistido localmente, continua na outbox; o reenvio retorna `duplicate`.

`last_acked_sequence` no servidor e no cliente avança apenas pela sequência
contígua persistida/confirmada começando em 1; não salta lacunas. O servidor
deriva isso das leituras persistidas por dispositivo dentro da transação. O
cliente mantém seu próprio ledger local porque o banco local e o servidor não
compartilham uma transação distribuída.

## Garantia e limites

A entrega do cliente é pelo menos uma vez. O servidor deduplica atomicamente a
identidade composta no banco; o efeito é único para as tentativas documentadas
com mesmo dispositivo, identificador e payload/hash, sujeito à disponibilidade
do banco e à persistência local do cliente. Isso não é uma promessa de entrega
exatamente uma vez sob qualquer falha, nem zero perda em qualquer circunstância.

No fluxo atual, o EdgeClient sincroniza mensagens individualmente; o endpoint
de lote responde por item, mas o cliente de borda não faz uma requisição em
lote. Falha HTTP parcial de lote e recuperação integrada com DLQ/blocked ainda
precisam de teste de integração dedicado. O fechamento completo seguirá em
S6-T1.
