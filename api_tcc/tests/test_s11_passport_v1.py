import io
import zipfile
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api_tcc.models import Decision, Event, LeituraTelemetria, Machine, Membership, Organization, WorkOrder
from api_tcc.services.passport import export_passport, import_passport, validate_passport


@override_settings(FIELDNODE_PASSPORT_SIGNING_KEY="round-trip-test-key", FIELDNODE_PASSPORT_SIGNING_KEY_ID="test")
class PassportRoundTripTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("passport-admin", password="pass")
        self.source = Organization.objects.create(nome="Origem")
        self.target = Organization.objects.create(nome="Destino")
        Membership.objects.create(user=self.user, organization=self.source, role="admin")
        Membership.objects.create(user=self.user, organization=self.target, role="admin")
        self.machine = Machine.objects.create(organization=self.source, external_code="PASS-01", tipo="trator")
        self.reading = LeituraTelemetria.objects.create(machine=self.machine, maquina_id="PASS-01", device_id="PASS-01", message_id="m-1", temperatura=80, vibracao=2, rpm=1500, timestamp=timezone.now(), data_origin="simulado")
        self.event = Event.objects.create(machine=self.machine, leitura_origem=self.reading, tipo=Event.Tipo.TEMP_ALTA, severidade=Event.Severidade.ATENCAO)
        self.decision = Decision.objects.create(machine=self.machine, event=self.event, texto="Inspecionar", acao_recomendada="Abrir OS", severidade=Event.Severidade.ATENCAO, status=Decision.Status.EXECUTADA, decidido_por=self.user, decidido_em=timezone.now(), outcome_texto="Concluida")
        WorkOrder.objects.create(decision=self.decision, machine=self.machine, titulo="OS", descricao="Descricao", prioridade=Event.Severidade.ATENCAO, responsavel_usuario=self.user, prazo=timezone.now() + timedelta(days=1), criado_por=self.user)

    def test_export_validate_import_reproduces_counts(self):
        blob = export_passport(organization=self.source)
        _, manifest = validate_passport(blob)
        self.assertEqual(manifest["record_counts"], {"telemetry": 1, "events": 1, "decisions": 1, "work_orders": 1})
        result = import_passport(blob, organization=self.target)
        self.assertEqual(result["counts"], {"telemetry": 1, "events": 1, "decisions": 1, "work_orders": 1})
        self.assertEqual(LeituraTelemetria.objects.filter(machine__organization=self.target).count(), 1)

    def test_manifest_does_not_contain_secrets_and_zip_paths_are_fixed(self):
        blob = export_passport(organization=self.source)
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            self.assertEqual(set(archive.namelist()), {"manifest.json", "telemetry.csv", "events.json", "decisions.json", "work_orders.json", "provenance.json", "FORMAT.md"})
            self.assertNotIn(b"webhook_secret", archive.read("manifest.json"))


class VersionedApiTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("v1-admin", password="pass")
        self.org = Organization.objects.create(nome="V1")
        Membership.objects.create(user=self.user, organization=self.org, role="admin")
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_v1_and_legacy_alias_are_exposed(self):
        v1 = self.client.get("/api/v1/auth/me/")
        legacy = self.client.get("/api/auth/me/")
        self.assertEqual(v1.status_code, 200)
        self.assertEqual(legacy.status_code, 200)
        self.assertEqual(legacy.headers["Deprecation"], "true")
        self.assertEqual(legacy.json(), v1.json())
