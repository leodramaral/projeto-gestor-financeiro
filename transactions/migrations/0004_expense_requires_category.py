from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0003_default_categories"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="transaction",
            constraint=models.CheckConstraint(
                condition=models.Q(("kind", "income"), ("category__isnull", False), _connector="OR"),
                name="transactions_expense_has_category",
            ),
        ),
    ]
