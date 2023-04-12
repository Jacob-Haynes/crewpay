from django.contrib.auth.models import User
from django.db import models


class CrewplannerUser(models.Model):
    user = models.ForeignKey(User, related_name="crewplanner_user", on_delete=models.CASCADE)
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
