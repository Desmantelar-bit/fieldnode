from math import sqrt


def confusion(predicted, labels):
    tp = sum(bool(p) and bool(y) for p, y in zip(predicted, labels))
    fp = sum(bool(p) and not bool(y) for p, y in zip(predicted, labels))
    fn = sum(not bool(p) and bool(y) for p, y in zip(predicted, labels))
    tn = sum(not bool(p) and not bool(y) for p, y in zip(predicted, labels))
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def ratio(numerator, denominator):
    return None if denominator == 0 else numerator / denominator


def metricas(predicted, labels, observed_seconds):
    counts = confusion(predicted, labels)
    precision = ratio(counts["tp"], counts["tp"] + counts["fp"])
    recall = ratio(counts["tp"], counts["tp"] + counts["fn"])
    f1 = None if precision is None or recall is None or precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {**counts, "precision": precision, "recall": recall, "f1": f1,
            "false_positive_per_hour": counts["fp"] / (observed_seconds / 3600),
            "observed_seconds": observed_seconds}


def tempo_ate_deteccao(res, rotulo):
    for item, expected in zip(res, rotulo):
        if expected and item["is_anomaly"]:
            return (item["event_time"] - res[0]["event_time"]).total_seconds()
    return None
