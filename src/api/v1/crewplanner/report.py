from typing import Dict, List, Optional, Tuple

import requests
from django.contrib.auth.decorators import user_passes_test
from pydantic import ValidationError
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.crewplanner.dto_cp_shift import CPShift
from crewpay.models import CrewplannerUser, Employer, InvalidShift


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def report_get(request: Request) -> Response:  # pylint: disable=unused-argument
    """Gets a specified CrewPlanner report. This is used by admin users for problem-solving."""
    employer = request.query_params["employer"]
    user = Employer.objects.get(id=employer).user
    start_date = request.query_params["start_date"]
    end_date = request.query_params["end_date"]
    access_token = CrewplannerUser.objects.get(user=user).access_key
    stub = CrewplannerUser.objects.get(user=user).stub
    return Response(api_get_cp_report(stub, access_token, start_date, end_date))


def api_get_cp_report(stub: str, access_token: str, start_date: str, end_date: str) -> List[Dict]:
    """Gets reports from the CrewPlanner API."""
    response = requests.get(
        f"https://{stub}.crewplanner.com/api/v1/client/report?filter[after]={start_date}&filter[before]={end_date}"
        f"&filter[include_external_workers]=false&filter[contract_types]=VSA,EMP",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if not response.ok:
        raise ValueError(response.json())
    results = response.json()["data"]
    cursor = response.json()["meta"]["next_cursor"]

    while cursor is not None:
        response = requests.get(
            f"https://{stub}.crewplanner.com/api/v1/client/report?filter[after]={start_date}&filter[before]={end_date}"
            f"&filter[include_external_workers]=false&filter[contract_types]=VSA,EMP&cursor={cursor}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if not response.ok:
            raise ValueError(response.json())
        results += response.json()["data"]
        cursor = response.json()["meta"]["next_cursor"]

    return results


def create_shift_lines(user, start_date: str, end_date: str) -> Tuple[List[Optional[CPShift]], int]:
    """Gets a CP report and creates a list of CPShift objects."""
    employer = Employer.objects.get(user=user).id
    stub = CrewplannerUser.objects.get(user=user).stub
    access_key = CrewplannerUser.objects.get(user=user).access_key
    cp_report = api_get_cp_report(stub, access_key, start_date, end_date)
    shift_lines = [validate_shift_line(employer, shift) for shift in cp_report]
    failures = len(cp_report) - len(shift_lines)
    return shift_lines, failures


def validate_shift_line(employer: str, shift: Dict) -> Optional[CPShift]:
    """Validates and creates a CPShift object from a CrewPlanner report line."""
    try:
        cp_shift = CPShift(**shift)
        return cp_shift
    except ValidationError as e:
        error = str(e)
        project = f"{shift['project']['id']}, {shift['project']['name']}"
        employee = f"{shift['worker']['id']}, {shift['worker']['name']}"
        invalid_shift = InvalidShift(
            project=project,
            employee=employee,
            error=error,
            employer=Employer.objects.get(id=employer),
        )
        invalid_shift.save()
