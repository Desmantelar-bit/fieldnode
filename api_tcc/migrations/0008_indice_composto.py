from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_tcc', '0007_telemetria_invalida'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='leituratelemetria',
            index=models.Index(fields=['maquina_id', '-timestamp'], name='leitura_maquina_timestamp_idx'),
        ),
    ]