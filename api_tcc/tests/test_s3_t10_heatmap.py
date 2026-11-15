import uuid
from datetime import datetime, timezone

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from api_tcc.models import Event, LeituraTelemetria
from api_tcc.services.telemetria import registrar_leitura


def _reading(machine_id, timestamp, temperature=70.0):
    status, reading_id = registrar_leitura({
        "id": str(uuid.uuid4()), "maquina_id": machine_id, "temperatura": temperature,
        "vibracao": 1.0, "rpm": 1800, "timestamp": timestamp,
    })
    assert status == "criado"
    return LeituraTelemetria.objects.get(id=reading_id)


@override_settings(DEMO_MODE=True)
class FleetHeatmapApiTest(TestCase):
    def test_agrupa_por_event_time_e_preserva_pior_severidade(self):
        early = _reading("HEAT-01", "2026-06-01T09:40:00Z")
        late = _reading("HEAT-01", "2026-06-01T10:20:00Z")
        early.machine.is_demo = True
        early.machine.save(update_fields=["is_demo"])
        Event.objects.create(machine=early.machine, leitura_origem=early, tipo=Event.Tipo.TEMP_ALTA, severidade=Event.Severidade.ATENCAO, evidence_quality="boa", needs_verification=False)
        Event.objects.create(machine=late.machine, leitura_origem=late, tipo=Event.Tipo.TEMP_ALTA, severidade=Event.Severidade.CRITICO, evidence_quality="insuficiente", needs_verification=True)

        response = APIClient().get("/api/events/heatmap/", {"start": "2026-06-01T09:00:00Z", "end": "2026-06-01T12:00:00Z"})

        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual([row["worst_severity"] for row in results], ["ATENCAO", "CRITICO"])
        self.assertEqual([row["event_count"] for row in results], [1, 1])
        self.assertTrue(results[1]["quality_issue"])

    def test_eventos_sem_timestamp_nao_sao_alocados(self):
        reading = _reading("HEAT-02", "2026-06-01T09:40:00Z")
        reading.timestamp = None
        reading.save(update_fields=["timestamp"])
        reading.machine.is_demo = True
        reading.machine.save(update_fields=["is_demo"])
        Event.objects.create(machine=reading.machine, leitura_origem=reading, tipo=Event.Tipo.TEMP_ALTA, severidade=Event.Severidade.CRITICO)

        response = APIClient().get("/api/events/heatmap/", {"start": "2026-06-01T09:00:00Z", "end": "2026-06-01T12:00:00Z"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])
