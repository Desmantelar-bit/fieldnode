from datetime import timedelta
from io import StringIO
from uuid import uuid4

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone

from api_tcc.models import Event, Machine, Organization, OrganizationPolicy, RetentionPurgeRun


class RetentionCommandTests(TestCase):
    def setUp(self):
        self.org_a = Organization.objects.create(nome="Retention A")
        self.org_b = Organization.objects.create(nome="Retention B")
        self.machine_a = Machine.objects.create(external_code="RET-A-" + uuid4().hex[:8], organization=self.org_a)
        self.machine_b = Machine.objects.create(external_code="RET-B-" + uuid4().hex[:8], organization=self.org_b)
        for org in (self.org_a, self.org_b):
            OrganizationPolicy.objects.create(
                organization=org, retention_policy={"eventos": 1}, retention_policy_version="test-v1"
            )

    def test_purga_isola_organizacao_e_respeita_dry_run(self):
        old = timezone.now() - timedelta(days=3)
        event_a = Event.objects.create(machine=self.machine_a, tipo=Event.Tipo.TEMP_ALTA)
        event_b = Event.objects.create(machine=self.machine_b, tipo=Event.Tipo.TEMP_ALTA)
        Event.objects.filter(pk__in=[event_a.pk, event_b.pk]).update(criado_em=old)
        output = StringIO()

        call_command("purgar_dados_antigos", organization=str(self.org_a.pk), category="eventos", dry_run=True, stdout=output)
        self.assertEqual(Event.objects.filter(pk=event_a.pk).count(), 1)
        self.assertEqual(Event.objects.filter(pk=event_b.pk).count(), 1)

        call_command("purgar_dados_antigos", organization=str(self.org_a.pk), category="eventos", execute=True, stdout=output)
        self.assertFalse(Event.objects.filter(pk=event_a.pk).exists())
        self.assertTrue(Event.objects.filter(pk=event_b.pk).exists())
        self.assertEqual(RetentionPurgeRun.objects.filter(organization_id_text=str(self.org_a.pk)).count(), 2)

    def test_politica_ausente_bloqueia(self):
        org = Organization.objects.create(nome="Sem política")
        with self.assertRaises(CommandError):
            call_command("purgar_dados_antigos", organization=str(org.pk), dry_run=True)
