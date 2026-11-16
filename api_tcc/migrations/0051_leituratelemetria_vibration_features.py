from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api_tcc", "0050_leituratelemetria_via_deliveryhop"),
    ]

    operations = [
        migrations.AddField(
            model_name="leituratelemetria",
            name="vibracao_curtose",
            field=models.JSONField(blank=True, null=True, verbose_name="Curtose de vibração por eixo"),
        ),
        migrations.AddField(
            model_name="leituratelemetria",
            name="vibracao_pico_g",
            field=models.JSONField(blank=True, null=True, verbose_name="Pico de vibração por eixo (g)"),
        ),
        migrations.AddField(
            model_name="leituratelemetria",
            name="vibracao_rms_g",
            field=models.JSONField(blank=True, null=True, verbose_name="Vibração RMS por eixo (g)"),
        ),
    ]
