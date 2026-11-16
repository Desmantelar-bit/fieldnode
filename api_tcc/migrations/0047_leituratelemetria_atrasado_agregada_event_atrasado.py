from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0046_machinespec_labeledwindow_maintenancerecord")]

    operations = [
        migrations.AddField(
            model_name="leituratelemetria",
            name="atrasado",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="Indica recebimento posterior ao evento; nao e anomalia mecanica.",
            ),
        ),
        migrations.AddField(
            model_name="leituratelemetria",
            name="agregada",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="Marca uma representacao agregada, nunca uma leitura original.",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="atrasado",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="Evento descoberto por leitura recebida fora da janela esperada.",
            ),
        ),
    ]
