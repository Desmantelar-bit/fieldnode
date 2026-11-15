from django.db import migrations


def forwards(apps, schema_editor):
    Prescricao = apps.get_model("api_tcc", "Prescricao")
    Decision = apps.get_model("api_tcc", "Decision")
    Machine = apps.get_model("api_tcc", "Machine")

    status_map = {
        "pendente": "PENDENTE",
        "concluida": "EXECUTADA",
        "cancelada": "REJEITADA",
    }
    for legacy in Prescricao.objects.select_related("colheitadeira").iterator():
        code = str(legacy.colheitadeira.maquina_id).strip().upper()
        machine, _ = Machine.objects.get_or_create(
            external_code=code,
            defaults={"colheitadeira_id": legacy.colheitadeira_id},
        )
        if machine.colheitadeira_id is None:
            machine.colheitadeira_id = legacy.colheitadeira_id
            machine.save(update_fields=["colheitadeira"])

        Decision.objects.get_or_create(
            machine_id=machine.id,
            event_id=None,
            texto=legacy.descricao,
            defaults={
                "acao_recomendada": legacy.titulo,
                "severidade": "ATENCAO",
                "status": status_map.get(legacy.status, "PENDENTE"),
                "detalhes": {
                    "migrated_from": "Prescricao",
                    "legacy_id": legacy.id,
                    "legacy_status": legacy.status,
                    "legacy_title": legacy.titulo,
                    "legacy_generated_at": legacy.data_geracao.isoformat(),
                },
            },
        )


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0040_leituratelemetria_api_tcc_lei_machine_96ac6f_idx")]
    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.DeleteModel(name="Prescricao"),
    ]
