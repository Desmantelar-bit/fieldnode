from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0058_canonical_provenance")]
    operations = [
        migrations.AlterField(
            model_name="rawtelemetry",
            name="origem",
            field=models.CharField(
                choices=[("medido", "medido"), ("calculado", "calculado"),
                         ("estimado", "estimado"), ("simulado", "simulado")],
                default="simulado", max_length=12,
            ),
        ),
    ]
