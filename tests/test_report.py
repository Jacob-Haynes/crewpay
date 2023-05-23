import pytest

from api.v1.crewplanner.report import api_get_cp_report
from api.v1.staffology.payruns import payroll_function, compute_report_dates
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


def test_compute_report_dates():
    # Arrange
    payrun_start_date = "2023-04-01"
    payrun_end_date = "2023-04-30"
    pay_period = "Monthly"
    arrears = 1
    result_start = "2023-03-01"
    result_end = "2023-03-31"

    # Act
    earnings_period_start, earnings_period_end = compute_report_dates(payrun_start_date, payrun_end_date, pay_period, arrears)

    # Asset
    assert earnings_period_start == result_start
    assert earnings_period_end == result_end

