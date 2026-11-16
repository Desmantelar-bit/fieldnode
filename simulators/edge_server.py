#!/usr/bin/env python3
"""HTTP edge outbox used by the Docker network proof.

This process owns the origin SQLite outbox.  The mule authenticates only to
export already-persisted messages; it never receives the signing secret.
"""

from __future__ import annotations

import argparse
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from connectivity.signing import sign_payload
from simulators.edge_client import EdgeBuffer, classify_priority, generate_payload


class EdgeHandler(BaseHTTPRequestHandler):
    server_version = "FieldNodeEdge/1.0"

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            return self._json(200, {"status": "ok"})
        if parsed.path != "/outbox/export":
            return self._json(404, {"detail": "not_found"})
        if self.headers.get("X-Mule-Token", "") != self.server.export_token:
            return self._json(401, {"detail": "mule_authentication_required"})
        query = parse_qs(parsed.query)
        raw_since = query.get("since", ["0"])[0]
        try:
            since = int(raw_since)
            if since < 0:
                raise ValueError
        except ValueError:
            return self._json(400, {"detail": "since_must_be_non_negative_integer"})
        try:
            limit = min(max(int(query.get("limit", ["100"])[0]), 1), 500)
        except ValueError:
            return self._json(400, {"detail": "limit_invalid"})
        rows = [row for row in self.server.buffer.transfer_candidates()
                if int(row["sequence_number"]) > since][:limit]
        messages = []
        for row in rows:
            payload = self.server.buffer._decode_row(row)
            messages.append({
                "device_id": row["device_id"], "message_id": row["message_id"],
                "sequence_number": row["sequence_number"], "payload": payload,
                "payload_hash": row["payload_hash"], "priority_class": row["priority_class"],
            })
        return self._json(200, {"schema": "sync.v1", "since": since, "messages": messages,
                               "next_since": messages[-1]["sequence_number"] if messages else since})

    def _json(self, code, body):
        encoded = json.dumps(body, sort_keys=True).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        print(format % args, flush=True)


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.getenv("EDGE_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("EDGE_PORT", "8081")))
    parser.add_argument("--db", default=os.getenv("EDGE_BUFFER_PATH", "/data/edge.db"))
    parser.add_argument("--device-id", default=os.getenv("DEVICE_ID", "edge-bench-01"))
    parser.add_argument("--seed", type=int, default=int(os.getenv("EDGE_SEED_COUNT", "0")))
    parser.add_argument("--signing-key", default=os.getenv("EDGE_SIGNING_KEY", ""))
    parser.add_argument("--mule-token", default=os.getenv("MULE_EXPORT_TOKEN", ""))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.mule_token or not args.signing_key:
        raise SystemExit("MULE_EXPORT_TOKEN e EDGE_SIGNING_KEY são obrigatórios")
    buffer = EdgeBuffer(args.db, args.device_id)
    for index in range(args.seed):
        payload = generate_payload(args.device_id, buffer.next_sequence(), index, source="data_mule")
        payload["priority_class"] = classify_priority(payload)
        payload = sign_payload(payload, args.signing_key)
        buffer.enqueue(payload)
    server = ThreadingHTTPServer((args.host, args.port), EdgeHandler)
    server.buffer = buffer
    server.export_token = args.mule_token
    print(json.dumps({"status": "ready", "device_id": args.device_id, "seeded": args.seed}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.shutdown()
        buffer.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
