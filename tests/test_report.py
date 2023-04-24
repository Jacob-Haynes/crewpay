import pytest

from api.v1.crewplanner.report import crewplanner_report_get
from crewpay.models import CrewplannerUser


def test_report_get():
    stub = "demo-4"
    start_date = "2023-01-13"
    end_date = "2023-04-13"
    access_token = CrewplannerUser.objects.get(stub=stub).access_key
    report = crewplanner_report_get(stub, access_token, start_date, end_date)
    return
