from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.crewplanner.api.employee import CPEmployeeAPI
from api.v1.crewplanner.api.report import CPReportAPI
from crewpay.models import Employer


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)  # type: ignore[union-attr]
def employees_get(request: Request) -> Response:
    """Lists CrewPlanner employees for a given employer. This is used in the settings tab by admin users."""
    employer = request.query_params["employer"]
    user = Employer.objects.get(id=employer).user
    return Response(CPEmployeeAPI(user).get_employees)


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)  # type: ignore[union-attr]
def report_get(request: Request) -> Response:
    """Gets a specified CrewPlanner report. This is used in the settings tab by admin users."""
    employer = request.query_params["employer"]
    user = Employer.objects.get(id=employer).user
    start_date = request.query_params["start_date"]
    end_date = request.query_params["end_date"]
    return Response(CPReportAPI(user=user).get_report(start_date, end_date))
