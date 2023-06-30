import requests
from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from crewpay.models import StaffologyUser


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def employers_get(request: Request) -> Response:
    """Get all employers from staffology. This is used by admin users for problem-solving."""
    access_key = StaffologyUser.objects.get(user=request.user).staffology_key
    response = requests.get("https://api.staffology.co.uk/employers", auth=("username", access_key), timeout=60)
    if not response.ok:
        raise ValueError(response.text)
    return Response(response.json())
