from django.core.management import call_command
from django.db import migrations


def create_throttle_cache_table(apps, schema_editor):
    call_command(
        "createcachetable",
        "fieldnode_throttle_cache",
        database=schema_editor.connection.alias,
        verbosity=0,
    )


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0034_trust_factors_temporal")]

    operations = [migrations.RunPython(create_throttle_cache_table, migrations.RunPython.noop)]
