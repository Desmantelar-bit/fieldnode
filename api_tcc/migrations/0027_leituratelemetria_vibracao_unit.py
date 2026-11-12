from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0026_rename_tempumi_ambiente")]
    operations = [
        migrations.AddField(
            model_name="leituratelemetria",
            name="vibracao_unit",
            field=models.CharField(default="indice_0_10", max_length=20, verbose_name="Unidade/escala da vibração"),
        ),
    ]
