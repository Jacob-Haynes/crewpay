import pytest

from api.v1.crewplanner.report import api_get_cp_report
from crewpay.models import CrewplannerUser, Employer


def test_report_get():
    stub = "demo-4"
    start_date = "2023-01-13"
    end_date = "2023-04-13"
    access_token = CrewplannerUser.objects.get(stub=stub).access_key
    report = api_get_cp_report(stub, access_token, start_date, end_date)
    return


# def test_run_payroll():
#     employer = Employer.objects.get(user__username="UK Payroll Test").id
#     tax_year = "Year2023"
#     run_payroll(employer, tax_year)
#     return
