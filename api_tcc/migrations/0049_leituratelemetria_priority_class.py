from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0048_telemetryaggregate")]

    operations = [
        migrations.AddField(
            model_name="leituratelemetria",
            name="priority_class",
            field=models.CharField(
                choices=[("A", "A"), ("B", "B"), ("C", "C")],
                db_index=True,
                default="C",
                help_text="Classe de transmissão atribuída pelo contrato Sync v1.",
                max_length=1,
                verbose_name="Classe de prioridade",
            ),
        ),
    ]
