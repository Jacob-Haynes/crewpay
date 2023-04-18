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


class Employee(models.Model):
    employer = models.ForeignKey(Employer, related_name="employees", on_delete=models.CASCADE)
    crewplanner_id = models.CharField(unique=True, help_text="Crewplanner employee ID", max_length=500)
    staffology_id = models.CharField(unique=True, help_text="Crewplanner employee ID", max_length=500)
    status = models.CharField(help_text="ACTIVE or ARCHIVED (CP driven)", max_length=20)
