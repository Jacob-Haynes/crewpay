import json
from typing import Dict, List, Optional

import requests
from django.contrib.auth.decorators import user_passes_test
from pydantic import ValidationError
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.crewplanner.dto.dto_cp_employee import CPEmployee
from crewpay.models import CrewplannerUser, Employer, InvalidEmployee

""" Handles all employee endpoint related CrewPlanner functions """


def crewplanner_employees_get(stub: str, access_token: str) -> List[CPEmployee]:  # pylint: disable=unused-argument
    """Get all and validating CrewPlanner employees."""
    results = api_get_cp_employees(stub, access_token)
    return [validate_employee(stub, employee) for employee in results]


def validate_employee(stub: str, employee: Dict) -> Optional[CPEmployee]:
    """Validates a CrewPlanner employee by checking for missing required fields. Saves the invalid employee creation
    attempt to the DB with the reason for failure."""
    try:
        for field in ["payroll_employee_statement", "payroll_student_loan_plan", "payroll_postgrad_loan"]:
            field_value = employee["custom_fields"].get(field, [])
            if isinstance(field_value, list) and len(field_value) > 0:
                employee["custom_fields"][field] = field_value[0]
            else:
                employee["custom_fields"][field] = None
        cp_employee = CPEmployee(**employee)
        return cp_employee
    except ValidationError as e:
        name = f"{employee['first_name']} {employee['last_name']}"
        invalid_employee = InvalidEmployee(
            employee_id=employee["id"],
            name=name,
            error=json.dumps(e.errors()),
            employer=Employer.objects.get(user__crewplanner_user__stub=stub),
        )
        invalid_employee.save()


def api_get_cp_employees(stub: str, access_token: str) -> List[Dict]:  # pylint: disable=unused-argument
    """Gets employees from the CrewPlanner API."""
    response = requests.get(
        f"https://{stub}.crewplanner.com/api/v1/client/employees?filter[status]=verified&filter["
        f"contract_types][]=VSA&filter[contract_types][]=EMP&filter[payrolling]=no",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if not response.ok:
        raise ValueError(response.json())
    results = response.json()["data"]
    cursor = response.json()["meta"]["next_cursor"]
    while cursor is not None:
        response = requests.get(
            f"https://{stub}.crewplanner.com/api/v1/client/employees?filter[status]=verified"
            f"&filter[contract_types][]=VSA&filter[contract_types][]=EMP&filter[payrolling]=no&cursor={cursor}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if not response.ok:
            raise ValueError(response.json())
        results += response.json()["data"]
        cursor = response.json()["meta"]["next_cursor"]

    return results
