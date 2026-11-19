from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api_tcc", "0055_organizationpolicy_custo_hora_parada_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkerHeartbeat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("worker_name", models.CharField(max_length=80, unique=True)),
                ("instance_id", models.CharField(max_length=80)),
                ("last_heartbeat_at", models.DateTimeField(db_index=True)),
                ("status", models.CharField(default="running", max_length=20)),
            ],
            options={
                "verbose_name": "Heartbeat do worker",
                "verbose_name_plural": "Heartbeats dos workers",
            },
        ),
    ]
