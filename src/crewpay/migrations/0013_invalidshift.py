# Generated by Django 4.2 on 2023-04-25 16:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("crewpay", "0012_employer_pay_period_alter_invalidemployee_employer"),
    ]

    operations = [
        migrations.CreateModel(
            name="InvalidShift",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("project", models.CharField(max_length=100)),
                ("employee", models.CharField(max_length=100)),
                ("error", models.TextField()),
                ("date_time", models.DateTimeField(auto_now_add=True)),
                (
                    "employer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invalid_shifts",
                        to="crewpay.employer",
                    ),
                ),
            ],
        ),
    ]
