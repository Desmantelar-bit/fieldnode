from datetime import timedelta
import uuid

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api_tcc.authentication import is_token_expired
from api_tcc.models import (
    Decision,
    Event,
    LeituraTelemetria,
    Machine,
    Membership,
    Organization,
    RegistroAnalise,
)
from api_tcc.services.telemetria import registrar_leitura


def _payload(maquina_id: str, temperatura: float, vibracao: float, rpm: int, minuto: int = 1):
    return {
        "id": str(uuid.uuid4()),
        "maquina_id": maquina_id,
        "temperatura": temperatura,
        "vibracao": vibracao,
        "rpm": rpm,
        "timestamp": f"2026-09-21T12:{minuto:02d}:00Z",
    }


class ContractBlockersAndRisksFixesTest(TestCase):
    """
    Testes de verificação dos bloqueadores e riscos resolvidos no contrato de integração:
    - GET /api/events/ (listagem, filtros, paginação, detalhe)
    - GET /api/decisions/ (listagem, filtros, paginação, detalhe)
    - GET /api/leituras/ultimas/ (paginação configurável)
    - ExpiringTokenAuthentication e POST /api/auth/login/
    - Resolução unificada de machine_id (UUID e string external_code)
    - GET /api/prescricoes/{maquina_id}/ sempre read-only; POST persiste explicitamente
    - GET /api/relatorio/exportar/ unificado (xlsx e csv)
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="contract-tester",
            password="secure-password-123",
        )
        self.organization = Organization.objects.create(nome="Org Teste Contrato")
        Membership.objects.create(
            user=self.user,
            organization=self.organization,
            role="operator",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.machine = Machine.objects.create(
            organization=self.organization,
            external_code="COLH-TEST-01",
        )

        # Máquina de outra organização para testar isolamento multi-tenant
        self.other_org = Organization.objects.create(nome="Org Outra")
        self.other_machine = Machine.objects.create(
            organization=self.other_org,
            external_code="COLH-OUTRA-01",
        )

    # 1. 🔴 Bloqueador: GET /api/events/
    def test_events_list_and_filters(self):
        event1 = Event.objects.create(
            machine=self.machine,
            tipo=Event.Tipo.TEMP_ALTA,
            severidade=Event.Severidade.CRITICO,
            status=Event.Status.ABERTO,
            dados_contexto={"detalhe": "Temperatura acima do limite crítico"},
        )
        event2 = Event.objects.create(
            machine=self.machine,
            tipo=Event.Tipo.VIBRACAO_ALTA,
            severidade=Event.Severidade.ATENCAO,
            status=Event.Status.ABERTO,
            dados_contexto={"detalhe": "Vibração elevada detectada"},
        )
        # Evento de outra org
        Event.objects.create(
            machine=self.other_machine,
            tipo=Event.Tipo.TEMP_ALTA,
            severidade=Event.Severidade.CRITICO,
            status=Event.Status.ABERTO,
            dados_contexto={"detalhe": "Evento confidencial da outra org"},
        )

        # Listagem padrão
        resp = self.client.get("/api/events/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["count"], 2)
        self.assertEqual(len(data["results"]), 2)

        # Filtro por tipo
        resp_filter_tipo = self.client.get(f"/api/events/?tipo={Event.Tipo.TEMP_ALTA}")
        self.assertEqual(resp_filter_tipo.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_filter_tipo.json()["count"], 1)
        self.assertEqual(resp_filter_tipo.json()["results"][0]["id"], str(event1.id))

        # Filtro por severidade
        resp_filter_sev = self.client.get(f"/api/events/?severidade={Event.Severidade.ATENCAO}")
        self.assertEqual(resp_filter_sev.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_filter_sev.json()["count"], 1)
        self.assertEqual(resp_filter_sev.json()["results"][0]["id"], str(event2.id))

        # Filtro por maquina_id (string)
        resp_filter_maq = self.client.get("/api/events/?maquina_id=COLH-TEST-01")
        self.assertEqual(resp_filter_maq.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_filter_maq.json()["count"], 2)

        # Filtro por maquina_id (UUID)
        resp_filter_uuid = self.client.get(f"/api/events/?maquina_id={self.machine.id}")
        self.assertEqual(resp_filter_uuid.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_filter_uuid.json()["count"], 2)

        # Detalhe do evento
        resp_detail = self.client.get(f"/api/events/{event1.id}/")
        self.assertEqual(resp_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_detail.json()["id"], str(event1.id))
        self.assertEqual(resp_detail.json()["machine_external_code"], "COLH-TEST-01")

    # 2. 🔴 Bloqueador: GET /api/decisions/
    def test_decisions_list_and_filters(self):
        dec1 = Decision.objects.create(
            machine=self.machine,
            acao_recomendada="reduzir_rotacao",
            severidade=Event.Severidade.CRITICO,
            status=Decision.Status.PENDENTE,
            texto="RPM excessivo",
        )
        dec2 = Decision.objects.create(
            machine=self.machine,
            acao_recomendada="inspecionar_pneus",
            severidade=Event.Severidade.ATENCAO,
            status=Decision.Status.APROVADA,
            texto="Pressão irregular",
        )
        # Decisão de outra org
        Decision.objects.create(
            machine=self.other_machine,
            acao_recomendada="outra_acao",
            severidade=Event.Severidade.CRITICO,
            status=Decision.Status.PENDENTE,
            texto="Outra org",
        )

        # Listagem
        resp = self.client.get("/api/decisions/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["count"], 2)

        # Filtro por status
        resp_pend = self.client.get(f"/api/decisions/?status={Decision.Status.PENDENTE}")
        self.assertEqual(resp_pend.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_pend.json()["count"], 1)
        self.assertEqual(resp_pend.json()["results"][0]["id"], str(dec1.id))

        # Detalhe da decisão via GET /api/decisions/<uuid:decision_id>/
        resp_detail = self.client.get(f"/api/decisions/{dec1.id}/")
        self.assertEqual(resp_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_detail.json()["id"], str(dec1.id))
        self.assertEqual(resp_detail.json()["acao_recomendada"], "reduzir_rotacao")

    # 3. 🟠 Risco Alto: Paginação em /api/leituras/ultimas/
    def test_ultimas_leituras_pagination(self):
        # Cria leituras para múltiplas máquinas
        machines = []
        for i in range(15):
            m = Machine.objects.create(
                organization=self.organization,
                external_code=f"COLH-FROTA-{i:02d}",
            )
            machines.append(m)
            LeituraTelemetria.objects.create(
                machine=m,
                maquina_id=f"COLH-FROTA-{i:02d}",
                device_id=f"COLH-FROTA-{i:02d}",
                message_id=f"msg-pag-{i:02d}",
                timestamp=timezone.now(),
                temperatura=70.0 + i,
                vibracao=2.0,
                rpm=1800,
            )

        resp = self.client.get("/api/leituras/ultimas/?limit=5&offset=0")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.headers.get("X-Limit"), "5")
        self.assertEqual(resp.headers.get("X-Offset"), "0")
        self.assertGreaterEqual(int(resp.headers.get("X-Total-Count", 0)), 15)
        self.assertEqual(len(resp.json()), 5)

        # Página 2
        resp_p2 = self.client.get("/api/leituras/ultimas/?page=2&page_size=5")
        self.assertEqual(resp_p2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_p2.json()), 5)

    # 4. 🟠 Risco Alto: ExpiringTokenAuthentication e POST /api/auth/login/
    def test_expiring_token_authentication(self):
        # Teste de login retornando token e expires_in
        anon_client = APIClient()
        resp_login = anon_client.post(
            "/api/auth/login/",
            {"username": "contract-tester", "password": "secure-password-123"},
            format="json",
        )
        self.assertEqual(resp_login.status_code, status.HTTP_200_OK)
        login_data = resp_login.json()
        self.assertIn("token", login_data)
        self.assertIn("expires_in", login_data)
        self.assertGreater(login_data["expires_in"], 0)

        # Autenticação com token válido funciona
        auth_client = APIClient()
        auth_client.credentials(HTTP_AUTHORIZATION=f"Token {login_data['token']}")
        resp_me = auth_client.get("/api/events/")
        self.assertEqual(resp_me.status_code, status.HTTP_200_OK)

        # Força expiração do token retroagindo o created
        token_obj = Token.objects.get(key=login_data["token"])
        token_obj.created = timezone.now() - timedelta(hours=25)
        token_obj.save()

        self.assertTrue(is_token_expired(token_obj))

        # Requisição com token expirado deve ser rejeitada com 401
        resp_expired = auth_client.get("/api/events/")
        self.assertEqual(resp_expired.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Token expirado", resp_expired.json().get("detail", ""))

        # Novo login gera/renova o token
        resp_renew = anon_client.post(
            "/api/auth/login/",
            {"username": "contract-tester", "password": "secure-password-123"},
            format="json",
        )
        self.assertEqual(resp_renew.status_code, status.HTTP_200_OK)
        new_token = resp_renew.json()["token"]
        self.assertNotEqual(new_token, token_obj.key)

    # 5. 🟡 Risco Médio: Resolução de machine_id (UUID vs string)
    def test_machine_health_accepts_uuid_and_string(self):
        # Acesso por external_code string
        resp_str = self.client.get(f"/api/machines/{self.machine.external_code}/health/")
        self.assertEqual(resp_str.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_str.json()["machine_id"], str(self.machine.id))
        self.assertEqual(resp_str.json()["external_code"], self.machine.external_code)

        # Acesso por UUID
        resp_uuid = self.client.get(f"/api/machines/{self.machine.id}/health/")
        self.assertEqual(resp_uuid.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_uuid.json()["machine_id"], str(self.machine.id))

    # 6. GET de prescrição é read-only; persistência explícita usa POST.
    def test_prescricao_preview_does_not_persist_decision(self):
        # Registrar telemetria crítica
        for m in range(3):
            registrar_leitura(
                _payload(
                    maquina_id=self.machine.external_code,
                    temperatura=92.0 + m,
                    vibracao=6.5,
                    rpm=2100,
                    minuto=m,
                )
            )

        decisions_before = Decision.objects.filter(machine=self.machine).count()
        analyses_before = RegistroAnalise.objects.count()

        # GET é sempre read-only; não depende de query param para evitar escrita.
        resp_preview = self.client.get(f"/api/prescricoes/{self.machine.external_code}/")
        self.assertEqual(resp_preview.status_code, status.HTTP_200_OK)
        self.assertTrue(resp_preview.json().get("preview", False))

        decisions_after = Decision.objects.filter(machine=self.machine).count()
        self.assertEqual(decisions_after, decisions_before, "Preview não deve criar nova Decision no banco")
        self.assertEqual(RegistroAnalise.objects.count(), analyses_before)

        # Geração explícita via POST /api/prescricoes/<maquina_id>/
        resp_post = self.client.post(f"/api/prescricoes/{self.machine.external_code}/")
        self.assertEqual(resp_post.status_code, status.HTTP_200_OK)
        self.assertFalse(resp_post.json().get("preview", True))
        self.assertGreater(Decision.objects.filter(machine=self.machine).count(), decisions_before)

    # 7. 🟡 Risco Médio: RelatorioExportarView unificado (xlsx e csv)
    def test_relatorio_exportar_formats(self):
        resp_xlsx = self.client.get(f"/api/relatorio/exportar/?maquina_id={self.machine.external_code}&formato=xlsx")
        self.assertEqual(resp_xlsx.status_code, status.HTTP_200_OK)
        self.assertIn("application/vnd.openxmlformats-officedocument", resp_xlsx.headers["Content-Type"])

        resp_csv = self.client.get(f"/api/relatorio/exportar/?maquina_id={self.machine.external_code}&formato=csv")
        self.assertEqual(resp_csv.status_code, status.HTTP_200_OK)
        self.assertIn("text/csv", resp_csv.headers["Content-Type"])
