from django.db import migrations

# Frozen copy on purpose: a migration must not change when the app's constants do.
DEFAULTS = [
    ("Alimentação", "🍔", "orange"),
    ("Transporte", "🚗", "blue"),
    ("Moradia", "🏠", "jade"),
    ("Lazer", "🎮", "purple"),
    ("Saúde", "💊", "pink"),
    ("Outros", "📦", "graphite"),
]
OTHER = "Outros"


def create_defaults(apps, schema_editor):
    Category = apps.get_model("transactions", "Category")
    Transaction = apps.get_model("transactions", "Transaction")
    for name, emoji, color in DEFAULTS:
        Category.objects.get_or_create(
            user=None, name=name, defaults={"emoji": emoji, "color": color}
        )
    other = Category.objects.get(user=None, name=OTHER)
    Transaction.objects.filter(kind="expense", category__isnull=True).update(category=other)


def remove_defaults(apps, schema_editor):
    Category = apps.get_model("transactions", "Category")
    Transaction = apps.get_model("transactions", "Transaction")
    Transaction.objects.update(category=None)
    Category.objects.filter(user=None, name__in=[name for name, _, _ in DEFAULTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0002_category"),
    ]

    operations = [
        migrations.RunPython(create_defaults, remove_defaults),
    ]
