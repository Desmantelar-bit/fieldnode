"""Teste de resiliência de concorrência e deduplicação.

Garante que pacotes com o mesmo UUID enviados simultaneamente não gerem
registros duplicados.
"""
import concurrent.futures
import time
import uuid

import requests
from decouple import config


API_URL = "http://localhost:8000/api/telemetria/"
API_KEY = config("FIELDNODE_API_KEY", default="")


def enviar_requisicao(payload_base: dict, headers: dict) -> requests.Response | None:
    """Envia uma leitura e preserva falhas de rede para o relatório do teste."""
    try:
        return requests.post(API_URL, json=payload_base, headers=headers, timeout=10)
    except requests.RequestException as exc:
        print(f"Falha de rede na requisição: {exc}")
        return None


def teste_deduplicacao() -> None:
    """Envia o mesmo UUID 10 vezes simultaneamente; deve persistir uma leitura."""
    id_fixo = str(uuid.uuid4())
    payload_base = {
        "id": id_fixo,
        "maquina_id": "teste-dedup-concorrencia",
        "temperatura": 70.0,
        "vibracao": 1.0,
        "rpm": 1500,
        "timestamp": "2026-08-12T10:00:00Z",
    }
    headers = {"X-API-Key": API_KEY} if API_KEY else {}

    print(f"Disparando 10 threads simultâneas com o UUID: {id_fixo}")
    inicio = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(enviar_requisicao, payload_base, headers) for _ in range(10)
        ]
        resultados = [future.result() for future in futures]

    status_codes = [resultado.status_code if resultado else 0 for resultado in resultados]
    print(f"Status codes retornados: {status_codes}")
    print(f"Duração total: {time.perf_counter() - inicio:.3f}s")
    print("\nATENÇÃO: Vá ao banco de dados ou painel admin do Django e confirme que o UUID")
    print(f"{id_fixo} possui APENAS UM registro na tabela LeituraTelemetria.")


if __name__ == "__main__":
    teste_deduplicacao()
