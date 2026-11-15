from datetime import timedelta

from django.http import HttpResponse
from django.core.paginator import InvalidPage, Paginator
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.models import AuditLog, Decision, ThresholdOverride, WorkOrder
from api_tcc.permissions import IsAuthenticatedOrPublicDemo, request_can_access_machine, user_can_access_machine
from api_tcc.services.audit import record as audit_record
from api_tcc.services.exporters import export_payload, ready_message, send_webhook, to_ics, whatsapp_url
from api_tcc.services.thresholds import create_threshold_override


def _order_payload(order, *, conflict=False):
    responsible = order.responsavel_usuario or order.responsavel_contato
    return {
        "id": str(order.id),
        "decision_id": str(order.decision_id),
        "titulo": order.titulo,
        "descricao": order.descricao,
        "machine": str(order.machine_id),
        "machine_external_code": order.machine.external_code,
        "responsavel": None if responsible is None else {
            "id": str(responsible.pk),
            "nome": getattr(responsible, "get_username", lambda: getattr(responsible, "nome", ""))() if order.responsavel_usuario_id else responsible.nome,
            "funcao": getattr(responsible, "funcao", "Operacao") if order.responsavel_contato_id else "Usuario",
            "tipo": "user" if order.responsavel_usuario_id else "contact",
        },
        "prazo": order.prazo,
        "status": order.status,
        "prioridade": order.prioridade,
        "criado_em": order.criado_em,
        "concluida_em": order.concluida_em,
        "conflito_responsavel": conflict,
    }


def _parse_period(value, *, end=False):
    if not value:
        return None
    try:
        parsed = timezone.datetime.fromisoformat(value)
    except ValueError:
        raise ValueError("periodo deve ser uma data ISO-8601") from None
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    if end and len(value) == 10:
        parsed = parsed + timedelta(days=1)
    return parsed


def _conflict_for(order, prazo):
    if order.responsavel_usuario_id:
        qs = WorkOrder.objects.filter(responsavel_usuario_id=order.responsavel_usuario_id)
    elif order.responsavel_contato_id:
        qs = WorkOrder.objects.filter(responsavel_contato_id=order.responsavel_contato_id)
    else:
        return False
    return qs.exclude(pk=order.pk).filter(prazo__date=prazo.date()).exclude(status__in=[WorkOrder.Status.CONCLUIDA, WorkOrder.Status.CANCELADA]).exists()


