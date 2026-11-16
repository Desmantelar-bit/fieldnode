# S7-T3/T4 - transporte por rede e entrega por salto

## Implementado

- `simulators/edge_server.py` expõe `GET /outbox/export?since=` com token do Mule,
  cursor inteiro, limite máximo de lote e cópia não destrutiva da outbox.
- `connectivity/signing.py` implementa HMAC-SHA256 canônico por dispositivo.
  O segredo não é enviado ao Mule.
- `docker-compose.mule.yml` separa `field_net` (`internal: true`) e `base_net`.
- `scripts/mule_demo.ps1` executa coleta HTTP, troca controlada de rede e entrega.
- O backend rejeita assinatura inválida com `assinatura_invalida` e registra DLQ.
- `DeliveryHop`, `LeituraTelemetria.via` e `GET /api/sync/report/?format=json|csv`
  registram e exportam os saltos.

## Decisão D-19

Foi escolhido HMAC-SHA256 para a prova em rede Docker por não exigir dependência
criptográfica adicional e por ser viável no simulador/edge. A chave é separada
por dispositivo e existe apenas no edge e no backend. Isso não representa ainda
provisionamento seguro de chave em ESP32 nem rotação operacional de produção.
Ed25519 continua sendo uma opção de evolução para separar assinatura privada e
verificação pública sem segredo compartilhado.

## Verificação executada

- `manage.py check` - VERIFICADO.
- Testes unitários de edge/mule/connectivity - VERIFICADO: 17 passaram.
- `manage.py test api_tcc.tests.test_data_mule_integration` - VERIFICADO: 1 passou.
- `manage.py test api_tcc.tests.test_s7_t3_signature_hops` - VERIFICADO: 1 passou.
- `docker version` - VERIFICADO: servidor Docker 29.4.3 disponível.
- Execução Docker completa - VERIFICADO: 20 coletadas, 20 entregues, 20 ACKED,
  cursor 20, 20 leituras no backend, 20 hops persistidos.
- Adulteração controlada - VERIFICADO: HTTP 400 `assinatura_invalida`, 1 DLQ,
  20 leituras válidas preservadas.
- Replay controlado - VERIFICADO: HTTP 200 `duplicate`, sem nova leitura.
- Volumes e redes do experimento - removidos com `docker compose -p fieldnode-s7 down -v`.
- Vídeo curto - NÃO PRODUZIDO nesta etapa.

## Limites

Esta prova é software em rede Docker local. Não valida rádio, ESP32 físico,
rede rural, alcance, disponibilidade externa ou operação em campo.
