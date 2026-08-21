"""Cenários determinísticos de telemetria para demonstrações do FieldNode.

Execute um cenário por vez, sempre com um ``maquina_id`` sem histórico para que
a janela de 500 leituras do pipeline não misture demonstrações anteriores.
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Optional

import requests
from decouple import config


API_URL = "http://localhost:8000/api/telemetria/"
INTERVALO_ENTRE_LEITURAS = 0.5
API_KEY = config("FIELDNODE_API_KEY", default="")


def enviar_leitura(maquina_id: str, temp: float, vib: float, rpm: int) -> Optional[str]:
    """Envia uma leitura válida e retorna o status calculado pela IA da API."""
    payload = {
        "id": str(uuid.uuid4()),
        "maquina_id": maquina_id,
        "temperatura": round(temp, 2),
        "vibracao": round(vib, 2),
        "rpm": rpm,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    headers = {"X-API-Key": API_KEY} if API_KEY else {}

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=2)
        response.raise_for_status()
        resposta = response.json()
        status_ia = resposta.get("ia", {}).get("status")
        print(
            f"  temp={payload['temperatura']:5.2f}°C | "
            f"vib={payload['vibracao']:4.2f} | rpm={rpm} | "
            f"IA={status_ia or 'sem status'}"
        )
        return status_ia
    except requests.exceptions.RequestException as exc:
        print(f"Erro ao enviar leitura para {maquina_id}: {exc}")
    except ValueError:
        print(f"Erro ao ler a resposta JSON da API para {maquina_id}.")
    return None


def _validar_quantidade(n_leituras: int, minimo: int = 1) -> None:
    if n_leituras < minimo:
        raise ValueError(f"n_leituras deve ser maior ou igual a {minimo}.")


def cenario_normal(maquina_id: str, n_leituras: int = 50):
    """Temperatura de 65--72°C, vibração baixa e RPM estável: sempre NORMAL."""
    _validar_quantidade(n_leituras)
    print(f"Iniciando cenário NORMAL para {maquina_id}...")
    temperaturas = (65.0, 66.5, 68.0, 69.5, 71.0, 72.0, 70.5, 68.5)
    vibracoes = (1.0, 1.2, 1.4, 1.6, 1.8, 1.5, 1.3, 1.1)

    for indice in range(n_leituras):
        enviar_leitura(maquina_id, temperaturas[indice % len(temperaturas)], vibracoes[indice % len(vibracoes)], 1500)
        time.sleep(INTERVALO_ENTRE_LEITURAS)


def cenario_temperatura_crescente(maquina_id: str, n_leituras: int = 50):
    """Temperatura sobe linearmente de 70 a 90°C; passa de 85°C na leitura 38/50."""
    _validar_quantidade(n_leituras, minimo=2)
    print(f"Iniciando cenário de TEMPERATURA CRESCENTE para {maquina_id}...")
    passo = (90.0 - 70.0) / (n_leituras - 1)

    for indice in range(n_leituras):
        temperatura = 70.0 + (passo * indice)
        enviar_leitura(maquina_id, temperatura, 1.5, 1500)
        time.sleep(INTERVALO_ENTRE_LEITURAS)


def cenario_vibracao_anormal(maquina_id: str, n_leituras: int = 50):
    """Vibração determinística entre 5.5 e 8.0: ATENCAO desde a primeira leitura."""
    _validar_quantidade(n_leituras)
    print(f"Iniciando cenário de VIBRAÇÃO ANORMAL para {maquina_id}...")
    vibracoes = (5.5, 6.8, 7.2, 5.9, 8.0, 6.3, 7.7, 5.7)

    for indice in range(n_leituras):
        enviar_leitura(maquina_id, 70.0, vibracoes[indice % len(vibracoes)], 1500)
        time.sleep(INTERVALO_ENTRE_LEITURAS)


def cenario_combinado_critico(maquina_id: str, n_leituras: int = 50):
    """Temperatura >85°C e vibração >5 simultâneas: sempre CRITICO."""
    _validar_quantidade(n_leituras)
    print(f"Iniciando cenário CRÍTICO COMBINADO para {maquina_id}...")
    temperaturas = (86.0, 88.0, 90.0, 87.0)
    vibracoes = (5.5, 6.2, 7.0, 5.8)

    for indice in range(n_leituras):
        enviar_leitura(
            maquina_id,
            temperaturas[indice % len(temperaturas)],
            vibracoes[indice % len(vibracoes)],
            1500,
        )
        time.sleep(INTERVALO_ENTRE_LEITURAS)


if __name__ == "__main__":
    MAQUINA_ID = "DEMO-CENARIO-NORMAL-01"

    # Descomente somente o cenário desejado. Use IDs distintos entre cenários.
    cenario_normal(MAQUINA_ID)
    # cenario_temperatura_crescente("DEMO-CENARIO-TEMP-01")
    # cenario_vibracao_anormal("DEMO-CENARIO-VIB-01")
    # cenario_combinado_critico("DEMO-CENARIO-CRITICO-01")
