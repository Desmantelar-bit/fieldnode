import numpy as np
import pytest

from .public_dataset import extract_window_features, evaluate


def test_features_drop_incomplete_window_and_use_pearson_kurtosis():
    result = extract_window_features(np.ones(10), window_size=4)
    assert result.shape == (2, 3)
    assert result[:, 0].tolist() == [1.0, 1.0]
    assert result[:, 1].tolist() == [1.0, 1.0]


def test_features_reject_nan_only_window():
    with pytest.raises(ValueError, match="janela completa"):
        extract_window_features(np.full(8, np.nan), window_size=4)


def test_public_evaluation_is_reproducible_and_compares_both_methods():
    rng = np.random.default_rng(7)
    training = rng.normal(size=(80, 3))
    test = np.vstack([rng.normal(size=(20, 3)), np.full((5, 3), 8.0)])
    labels = np.r_[np.zeros(20, dtype=int), np.ones(5, dtype=int)]
    first = evaluate(training, test, labels)
    second = evaluate(training, test, labels)
    assert first == second
    assert set(first) == {"isolation_forest", "limiar_simples", "config"}
    assert first["isolation_forest"]["tp"] + first["isolation_forest"]["fn"] == 5


def test_invalid_window_parameters_are_rejected():
    with pytest.raises(ValueError):
        extract_window_features(np.ones(10), window_size=4, overlap=4)
