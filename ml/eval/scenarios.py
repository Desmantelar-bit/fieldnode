from dataclasses import dataclass

import numpy as np
import pandas as pd

from api_tcc.services.regime import inferir_regime


@dataclass(frozen=True)
class Cenario:
    nome: str
    serie: pd.DataFrame
    rotulo: np.ndarray
    esperado: str


def _base(seed: int, n: int = 300) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "event_time": pd.date_range("2026-01-01", periods=n, freq="min"),
        "temperatura": rng.normal(70, 1.5, n),
        "vibracao": rng.normal(0.8, 0.08, n),
        "rpm": rng.normal(1700, 45, n),
    }).assign(regime=lambda frame: [inferir_regime(rpm) for rpm in frame["rpm"]])


def _scenario(name, seed, expected, start=None, mutate=None):
    frame = _base(seed)
    labels = np.zeros(len(frame), dtype=bool)
    if start is not None:
        labels[start:] = True
    if mutate:
        mutate(frame, labels)
    frame["regime"] = [inferir_regime(rpm, speed) for rpm, speed in zip(frame["rpm"], frame.get("velocidade_kmh", pd.Series(0.0, index=frame.index)))]
    return Cenario(name, frame, labels, expected)


def normal(seed):
    return _scenario("normal", seed, "sem_alerta")


def subida_gradual(seed, passo=0.05):
    def mutate(frame, labels):
        frame.loc[200:, "temperatura"] += np.arange(len(frame) - 200) * passo
    return _scenario("subida_gradual", seed, "alerta", 200, mutate)


def pico_isolado(seed):
    def mutate(frame, labels):
        frame.loc[150, "temperatura"] = 110.0
        labels[150] = True
    return _scenario("pico_isolado", seed, "alerta", None, mutate)


def sensor_travado(seed):
    def mutate(frame, labels):
        frame.loc[180:209, "vibracao"] = frame.loc[179, "vibracao"]
        labels[180:210] = True
    return _scenario("sensor_travado", seed, "alerta", None, mutate)


def lacuna_comunicacao(seed):
    frame = _base(seed)
    frame = frame.drop(index=range(120, 160)).reset_index(drop=True)
    labels = np.zeros(len(frame), dtype=bool)
    return Cenario("lacuna_comunicacao", frame, labels, "inconclusivo")


def maquina_desligada(seed):
    def mutate(frame, labels):
        frame.loc[200:, "rpm"] = 0.0
        frame.loc[200:, "temperatura"] = 68.0
    return _scenario("maquina_desligada", seed, "sem_alerta", None, mutate)


def fora_de_ordem(seed):
    scenario = subida_gradual(seed)
    order = scenario.serie.sample(frac=1, random_state=seed).index.to_numpy()
    shuffled = scenario.serie.loc[order].reset_index(drop=True)
    return Cenario(scenario.nome + "_fora_de_ordem", shuffled, scenario.rotulo[order], scenario.esperado)


def mudanca_de_carga(seed):
    def mutate(frame, labels):
        frame.loc[200:, "rpm"] += 300
        frame.loc[200:, "temperatura"] += 4
    return _scenario("mudanca_de_carga", seed, "sem_alerta", None, mutate)


SCENARIO_FACTORIES = [normal, subida_gradual, pico_isolado, sensor_travado,
                      lacuna_comunicacao, maquina_desligada, fora_de_ordem,
                      mudanca_de_carga]
