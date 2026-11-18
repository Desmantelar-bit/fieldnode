from django.test import TestCase, override_settings

from api_tcc.metrics import metrics_payload, record_ingest_result, reset_metrics_for_tests


@override_settings(FIELDNODE_METRICS_TOKEN="test-metrics-token")
class PrometheusMetricsTests(TestCase):
    def setUp(self):
        reset_metrics_for_tests()

    def test_endpoint_requires_token(self):
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 403)

    def test_endpoint_returns_prometheus_with_valid_token(self):
        response = self.client.get("/metrics", HTTP_X_METRICS_TOKEN="test-metrics-token")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"fieldnode_ingest_total", response.content)

    def test_three_accepted_operations_increment_exactly_three(self):
        for _ in range(3):
            record_ingest_result("accepted", 0.0)
        payload = metrics_payload().decode("utf-8")
        line = next(
            line for line in payload.splitlines()
            if line.startswith('fieldnode_ingest_total{status="accepted"}')
        )
        self.assertTrue(line.endswith(" 3.0"))
