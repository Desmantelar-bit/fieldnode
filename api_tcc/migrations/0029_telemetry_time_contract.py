from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api_tcc", "0028_event_evidence_quality"),
    ]

    operations = [
        migrations.AddField(
            model_name="leituratelemetria",
            name="boot_id",
            field=models.UUIDField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="leituratelemetria",
            name="uptime_ms",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="leituratelemetria",
            name="time_source",
            field=models.CharField(
                choices=[
                    ("rtc", "RTC"),
                    ("gateway", "Gateway"),
                    ("ntp", "NTP"),
                    ("unsynced", "Sem sincronização"),
                ],
                default="unsynced",
                max_length=12,
            ),
        ),
        migrations.AddField(
            model_name="leituratelemetria",
            name="clock_skew_ms",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="DeviceClockAnchor",
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
                ("device_id", models.CharField(max_length=100)),
                ("boot_id", models.UUIDField()),
                ("anchor_uptime_ms", models.BigIntegerField()),
                ("anchor_timestamp", models.DateTimeField()),
                ("time_source", models.CharField(max_length=12)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("device_id", "boot_id"),
                        name="uniq_clock_anchor_device_boot",
                    ),
                ],
            },
        ),
    ]
