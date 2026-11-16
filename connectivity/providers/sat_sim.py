"""Provider de satélite SIMULADO; não acessa hardware ou serviço comercial."""

from datetime import datetime
from math import isfinite


class SatelliteSimProvider:
    """Test double com custo, relógio e orçamento diário controláveis."""

    name = "sat_sim"
    budget_managed = True

    def __init__(self, sender=None, *, available: bool = True, cost: float = 1.0,
                 daily_budget: float | None = None, clock=None, max_bytes: int = 4096):
        if not isinstance(cost, (int, float)) or not isfinite(float(cost)) or cost < 0:
            raise ValueError("custo SIMULADO deve ser finito e não negativo")
        if daily_budget is not None and (not isinstance(daily_budget, (int, float)) or daily_budget < 0):
            raise ValueError("orçamento SIMULADO deve ser não negativo")
        if max_bytes <= 0:
            raise ValueError("limite de payload inválido")
        self._sender = sender or self._default_sender
        self._available, self._cost = available, float(cost)
        self._daily_budget, self._clock, self._max_bytes = daily_budget, (clock or datetime.now), max_bytes
        self._spent = {}
        self._delivered = set()
        self._report = {"provider": "SIMULADO:sat_sim", "eligible": 0, "sent": 0,
                        "blocked_budget": 0, "duplicates": 0, "consumed": 0.0, "blocked": []}

    def available(self) -> bool:
        return self._available

    def max_payload_bytes(self) -> int:
        return self._max_bytes

    def cost_per_msg(self) -> float:
        return self._cost

    @staticmethod
    def _default_sender(batch):
        return [{"status": "acked", "message_id": item["message_id"], "device_id": item["device_id"],
                 "sequence_number": item["sequence_number"], "payload_hash": item["payload_hash"],
                 "attempted": True, "charged": True} for item in batch]

    def send(self, batch):
        if not self._available:
            return [{"status": "error", "error": "SIMULADO indisponível", "attempted": False}]
        today = self._clock().date()
        spent = self._spent.get(today, 0.0)
        eligible, acks = [], []
        reserved = spent
        for item in batch:
            self._report["eligible"] += 1
            identity = (str(item.get("device_id", "")), int(item.get("sequence_number", -1)))
            if identity in self._delivered:
                self._report["duplicates"] += 1
                acks.append({"status": "duplicate", "message_id": item["message_id"], "device_id": item["device_id"],
                             "sequence_number": item["sequence_number"], "payload_hash": item["payload_hash"],
                             "attempted": False, "charged": False})
                continue
            if self._daily_budget is not None and reserved + self._cost > float(self._daily_budget):
                self._report["blocked_budget"] += 1
                self._report["blocked"].append(item.get("message_id"))
                acks.append({"status": "budget_exceeded", "message_id": item["message_id"], "device_id": item["device_id"],
                             "sequence_number": item["sequence_number"], "payload_hash": item["payload_hash"],
                             "attempted": False, "charged": False, "error": "SIMULADO orçamento diário esgotado"})
                continue
            eligible.append(item)
            reserved += self._cost
        if eligible:
            sent_acks = self._sender(eligible)
            acks.extend(sent_acks)
            valid_ids = {ack.get("message_id") for ack in sent_acks if ack.get("status") == "acked"}
            for item in eligible:
                if item.get("message_id") in valid_ids:
                    self._delivered.add((str(item["device_id"]), int(item["sequence_number"])))
                    spent += self._cost
                    self._report["sent"] += 1
            self._spent[today] = spent
            self._report["consumed"] = spent
        return acks

    def report(self):
        today = self._clock().date()
        spent = self._spent.get(today, 0.0)
        return {**self._report, "period": today.isoformat(), "configured_cost": self._cost,
                "daily_budget": self._daily_budget, "consumed": spent,
                "remaining": None if self._daily_budget is None else float(self._daily_budget) - spent,
                "simulation_only": True}
