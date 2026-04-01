from django.db import migrations


def create_default_gates(apps, schema_editor):
    Gate = apps.get_model("visitors", "Gate")
    for name in ("Gate A", "Gate B", "Gate C", "Main Entrance"):
        Gate.objects.get_or_create(name=name, defaults={"is_active": True})


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("visitors", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_gates, noop_reverse),
    ]
