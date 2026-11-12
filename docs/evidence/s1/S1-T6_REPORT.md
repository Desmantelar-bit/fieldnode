# S1-T6 — Relatório de evidência de ACK e outbox

## Fluxo implementado

O cliente grava payload e hash na SQLite antes do POST. O servidor calcula o
hash canônico, grava por `(device_id, message_id)` dentro de transação e só
depois responde `acked`. Hash igual em replay responde `duplicate`; hash
diferente responde `conflict` e registra `DeadLetterEntry` com `contexto=SYNC`.
O EdgeClient exige status de sucesso, message_id, device_id, sequence_number e
payload_hash correspondentes. A confirmação local entra no ledger, atualiza o
cursor contíguo e remove a linha da outbox na mesma transação SQLite. `rejected`
permanece como erro visível e conflito fica `BLOCKED`.

O hash ignora o campo auxiliar `id` quando há `message_id`: `id` é a chave física
legada da linha, não conteúdo lógico. Os demais dados normalizados recebidos
participam do SHA-256.

## Cenários verificados

- **Queda após persistência antes do ACK:** teste integrado Django + EdgeBuffer.
  Primeira chamada persiste no servidor e simula conexão perdida; após reinício
  da SQLite, mesma mensagem/hash retorna `duplicate`; outbox fica vazia, cursor
  local chega a 1 e existe uma linha no banco.
- **Hash divergente:** teste integrado retorna HTTP 409 `conflict`, cria DLQ
  `SYNC`, mantém uma única linha original e bloqueia a mensagem na outbox.
- **Falha parcial:** teste de lote força falha de persistência no segundo item;
  HTTP 500 contém o ACK do primeiro, identifica o segundo em `failure`, mantém
  o terceiro em `pending_message_ids` e o banco preserva uma linha. Teste do
  EdgeClient confirma item 1 e recebe HTTP 500 para item 2: somente item 2
  continua na outbox e cursor fica em 1.

## Validação executada

`VERIFICADO`: `python manage.py test api_tcc.tests.test_telemetria
api_tcc.tests.test_identity_contract api_tcc.tests.test_data_health --verbosity 0`
— 63 testes passaram. Cobrem queda pós-POST com reinício real do EdgeBuffer,
hash divergente + DLQ + estado blocked e lote HTTP 500 com ACK anterior
confirmado.

`VERIFICADO`: `python -m unittest simulators.test_edge_client -v` — 11 testes
passaram, incluindo ACK incompleto/status desconhecido, hash divergente, falha
SQLite ao registrar ACK e recuperação no reinício.

`VERIFICADO`: `python manage.py makemigrations --check --dry-run` e
`python manage.py check` passaram; `python -m compileall -q api_tcc simulators`
terminou sem erro.

## Garantia e limites

Entrega pelo menos uma vez. Com identidade, hash e armazenamento local estáveis,
deduplicação do servidor fornece efeito único nos cenários testados. Não é uma
garantia de exatamente uma vez em qualquer condição nem de zero perda. O
EdgeClient envia chamadas unitárias; o HTTP 500 por item de lote foi verificado
no contrato do servidor, mas não existe ainda cliente de borda que envie o
endpoint de lote. Sequência começando acima de 1 mantém cursor contíguo em zero
até as lacunas serem preenchidas. Validação concorrente entre processos e falha
real de hardware/armazenamento local permanecem fora dos testes desta tarefa.

**Classificação desta evidência: PARCIAL**: os três cenários de aceite estão
verificados, mas reenvio concorrente por múltiplos processos e mistura de todos
os status em um único lote ainda não têm teste automatizado. Execução do cliente
contra hardware de campo também não faz parte desta evidência.
