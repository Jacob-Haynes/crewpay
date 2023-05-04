import json
from typing import Dict, List, Optional

import requests
from django.contrib.auth.decorators import user_passes_test
from rest_framework.authtoken.admin import User
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.staffology.dto_so_employer import StaffologyEmployer, DefaultPayOptions, LeaveSettings
from crewpay.models import Employer, StaffologyUser


@api_view(["GET"])
@user_passes_test(lambda u: u.is_superuser)
def employers_get(request: Request) -> Response:  # pylint: disable=unused-argument
    """Get all employers from staffology. This is used by admin users for problem-solving."""
    access_key = StaffologyUser.objects.get(user=request.user).staffology_key
    response = requests.get("https://api.staffology.co.uk/employers", auth=("username", access_key))
    if not response.ok:
        raise ValueError(response.text)
    return Response(response.json())


def create_employer(user: User, pay_period: str, tax_year: str, period_end: str, payment_date: str, so_employer: StaffologyEmployer) -> None:
    """Create a new employer in staffology and the db from their crewplanner data."""
    payload = so_employer.dict()
    employer_data = StaffologyEmployerAPI().create_employer(payload)
    schedule(employer_data["id"], pay_period, tax_year, period_end, payment_date)
    employer = Employer(user=user, id=employer_data["id"], pay_period=pay_period)
    employer.save()


def schedule(employer: str, pay_period: str, tax_year: str, period_end: str, payment_date: str) -> None:
    """Set up the pay schedule for a given employer."""
    payload = {"firstPeriodEndDate": period_end, "firstPaymentDate": payment_date}
    StaffologyEmployerAPI().update_pay_schedule(
        employer=employer, tax_year=tax_year, pay_period=pay_period, payload=payload
    )


def activate_payruns(schedule_to_run: Dict, employer: str, tax_year: str, pay_period: str) -> Dict:
    """Activate payruns for a given employers pay schedule."""
    # activate if needed
    if schedule_to_run["isRequired"] is True and schedule_to_run["hasOpenPayRunPeriod"] is not True:
        StaffologyEmployerAPI().start_next_payrun(employer, tax_year, pay_period)
    # get the next pay run
    pay_run = next_pay_run(StaffologyEmployerAPI().get_pay_schedule(employer, tax_year, pay_period))
    return pay_run


def next_pay_run(pay_schedule: Dict) -> Dict:
    """Identify the next pay run for a given pay schedule."""
    if "currentPayRun" in pay_schedule and pay_schedule["currentPayRun"]["metadata"]["isClosed"] is not True:
        pay_run = pay_schedule["currentPayRun"]
    elif pay_schedule["nextPayRun"]["isClosed"] is not True:
        pay_run = pay_schedule["nextPayRun"]
    else:
        return {}
    return pay_run


def staffology_employer(request) -> StaffologyEmployer:
    """creates a staffology employer object from the ui create employer form"""
    return StaffologyEmployer(
        name=request.POST["name"],
        defaultPayOptions=DefaultPayOptions(
            payPeriod=request.POST["pay_period"],
        ),
        leaveSettings=LeaveSettings(
            holidayType=request.POST["leave_type"],
            accrueSetAmount=request.POST["accrue_set_amount"],
            accrueHoursPerDay=request.POST["accrue_hours_per_day"],
            showAllowanceOnPayslip=request.POST["show_allowance_on_pay_slip"],
            showAhpOnPayslip=request.POST["show_ahp_on_pay_slip"],
            accruePaymentInLieuRate=request.POST["accrue_payment_in_lieu_rate"],
            accruePaymentInLieuPayAutomatically=request.POST["accrue_payment_in_lieu_pay_automatically"],
        )
    )


class StaffologyEmployerAPI:
    """Handles all staffology employer api calls"""

    def __init__(self, admin_user: str = "admin"):
        self.base_url = "https://api.staffology.co.uk/"
        self.admin_user = admin_user
        self.headers = {"content-type": "text/json"}
        access_key = StaffologyUser.objects.get(user__username=admin_user).staffology_key
        self.auth = ("username", access_key)

    def get(self, endpoint: str) -> requests.Response:
        response = requests.get(
            f"{self.base_url}{endpoint}",
            auth=self.auth,
            headers=self.headers,
        )
        if not response.ok:
            raise ValueError(response.text)
        return response

    def post(self, endpoint: str, data: Optional[str] = None) -> requests.Response:
        response = requests.post(
            f"{self.base_url}{endpoint}",
            auth=self.auth,
            data=data,
            headers=self.headers,
        )
        if not response.ok:
            raise ValueError(response.text)
        return response

    def put(self, endpoint: str, data: str, params: Optional[Dict] = None) -> requests.Response:
        response = requests.put(
            f"{self.base_url}{endpoint}", auth=self.auth, data=data, headers=self.headers, params=params
        )
        if not response.ok:
            raise ValueError(response.text)
        return response

    def delete(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        response = requests.delete(f"{self.base_url}{endpoint}", auth=self.auth, headers=self.headers, params=params)
        if not response.ok:
            raise ValueError(response.text)
        return response

    def update_pay_schedule(self, employer: str, tax_year: str, pay_period: str, payload) -> None:
        self.put(f"/employers/{employer}/schedules/{tax_year}/{pay_period}/1", data=json.dumps(payload))

    def create_employer(self, payload: Dict) -> Dict:
        return self.post("/employers", data=json.dumps(payload)).json()

    def get_pay_schedules(self, employer: str, tax_year: str) -> List[Dict]:
        return self.get(f"/employers/{employer}/schedules/{tax_year}").json()

    def get_pay_schedule(self, employer: str, tax_year: str, pay_period: str) -> Dict:
        return self.get(f"/employers/{employer}/schedules/{tax_year}/{pay_period}/1").json()

    def get_pay_run(self, employer: str, tax_year: str, pay_period: str, period: int) -> Dict:
        return self.get(f"/employers/{employer}/payrun/{tax_year}/{pay_period}/{period}").json()

    def start_next_payrun(self, employer: str, tax_year: str, pay_period: str) -> None:
        self.post(f"/employers/{employer}/payrun/{tax_year}/{pay_period}")

    def delete_pay_run(self, employer: str, tax_year: str, pay_period: str, period: int) -> None:
        self.delete(f"/employers/{employer}/payrun/{tax_year}/{pay_period}/{period}")

    def update_pay_run(self, employer: str, tax_year: str, pay_period: str, period: int) -> Dict:
        return self.put(f"/employers/{employer}/payrun/{tax_year}/{pay_period}/{period}").json()

    def import_pay(self, employer: str, pay_period: str, payload: List[Dict]) -> None:
        self.post(f"/employers/{employer}/payrun/{pay_period}/importpay?linesOnly=true", data=json.dumps(payload))
