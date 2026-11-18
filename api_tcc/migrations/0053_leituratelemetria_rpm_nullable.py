from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0052_event_falha_dtc")]

    operations = [
        migrations.AlterField(
            model_name="leituratelemetria",
            name="rpm",
            field=models.IntegerField(
                blank=True,
                help_text="RPM medido; nulo quando o sensor não estiver disponível. Nulo não significa RPM zero.",
                null=True,
                verbose_name="RPM",
            ),
        ),
    ]
