from django.contrib.auth.models import User
from django.db import models


class CrewplannerUser(models.Model):
    user = models.OneToOneField(User, related_name="crewplanner_user", on_delete=models.CASCADE)
    access_key = models.CharField(
        unique=True,
        help_text="Required. Crewplanner API key",
        max_length=500,
    )
    stub = models.CharField(
        unique=True,
        help_text="Required. Crewplanner Stub",
        max_length=500,
    )


class StaffologyUser(models.Model):
    user = models.OneToOneField(User, related_name="staffology_user", on_delete=models.CASCADE)
    staffology_key = models.CharField(
        unique=True,
        help_text="Required. Staffology API key",
        max_length=500,
    )


class Employer(models.Model):
    user = models.OneToOneField(User, related_name="employer", on_delete=models.CASCADE)
    id = models.CharField(
        primary_key=True,
        unique=True,
        help_text="staffology employer ID",
        max_length=500,
    )
    pay_period = models.CharField(max_length=20, default="Monthly")


class Employee(models.Model):
    employer = models.ForeignKey(Employer, related_name="employees", on_delete=models.CASCADE)
    crewplanner_id = models.CharField(unique=True, help_text="Crewplanner employee ID", max_length=500)
    staffology_id = models.CharField(unique=True, help_text="Crewplanner employee ID", max_length=500)
    status = models.CharField(help_text="ACTIVE or ARCHIVED (CP driven)", max_length=20)


class InvalidEmployee(models.Model):
    employee_id = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    error = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    employer = models.ForeignKey(Employer, related_name="invalid_employees", on_delete=models.CASCADE)


class InvalidShift(models.Model):
    project = models.CharField(max_length=100)
    employee = models.CharField(max_length=100)
    error = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    employer = models.ForeignKey(Employer, related_name="invalid_shifts", on_delete=models.CASCADE)
