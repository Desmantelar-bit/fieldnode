"""Endpoint de leitura do protótipo de motor CAN."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.models import DTCMotor, LeituraCANMotor
from api_tcc.permissions import IsAuthenticatedOrPublicDemo, get_machine_for_request
from api_tcc.services.can_motor import resumir_qualidade
from api_tcc.ia.prescricao_motor import DTC_REFERENCIAS, gerar_prescricoes

CAMPOS_SERIE = (
    "rpm", "carga_pct", "horimetro_h", "oleo_pressao_kpa", "oleo_temp_c",
    "oleo_nivel_pct", "liquido_temp_c", "liquido_nivel_pct", "rail_pressao_kpa",
    "combustivel_temp_c", "consumo_lh", "turbo_pressao_kpa", "escape_temp_c", "bateria_v",
)


def _serializar_leitura(leitura):
    dados = {
        "id": str(leitura.id),
        "maquina_id": leitura.maquina_id,
        "timestamp": leitura.timestamp.isoformat(),
        "recebido_em": leitura.recebido_em.isoformat(),
        "simulado": leitura.simulado,
    }
    dados.update({campo: getattr(leitura, campo) for campo in CAMPOS_SERIE})
    return dados


class MotorCANView(APIView):
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request):
        maquina_id = request.query_params.get("maquina_id")
        if not maquina_id or not maquina_id.strip():
            return Response({"erro": "maquina_id é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)
        maquina_id = maquina_id.strip().upper()
        if len(maquina_id) > 50:
            return Response({"erro": "maquina_id excede 50 caracteres"}, status=status.HTTP_400_BAD_REQUEST)
        machine = get_machine_for_request(request, maquina_id)
        if machine is None:
            return Response({"erro": "máquina não disponível para este usuário"}, status=status.HTTP_404_NOT_FOUND)

        qualidade = resumir_qualidade(maquina_id)
        leituras_recentes = qualidade.pop("_validas_recentes")
        prescricoes = gerar_prescricoes(leituras_recentes[-60:])
        dtcs_query = DTCMotor.objects.filter(maquina_id=maquina_id, ativo=True).order_by("-ultima_vez")
        dtcs = [
            {
                "spn": dtc.spn,
                "fmi": dtc.fmi,
                "ocorrencias": dtc.ocorrencias,
                "ativo": dtc.ativo,
                "primeira_vez": dtc.primeira_vez.isoformat(),
                "ultima_vez": dtc.ultima_vez.isoformat(),
                "subsistema": _subsistema_dtc(dtc.spn),
                "descricao_referencia": DTC_REFERENCIAS.get((dtc.spn, dtc.fmi)),
                "simulado": dtc.simulado,
            }
            for dtc in dtcs_query
        ]
        simuladas = LeituraCANMotor.objects.filter(maquina_id=maquina_id, simulado=True).count()
        recebidas = qualidade["recebidas"]
        misto = 0 < simuladas < recebidas
        simulado = bool(simuladas) if recebidas else bool(machine.is_demo)
        origem = "MISTO" if misto else ("SIMULADO" if simulado else "REAL")
        return Response({
            "ultima_leitura": _serializar_leitura(leituras_recentes[-1]) if leituras_recentes else None,
            "serie": [_serializar_leitura(item) for item in leituras_recentes],
            "dtcs_ativos": dtcs,
            "prescricoes": prescricoes,
            "qualidade": qualidade,
            "simulado": simulado,
            "origem_dados": origem,
        })


def _subsistema_dtc(spn):
    return {
        100: "lubrificacao",
        102: "admissao",
        110: "arrefecimento",
        157: "combustivel_alta_pressao",
    }.get(spn, "nao_classificado")
