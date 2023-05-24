from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.staffology.payroll_manager import PayrollManager


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def run_payroll(request: Request) -> Response:
    """API endpoint for running payroll"""
    employer = request.GET["employer"]
    tax_year = request.GET["tax_year"]
    arrears = int(request.GET["period_arrears"])
    manager = PayrollManager(employer=employer, tax_year=tax_year, arrears=arrears)
    result = manager.process_payroll()
    return Response(result)
