from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.staffology.employees.sync import sync_employees


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def sync_employees_get(request: Request) -> Response:
    """API endpoint for syncing employees"""
    employer = request.GET["employer"]
    return Response(sync_employees(employer))


# TODO: create this report in the UI - provide a way to view this with a user login?
