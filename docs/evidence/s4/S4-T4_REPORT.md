# S4-T4 · Exportação de WorkOrder

## Implementado

- `GET /api/workorders/<id>/export.ics`: calendário RFC 5545 mínimo, UTF-8, CRLF, UID estável e horário UTC.
- `GET /api/workorders/<id>/export.json`: payload mínimo `fieldnode.workorder.v1`, mensagem pronta e `whatsapp_url` somente quando o telefone profissional é válido.
- `POST /api/workorders/<id>/export.webhook`: envio explícito para a URL da política da organização.
- HMAC-SHA256 em `X-FieldNode-Signature: sha256=<digest>`.
- Três tentativas com timeout; falha persistente registra `DeadLetterEntry` com `contexto=WEBHOOK` e não altera aprovação/OS.
- O link de WhatsApp apenas abre uma URL com texto preenchido. O FieldNode não envia mensagens.

## Segurança e limites

O payload não inclui telemetria, credenciais ou dados de outras organizações. O destino exige HTTP(S), não aceita credenciais embutidas, localhost ou endereços privados/reservados. O segredo não é retornado pela API.

## Verificação

- VERIFICADO: `api_tcc/tests/test_s4_t4_t5.py`, `.ics` estrutural e assinatura HMAC.
- VERIFICADO: `python manage.py check`, `python manage.py makemigrations --check --dry-run`, `git diff --check`.
- PENDENTE: teste manual com captura abrindo o arquivo no Google Agenda e no Outlook.
- PENDENTE: chamada contra um webhook externo autorizado; o teste local usa transporte controlado.

## Arquivos principais

`api_tcc/services/exporters.py`, `api_tcc/api/views_workorders.py`, `api_tcc/models.py`, `api_tcc/migrations/0043_organizationpolicy_reevaluation_policy_and_more.py`, `frontend-next/src/app/decisoes/page.tsx`.
