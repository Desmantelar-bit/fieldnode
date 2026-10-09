from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0024_fabricantemapping_rawtelemetry_canonicaltelemetry_and_more")]

    operations = [
        migrations.AlterField(
            model_name="deadletterentry",
            name="contexto",
            field=models.CharField(
                choices=[
                    ("VALIDACAO", "Validação"),
                    ("EVENTO", "Evento"),
                    ("DECISAO", "Decisão"),
                    ("AGENTIC_LLM", "Agentic LLM"),
                    ("SYNC", "Sincronização"),
                ],
                db_index=True,
                max_length=20,
            ),
        ),
    ]
