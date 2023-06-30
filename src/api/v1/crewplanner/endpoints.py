from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.crewplanner.employees import api_get_cp_employees
from api.v1.crewplanner.report import api_get_cp_report
from crewpay.models import CrewplannerUser, Employer


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def employees_get(request: Request) -> Response:
    """Lists CrewPlanner employees for a given employer. This is used by admin users for problem-solving."""
    employer = request.query_params["employer"]
    user = Employer.objects.get(id=employer).user
    stub = CrewplannerUser.objects.get(user=user).stub
    access_token = CrewplannerUser.objects.get(user=user).access_key
    results = api_get_cp_employees(stub, access_token)
    return Response(results)


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def report_get(request: Request) -> Response:
    """Gets a specified CrewPlanner report. This is used by admin users for problem-solving."""
    employer = request.query_params["employer"]
    user = Employer.objects.get(id=employer).user
    start_date = request.query_params["start_date"]
    end_date = request.query_params["end_date"]
    access_token = CrewplannerUser.objects.get(user=user).access_key
    stub = CrewplannerUser.objects.get(user=user).stub
    return Response(api_get_cp_report(stub, access_token, start_date, end_date))
