import hashlib

from django.core.management.base import BaseCommand

from api_tcc.models import DeviceCredential


class Command(BaseCommand):
    help = "Provisiona uma credencial HTTP de dispositivo para bancada."

    def add_arguments(self, parser):
        parser.add_argument("device_id")
        parser.add_argument("device_key")

    def handle(self, *args, **options):
        device_id = options["device_id"]
        key = options["device_key"]
        credential, _ = DeviceCredential.objects.update_or_create(
            device_id=device_id,
            defaults={
                "username": f"device-{device_id}",
                "credential_hash": hashlib.sha256(key.encode()).hexdigest(),
                "http_key_hash": hashlib.sha256(key.encode()).hexdigest(),
                "active": True,
                "http_revoked_at": None,
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Provisionado {credential.device_id}"))
