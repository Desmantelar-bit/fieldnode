import csv
import io

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.models import Front, Machine, MachineLink
from api_tcc.permissions import IsAuthenticatedOrPublicDemo, get_machines_for_request, user_can_access_machine
from api_tcc.services.operation_graph import criar_machine_link


def _machine_payload(machine):
    return {"id": str(machine.pk), "external_code": machine.external_code, "tipo": machine.tipo}


def _parse_date(value):
    parsed = parse_datetime((value or "").strip())
    if parsed is not None and timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)
    return parsed


def _front_for(value, organization):
    if not (value or "").strip():
        return None
    token = value.strip()
    return Front.objects.filter(organization=organization, ativo=True).filter(
        pk=token
    ).first() or Front.objects.filter(organization=organization, ativo=True, codigo=token).first()


class OperationGraphView(APIView):
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def get(self, request):
        machines = get_machines_for_request(request).select_related("organization", "site")
        organizations = machines.values_list("organization_id", flat=True).distinct()
        fronts = Front.objects.filter(organization_id__in=organizations, ativo=True)
        links = MachineLink.objects.filter(
            organization_id__in=organizations,
            origem__in=machines,
        ).select_related("origem", "destino", "front")
        return Response({
            "machines": [_machine_payload(machine) for machine in machines],
            "fronts": [{"id": str(front.pk), "nome": front.nome, "codigo": front.codigo} for front in fronts],
            "links": [{
                "id": str(link.pk),
                "origem": link.origem.external_code,
                "destino": link.destino.external_code,
                "tipo": link.tipo,
                "front": str(link.front_id) if link.front_id else None,
                "de": link.valido_de.isoformat(),
                "ate": link.valido_ate.isoformat() if link.valido_ate else None,
            } for link in links],
        })

    def post(self, request):
        payload = request.data
        origem = get_machines_for_request(request).filter(external_code=str(payload.get("origem", "")).strip().upper()).first()
        destino = get_machines_for_request(request).filter(external_code=str(payload.get("destino", "")).strip().upper()).first()
        if not origem or not destino or not user_can_access_machine(request.user, origem, write=True) or not user_can_access_machine(request.user, destino, write=True):
            return Response({"detail": "origem ou destino não disponível para este usuário"}, status=status.HTTP_403_FORBIDDEN)
        front = _front_for(str(payload.get("front", "")), origem.organization)
        start = _parse_date(str(payload.get("de", "")))
        end = _parse_date(str(payload.get("ate", ""))) if payload.get("ate") else None
        if start is None:
            return Response({"detail": "de deve ser uma data ISO-8601 válida"}, status=status.HTTP_400_BAD_REQUEST)
        if payload.get("front") and front is None:
            return Response({"detail": "front não pertence à organização ou não existe"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            link = criar_machine_link(origem=origem, destino=destino, tipo=payload.get("tipo"), valido_de=start, valido_ate=end, front=front, organization=origem.organization)
        except (ValidationError, ValueError) as exc:
            return Response({"detail": exc.message_dict if hasattr(exc, "message_dict") else str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"id": str(link.pk)}, status=status.HTTP_201_CREATED)


class OperationGraphImportView(APIView):
    permission_classes = [IsAuthenticatedOrPublicDemo]

    def post(self, request):
        upload = request.FILES.get("file")
        if upload is None:
            return Response({"detail": "envie o CSV no campo file"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            content = upload.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            return Response({"detail": "CSV deve estar em UTF-8"}, status=status.HTTP_400_BAD_REQUEST)
        rows = list(csv.DictReader(io.StringIO(content)))
        required = {"origem", "destino", "tipo", "front", "de", "ate"}
        if not rows or set(rows[0].keys() or ()) != required:
            return Response({"detail": "cabeçalho deve ser origem,destino,tipo,front,de,ate"}, status=status.HTTP_400_BAD_REQUEST)
        machines = {m.external_code: m for m in get_machines_for_request(request).select_related("organization")}
        errors = []
        prepared = []
        for line, row in enumerate(rows, start=2):
            origem = machines.get((row.get("origem") or "").strip().upper())
            destino = machines.get((row.get("destino") or "").strip().upper())
            start = _parse_date(row.get("de"))
            end = _parse_date(row.get("ate")) if (row.get("ate") or "").strip() else None
            front = _front_for(row.get("front"), origem.organization) if origem else None
            if not origem or not destino or not start or ((row.get("front") or "").strip() and front is None):
                errors.append({"linha": line, "erro": "máquina ou data inválida"})
                continue
            if not user_can_access_machine(request.user, origem, write=True) or not user_can_access_machine(request.user, destino, write=True):
                errors.append({"linha": line, "erro": "máquina sem permissão de escrita"})
                continue
            prepared.append((line, origem, destino, row.get("tipo"), start, end, front))
        if errors:
            return Response({"gravado": 0, "rejeitadas": errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                for line, origem, destino, tipo, start, end, front in prepared:
                    criar_machine_link(origem=origem, destino=destino, tipo=tipo, valido_de=start, valido_ate=end, front=front, organization=origem.organization)
        except (ValidationError, ValueError) as exc:
            return Response({"gravado": 0, "rejeitadas": [{"linha": line, "erro": str(exc)}]}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"gravado": len(prepared), "rejeitadas": []}, status=status.HTTP_201_CREATED)
