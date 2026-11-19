"""Formatos autorais demonstrativos, não APIs de fabricantes."""

from .base import Adapter, _unknown, register
from api_tcc.services.j1939 import Param


DEMO_NOTICE = "Formato demonstrativo inspirado em padrões públicos de telemática; não é API oficial de fabricante."


@register("demo_metrics_v1")
class MetricsAdapter(Adapter):
    """Formato demonstrativo A: métricas agrupadas por nome."""

    def fingerprint(self):
        return "demo-metrics-v1"

    def _parse(self, payload):
        source = "adapter:demo_metrics_v1"
        result = []
        metrics = payload.get("metrics", {})
        names = {"rpm": "engine.rpm", "coolant_temp": "engine.coolant_temp"}
        for name, item in metrics.items():
            if name not in names:
                result.append(_unknown(f"metrics.{name}", item, source))
                continue
            if not isinstance(item, dict) or "value" not in item:
                result.append(Param(names[name], None, None, status="invalid", quality="invalid_shape", origem="simulado", fonte=source, raw_field=f"metrics.{name}"))
                continue
            result.append(Param(names[name], item["value"], item.get("unit"), origem="simulado", fonte=source, mapping_version=self.fingerprint(), raw_field=f"metrics.{name}"))
        for field, value in payload.items():
            if field not in {"metrics", "device_id", "timestamp"}:
                result.append(_unknown(field, value, source))
        return result


@register("demo_readings_v1")
class ReadingsAdapter(Adapter):
    """Formato demonstrativo B: lista de leituras nomeadas."""

    def fingerprint(self):
        return "demo-readings-v1"

    def _parse(self, payload):
        source = "adapter:demo_readings_v1"
        result = []
        names = {"engine_speed": "engine.rpm", "coolant_temperature": "engine.coolant_temp"}
        for index, item in enumerate(payload.get("readings", [])):
            if not isinstance(item, dict) or item.get("name") not in names:
                result.append(_unknown(f"readings[{index}]", item, source))
                continue
            result.append(Param(names[item["name"]], item.get("value"), item.get("unit"), origem="simulado", fonte=source, mapping_version=self.fingerprint(), raw_field=f"readings[{index}]"))
        for field, value in payload.items():
            if field not in {"readings", "asset_id", "observed_at"}:
                result.append(_unknown(field, value, source))
        return result
