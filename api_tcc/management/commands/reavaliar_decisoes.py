from django.core.management.base import BaseCommand

from api_tcc.models import WorkOrder
from api_tcc.services.reevaluation import RESULTS, reevaluate_work_order


class Command(BaseCommand):
    help = "Reavalia WorkOrders concluídas usando a política de telemetria da organização."

    def handle(self, *args, **options):
        counts = {"avaliadas": 0, "insuficientes": 0, "falhas": 0}
        orders = WorkOrder.objects.filter(status=WorkOrder.Status.CONCLUIDA).select_related("decision", "machine", "machine__organization")
        for order in orders.iterator():
            try:
                record = reevaluate_work_order(order)
                counts["avaliadas"] += 1
                if record.resultado == RESULTS.DADOS_INSUFICIENTES:
                    counts["insuficientes"] += 1
            except Exception as exc:
                counts["falhas"] += 1
                self.stderr.write(self.style.ERROR(f"OS {order.id}: {exc}"))
        self.stdout.write(self.style.SUCCESS("Reavaliação concluída: " + ", ".join(f"{key}={value}" for key, value in counts.items())))
