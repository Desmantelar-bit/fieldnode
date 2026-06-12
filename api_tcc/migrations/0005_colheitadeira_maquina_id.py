# Generated migration to add maquina_id field to Colheitadeira
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_tcc', '0004_leituratelemetria_latitude_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='colheitadeira',
            name='maquina_id',
            field=models.CharField(
                max_length=50,
                unique=True,
                null=True,
                blank=True,
                verbose_name='ID da Máquina (Telemetria)',
                help_text='ID usado nas leituras de telemetria (ex: COLH-01)'
            ),
        ),
    ]