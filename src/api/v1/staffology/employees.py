from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.staffology.employee_manager import EmployeeManager
from api.v1.staffology.employers import update_employer_db


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def sync_employees(request: Request) -> Response:  # pylint: disable=unused-argument
    """API endpoint for syncing employees"""
    employer = request.GET["employer"]
    # check for employer updates
    update_employer_db(employer)
    # run employee manager
    manager = EmployeeManager(employer)
    response = manager.run()
    return response

# TODO: create this report in the UI - provide a way to view this with a user login?
