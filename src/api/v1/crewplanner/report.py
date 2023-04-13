import requests
from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from crewpay.models import CrewplannerUser


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def report_get(request: Request) -> Response:  # pylint: disable=unused-argument
    stub = request.query_params["stub"]
    start_date = request.query_params["start_date"]
    end_date = request.query_params["end_date"]
    access_token = CrewplannerUser.objects.get(stub=stub).access_key
    response = requests.get(
        f"https://{stub}.crewplanner.com/api/v1/client/report?filter[after]={start_date}&filter[before]={end_date}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if not response.ok:
        raise ValueError(response.json())
    return Response(response.json())
