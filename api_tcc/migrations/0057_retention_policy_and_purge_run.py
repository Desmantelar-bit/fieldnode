from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0056_workerheartbeat")]

    operations = [
        migrations.AddField(
            model_name="organizationpolicy",
            name="retention_policy",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Prazos aprovados por categoria, em dias; vazio nao autoriza exclusao automatica.",
            ),
        ),
        migrations.AddField(
            model_name="organizationpolicy",
            name="retention_policy_effective_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="organizationpolicy",
            name="retention_policy_version",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.CreateModel(
            name="RetentionPurgeRun",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("started_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("executor", models.CharField(max_length=120)),
                ("organization_id_text", models.CharField(blank=True, max_length=36)),
                ("categories", models.JSONField(default=list)),
                ("policy_version", models.CharField(blank=True, max_length=40)),
                ("reference_at", models.DateTimeField()),
                ("evaluated", models.PositiveIntegerField(default=0)),
                ("deleted", models.PositiveIntegerField(default=0)),
                ("preserved", models.PositiveIntegerField(default=0)),
                ("preservation_reasons", models.JSONField(blank=True, default=dict)),
                ("export_manifest", models.JSONField(blank=True, default=dict)),
                ("result", models.CharField(default="running", max_length=20)),
                ("errors", models.JSONField(blank=True, default=list)),
            ],
            options={"ordering": ["-started_at"], "indexes": [models.Index(fields=["organization_id_text", "-started_at"], name="api_tcc_ret_organiz_35aec2_idx")]},
        ),
    ]