class WorkOrderListView(APIView):
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request):
        qs = WorkOrder.objects.select_related("machine", "decision", "responsavel_usuario", "responsavel_contato")
        # Use the same machine authorization source as every other operational endpoint.
        from api_tcc.permissions import get_machines_for_request
        qs = WorkOrder.objects.filter(machine__in=get_machines_for_request(request)).select_related("machine", "decision", "responsavel_usuario", "responsavel_contato")
        try:
            start = _parse_period(request.query_params.get("de"))
            end = _parse_period(request.query_params.get("ate"), end=True)
            if start and end and start > end:
                raise ValueError("de nao pode ser posterior a ate")
        except ValueError as exc:
            return Response({"status": "erro", "detalhe": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        if start:
            qs = qs.filter(prazo__gte=start)
        if end:
            qs = qs.filter(prazo__lt=end)
        for field in ("status", "prioridade"):
            if request.query_params.get(field):
                qs = qs.filter(**{field: request.query_params[field]})
        if request.query_params.get("maquina_id"):
            qs = qs.filter(machine_id=request.query_params["maquina_id"])
        if request.query_params.get("responsavel_id"):
            ident = request.query_params["responsavel_id"]
            qs = qs.filter(responsavel_usuario_id=ident) | qs.filter(responsavel_contato_id=ident)
        try:
            page_size = min(max(int(request.query_params.get("page_size", 100)), 1), 200)
            page_number = max(int(request.query_params.get("page", 1)), 1)
        except ValueError:
            return Response({"status": "erro", "detalhe": "paginacao invalida"}, status=status.HTTP_400_BAD_REQUEST)
        paginator = Paginator(qs.order_by("prazo", "-criado_em"), page_size)
        try:
            page = paginator.page(page_number)
        except InvalidPage:
            return Response({"status": "erro", "detalhe": "pagina inexistente"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"count": paginator.count, "next": page.has_next(), "previous": page.has_previous(), "results": [_order_payload(item) for item in page.object_list]})


class WorkOrderDetailView(APIView):
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def _get(self, request, work_order_id):
        order = WorkOrder.objects.select_for_update().select_related("machine", "decision", "responsavel_usuario", "responsavel_contato").filter(pk=work_order_id).first()
        if order is None or not request_can_access_machine(request, order.machine):
            return None
        return order

    def patch(self, request, work_order_id):
        with transaction.atomic():
            order = self._get(request, work_order_id)
            if order is None:
                return Response({"status": "erro", "detalhe": "OS nao encontrada"}, status=status.HTTP_404_NOT_FOUND)
            if not user_can_access_machine(request.user, order.machine, write=True):
                return Response({"status": "erro", "detalhe": "sem permissao"}, status=status.HTTP_403_FORBIDDEN)
            allowed = set(request.data) - {"prazo", "status"}
            if allowed:
                return Response({"status": "erro", "detalhe": "campo nao permitido"}, status=status.HTTP_400_BAD_REQUEST)
            before = {"prazo": order.prazo.isoformat(), "status": order.status}
            if "prazo" in request.data:
                field = serializers.DateTimeField()
                try:
                    prazo = field.run_validation(request.data["prazo"])
                except serializers.ValidationError as exc:
                    return Response({"prazo": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
                if prazo <= timezone.now():
                    return Response({"status": "erro", "detalhe": "prazo deve estar no futuro"}, status=status.HTTP_400_BAD_REQUEST)
                order.prazo = prazo
            if request.data.get("status"):
                if request.data["status"] != WorkOrder.Status.CONCLUIDA or order.status in {WorkOrder.Status.CONCLUIDA, WorkOrder.Status.CANCELADA}:
                    return Response({"status": "erro", "detalhe": "transicao de OS invalida"}, status=status.HTTP_400_BAD_REQUEST)
                order.status = WorkOrder.Status.CONCLUIDA
                order.concluida_em = timezone.now()
                if order.decision.status == Decision.Status.APROVADA:
                    order.decision.status = Decision.Status.EXECUTADA
                    order.decision.decidido_por = request.user
                    order.decision.decidido_em = timezone.now()
                    order.decision.save(update_fields=["status", "decidido_por", "decidido_em"])
            after = {"prazo": order.prazo.isoformat(), "status": order.status}
            order.historico = [*order.historico, {"tipo": "reagendamento" if "prazo" in request.data else "status", "antes": before, "depois": after, "at": timezone.now().isoformat(), "by": request.user.pk}]
            order.save(update_fields=["prazo", "status", "concluida_em", "historico"])
            audit_record("workorder.reschedule" if "prazo" in request.data else "workorder.complete", order, request, before=before, after=after, metadata={"conflito_responsavel": _conflict_for(order, order.prazo)})
            return Response(_order_payload(order, conflict=_conflict_for(order, order.prazo)))


class ThresholdOverrideView(APIView):
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def post(self, request, decision_id):
        try:
            from api_tcc.models import Decision
            decision = Decision.objects.select_related("machine").get(pk=decision_id)
        except Decision.DoesNotExist:
            return Response({"status": "erro", "detalhe": "Decision nao encontrada"}, status=status.HTTP_404_NOT_FOUND)
        if not request_can_access_machine(request, decision.machine):
            return Response({"status": "erro", "detalhe": "Decision nao encontrada"}, status=status.HTTP_404_NOT_FOUND)
        if not user_can_access_machine(request.user, decision.machine, write=True):
            return Response({"status": "erro", "detalhe": "sem permissao"}, status=status.HTTP_403_FORBIDDEN)
        if decision.status != Decision.Status.REJEITADA or decision.motivo_rejeicao != "FALSO_ALARME":
            return Response({"status": "erro", "detalhe": "override exige rejeicao por FALSO_ALARME"}, status=status.HTTP_400_BAD_REQUEST)
        fields = {"metric", "atencao", "critico", "motivo", "expira_em"}
        if set(request.data) != fields:
            return Response({"status": "erro", "detalhe": "metric, atencao, critico, motivo e expira_em sao obrigatorios"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            expira_em = serializers.DateTimeField().run_validation(request.data["expira_em"])
            override = create_threshold_override(machine=decision.machine, metric=request.data["metric"], atencao=request.data["atencao"], critico=request.data["critico"], motivo=request.data["motivo"], criado_por=request.user, expira_em=expira_em)
            audit_record("threshold.override.create", override, request, after={"machine_id": str(override.machine_id), "metric": override.metric, "atencao": override.atencao, "critico": override.critico, "expira_em": override.expira_em, "motivo": override.motivo})
        except (ValueError, serializers.ValidationError) as exc:
            return Response({"status": "erro", "detalhe": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"id": str(override.id), "machine": str(override.machine_id), "metric": override.metric, "atencao": override.atencao, "critico": override.critico, "motivo": override.motivo, "expira_em": override.expira_em}, status=status.HTTP_201_CREATED)


class WorkOrderExportView(APIView):
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def _get_order(self, request, work_order_id):
        order = WorkOrder.objects.select_related("decision", "machine", "machine__organization", "responsavel_contato", "responsavel_usuario").filter(pk=work_order_id).first()
        if order is None or not request_can_access_machine(request, order.machine):
            return None
        return order

    def get(self, request, work_order_id, export_type):
        order = self._get_order(request, work_order_id)
        if order is None:
            return Response({"status": "erro", "detalhe": "OS não encontrada"}, status=status.HTTP_404_NOT_FOUND)
        if export_type == "ics":
            response = HttpResponse(to_ics(order), content_type="text/calendar; charset=utf-8")
            response["Content-Disposition"] = f'attachment; filename="fieldnode-os-{order.id}.ics"'
            return response
        if export_type == "json":
            return Response({**export_payload(order), "mensagem": ready_message(order), "whatsapp_url": whatsapp_url(order)})
        return Response({"status": "erro", "detalhe": "formato não suportado"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, work_order_id, export_type):
        if export_type != "webhook":
            return Response({"status": "erro", "detalhe": "operação não suportada"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        order = self._get_order(request, work_order_id)
        if order is None:
            return Response({"status": "erro", "detalhe": "OS não encontrada"}, status=status.HTTP_404_NOT_FOUND)
        if not user_can_access_machine(request.user, order.machine, write=True):
            return Response({"status": "erro", "detalhe": "sem permissão para esta máquina"}, status=status.HTTP_403_FORBIDDEN)
        try:
            return Response(send_webhook(order), status=status.HTTP_200_OK)
        except ValueError as exc:
            return Response({"status": "erro", "detalhe": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
