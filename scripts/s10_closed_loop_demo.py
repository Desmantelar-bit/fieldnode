#!/usr/bin/env python3
"""Prepara e verifica a parte automatizável da demonstração S10.

O script usa o EdgeClient real para gerar uma leitura crítica determinística,
sincronizá-la via HTTP e consultar a análise que cria/reutiliza a Decision.
Ele não aprova nem executa a Decision: essas ações continuam sendo feitas no
dashboard autenticado, como parte da demonstração humana.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulators.edge_client import EdgeBuffer, EdgeClient, generate_payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device-id", default=os.getenv("S10_DEVICE_ID", "COLH-01"))
    parser.add_argument("--api-url", default=os.getenv("FIELDNODE_API_URL", "http://127.0.0.1:8000/api") + "/telemetria/")
    parser.add_argument("--api-key", default=os.getenv("FIELDNODE_API_KEY", ""))
    parser.add_argument("--auth-token", default=os.getenv("FIELDNODE_AUTH_TOKEN", ""))
    parser.add_argument("--buffer-path", default=os.getenv("S10_BUFFER_PATH", "artifacts/s10/edge-buffer.db"))
    parser.add_argument("--temperature", type=float, default=115.0)
    parser.add_argument("--vibration", type=float, default=2.0)
    parser.add_argument("--rpm", type=int, default=1800)
    parser.add_argument("--machine-id", default=os.getenv("S10_MACHINE_ID", "COLH-01"))
    parser.add_argument("--timeout", type=float, default=10.0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.api_key:
        print("ERRO: informe FIELDNODE_API_KEY ou --api-key; nenhum segredo será impresso.", file=sys.stderr)
        return 2

    buffer = EdgeBuffer(Path(args.buffer_path), args.device_id)
    payload = generate_payload(args.device_id, buffer.next_sequence(), 0, source="s10-demo")
    payload.update(
        {
            "id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "maquina_id": args.machine_id,
            "temperatura": args.temperature,
            "vibracao": args.vibration,
            "rpm": args.rpm,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    buffer.enqueue(payload)
    try:
        client = EdgeClient(buffer, args.api_url, args.api_key, timeout=args.timeout, backoff_base=0)
        synced = client.synchronize()
        if synced != 1:
            print(json.dumps({"status": "erro", "synced": synced, "outbox": buffer.counts()}, ensure_ascii=False))
            return 1

        base_url = args.api_url.rsplit("/telemetria/", 1)[0]
        analysis = requests.get(
            f"{base_url}/prescricoes/{args.machine_id}/",
            headers={
                "X-API-Key": args.api_key,
                "Accept": "application/json",
                **({"Authorization": f"Token {args.auth_token}"} if args.auth_token else {}),
            },
            timeout=args.timeout,
        )
        analysis.raise_for_status()
        data = analysis.json()
        result = {
            "status": "preparado_para_aprovacao_humana",
            "reading_id": payload["id"],
            "message_id": payload["message_id"],
            "device_id": payload["device_id"],
            "sequence_number": payload["sequence_number"],
            "temperature": payload["temperatura"],
            "outbox": buffer.counts(),
            "cursor": buffer.cursor(),
            "analysis_status": data.get("status"),
            "decision_id": data.get("decision_id"),
            "decision_status": data.get("decision_status"),
            "next_step": "abrir a prescrição no dashboard, autenticar e aprovar a Decision",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (requests.RequestException, ValueError) as exc:
        print(json.dumps({"status": "erro", "tipo": type(exc).__name__, "detalhe": str(exc)}, ensure_ascii=False))
        return 1
    finally:
        buffer.close()


if __name__ == "__main__":
    raise SystemExit(main())
