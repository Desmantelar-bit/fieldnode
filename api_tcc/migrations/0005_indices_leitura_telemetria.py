from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_tcc', '0004_protect_colheitadeira_fks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leituratelemetria',
            name='maquina_id',
            field=models.CharField(
                max_length=50,
                verbose_name='ID da Máquina',
                db_index=True,
            ),
        ),
        migrations.AlterField(
            model_name='leituratelemetria',
            name='timestamp',
            field=models.DateTimeField(
                verbose_name='Timestamp do Sensor',
                db_index=True,
            ),
        ),
    ]
