from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from api_tcc.models import Event, LeituraTelemetria, Machine, Organization
from api_tcc.services import agentic
from api_tcc.services.operation_graph import criar_machine_link


class AgenticOperationGraphGoldenTest(TestCase):
    def test_contexto_golden_inclui_grafo_real_e_eh_repetivel(self):
        organization = Organization.objects.create(nome="Org Golden")
        source = Machine.objects.create(external_code="COLH-GOLDEN", tipo="colhedora", organization=organization)
        transbordo = Machine.objects.create(external_code="TRB-GOLDEN", tipo="transbordo", organization=organization)
        caminhao = Machine.objects.create(external_code="CAM-GOLDEN", tipo="caminhao", organization=organization)
        inicio = timezone.now() - timedelta(minutes=5)
        criar_machine_link(origem=source, destino=transbordo, tipo="TRANSPORTA_PARA", valido_de=inicio, organization=organization)
        criar_machine_link(origem=transbordo, destino=caminhao, tipo="TRANSPORTA_PARA", valido_de=inicio, organization=organization)
        reading = LeituraTelemetria.objects.create(
            maquina_id=source.external_code, machine=source, device_id=source.external_code,
            message_id="golden-1", timestamp=timezone.now(), temperatura=91.2, vibracao=0.5,
        )
        event = Event.objects.create(
            machine=source, leitura_origem=reading, tipo=Event.Tipo.TEMP_ALTA,
            severidade=Event.Severidade.CRITICO, priority_score=0.93,
            dados_contexto={"temperatura": 91.2},
        )

        first = agentic.montar_contexto(source, [event])
        second = agentic.montar_contexto(source, [event])

        self.assertEqual(first, second)
        graph = first["operation_graph"]
        self.assertEqual(graph["schema_version"], "operation_graph.v1")
        self.assertEqual(graph["status"], "disponivel")
        self.assertEqual([item["codigo"] for item in graph["affected_machines"]], ["TRB-GOLDEN", "CAM-GOLDEN"])
        self.assertEqual(graph["affected_machines"][1]["path"][0]["type"], "TRANSPORTA_PARA")
