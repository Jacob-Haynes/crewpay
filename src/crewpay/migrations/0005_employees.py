# Generated by Django 4.2 on 2023-04-17 13:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("crewpay", "0004_employer"),
    ]

    operations = [
        migrations.CreateModel(
            name="Employees",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("crewplanner_id", models.CharField(help_text="Crewplanner employee ID", max_length=500, unique=True)),
                ("staffology_id", models.CharField(help_text="Crewplanner employee ID", max_length=500, unique=True)),
                (
                    "employer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="employees", to="crewpay.employer"
                    ),
                ),
            ],
        ),
    ]
