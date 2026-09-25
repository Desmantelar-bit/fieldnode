from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api_tcc.models import Colheitadeira, LeituraTelemetria, Machine, Membership, Organization


class Command(BaseCommand):
    help = (
        "Vincula colheitadeiras e leituras legadas a uma organização e a um usuário administrador."
    )

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True, help="Usuário que administrará a frota legada.")
        parser.add_argument("--organization", required=True, help="Organização proprietária da frota legada.")

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"].strip()
        organization_name = options["organization"].strip()
        if not username or not organization_name:
            raise CommandError("--username e --organization não podem ser vazios.")

        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=username)
        except user_model.DoesNotExist as error:
            raise CommandError(f"Usuário '{username}' não encontrado.") from error

        organization, organization_created = Organization.objects.get_or_create(nome=organization_name)
        _, membership_created = Membership.objects.get_or_create(
            user=user,
            organization=organization,
            defaults={"role": "admin"},
        )

        machines_created = 0
        readings_linked = 0
        for colheitadeira in Colheitadeira.objects.filter(ativo=True, machine__isnull=True):
            external_code = (colheitadeira.maquina_id or "").strip().upper()
            if not external_code:
                self.stderr.write(
                    self.style.WARNING(
                        f"Colheitadeira #{colheitadeira.pk} ignorada: maquina_id ausente."
                    )
                )
                continue

            machine, created = Machine.objects.get_or_create(
                external_code=external_code,
                defaults={
                    "organization": organization,
                    "colheitadeira": colheitadeira,
                    "ativo": colheitadeira.ativo,
                },
            )
            if not created and machine.organization_id != organization.id:
                raise CommandError(
                    f"A máquina '{external_code}' já pertence a outra organização; nada foi alterado."
                )

            if created:
                machines_created += 1
            elif machine.colheitadeira_id is None:
                machine.colheitadeira = colheitadeira
                machine.save(update_fields=["colheitadeira"])

            readings_linked += LeituraTelemetria.objects.filter(
                machine__isnull=True,
                maquina_id__iexact=colheitadeira.maquina_id,
            ).update(machine=machine)

        self.stdout.write(
            self.style.SUCCESS(
                "Frota legada vinculada: "
                f"organização={'criada' if organization_created else 'existente'}, "
                f"membership={'criado' if membership_created else 'existente'}, "
                f"máquinas criadas={machines_created}, leituras vinculadas={readings_linked}."
            )
        )
