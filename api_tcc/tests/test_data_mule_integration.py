from __future__ import annotations

import tempfile
from pathlib import Path

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from simulators.edge_client import EdgeBuffer, generate_payload
from simulators.transbordo_mule_client import MuleBuffer, MuleClient, collect_from_harvester
from api_tcc.models import LeituraTelemetria


class _DjangoResponse:
    def __init__(self, response):
        self.status_code = response.status_code
        self._data = response.data

    def json(self):
        return self._data


class _DjangoSession:
    def __init__(self, client):
        self.client = client

    def post(self, url, *, json, headers, timeout):
        response = self.client.post(
            url,
            json,
            format="json",
            HTTP_X_API_KEY=headers["X-API-Key"],
        )
        return _DjangoResponse(response)


@override_settings(FIELDNODE_API_KEY="data-mule-test-key")
class DataMuleEndpointIntegrationTest(TestCase):
    def test_20_leituras_chegam_no_endpoint_com_identidade_da_colhedora(self):
        with tempfile.TemporaryDirectory() as directory:
            edge_path = Path(directory) / "colhedora.db"
            mule_path = Path(directory) / "transbordo.db"
            edge = EdgeBuffer(edge_path, "COLH-DATA-MULE-01")
            mule = MuleBuffer(mule_path, "TRB-DATA-MULE-01")
            try:
                for index in range(20):
                    edge.enqueue(generate_payload(
                        "COLH-DATA-MULE-01",
                        edge.next_sequence(),
                        index,
                        source="data_mule",
                    ))
                self.assertEqual(collect_from_harvester(edge, mule), (20, 0))
                self.assertEqual(collect_from_harvester(edge, mule), (0, 20))

                api_client = APIClient()
                synced = MuleClient(
                    mule,
                    "/api/telemetria/",
                    "data-mule-test-key",
                    session=_DjangoSession(api_client),
                    sleep=lambda _: None,
                ).synchronize()

                self.assertEqual(synced, 20)
                readings = LeituraTelemetria.objects.filter(device_id="COLH-DATA-MULE-01")
                self.assertEqual(readings.count(), 20)
                self.assertEqual(readings.values_list("source", flat=True).distinct().get(), "data_mule")
                self.assertEqual(
                    set(readings.values_list("message_id", flat=True)),
                    {row["message_id"] for row in edge.transfer_candidates()},
                )
                self.assertEqual(
                    readings.values_list("device_id", flat=True).distinct().get(),
                    "COLH-DATA-MULE-01",
                )
            finally:
                mule.close()
                edge.close()
