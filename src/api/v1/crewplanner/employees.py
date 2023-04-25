from typing import Dict, List, Optional

import requests
from django.contrib.auth.decorators import user_passes_test
from pydantic import ValidationError
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.crewplanner.dto_cp_employee import CPEmployee
from crewpay.models import CrewplannerUser, Employer, InvalidEmployee


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def employees_get(request: Request) -> Response:  # pylint: disable=unused-argument
    employer = request.query_params["employer"]
    user = Employer.objects.get(id=employer).user
    stub = CrewplannerUser.objects.get(user=user).stub
    access_token = CrewplannerUser.objects.get(user=user).access_key
    results = api_get_employees(stub, access_token)
    return Response(results)


def crewplanner_employees_get(stub: str, access_token: str) -> List[CPEmployee]:  # pylint: disable=unused-argument
    results = api_get_employees(stub, access_token)
    return [validate_employee(stub, employee) for employee in results]


def validate_employee(stub: str, employee: Dict) -> Optional[CPEmployee]:
    try:
        cp_employee = CPEmployee(**employee)
        return cp_employee
    except ValidationError as e:
        error = str(e)
        name = f"{employee['first_name']} {employee['last_name']}"
        invalid_employee = InvalidEmployee(
            employee_id=employee["id"],
            name=name,
            error=error,
            employer=Employer.objects.get(user__crewplanner_user__stub=stub),
        )
        invalid_employee.save()


def api_get_employees(stub: str, access_token: str) -> List[Dict]:  # pylint: disable=unused-argument
    response = requests.get(
        f"https://{stub}.crewplanner.com/api/v1/client/employees?filter[status]=verified"
        f"&filter[contract_type]=VSA&filter[contract_type]=EMP&filter[payrolling]=no",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if not response.ok:
        raise ValueError(response.json())
    results = response.json()["data"]
    cursor = response.json()["meta"]["next_cursor"]

    while cursor is not None:
        response = requests.get(
            f"https://{stub}.crewplanner.com/api/v1/client/employees?filter[status]=verified"
            f"&filter[contract_type]=VSA&filter[contract_type]=EMP&filter[payrolling]=no&cursor={cursor}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if not response.ok:
            raise ValueError(response.json())
        results += response.json()["data"]
        cursor = response.json()["meta"]["next_cursor"]
    return results
