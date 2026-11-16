from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api_tcc", "0051_leituratelemetria_vibration_features"),
    ]

    operations = [
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
                    ("FALHA_DTC", "Falha DTC"),
                ],
                db_index=True,
                max_length=40,
            ),
        ),
    ]
