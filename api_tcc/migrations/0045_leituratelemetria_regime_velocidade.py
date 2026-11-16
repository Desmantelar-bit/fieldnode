from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0044_decision_motivo_rejeicao_thresholdoverride")]

    operations = [
        migrations.AddField(
            model_name="leituratelemetria",
            name="velocidade_kmh",
            field=models.FloatField(
                blank=True,
                help_text="Velocidade GPS quando disponível; ausência não significa velocidade zero.",
                null=True,
                verbose_name="Velocidade (km/h)",
            ),
        ),
        migrations.AddField(
            model_name="leituratelemetria",
            name="evidence_quality",
            field=models.CharField(
                choices=[("boa", "Boa"), ("suspeita", "Suspeita"), ("insuficiente", "Insuficiente")],
                default="insuficiente",
                help_text="Qualidade da observação para fins de treinamento; não é confiança do modelo.",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="leituratelemetria",
            name="regime",
            field=models.CharField(
                choices=[
                    ("desligada", "Desligada"),
                    ("marcha_lenta", "Marcha lenta"),
                    ("trabalhando", "Trabalhando"),
                    ("deslocamento", "Deslocamento"),
                    ("desconhecido", "Desconhecido"),
                ],
                db_index=True,
                default="desconhecido",
                max_length=20,
            ),
        ),
    ]
