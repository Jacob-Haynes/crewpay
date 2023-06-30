from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.staffology.payroll.payruns import run_payroll


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def run_payroll_get(request: Request) -> Response:
    """API endpoint for running payroll"""
    employer = request.GET["employer"]
    tax_year = request.GET["tax_year"]
    arrears = int(request.GET["period_arrears"])
    result = run_payroll(employer, tax_year, arrears)
    return Response(result)

# TODO: payrun table UI
