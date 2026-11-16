from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0047_leituratelemetria_atrasado_agregada_event_atrasado")]

    operations = [
        migrations.CreateModel(
            name="TelemetryAggregate",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("device_id", models.CharField(db_index=True, max_length=100)),
                ("boot_id", models.UUIDField(blank=True, db_index=True, null=True)),
                ("window_start", models.DateTimeField(db_index=True)),
                ("window_end", models.DateTimeField(db_index=True)),
                ("priority_class", models.CharField(default="C", max_length=1)),
                ("sample_count", models.PositiveIntegerField()),
                ("valid_count", models.PositiveIntegerField()),
                ("missing_count", models.PositiveIntegerField(default=0)),
                ("statistics", models.JSONField(default=dict)),
                ("source_message_ids", models.JSONField(default=list)),
                ("aggregate_hash", models.CharField(max_length=64, unique=True)),
                ("recebido_em", models.DateTimeField(auto_now_add=True)),
                ("machine", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="telemetry_aggregates", to="api_tcc.machine")),
            ],
            options={"ordering": ["-window_start"]},
        ),
        migrations.AddIndex(
            model_name="telemetryaggregate",
            index=models.Index(fields=["machine", "-window_start"], name="api_tcc_tel_machine_649a30_idx"),
        ),
    ]
