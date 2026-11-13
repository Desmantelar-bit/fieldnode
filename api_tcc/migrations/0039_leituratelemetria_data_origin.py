from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0038_s2_t7_t8_audit_device_http")]

    operations = [
        migrations.AddField(
            model_name="leituratelemetria",
            name="data_origin",
            field=models.CharField(
                blank=True,
                choices=[
                    ("medido", "medido"),
                    ("simulado", "simulado"),
                    ("calculado", "calculado"),
                    ("estimado", "estimado"),
                ],
                help_text="Proveniência conhecida pela API; nulo indica histórico ou origem ainda não comprovada.",
                max_length=12,
                null=True,
            ),
        ),
    ]
