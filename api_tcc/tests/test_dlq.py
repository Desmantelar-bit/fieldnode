import uuid
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from api_tcc.models import DeadLetterEntry, TelemetriaInvalida
from api_tcc.services.decisions import persistir_decision_da_analise
from api_tcc.services.eventos import avaliar_leitura
from api_tcc.services.telemetria import registrar_leitura


def payload(**overrides):
    data = {
        "id": str(uuid.uuid4()),
        "maquina_id": "COLH-DLQ-01",
        "device_id": "esp32-dlq-01",
        "message_id": str(uuid.uuid4()),
        "sequence_number": 7,
        "temperatura": 86.0,
        "vibracao": 0.35,
        "rpm": 1800,
        "timestamp": "2026-06-01T10:00:00Z",
    }
    data.update(overrides)
    return data


class DeadLetterEntryTest(TestCase):
    def test_falha_de_evento_apos_leitura_valida_persiste_dlq_sem_mascarar_erro(self):
        leitura_payload = payload()
        with patch(
            "api_tcc.services.eventos._criar_evento_se_nao_suprimido",
            side_effect=RuntimeError("synthetic DLQ failure"),
        ):
            resultado, detalhe = registrar_leitura(leitura_payload)

        self.assertEqual(resultado, "erro")
        self.assertIn("synthetic DLQ failure", detalhe)
        entrada = DeadLetterEntry.objects.get()
        self.assertEqual(entrada.contexto, DeadLetterEntry.Contexto.EVENTO)
        self.assertEqual(entrada.tentativas, 1)
        self.assertFalse(entrada.resolvido)
        self.assertEqual(entrada.payload_referencia["device_id"], "esp32-dlq-01")
        self.assertEqual(entrada.payload_referencia["message_id"], leitura_payload["message_id"])
        self.assertIn("synthetic DLQ failure", entrada.motivo)

    def test_payload_invalido_fica_em_telemetria_invalida_e_nao_na_dlq(self):
        resultado, _ = registrar_leitura(payload(temperatura=-999))

        self.assertEqual(resultado, "invalido")
        self.assertEqual(TelemetriaInvalida.objects.count(), 1)
        self.assertEqual(DeadLetterEntry.objects.count(), 0)

    def test_avaliar_leitura_repropaga_excecao_quando_chamada_direta(self):
        resultado, leitura_id = registrar_leitura(payload())
        self.assertEqual(resultado, "criado")

        from api_tcc.models import LeituraTelemetria

        leitura = LeituraTelemetria.objects.get(id=leitura_id)
        with patch(
            "api_tcc.services.eventos._criar_evento_se_nao_suprimido",
            side_effect=RuntimeError("direct evaluation failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "direct evaluation failure"):
                avaliar_leitura(leitura)

        self.assertEqual(DeadLetterEntry.objects.count(), 1)

    def test_decisao_registra_dlq_e_repropaga_falha(self):
        analise = SimpleNamespace(
            maquina_id="COLH-DLQ-DEC-01",
            status="CRITICO",
            recomendacao="Investigar",
        )
        with patch(
            "api_tcc.services.decisions.Decision.objects.create",
            side_effect=RuntimeError("synthetic decision failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "synthetic decision failure"):
                persistir_decision_da_analise(analise)

        entrada = DeadLetterEntry.objects.get()
        self.assertEqual(entrada.contexto, DeadLetterEntry.Contexto.DECISAO)
        self.assertEqual(entrada.payload_referencia["maquina_id"], "COLH-DLQ-DEC-01")


class DeadLetterEntryViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="dlq-reader", password="senha-forte-123")
        self.token = Token.objects.create(user=self.user)

    def test_endpoint_exige_autenticacao(self):
        self.assertEqual(self.client.get("/api/dlq/").status_code, 401)

    def test_endpoint_retorna_somente_entradas_nao_resolvidas(self):
        pendente = DeadLetterEntry.objects.create(
            contexto=DeadLetterEntry.Contexto.EVENTO,
            payload_referencia={"leitura_id": str(uuid.uuid4())},
            motivo="falha pendente",
        )
        DeadLetterEntry.objects.create(
            contexto=DeadLetterEntry.Contexto.DECISAO,
            payload_referencia={"maquina_id": "COLH-RESOLVIDA"},
            motivo="falha resolvida",
            resolvido=True,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        response = self.client.get("/api/dlq/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(pendente.id))
        self.assertEqual(response.data[0]["resolvido"], False)
