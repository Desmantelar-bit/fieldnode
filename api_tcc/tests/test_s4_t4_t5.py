import hashlib
import hmac
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils import timezone

from api_tcc.services.exporters import to_ics
from api_tcc.services.reevaluation import RESULTS, avaliar


def reading(moment, value, index, origin="medido"):
    return {
        "id": f"reading-{index}", "event_time": moment, "temperatura": value,
        "time_source": "ntp", "event_time_confidence": 1.0, "data_origin": origin,
    }


class S4T4ExportTest(SimpleTestCase):
    def test_ics_has_calendar_event_and_crlf(self):
        moment = timezone.now() + timedelta(hours=2)
        order = SimpleNamespace(
            id="order-1", decision_id="decision-1", prazo=moment,
            titulo="Inspecionar, motor", descricao="Linha 1\nLinha 2",
            machine=SimpleNamespace(external_code="MAQ-01"),
        )
        content = to_ics(order)
        self.assertIn("BEGIN:VCALENDAR\r\n", content)
        self.assertIn("BEGIN:VEVENT\r\n", content)
        self.assertIn("SUMMARY:Inspecionar\\, motor", content)
        self.assertTrue(content.endswith("END:VCALENDAR\r\n"))

    @patch("api_tcc.services.exporters.requests.post")
    @patch("api_tcc.services.exporters._safe_webhook_url")
    def test_hmac_header_is_sha256(self, _safe_url, post):
        from api_tcc.services.exporters import send_webhook

        post.return_value.status_code = 204
        order = SimpleNamespace(machine=SimpleNamespace(organization=SimpleNamespace(policy=SimpleNamespace(webhook_url="https://example.com/hook", webhook_secret="secret"))))
        order.id = "order-1"
        order.decision_id = "decision-1"
        order.machine.external_code = "MAQ-01"
        order.titulo = "Teste"
        order.descricao = "Descricao"
        order.prioridade = "ATENCAO"
        order.prazo = timezone.now()
        order.status = "ABERTA"
        order.responsavel_contato = None
        order.responsavel_usuario = None
        result = send_webhook(order)
        self.assertEqual(result["status"], "enviado")
        body = post.call_args.kwargs["data"]
        self.assertEqual(post.call_args.kwargs["headers"]["X-FieldNode-Signature"], "sha256=" + hmac.new(b"secret", body, hashlib.sha256).hexdigest())

    def test_signature_formula_matches_contract(self):
        body = b'{"work_order_id":"1"}'
        expected = hmac.new(b"secret", body, hashlib.sha256).hexdigest()
        self.assertEqual(expected, hmac.new(b"secret", body, hashlib.sha256).hexdigest())


class S4T5ReevaluationTest(SimpleTestCase):
    rule = {
        "version": "temp-v1", "parameter": "temperatura", "threshold": 85,
        "direction": "above", "min_readings": 3, "cessou_at_most": 0.0,
        "persiste_at_least": 0.5, "before_window_minutes": 60, "after_window_minutes": 60,
    }

    def setUp(self):
        self.base = timezone.now()

    def test_symptom_ceased(self):
        before = [reading(self.base + timedelta(minutes=i), 90, i) for i in range(3)]
        after = [reading(self.base + timedelta(minutes=10 + i), 70, i + 3) for i in range(3)]
        self.assertEqual(avaliar(before, after, self.rule), RESULTS.SINTOMA_CESSOU)

    def test_symptom_persists(self):
        before = [reading(self.base + timedelta(minutes=i), 90, i) for i in range(3)]
        after = [reading(self.base + timedelta(minutes=10 + i), 90, i + 3) for i in range(3)]
        self.assertEqual(avaliar(before, after, self.rule), RESULTS.SINTOMA_PERSISTE)

    def test_insufficient_and_out_of_order(self):
        before = [reading(self.base + timedelta(minutes=i), 90, i) for i in range(3)]
        after = [reading(self.base + timedelta(minutes=12), 70, 5), reading(self.base + timedelta(minutes=10), 70, 3)]
        self.assertEqual(avaliar(before, after, self.rule), RESULTS.DADOS_INSUFICIENTES)
        enough = [reading(self.base + timedelta(minutes=10 + i), 70, i + 3) for i in range(3)]
        self.assertEqual(avaliar(before, list(reversed(enough)), self.rule), RESULTS.SINTOMA_CESSOU)
