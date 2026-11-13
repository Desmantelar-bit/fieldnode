import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from api_tcc.models import SecurityCounter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Remove contadores expirados de autenticação e throttling."

    def handle(self, *args, **options):
        deleted, _ = SecurityCounter.objects.filter(expires_at__lte=timezone.now()).delete()
        logger.info("Contadores de segurança expirados removidos: %d", deleted)
        self.stdout.write(str(deleted))
