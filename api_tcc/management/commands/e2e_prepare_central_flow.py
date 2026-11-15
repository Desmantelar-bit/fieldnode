"""Prepare isolated, deterministic data for the S3-T11 real-stack E2E.

This command deliberately uses the telemetry domain service.  It does not
insert Event or Decision rows directly, so the browser test still exercises
the production ingestion and decision paths.
"""

import json
import uuid
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from rest_framework.authtoken.models import Token

from api_tcc.models import Event, Machine, Membership, Organization
from api_tcc.services.decisions import persistir_decision_da_analise
from api_tcc.services.telemetria import registrar_leitura


class Command(BaseCommand):
    help = "Prepara dados isolados para o E2E real do fluxo central S3-T11."

    def add_arguments(self, parser):
        parser.add_argument("--run-id", default=None)

    def handle(self, *args, **options):
        run_id = (options["run_id"] or uuid.uuid4().hex[:12]).lower()
        machine_code = f"E2E-S3-T11-{run_id}".upper()
        username = f"e2e_{run_id}"

        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.invalid"},
        )
        if not user.has_usable_password():
            user.set_unusable_password()
            user.save(update_fields=["password"])

        organization = Organization.objects.create(nome=f"E2E S3-T11 {run_id}")
        machine = Machine.objects.create(
            external_code=machine_code,
            organization=organization,
            is_demo=False,
        )
        Membership.objects.create(user=user, organization=organization, role="admin")

        message_id = str(uuid.uuid4())
        result, reading_id = registrar_leitura(
            {
                "maquina_id": machine_code,
                "device_id": machine_code,
                "message_id": message_id,
                "sequence_number": 1,
                "temperatura": 115.0,
                "vibracao": 2.0,
                "vibracao_unit": "indice_0_10",
                "rpm": 1800,
                "timestamp": timezone.now().isoformat(),
                "time_source": "gateway",
                "source": "e2e_s3_t11",
                "transport": "management_command",
                "manufacturer": "fieldnode_e2e_s3_t11",
                "schema_version": "1.0",
            }
        )
        if result != "criado":
            raise CommandError(f"ingestão E2E falhou: {result} {reading_id}")

        event = (
            Event.objects.filter(machine=machine, leitura_origem_id=reading_id)
            .order_by("-criado_em")
            .first()
        )
        if event is None or event.severidade != Event.Severidade.CRITICO:
            raise CommandError("a leitura não produziu um Event CRITICO")

        # Reuse the central Decision service with the real Event produced by
        # ingestion.  The analysis object is deliberately minimal here: this
        # command is a deterministic test-data adapter, not a second ML path.
        analysis = SimpleNamespace(
            maquina_id=machine_code,
            status=Event.Severidade.CRITICO,
            recomendacao="Investigar a leitura crítica e validar o sensor antes de intervir.",
        )
        decision = persistir_decision_da_analise(analysis)
        if decision.event_id != event.id:
            decision.event = event
            decision.save(update_fields=["event"])

        token, _ = Token.objects.get_or_create(user=user)
        self.stdout.write(json.dumps({
            "run_id": run_id,
            "username": username,
            "token": token.key,
            "machine_code": machine_code,
            "reading_id": str(reading_id),
            "event_id": str(event.id),
            "event_severity": event.severidade,
            "priority_band": "P1" if event.severidade == Event.Severidade.CRITICO else "P2",
            "decision_id": str(decision.id),
            "origin": "simulado_e2e",
        }))
