"""
Simula N máquinas enviando telemetria simultaneamente e mede:
- taxa de sucesso de ingestão
- latência p50/p95
- respostas do rate limiter

Cada leitura usa um UUID exclusivo. Portanto, este teste não valida a
deduplicação sob concorrência; isso exige uma bateria específica com UUIDs
reutilizados.
"""
import time
import concurrent.futures
from collections import Counter
import requests
import uuid
import os
import json

API_URL = 'http://localhost:8000/api/telemetria/'
DEVICE_KEYS = json.loads(os.getenv('FIELDNODE_HTTP_DEVICE_KEYS', '{}'))


def enviar_leitura(maquina_id: str):
    payload = {
        'id': str(uuid.uuid4()),
        'maquina_id': maquina_id,
        'device_id': maquina_id,
        'temperatura': 75.0,
        'vibracao': 3.2,
        'rpm': 1800,
        'timestamp': '2026-08-12T10:00:00Z',
    }
    inicio = time.perf_counter()
    try:
        key = DEVICE_KEYS.get(maquina_id, '')
        headers = {'X-Device-Id': maquina_id, 'X-Device-Key': key} if key else {}
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=5)
        status_code = resp.status_code
    except requests.RequestException:
        status_code = 0  # Falha de conexão/timeout

    duracao = time.perf_counter() - inicio
    return status_code, duracao


def rodar_teste(n_maquinas: int, leituras_por_maquina: int):
    tarefas = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for m in range(n_maquinas):
            for _ in range(leituras_por_maquina):
                tarefas.append(executor.submit(enviar_leitura, f'maquina-{m}'))

        resultados = [t.result() for t in concurrent.futures.as_completed(tarefas)]

    codigos = [r[0] for r in resultados]
    latencias = sorted(r[1] for r in resultados)

    sucessos = codigos.count(201) + codigos.count(200)
    total = len(codigos)

    print(f"total de requests: {total}")
    print(f"taxa de sucesso (201/200): {sucessos}/{total}")
    print(f"distribuição de status HTTP: {dict(sorted(Counter(codigos).items()))}")

    # Tratamento caso todas as requisições falhem (timeout total)
    if latencias:
        print(f"latência p50: {latencias[len(latencias)//2]:.3f}s")
        print(f"latência p95: {latencias[int(len(latencias)*0.95)]:.3f}s")

    # Conta quantos caíram no Rate Limit (429) ou Erro (500)
    if codigos.count(429) > 0:
        print(f"Alerta: {codigos.count(429)} requisições bloqueadas pelo Rate Limiter (429).")


if __name__ == '__main__':
    for n in [1, 5, 10, 20]:
        print(f"\n--- {n} máquinas, 20 leituras cada ---")
        rodar_teste(n, 20)
