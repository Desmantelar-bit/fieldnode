from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api_tcc", "0027_leituratelemetria_vibracao_unit"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="evidence_quality",
            field=models.CharField(
                choices=[
                    ("boa", "Boa"),
                    ("suspeita", "Suspeita"),
                    ("insuficiente", "Insuficiente"),
                ],
                default="insuficiente",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="needs_verification",
            field=models.BooleanField(default=True),
        ),
    ]