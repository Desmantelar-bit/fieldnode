from datetime import timedelta
import uuid

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from api_tcc.models import Decision, Event, Machine
from api_tcc.services.decisions import DECISION_DEDUP_WINDOW
from api_tcc.services.telemetria import registrar_leitura


def _payload(maquina_id: str, temperatura: float, vibracao: float, rpm: int, minuto: int):
    return {
        "id": str(uuid.uuid4()),
        "maquina_id": maquina_id,
        "temperatura": temperatura,
        "vibracao": vibracao,
        "rpm": rpm,
        "timestamp": f"2026-09-21T12:{minuto:02d}:00Z",
    }


class DecisionPrescricaoIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def _registrar_janela_critica(self, maquina_id="COLH-DEC-01"):
        for minuto in range(3):
            registrar_leitura(
                _payload(
                    maquina_id=maquina_id,
                    temperatura=90.0 + minuto,
                    vibracao=6.2,
                    rpm=2100,
                    minuto=minuto,
                )
            )
        return Machine.objects.get(external_code=maquina_id)

    def test_prescricao_persiste_decision_e_retorna_decision_id(self):
        machine = self._registrar_janela_critica()

        response = self.client.get("/api/prescricoes/?maquina_id=COLH-DEC-01")

        self.assertEqual(response.status_code, 200)
        self.assertIn("decision_id", response.data)
        decision = Decision.objects.get(id=response.data["decision_id"])
        self.assertEqual(decision.machine, machine)
        self.assertEqual(decision.status, Decision.Status.PENDENTE)
        self.assertEqual(decision.severidade, Event.Severidade.CRITICO)
        self.assertIsNone(decision.confianca)
        self.assertIsNone(decision.decidido_por)
        self.assertIsNone(decision.decidido_em)
        self.assertIsNone(decision.outcome_texto)
        self.assertEqual(Decision.objects.filter(machine=machine).count(), 1)

    def test_prescricao_idempotente_reutiliza_decision_pendente_na_janela(self):
        self._registrar_janela_critica()

        primeira = self.client.get("/api/prescricoes/?maquina_id=COLH-DEC-01")
        segunda = self.client.get("/api/prescricoes/?maquina_id=COLH-DEC-01")

        self.assertEqual(primeira.status_code, 200)
        self.assertEqual(segunda.status_code, 200)
        self.assertEqual(primeira.data["decision_id"], segunda.data["decision_id"])
        self.assertEqual(Decision.objects.count(), 1)

    def test_decision_fora_da_janela_nao_bloqueia_nova_decision(self):
        machine = self._registrar_janela_critica()
        primeira = self.client.get("/api/prescricoes/?maquina_id=COLH-DEC-01")
        antiga = Decision.objects.get(id=primeira.data["decision_id"])
        Decision.objects.filter(id=antiga.id).update(
            criado_em=timezone.now() - DECISION_DEDUP_WINDOW - timedelta(minutes=1)
        )

        response = self.client.get("/api/prescricoes/?maquina_id=COLH-DEC-01")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decision.objects.filter(machine=machine).count(), 2)
        self.assertNotEqual(str(antiga.id), response.data["decision_id"])

    def test_aprovada_nao_participa_da_deduplicacao(self):
        machine = self._registrar_janela_critica()
        primeira = self.client.get("/api/prescricoes/?maquina_id=COLH-DEC-01")
        Decision.objects.filter(id=primeira.data["decision_id"]).update(
            status=Decision.Status.APROVADA
        )

        response = self.client.get("/api/prescricoes/?maquina_id=COLH-DEC-01")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decision.objects.filter(machine=machine).count(), 2)

    def test_decision_isolada_por_machine(self):
        machine_a = self._registrar_janela_critica("COLH-DEC-A")
        machine_b = self._registrar_janela_critica("COLH-DEC-B")

        response_a = self.client.get("/api/prescricoes/?maquina_id=COLH-DEC-A")
        response_b = self.client.get("/api/prescricoes/?maquina_id=COLH-DEC-B")

        self.assertEqual(response_a.status_code, 200)
        self.assertEqual(response_b.status_code, 200)
        self.assertNotEqual(response_a.data["decision_id"], response_b.data["decision_id"])
        self.assertEqual(Decision.objects.filter(machine=machine_a).count(), 1)
        self.assertEqual(Decision.objects.filter(machine=machine_b).count(), 1)

    def test_decision_aponta_para_event_aberto_da_mesma_machine(self):
        machine = self._registrar_janela_critica()
        event = Event.objects.filter(machine=machine).latest("criado_em")

        response = self.client.get("/api/prescricoes/?maquina_id=COLH-DEC-01")

        decision = Decision.objects.get(id=response.data["decision_id"])
        self.assertEqual(decision.event, event)
        self.assertEqual(decision.machine, event.machine)
