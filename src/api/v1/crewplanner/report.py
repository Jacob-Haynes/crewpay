import requests
from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.staffology.employers import next_pay_run, StaffologyAPI, open_schedules, active_schedules
from crewpay.models import CrewplannerUser


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def report_get(request: Request) -> Response:  # pylint: disable=unused-argument
    stub = request.query_params["stub"]
    start_date = request.query_params["start_date"]
    end_date = request.query_params["end_date"]
    access_token = CrewplannerUser.objects.get(stub=stub).access_key
    return crewplanner_report_get(stub, access_token, start_date, end_date)


# TODO: do we need FPT as well?

def crewplanner_report_get(stub: str, access_token: str, start_date: str, end_date: str) -> Response:
    response = requests.get(
        f"https://{stub}.crewplanner.com/api/v1/client/report?filter[after]={start_date}&filter[before]={end_date}"
        f"&filter[include_external_workers]=false&filter[contract_types]=VSA,EMP",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if not response.ok:
        raise ValueError(response.json())
    results = response.json()["data"]
    cursor = response.json()["meta"]["next_cursor"]

    while cursor is not None:
        response = requests.get(
            f"https://{stub}.crewplanner.com/api/v1/client/report?filter[after]={start_date}&filter[before]={end_date}"
            f"&filter[include_external_workers]=false&filter[contract_types]=VSA,EMP&cursor={cursor}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if not response.ok:
            raise ValueError(response.json())
        results += response.json()["data"]
        cursor = response.json()["meta"]["next_cursor"]

    return Response(results)

def run_payroll(employer, tax_year):
    # create missing pay runs
    schedules_to_run = open_schedules(employer, tax_year)
    for schedule_to_run in schedules_to_run:
        # activate the pay runs
        pay_run = next_pay_run(employer, schedule_to_run)
        StaffologyAPI().start_next_payrun(employer, tax_year, pay_run["payPeriod"])
    # process pay runs
    schedules_to_process = active_schedules(employer, tax_year)
    for schedule_to_process in schedules_to_process:
        # get the pay run
        pay_run = next_pay_run(employer, schedule_to_process)
        # get the cp report for the pay period
        # group by employee
        # create paylines for each employee
        # update payrun


# TODO: Payoptions and payruns


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
