from django.core.management.base import BaseCommand, CommandError

from api_tcc.services.device_credentials import provision_http_credential


class Command(BaseCommand):
    help = "Provisiona, rotaciona ou revoga uma credencial HTTP individual de dispositivo."

    def add_arguments(self, parser):
        parser.add_argument("device_id")
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument("--rotate", action="store_true")
        mode.add_argument("--revoke", action="store_true")

    def handle(self, *args, **options):
        try:
            key = provision_http_credential(
                options["device_id"], rotate=options["rotate"], revoke=options["revoke"]
            )
        except ValueError as exc:
            raise CommandError(str(exc)) from exc
        if key:
            self.stdout.write(f"X-Device-Id: {options['device_id']}\nX-Device-Key (exibida uma vez): {key}")
        else:
            self.stdout.write(self.style.SUCCESS("Credencial HTTP revogada."))
