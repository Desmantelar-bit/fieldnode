from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api_tcc", "0019_decision"),
    ]

    operations = [
        migrations.AddField(
            model_name="decision",
            name="detalhes",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="machinedatahealth",
            name="anomalias_detectadas",
            field=models.PositiveIntegerField(default=0, verbose_name="Anomalias detectadas"),
        ),
        migrations.AlterField(
            model_name="event",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("TEMP_ALTA", "Temperatura alta"),
                    ("VIBRACAO_ALTA", "Vibracao alta"),
                    ("ANOMALIA_ML", "Anomalia ML"),
                    ("ANOMALIA_ESTATISTICA", "Anomalia estatistica"),
                    ("TENDENCIA_RISCO", "Tendencia de risco"),
                ],
                db_index=True,
                max_length=40,
            ),
        ),
    ]
