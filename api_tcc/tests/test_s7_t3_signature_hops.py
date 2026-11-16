from django.test import TestCase, override_settings

from api_tcc.models import DeadLetterEntry, DeliveryHop, LeituraTelemetria
from api_tcc.services.telemetria import registrar_leitura
from connectivity.signing import sign_payload
from simulators.edge_client import generate_payload


class S7T3SignatureAndHopsTest(TestCase):
    @override_settings(
        FIELDNODE_DEVICE_SIGNING_KEYS={"S7-EDGE": "test-signing-key"},
        REQUIRE_MESSAGE_SIGNATURES=True,
    )
    def test_tampering_goes_to_dlq_and_replay_is_duplicate(self):
        payload = sign_payload(generate_payload("S7-EDGE", 1, 1), "test-signing-key")
        payload["via"] = [
            {"node": "mule-a", "t": "2026-11-16T03:00:00+00:00"},
            {"node": "mule-b", "t": "2026-11-16T03:01:00+00:00"},
        ]
        tampered = dict(payload)
        tampered["rpm"] = 1900
        result, reason = registrar_leitura(tampered)
        self.assertEqual(result, "invalido")
        self.assertEqual(reason, "assinatura_invalida")
        self.assertTrue(DeadLetterEntry.objects.filter(motivo="assinatura_invalida").exists())

        result, leitura_id = registrar_leitura(payload)
        self.assertEqual(result, "criado")
        self.assertEqual(LeituraTelemetria.objects.count(), 1)
        self.assertEqual(DeliveryHop.objects.filter(leitura_id=leitura_id).count(), 2)
        duplicate, duplicate_id = registrar_leitura(payload)
        self.assertEqual(duplicate, "duplicata")
        self.assertEqual(duplicate_id, leitura_id)
