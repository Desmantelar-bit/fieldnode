import hashlib
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.authentication import ExpiringTokenAuthentication, OrganizationTokenAuthentication
from api_tcc.models import Machine, Membership, Organization, OrganizationToken
from api_tcc.permissions import get_machine_for_request
from api_tcc.services.passport import export_passport, issue_raw_token


class PassportExportView(APIView):
    authentication_classes = [OrganizationTokenAuthentication, ExpiringTokenAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        integration = getattr(request, "organization_token", None)
        if integration:
            if "passport:export" not in integration.scopes:
                return Response({"detail": "escopo passport:export ausente"}, status=status.HTTP_403_FORBIDDEN)
            organization = integration.organization
        else:
            organization_id = request.query_params.get("organization_id")
            membership = Membership.objects.filter(user=request.user, organization_id=organization_id, role__in=("admin", "member")).select_related("organization").first()
            if not membership:
                return Response({"detail": "organização não autorizada"}, status=status.HTTP_403_FORBIDDEN)
            organization = membership.organization
        machine = None
        if request.query_params.get("machine"):
            if integration:
                ident = request.query_params["machine"].strip()
                machine = Machine.objects.filter(organization=organization).filter(external_code=ident.upper()).first() or Machine.objects.filter(organization=organization, pk=ident).first()
            else:
                machine = get_machine_for_request(request, request.query_params["machine"])
            if not machine or machine.organization_id != organization.id:
                return Response({"detail": "máquina não autorizada"}, status=status.HTTP_404_NOT_FOUND)
        try:
            blob = export_passport(organization=organization, machine=machine, start=request.query_params.get("start") or None, end=request.query_params.get("end") or None)
        except (ValueError, TypeError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        from django.http import HttpResponse
        response = HttpResponse(blob, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="fieldnode-passport-{organization.id}.zip"'
        return response


class OrganizationTokenView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        organization_id = request.data.get("organization_id")
        membership = Membership.objects.filter(user=request.user, organization_id=organization_id, role="admin").select_related("organization").first()
        if not membership:
            return Response({"detail": "somente administrador da organização pode emitir token"}, status=status.HTTP_403_FORBIDDEN)
        requested = request.data.get("scopes", ["passport:export"])
        allowed = {"passport:export"}
        scopes = sorted(set(requested) & allowed)
        if set(requested) - allowed or not scopes:
            return Response({"detail": "escopo não permitido"}, status=status.HTTP_400_BAD_REQUEST)
        raw = issue_raw_token()
        token = OrganizationToken.objects.create(organization=membership.organization, name=str(request.data.get("name", "integração"))[:120], token_prefix=raw[:12], token_hash=hashlib.sha256(raw.encode()).hexdigest(), scopes=scopes, created_by=request.user, expires_at=timezone.now() + timedelta(days=min(int(request.data.get("expires_days", 30)), 365)))
        return Response({"id": str(token.id), "token": raw, "organization_id": str(token.organization_id), "scopes": scopes, "expires_at": token.expires_at}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        token_id = request.data.get("id")
        token = OrganizationToken.objects.filter(pk=token_id, created_by=request.user, revoked_at__isnull=True).first()
        if not token:
            return Response({"detail": "token não encontrado"}, status=status.HTTP_404_NOT_FOUND)
        token.revoked_at = timezone.now(); token.save(update_fields=["revoked_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
