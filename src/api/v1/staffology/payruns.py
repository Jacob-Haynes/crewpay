from typing import Dict, Optional

from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.crewplanner.report import create_shift_lines
from api.v1.staffology.employers import StaffologyAPI, activate_payruns
from crewpay.models import Employer


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def run_payroll(request: Request):
    employer = request.GET["employer"]
    tax_year = request.GET["tax_year"]
    user = Employer.objects.get(id=employer).user
    pay_period = Employer.objects.get(id=employer).pay_period
    # get pay schedules
    schedule_to_run = StaffologyAPI().get_pay_schedule(employer, tax_year, pay_period)
    # activate/get the payrun
    pay_run = activate_payruns(schedule_to_run, employer, tax_year, pay_period)
    # get the full payrun to edit
    pay_run = StaffologyAPI().get_pay_run(employer, tax_year, pay_period, pay_run["metadata"]["periodNumber"])
    # get shift lines from CP
    start_date = pay_run["startDate"]
    end_date = pay_run["endDate"]
    shift_lines = create_shift_lines(user, start_date, end_date)
    ###
    # TODO: group by employee
    ###
    # TODO: convert to paylines for each employee
    ###
    # TODO: update the payrun
    return Response(shift_lines)

    # # get the cp report for the pay period
    # start_date = pay_run["startDate"]
    # end_date = pay_run["endDate"]
    # stub = CrewplannerUser.objects.get(user=user).stub
    # access_key = CrewplannerUser.objects.get(user=user).access_key
    # cp_report = crewplanner_report_get(stub, access_key, start_date, end_date)
    # shift_lines = [validate_shift_line(employer, shift) for shift in cp_report]
    # # group by employee

    # create paylines for each employee

    # update payrun


# def create_pay_line:
#     # https://app.staffology.co.uk/api/docs/guides/gettingstarted/payoptions
#     # "regularPayLines": [
#     #     {
#     #         "value": 50.0,
#     #         "description": "Performance bonus for October",
#     #         "code": "BONUS"
#     #     }
#     # ],
#     return
