# FieldNode Sync Protocol v1

## Escopo e garantia

Este é o contrato de store-and-forward entre edge, transportador e ingestor.
Ele é independente do transporte HTTP, MQTT ou Data Mule. A entrega é pelo
menos uma vez; o servidor deduplica atomicamente por `(device_id, message_id)`.
Não há promessa de entrega exatamente uma vez, zero perda ou disponibilidade
quando o armazenamento local está fisicamente cheio.

## Envelope

O schema compartilhado está em `contracts/sync.v1.json`. O cliente de borda e
o serviço Django validam os campos do envelope versionado. Para compatibilidade
com o contrato S1 existente, o payload continua plano no wire e aceita
`timestamp` como alias de `event_time`.

Campos centrais:

| Campo | Regra |
|---|---|
| `device_id` | identidade persistente do produtor |
| `message_id` | identificador idempotente do evento |
| `sequence_number` | inteiro positivo, monotônico por dispositivo |
| `boot_id` | identifica o boot do edge quando disponível |
| `time_source` | `rtc`, `gateway`, `ntp` ou `unsynced` |
| `priority_class` | `A`, `B` ou `C`; A é crítica |
| `schema_version` | versão explícita do contrato |
| `ttl_s` | retenção pretendida, ainda dependente da política aprovada |
| `payload_hash` | SHA-256 do JSON canônico, com chaves ordenadas |
| `encoding` | `json` ou `gzip+base64` |

O `id` legado não entra no hash quando `message_id` existe. Assim, a linha
física local pode mudar sem transformar o mesmo evento em outro evento.

## ACK e cursor

O ACK contém `status`, `message_id`, `device_id`, `sequence_number`,
`payload_hash` e `last_acked_sequence`. Os status são:

| Status | HTTP | Comportamento |
|---|---:|---|
| `acked` | 201 | leitura nova persistida na transação |
| `duplicate` | 200 | mesma identidade e mesmo hash já persistidos |
| `rejected` | 400 | contrato ou dado inválido; permanece em erro local |
| `conflict` | 409 | mesma identidade com hash divergente; permanece bloqueada |

O cursor só avança por sequências contíguas começando em 1. Uma lacuna não é
pulada. O edge grava o ledger local, confirma o ACK e remove a outbox na mesma
transação SQLite. Se a resposta se perder, o reenvio legítimo retorna
`duplicate`.

## Reenvio e falhas

- falha de rede, HTTP 429 ou HTTP 5xx mantém a mensagem pendente;
- ACK incompleto ou com identidade/hash divergente não remove a mensagem;
- falha de persistência não gera ACK;
- conflito não substitui a mensagem original e deve ser investigado;
- reinicialização recupera mensagens que estavam em `ENVIANDO`.

## Custódia do Data Mule

Quando o Mule coleta uma mensagem, persiste uma cópia e um token antes de
qualquer confirmação de coleta. A origem mantém sua cópia em `ORIGEM`; a cópia
do Mule fica em `COLETADO`. Coleta não equivale a entrega.

```text
ORIGEM -> COLETADO -> ENTREGUE -> ACKED -> LIBERADO
```

O token registra origem, Mule, `message_id` e `payload_hash`. O Mule mantém a
cópia até ACK compatível com identidade, sequência e hash. A origem só aplica
a confirmação com `EdgeBuffer.apply_backend_ack`; o Mule não fabrica ACK e não
troca `device_id` pelo seu identificador.

O estado de custódia e o ACK ficam no SQLite do Mule, permitindo recuperação
após reinício. Coletas repetidas e reenvios podem existir, mas a deduplicação
do backend continua sendo a garantia de efeito único persistido.

O token atual é correlação e integridade local, não assinatura criptográfica.
Autenticidade verificável do ACK e da origem ainda depende de uma decisão
criptográfica compatível com as credenciais de dispositivo.

## Prioridade, TTL e compressão

A classe de transmissão é determinada pelas regras de severidade existentes.
A e B não são descartadas automaticamente. As hipóteses de TTL são A sem
expiração automática, B 72 horas e C 14 dias, ainda sujeitas a aprovação de
produto. TTL, compressão, agregação, descarte por falta de espaço e rejeição
por falha de persistência são eventos diferentes.

Compressão só é aplicada à classe C quando a política de armazenamento entra
no estágio configurado. A codificação fica registrada no SQLite e é revertida
antes do envio, preservando o payload lógico e o hash.

## Versionamento e erros

Mudanças incompatíveis exigem nova versão do schema. Campos adicionais podem
ser ignorados por consumidores compatíveis, mas não se deve alterar o sentido
de um campo existente silenciosamente. A origem, o hash, a sequência e o
dispositivo devem permanecer auditáveis em todo reenvio.

## Testes e evidência

O contrato é exercitado por `api_tcc/tests/test_sync_contract.py` e pelos
testes do edge. A política de capacidade fica em `scripts/capacity_calc.py`,
com medição real em `scripts/measure_storage.py`. Resultados publicados devem
ser produzidos por comandos executados e não por valores ilustrativos.
