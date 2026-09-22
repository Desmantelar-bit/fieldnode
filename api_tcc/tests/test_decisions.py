from datetime import timedelta
import uuid

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api_tcc.models import Decision, Event, Machine
from api_tcc.services.decisions import (
    DECISION_DEDUP_WINDOW,
    validar_transicao_decision,
)
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


class DecisionActionViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_a = User.objects.create_user(
            username="operador-a",
            password="senha-forte-123",
        )
        self.user_b = User.objects.create_user(
            username="operador-b",
            password="senha-forte-123",
        )
        self.token_a = Token.objects.create(user=self.user_a)
        self.token_b = Token.objects.create(user=self.user_b)
        self.machine = Machine.objects.create(external_code="COLH-ACTION-01")

    def _auth_as(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def _decision(self, status_atual=Decision.Status.PENDENTE, **kwargs):
        return Decision.objects.create(
            machine=self.machine,
            texto="Temperatura alta detectada.",
            acao_recomendada="Inspecionar sistema de arrefecimento.",
            severidade=Event.Severidade.CRITICO,
            status=status_atual,
            **kwargs,
        )

    def test_matriz_de_transicoes_da_decision(self):
        casos = [
            (Decision.Status.PENDENTE, Decision.Status.APROVADA, True),
            (Decision.Status.PENDENTE, Decision.Status.REJEITADA, True),
            (Decision.Status.PENDENTE, Decision.Status.EXPIRADA, True),
            (Decision.Status.PENDENTE, Decision.Status.EXECUTADA, False),
            (Decision.Status.APROVADA, Decision.Status.EXECUTADA, True),
            (Decision.Status.APROVADA, Decision.Status.REJEITADA, False),
            (Decision.Status.APROVADA, Decision.Status.APROVADA, False),
            (Decision.Status.REJEITADA, Decision.Status.APROVADA, False),
            (Decision.Status.REJEITADA, Decision.Status.EXECUTADA, False),
            (Decision.Status.EXECUTADA, Decision.Status.APROVADA, False),
            (Decision.Status.EXECUTADA, Decision.Status.REJEITADA, False),
            (Decision.Status.EXPIRADA, Decision.Status.APROVADA, False),
            (Decision.Status.EXPIRADA, Decision.Status.EXECUTADA, False),
        ]

        for origem, destino, esperado in casos:
            with self.subTest(origem=origem, destino=destino):
                self.assertEqual(validar_transicao_decision(origem, destino), esperado)

    def test_aprovacao_valida_registra_auditoria_do_usuario_autenticado(self):
        decision = self._decision()
        self._auth_as(self.token_a)

        response = self.client.patch(
            f"/api/decisions/{decision.id}/",
            {"status": Decision.Status.APROVADA},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        decision.refresh_from_db()
        self.assertEqual(decision.status, Decision.Status.APROVADA)
        self.assertEqual(decision.decidido_por, self.user_a)
        self.assertIsNotNone(decision.decidido_em)
        self.assertEqual(response.data["decidido_por"], self.user_a.id)

    def test_rejeicao_valida_persiste_outcome(self):
        decision = self._decision()
        self._auth_as(self.token_a)

        response = self.client.patch(
            f"/api/decisions/{decision.id}/",
            {
                "status": Decision.Status.REJEITADA,
                "outcome_texto": "Inspecao manual nao confirmou a condicao.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        decision.refresh_from_db()
        self.assertEqual(decision.status, Decision.Status.REJEITADA)
        self.assertEqual(decision.decidido_por, self.user_a)
        self.assertIsNotNone(decision.decidido_em)
        self.assertEqual(
            decision.outcome_texto,
            "Inspecao manual nao confirmou a condicao.",
        )

    def test_execucao_valida_preserva_autor_original_da_aprovacao(self):
        aprovado_em = timezone.now() - timedelta(minutes=5)
        decision = self._decision(
            Decision.Status.APROVADA,
            decidido_por=self.user_a,
            decidido_em=aprovado_em,
            outcome_texto="Inspecao autorizada.",
        )
        self._auth_as(self.token_b)

        response = self.client.patch(
            f"/api/decisions/{decision.id}/",
            {
                "status": Decision.Status.EXECUTADA,
                "outcome_texto": "Filtro substituido durante manutencao.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        decision.refresh_from_db()
        self.assertEqual(decision.status, Decision.Status.EXECUTADA)
        self.assertEqual(decision.decidido_por, self.user_a)
        self.assertEqual(decision.decidido_em, aprovado_em)
        self.assertEqual(
            decision.outcome_texto,
            "Filtro substituido durante manutencao.",
        )

    def test_transicao_invalida_pendente_para_executada_retorna_400_sem_alterar(self):
        decision = self._decision(outcome_texto="Texto original.")
        self._auth_as(self.token_a)

        response = self.client.patch(
            f"/api/decisions/{decision.id}/",
            {"status": Decision.Status.EXECUTADA, "outcome_texto": "Nao salvar."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        decision.refresh_from_db()
        self.assertEqual(decision.status, Decision.Status.PENDENTE)
        self.assertIsNone(decision.decidido_por)
        self.assertIsNone(decision.decidido_em)
        self.assertEqual(decision.outcome_texto, "Texto original.")

    def test_endpoint_exige_token_valido(self):
        decision = self._decision()

        sem_token = self.client.patch(
            f"/api/decisions/{decision.id}/",
            {"status": Decision.Status.APROVADA},
            format="json",
        )
        self.assertEqual(sem_token.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION="Token token-invalido")
        token_invalido = self.client.patch(
            f"/api/decisions/{decision.id}/",
            {"status": Decision.Status.APROVADA},
            format="json",
        )
        self.assertEqual(token_invalido.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cliente_nao_consegue_falsificar_campos_de_auditoria_ou_origem(self):
        outra_machine = Machine.objects.create(external_code="COLH-OUTRA")
        decision = self._decision(confianca=0.25)
        criado_em_original = decision.criado_em
        self._auth_as(self.token_a)

        response = self.client.patch(
            f"/api/decisions/{decision.id}/",
            {
                "status": Decision.Status.APROVADA,
                "decidido_por": self.user_b.id,
                "confianca": 0.99,
                "machine": str(outra_machine.id),
                "criado_em": "2020-01-01T00:00:00Z",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        decision.refresh_from_db()
        self.assertEqual(decision.status, Decision.Status.PENDENTE)
        self.assertIsNone(decision.decidido_por)
        self.assertEqual(decision.confianca, 0.25)
        self.assertEqual(decision.machine, self.machine)
        self.assertEqual(decision.criado_em, criado_em_original)

    def test_status_obrigatorio_e_decision_inexistente(self):
        decision = self._decision()
        self._auth_as(self.token_a)

        sem_status = self.client.patch(
            f"/api/decisions/{decision.id}/",
            {"outcome_texto": "Sem acao."},
            format="json",
        )
        self.assertEqual(sem_status.status_code, status.HTTP_400_BAD_REQUEST)

        inexistente = self.client.patch(
            f"/api/decisions/{uuid.uuid4()}/",
            {"status": Decision.Status.APROVADA},
            format="json",
        )
        self.assertEqual(inexistente.status_code, status.HTTP_404_NOT_FOUND)
