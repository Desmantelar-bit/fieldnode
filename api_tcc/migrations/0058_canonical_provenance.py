from django.db import migrations, models


def backfill_provenance(apps, schema_editor):
    RawTelemetry = apps.get_model("api_tcc", "RawTelemetry")
    CanonicalTelemetry = apps.get_model("api_tcc", "CanonicalTelemetry")
    CanonicalTelemetry.objects.all().update(origem="simulado", fonte="")
    for raw in RawTelemetry.objects.all().iterator():
        if not raw.origem:
            raw.origem = "simulado"
            raw.save(update_fields=["origem"])
    for canonical in CanonicalTelemetry.objects.select_related("raw_telemetry").iterator():
        canonical.fonte = canonical.raw_telemetry.source_protocol_simulado or ""
        canonical.unidade_original = canonical.raw_telemetry.unit or ""
        canonical.save(update_fields=["fonte", "unidade_original"])


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0057_retention_policy_and_purge_run")]
    operations = [
        migrations.AddField(
            model_name="fabricantemapping", name="unit_conversion_offset",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="rawtelemetry", name="origem",
            field=models.CharField(
                choices=[("medido", "medido"), ("calculado", "calculado"),
                         ("estimado", "estimado"), ("simulado", "simulado")],
                max_length=12, default="simulado"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="canonicaltelemetry", name="origem",
            field=models.CharField(
                choices=[("medido", "medido"), ("calculado", "calculado"),
                         ("estimado", "estimado"), ("simulado", "simulado")],
                max_length=12, default="simulado"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="canonicaltelemetry", name="fonte",
            field=models.CharField(max_length=200, default=""), preserve_default=False,
        ),
        migrations.AddField(
            model_name="canonicaltelemetry", name="unidade_original",
            field=models.CharField(blank=True, default="", max_length=30),
        ),
        migrations.AddField(
            model_name="canonicaltelemetry", name="fator_conversao",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="canonicaltelemetry", name="offset_conversao",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.RunPython(backfill_provenance, migrations.RunPython.noop),
    ]
