import json

import requests
from django.contrib.auth.decorators import user_passes_test
from rest_framework.authtoken.admin import User
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from crewpay.models import Employer, StaffologyUser


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def employers_get(request: Request) -> Response:  # pylint: disable=unused-argument
    access_key = StaffologyUser.objects.get(user=request.user).staffology_key
    response = requests.get("https://api.staffology.co.uk/employers", auth=("username", access_key))
    if not response.ok:
        raise ValueError(response.text)
    return Response(response.json())


def create_employer(user: User, access_key: str) -> None:  # pylint: disable=unused-argument
    payload = {"name": user.username}
    response = requests.post(
        "https://api.staffology.co.uk/employers",
        auth=("username", access_key),
        data=json.dumps(payload),
        headers={"content-type": "text/json"},
    )
    if not response.ok:
        raise ValueError(response.text)
    employer = Employer(user=user, id=response.json()["id"])
    employer.save()
