# Generated by Django 4.2 on 2023-05-03 13:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("crewpay", "0015_rename_payrollcode_employee_payroll_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employee",
            name="payroll_code",
            field=models.CharField(help_text="Staffology payroll code", max_length=20),
        ),
    ]
