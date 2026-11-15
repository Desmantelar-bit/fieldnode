"""Saídas explícitas da WorkOrder, sem envio automático a serviços externos."""

import hashlib
import hmac
import ipaddress
import json
import socket
from datetime import timezone as dt_timezone
from urllib.parse import quote, urlparse

import requests
from django.utils import timezone

from api_tcc.models import DeadLetterEntry, WorkOrder
from api_tcc.services.dlq import registrar_falha_dlq


def _text(value):
    return str(value or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\r", "").replace("\n", "\\n")


def to_ics(order: WorkOrder) -> str:
    deadline = order.prazo.astimezone(dt_timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stamp = timezone.now().astimezone(dt_timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    description = f"{_text(order.descricao)}\\nDecisao: {order.decision_id}"
    return "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//FieldNode//OS//PT-BR",
        "CALSCALE:GREGORIAN", "BEGIN:VEVENT", f"UID:{order.id}@fieldnode",
        f"DTSTAMP:{stamp}", f"DTSTART:{deadline}", f"SUMMARY:{_text(order.titulo)}",
        f"DESCRIPTION:{description}", "END:VEVENT", "END:VCALENDAR", "",
    ])


def export_payload(order: WorkOrder) -> dict:
    responsible = order.responsavel_contato or order.responsavel_usuario
    return {
        "schema": "fieldnode.workorder.v1",
        "work_order_id": str(order.id),
        "decision_id": str(order.decision_id),
        "machine": order.machine.external_code,
        "titulo": order.titulo,
        "descricao": order.descricao,
        "prioridade": order.prioridade,
        "prazo": order.prazo.isoformat(),
        "status": order.status,
        "responsavel": getattr(responsible, "nome", None) or getattr(responsible, "username", None),
    }


def ready_message(order: WorkOrder) -> str:
    return f"OS FieldNode {order.id}\nMáquina: {order.machine.external_code}\n{order.titulo}\nPrazo: {order.prazo.astimezone().strftime('%d/%m/%Y %H:%M')}\nPrioridade: {order.prioridade}\n{order.descricao}"


def whatsapp_url(order: WorkOrder) -> str | None:
    contact = order.responsavel_contato
    number = getattr(contact, "telefone_profissional", "") if contact else ""
    digits = "".join(char for char in number if char.isdigit())
    if not digits or len(digits) < 8:
        return None
    return f"https://wa.me/{digits}?text={quote(ready_message(order))}"


def _safe_webhook_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("webhook deve usar uma URL HTTP(S) válida")
    if parsed.username or parsed.password:
        raise ValueError("webhook não pode conter credenciais na URL")
    host = parsed.hostname.lower()
    if host in {"localhost", "localhost.localdomain"}:
        raise ValueError("webhook não pode apontar para localhost")
    try:
        addresses = {ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)}
    except OSError as exc:
        raise ValueError("não foi possível resolver o destino do webhook") from exc
    if any(address.is_private or address.is_loopback or address.is_link_local or address.is_reserved for address in addresses):
        raise ValueError("webhook não pode apontar para rede privada")


def send_webhook(order: WorkOrder, *, attempts: int = 3) -> dict:
    policy = getattr(order.machine.organization, "policy", None)
    if policy is None or not policy.webhook_url or not policy.webhook_secret:
        raise ValueError("webhook não configurado para a organização")
    _safe_webhook_url(policy.webhook_url)
    body = json.dumps(export_payload(order), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(policy.webhook_secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    last_error = "destino indisponível"
    for attempt in range(1, attempts + 1):
        try:
            response = requests.post(policy.webhook_url, data=body, headers={"Content-Type": "application/json", "X-FieldNode-Signature": f"sha256={signature}"}, timeout=(3, 8), allow_redirects=False)
            if 200 <= response.status_code < 300:
                return {"status": "enviado", "tentativas": attempt, "http_status": response.status_code}
            last_error = f"HTTP {response.status_code}"
        except requests.RequestException as exc:
            last_error = str(exc)[:300]
    registrar_falha_dlq(contexto=DeadLetterEntry.Contexto.WEBHOOK, payload_referencia={"work_order_id": str(order.id), "organization_id": str(order.machine.organization_id)}, motivo=f"webhook falhou após {attempts} tentativas: {last_error}")
    return {"status": "falhou", "tentativas": attempts, "detalhe": "webhook indisponível; aprovação não é revertida"}
