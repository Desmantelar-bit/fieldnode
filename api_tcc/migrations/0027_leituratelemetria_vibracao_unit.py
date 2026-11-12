from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api_tcc", "0026_rename_tempumi_ambiente"),
    ]

    operations = [
        migrations.AddField(
            model_name="leituratelemetria",
            name="vibracao_unit",
            field=models.CharField(
                default="indice_0_10",
                help_text="Contrato v1: índice adimensional de 0 a 10.",
                max_length=30,
                verbose_name="Unidade da vibração",
            ),
        ),
    ]
