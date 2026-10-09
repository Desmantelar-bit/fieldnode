from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api_tcc", "0022_alter_deadletterentry_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="priority_score",
            field=models.DecimalField(
                blank=True,
                decimal_places=4,
                help_text=(
                    "Prioridade heurística 0..1 calculada no momento da ocorrência; "
                    "NULL indica evento histórico sem dados suficientes para reconstrução."
                ),
                max_digits=5,
                null=True,
            ),
        ),
    ]
