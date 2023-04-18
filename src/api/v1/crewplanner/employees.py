from typing import List

import requests
from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.crewplanner.dto import CPEmployee
from crewpay.models import CrewplannerUser


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def employees_get(request: Request) -> Response:  # pylint: disable=unused-argument
    stub = request.query_params["stub"]
    access_token = CrewplannerUser.objects.get(stub=stub).access_key
    employees = crewplanner_employees_get(stub, access_token)
    return Response(employees)


def crewplanner_employees_get(stub: str, access_token: str) -> List[CPEmployee]:  # pylint: disable=unused-argument
    response = requests.get(
        f"https://{stub}.crewplanner.com/api/v1/client/employees?filter[status]=verified"
        f"&filter[contract_type]=VSA&filter[contract_type]=EMP",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if not response.ok:
        raise ValueError(response.json())

    return [CPEmployee(**employee) for employee in response.json()["data"]]
