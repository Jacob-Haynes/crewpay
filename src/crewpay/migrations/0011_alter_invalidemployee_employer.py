# Generated by Django 4.2 on 2023-04-20 12:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("crewpay", "0010_invalidemployee_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invalidemployee",
            name="employer",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="crewpay.employer"),
        ),
    ]
