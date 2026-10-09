from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from api_tcc.models import DeadLetterEntry
from api_tcc.services.agentic import (
    METHODOLOGY,
    chamar_gemini,
    carregar_prompt,
    candidatos_agenticos,
    decisao_agentica_existente,
    montar_contexto,
    persistir_decisao_agentica,
)
from api_tcc.services.dlq import registrar_falha_dlq


class Command(BaseCommand):
    help = "Propõe Decisions via Gemini para Events de maior prioridade; nunca executa ações."

    def add_arguments(self, parser):
        parser.add_argument("--horas", type=int, default=24)
        parser.add_argument("--limite-eventos", type=int, default=5)
        parser.add_argument("--machine", dest="machine_id")
        parser.add_argument("--force", action="store_true", help="ignora a deduplicação diária")

    def handle(self, *args, **options):
        if options["horas"] <= 0 or options["limite_eventos"] <= 0:
            self.stderr.write(self.style.ERROR("horas e limite-eventos devem ser positivos"))
            return

        agora = timezone.now()
        desde = agora - timedelta(hours=options["horas"])
        candidatos = candidatos_agenticos(
            horas=options["horas"],
            limite_eventos=options["limite_eventos"],
            machine_id=options.get("machine_id"),
        )
        criadas = ignoradas = falhas = 0

        for machine, events in candidatos:
            if not options["force"] and decisao_agentica_existente(machine, desde=desde):
                ignoradas += 1
                continue
            contexto = montar_contexto(machine, events)
            try:
                saida = chamar_gemini(carregar_prompt(contexto))
                decision = persistir_decisao_agentica(machine, events, saida)
            except Exception as exc:
                falhas += 1
                registrar_falha_dlq(
                    contexto=DeadLetterEntry.Contexto.AGENTIC_LLM,
                    payload_referencia={
                        "metodologia": METHODOLOGY,
                        "machine_id": str(machine.id),
                        "machine_external_code": machine.external_code,
                        "event_ids": [str(event.id) for event in events],
                    },
                    motivo=str(exc),
                )
                self.stderr.write(self.style.WARNING(f"{machine.external_code}: tentativa enviada à DLQ"))
                continue

            criadas += 1
            self.stdout.write(self.style.SUCCESS(
                f"Decision {decision.id} criada para {machine.external_code} (PENDENTE, {METHODOLOGY})"
            ))

        self.stdout.write(f"Resumo: candidatas={len(candidatos)} criadas={criadas} ignoradas={ignoradas} falhas={falhas}")
