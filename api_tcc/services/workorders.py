from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from api_tcc.models import Decision, MaintenanceContact, OrganizationPolicy, User, WorkOrder
from api_tcc.permissions import user_can_access_machine
from api_tcc.services.audit import record as audit_record


def approve(decision, user, *, responsavel_tipo=None, responsavel_id=None, prazo=None, request=None):
    """Aprova uma Decision e cria sua OS na mesma transacao."""
    if not user_can_access_machine(user, decision.machine, write=True):
        raise PermissionError("usuario sem permissao para a machine")
    if responsavel_tipo not in {"user", "contact"} or not responsavel_id:
        raise ValueError("responsavel_tipo e responsavel_id sao obrigatorios")

    with transaction.atomic():
        locked = Decision.objects.select_for_update().select_related("machine").get(pk=decision.pk)
        if locked.status != Decision.Status.PENDENTE:
            raise ValueError("somente Decision pendente pode gerar WorkOrder")
        responsible = {"responsavel_usuario": None, "responsavel_contato": None}
        if responsavel_tipo == "user":
            responsible["responsavel_usuario"] = User.objects.filter(pk=responsavel_id).first()
            if responsible["responsavel_usuario"] is None or not user_can_access_machine(responsible["responsavel_usuario"], locked.machine):
                raise ValueError("usuario responsavel fora da organizacao")
        else:
            responsible["responsavel_contato"] = MaintenanceContact.objects.filter(pk=responsavel_id, organization_id=locked.machine.organization_id, ativo=True).first()
            if responsible["responsavel_contato"] is None:
                raise ValueError("contato responsavel fora da organizacao")
        if prazo is None:
            policy = OrganizationPolicy.objects.filter(organization_id=locked.machine.organization_id).first()
            minutes = (policy.prazo_por_severidade or {}).get(locked.severidade) if policy else None
            if minutes is None:
                raise ValueError("prazo manual obrigatorio: nenhuma politica configurada")
            prazo = timezone.now() + timedelta(minutes=int(minutes))
        if prazo <= timezone.now():
            raise ValueError("prazo deve estar no futuro")
        before = {"status": locked.status}
        order = WorkOrder.objects.create(
            decision=locked,
            machine=locked.machine,
            titulo=locked.acao_recomendada[:255],
            descricao=locked.texto,
            prioridade=locked.severidade,
            prazo=prazo,
            criado_por=user,
            historico=[{"status": WorkOrder.Status.ABERTA, "at": timezone.now().isoformat(), "by": user.pk}],
            **responsible,
        )
        locked.status = Decision.Status.APROVADA
        locked.decidido_por = user
        locked.decidido_em = timezone.now()
        locked.save(update_fields=["status", "decidido_por", "decidido_em"])
        audit_record("decision.approve", locked, request, before=before, after={"status": locked.status}, metadata={"work_order_id": str(order.id)})
        return order
