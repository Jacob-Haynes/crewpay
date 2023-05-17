import pytest

from api.v1.crewplanner.report import api_get_cp_report
from api.v1.staffology.payruns import payroll_function
from crewpay.models import CrewplannerUser, Employer


def test_report_get():
    stub = "demo-4"
    start_date = "2023-01-13"
    end_date = "2023-04-13"
    access_token = CrewplannerUser.objects.get(stub=stub).access_key
    report = api_get_cp_report(stub, access_token, start_date, end_date)
    return


def test_run_payroll():
    employer = Employer.objects.get(user__username="CP demo").id
    tax_year = "Year2023"
    payroll_function(employer, tax_year)
    return
