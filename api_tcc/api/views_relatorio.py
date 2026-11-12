"""Exportação de relatórios executivos FieldNode em formato Excel e CSV."""

import csv
from io import BytesIO

from django.conf import settings
from django.db import models
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from rest_framework.views import APIView

from api_tcc.models import Colheitadeira, LeituraTelemetria, Machine, RegistroAnalise
from api_tcc.permissions import IsAuthenticatedOrPublicDemo, get_machine_for_request
from api_tcc.services.relatorios import preparar_dados_relatorio, _gerar_relatorio_csv_exportar


def _is_demo_publico(request) -> bool:
    return bool(settings.DEMO_MODE and not request.user.is_authenticated)


class RelatorioExportarView(APIView):
    """
    GET /api/relatorio/exportar/?maquina_id=COLH-01&formato=xlsx
    GET /api/relatorio/exportar/?maquina_id=COLH-01&formato=csv&data_inicio=2026-01-01&data_fim=2026-01-31

    Exporta relatório operacional da máquina em formato Excel (.xlsx, padrão) ou CSV (;).
    """

    permission_classes = [IsAuthenticatedOrPublicDemo]

    content_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    verde_fieldnode = "1A3326"
    cinza_fieldnode = "2D3748"

    def get(self, request):
        maquina_id = request.query_params.get("maquina_id")
        if not maquina_id:
            return HttpResponse('Parâmetro "maquina_id" é obrigatório', status=400)

        machine = get_machine_for_request(request, maquina_id)
        if machine is None:
            return HttpResponse("Máquina não encontrada", status=404)

        formato = request.query_params.get("formato", "").lower()
        accept = request.META.get("HTTP_ACCEPT", "")

        # Exportação CSV
        if formato == "csv" or "text/csv" in accept:
            return self._exportar_csv(request, maquina_id, machine)

        # Exportação Excel (.xlsx, padrão)
        return self._exportar_xlsx(machine, maquina_id)

    def _exportar_csv(self, request, maquina_id, machine=None):
        data_inicio = request.query_params.get("data_inicio")
        data_fim = request.query_params.get("data_fim")

        if data_inicio and not parse_date(data_inicio):
            return HttpResponse("data_inicio inválida; use AAAA-MM-DD", status=400)
        if data_fim and not parse_date(data_fim):
            return HttpResponse("data_fim inválida; use AAAA-MM-DD", status=400)

        di = parse_date(data_inicio) if data_inicio else None
        df = parse_date(data_fim) if data_fim else None

        if di and df and df < di:
            return HttpResponse("data_fim deve ser posterior a data_inicio", status=400)

        dados, data_inicio_parsed, data_fim_parsed = preparar_dados_relatorio(
            maquina_id, di, df
        )
        if not dados and machine and machine.external_code != maquina_id:
            dados, data_inicio_parsed, data_fim_parsed = preparar_dados_relatorio(
                machine.external_code, di, df
            )

        if not dados:
            response = HttpResponse(content_type="text/csv; charset=utf-8")
            response["Content-Disposition"] = f'attachment; filename="relatorio_sem_dados_{maquina_id}.csv"'
            response.write("\ufeff")
            writer = csv.writer(response, delimiter=";", lineterminator="\n")
            writer.writerow(["Relatório FieldNode"])
            writer.writerow(["Máquina", maquina_id])
            writer.writerow(["Status", "Sem dados para o período informado"])
            writer.writerow(["Orientação", "Selecione outro período ou aguarde novas leituras de telemetria."])
            return response

        return _gerar_relatorio_csv_exportar(
            maquina_id, data_inicio_parsed, data_fim_parsed,
            dados["stats"], dados["leituras"], dados["prescricoes"]
        )

    def _exportar_xlsx(self, machine, maquina_id):
        leituras_qs = LeituraTelemetria.objects.filter(
            models.Q(machine=machine) | models.Q(maquina_id=machine.external_code) | models.Q(maquina_id=maquina_id)
        )
        leituras = leituras_qs.order_by("timestamp")
        analises = RegistroAnalise.objects.filter(
            models.Q(maquina_id=machine.external_code) | models.Q(maquina_id=maquina_id)
        ).order_by("criado_em")

        workbook = Workbook()
        resumo = workbook.active
        resumo.title = "Resumo"
        self._montar_aba_resumo(resumo, maquina_id, leituras, analises)

        telemetria = workbook.create_sheet("Telemetria")
        self._montar_aba_dados(telemetria, leituras)

        eventos = workbook.create_sheet("Eventos")
        self._montar_aba_eventos(eventos, analises)

        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type=self.content_type)
        response["Content-Disposition"] = (
            f'attachment; filename="fieldnode_relatorio_{maquina_id}.xlsx"'
        )
        return response

    def _montar_aba_resumo(self, ws, maquina_id, leituras, analises):
        ws["A1"] = "FieldNode — Relatório Executivo de Telemetria"
        ws["A1"].font = Font(name="Calibri", bold=True, size=16, color=self.verde_fieldnode)
        ws["A1"].alignment = Alignment(vertical="center")
        ws.merge_cells("A1:D1")
        ws.row_dimensions[1].height = 28

        metricas = (
            ("Identificador da Máquina", maquina_id),
            ("Total de Leituras Capturadas", leituras.count()),
            ("Alertas Críticos Registrados", analises.filter(status="CRITICO").count()),
            ("Alertas de Atenção Registrados", analises.filter(status="ATENCAO").count()),
        )
        for row, (titulo, valor) in enumerate(metricas, start=3):
            ws.cell(row=row, column=1, value=titulo).font = Font(name="Calibri", bold=True)
            ws.cell(row=row, column=2, value=valor)
            ws.cell(row=row, column=2).alignment = Alignment(horizontal="left")

        for col, largura in zip("ABCD", (30, 22, 22, 22)):
            ws.column_dimensions[col].width = largura

    def _aplicar_cabecalho(self, ws, cabecalhos, cor):
        preenchimento = PatternFill(start_color=cor, end_color=cor, fill_type="solid")
        fonte = Font(name="Calibri", color="FFFFFF", bold=True)
        for coluna, titulo in enumerate(cabecalhos, start=1):
            celula = ws.cell(row=1, column=coluna, value=titulo)
            celula.fill = preenchimento
            celula.font = fonte
            celula.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 22
        ws.freeze_panes = "A2"

    def _montar_aba_dados(self, ws, leituras):
        cabecalhos = ("Timestamp", "Temperatura (°C)", "Vibração", "RPM")
        self._aplicar_cabecalho(ws, cabecalhos, self.verde_fieldnode)

        if not leituras.exists():
            ws.cell(row=2, column=1, value="Nenhuma leitura registrada para esta máquina.")
        else:
            for linha, leitura in enumerate(leituras.iterator(), start=2):
                timestamp = self._normalizar_timestamp_excel(leitura.timestamp)
                celula_timestamp = ws.cell(row=linha, column=1, value=timestamp)
                if timestamp:
                    celula_timestamp.number_format = "DD/MM/YYYY HH:MM:SS"
                ws.cell(row=linha, column=2, value=leitura.temperatura)
                ws.cell(row=linha, column=3, value=leitura.vibracao)
                ws.cell(row=linha, column=4, value=leitura.rpm)

            # Destaca temperaturas críticas no Excel e em leitores compatíveis.
            ws.conditional_formatting.add(
                f"B2:B{ws.max_row}",
                CellIsRule(
                    operator="greaterThan",
                    formula=["85"],
                    fill=PatternFill(start_color="FDE8E8", end_color="FDE8E8", fill_type="solid"),
                    font=Font(color="9B1C1C", bold=True),
                ),
            )
            ws.auto_filter.ref = f"A1:D{ws.max_row}"

        self._definir_larguras(ws, (22, 18, 14, 12))

    def _montar_aba_eventos(self, ws, analises):
        cabecalhos = (
            "Data/Hora",
            "Status do Risco",
            "Motivos da Anomalia",
            "Recomendação Operacional",
        )
        self._aplicar_cabecalho(ws, cabecalhos, self.cinza_fieldnode)

        if not analises.exists():
            ws.cell(row=2, column=1, value="Nenhum evento anômalo registrado no período.")
        else:
            for linha, analise in enumerate(analises.iterator(), start=2):
                timestamp = self._normalizar_timestamp_excel(analise.criado_em)
                celula_timestamp = ws.cell(row=linha, column=1, value=timestamp)
                if timestamp:
                    celula_timestamp.number_format = "DD/MM/YYYY HH:MM:SS"
                ws.cell(row=linha, column=2, value=analise.status)
                motivos = analise.motivos if isinstance(analise.motivos, list) else []
                ws.cell(row=linha, column=3, value="; ".join(map(str, motivos)))
                ws.cell(row=linha, column=4, value=analise.recomendacao or "")
                for coluna in (3, 4):
                    ws.cell(row=linha, column=coluna).alignment = Alignment(wrap_text=True, vertical="top")
            ws.auto_filter.ref = f"A1:D{ws.max_row}"

        self._definir_larguras(ws, (22, 16, 45, 45))

    @staticmethod
    def _definir_larguras(ws, larguras):
        for coluna, largura in enumerate(larguras, start=1):
            ws.column_dimensions[get_column_letter(coluna)].width = largura

    @staticmethod
    def _normalizar_timestamp_excel(timestamp):
        """Converte datetimes do Django para o tipo aceito no formato XLSX."""
        if timestamp and timezone.is_aware(timestamp):
            return timezone.make_naive(timestamp, timezone.get_current_timezone())
        return timestamp
