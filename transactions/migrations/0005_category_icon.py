from django.db import migrations, models

# Frozen on purpose: a migration must not change when the app's constants do.
EMOJI_TO_ICON = {
    "🍔": "utensils",
    "🚗": "car",
    "🏠": "house",
    "🎮": "gamepad-2",
    "💊": "pill",
    "📦": "package",
    "🛒": "shopping-cart",
    "🎓": "graduation-cap",
    "👕": "shirt",
    "🐶": "paw-print",
    "🧳": "luggage",
    "🎁": "gift",
    "💡": "lightbulb",
    "📱": "smartphone",
    "💳": "credit-card",
    "☕": "coffee",
    "💪": "dumbbell",
    "🎬": "clapperboard",
    "👶": "baby",
    "🧾": "receipt",
}
ICON_TO_EMOJI = {icon: emoji for emoji, icon in EMOJI_TO_ICON.items()}
FALLBACK_ICON = "package"
FALLBACK_EMOJI = "📦"


def _convert(apps, mapping, fallback):
    Category = apps.get_model("transactions", "Category")
    for category in Category.objects.all():
        category.icon = mapping.get(category.icon, fallback)
        category.save(update_fields=["icon"])


def emoji_to_icon(apps, schema_editor):
    _convert(apps, EMOJI_TO_ICON, FALLBACK_ICON)


def icon_to_emoji(apps, schema_editor):
    _convert(apps, ICON_TO_EMOJI, FALLBACK_EMOJI)


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0004_expense_requires_category"),
    ]

    operations = [
        migrations.RenameField(model_name="category", old_name="emoji", new_name="icon"),
        migrations.AlterField(
            model_name="category",
            name="icon",
            field=models.CharField(default="package", max_length=24, verbose_name="ícone"),
        ),
        migrations.RunPython(emoji_to_icon, icon_to_emoji),
    ]
